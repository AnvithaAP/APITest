from __future__ import annotations

from pathlib import Path

import pytest

from tagging.tag_governance import TagGovernance


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_feature_file_requires_key_value_tags(tmp_path: Path) -> None:
    feature = tmp_path / "bad.feature"
    feature.write_text("@scope\nFeature: sample\n", encoding="utf-8")

    report = TagGovernance().scan([tmp_path])

    assert not report.ok
    assert any("key:value" in issue.message for issue in report.issues)


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_pytest_file_with_required_tags_passes(tmp_path: Path) -> None:
    test_file = tmp_path / "test_sample.py"
    test_file.write_text(
        "\n".join(
            [
                "import pytest",
                "@pytest.mark.tag(",
                "    \"scope=api\",",
                "    \"intent=functional\",",
                "    \"concern=data\",",
                "    \"type=smoke\",",
                "    \"module=platform\",",
                "    \"release=R2026.04-S1\",",
                ")",
                "def test_ok():",
                "    assert True",
            ]
        ),
        encoding="utf-8",
    )

    report = TagGovernance().scan([tmp_path])

    assert report.ok


@pytest.mark.tag("scope=api", "intent=functional", "concern=contract", "type=system", "module=platform", "release=R2026.04-S1")
def test_feature_file_enforces_intent_to_type_governance_rules(tmp_path: Path) -> None:
    feature = tmp_path / "api_health.feature"
    feature.write_text(
        "\n".join(
            [
                "@scope:api",
                "@intent:functional",
                "@concern:data",
                "@type:load",
                "@module:platform",
                "@release:R2026.04-S1",
                "Feature: API health checks",
            ]
        ),
        encoding="utf-8",
    )

    report = TagGovernance().scan([tmp_path])

    assert not report.ok
    assert any("functional type must be one of" in issue.message for issue in report.issues)
