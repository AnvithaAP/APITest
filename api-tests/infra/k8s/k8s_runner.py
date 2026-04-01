from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KubernetesJobSpec:
    job_name: str
    image: str
    command: list[str]
    namespace: str = "qa"
    parallelism: int = 1
    completions: int = 1


class KubernetesRunner:
    """Apply Kubernetes Job manifests to a real cluster via kubectl."""

    def __init__(self, kubectl_bin: str = "kubectl") -> None:
        self.kubectl_bin = kubectl_bin

    def build_job_manifest(self, spec: KubernetesJobSpec) -> dict:
        return {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {"name": spec.job_name, "namespace": spec.namespace},
            "spec": {
                "parallelism": spec.parallelism,
                "completions": spec.completions,
                "template": {
                    "metadata": {"labels": {"app": spec.job_name}},
                    "spec": {
                        "restartPolicy": "Never",
                        "containers": [
                            {
                                "name": "test-runner",
                                "image": spec.image,
                                "command": spec.command,
                            }
                        ],
                    },
                },
                "backoffLimit": 0,
            },
        }

    def apply_job(self, spec: KubernetesJobSpec) -> dict:
        manifest = self.build_job_manifest(spec)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            json.dump(manifest, tmp)
            tmp_path = Path(tmp.name)

        cmd = [self.kubectl_bin, "apply", "-f", str(tmp_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        tmp_path.unlink(missing_ok=True)

        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "manifest": manifest,
            "command": cmd,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Kubernetes Job for distributed API tests")
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--namespace", default="qa")
    parser.add_argument("--parallelism", type=int, default=1)
    parser.add_argument("--completions", type=int, default=1)
    parser.add_argument("--cmd", nargs="+", required=True, help="Container command array")
    args = parser.parse_args()

    runner = KubernetesRunner()
    result = runner.apply_job(
        KubernetesJobSpec(
            job_name=args.job_name,
            image=args.image,
            command=args.cmd,
            namespace=args.namespace,
            parallelism=max(1, args.parallelism),
            completions=max(1, args.completions),
        )
    )
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
