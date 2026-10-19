import json
import time
from typing import Any

import httpx

from open_decisions_ingest_at import BASE_URL, LIST_ID

USER_AGENT = "open-decisions-ingest-at/0.1 (+https://github.com; open data, CC BY 4.0 consumer)"


class ParliamentClient:
    def __init__(self, base_url: str = BASE_URL, delay_seconds: float = 0.5, timeout: float = 90.0):
        self.base_url = base_url
        self.delay_seconds = delay_seconds
        self._http = httpx.Client(base_url=base_url, timeout=timeout, headers={"User-Agent": USER_AGENT}, follow_redirects=True)
        self._last = 0.0

    def _throttle(self) -> None:
        wait = self._last + self.delay_seconds - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def list_items(self, gp: str) -> dict[str, Any]:
        self._throttle()
        r = self._http.post(
            f"/Filter/api/filter/data/{LIST_ID}",
            params={"js": "eval", "showAll": "true"},
            content=json.dumps({"GP_CODE": [gp]}),
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        return r.json()

    def get_item(self, gp: str, ityp: str, inr: str) -> dict[str, Any]:
        self._throttle()
        r = self._http.get(f"/gegenstand/{gp}/{ityp}/{inr}", params={"json": "TRUE"})
        r.raise_for_status()
        return r.json()

    def get_document(self, path: str) -> tuple[bytes, str | None]:
        self._throttle()
        r = self._http.get(path)
        r.raise_for_status()
        return r.content, r.headers.get("content-type")

    def close(self) -> None:
        self._http.close()


def list_rows(listing: dict[str, Any]) -> list[dict[str, Any]]:
    labels = [h["label"] for h in listing["header"]]
    return [dict(zip(labels, row, strict=False)) for row in listing["rows"]]


def parse_his_url(his_url: str) -> tuple[str, str, str] | None:
    parts = his_url.strip("/").split("/")
    if len(parts) != 4 or parts[0] != "gegenstand":
        return None
    return parts[1], parts[2], parts[3]
