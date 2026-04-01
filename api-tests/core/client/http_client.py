from __future__ import annotations

from dataclasses import dataclass
import requests


@dataclass
class HttpClient:
    base_url: str
    timeout_seconds: int = 20

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        return requests.request(method=method, url=url, timeout=self.timeout_seconds, **kwargs)
