"""Archive the official public package landing page without transferring data."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OFFICIAL = ROOT / "source_cache" / "upenn_gbm_collection_page_2026-10-01.html"
OUT = ROOT / "source_cache" / "upenn_gbm_public_package_page_2026-10-01"


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.hrefs.append(attrs["href"])
        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    links = Links()
    links.feed(OFFICIAL.read_text(encoding="utf-8"))
    candidates = [url for url in links.hrefs
                  if url.startswith("https://faspex.cancerimagingarchive.net/aspera/faspex/public/package?")]
    if not candidates:
        raise ValueError("Official page has no NIfTI public package link")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(candidates[0], headers={"User-Agent": "MRI-source-audit/1.0"})
    with opener.open(request, timeout=35) as response:
        raw = response.read(2_000_001)
        if response.status != 200 or len(raw) > 2_000_000 or "text/html" not in response.headers.get("Content-Type", ""):
            raise RuntimeError("Expected bounded official HTML page")
        final_url = response.geturl()
    page = Links()
    page.feed(raw.decode("utf-8", "replace"))
    OUT.mkdir(parents=True)
    (OUT / "landing.html").write_bytes(raw)
    index = {
        "official_collection_page": OFFICIAL.relative_to(ROOT).as_posix(),
        "official_link_path": urllib.parse.urlsplit(candidates[0]).path,
        "official_link_sha256": hashlib.sha256(candidates[0].encode()).hexdigest(),
        "response_path": urllib.parse.urlsplit(final_url).path,
        "response_bytes": len(raw),
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "scripts": [urllib.parse.urlsplit(urllib.parse.urljoin(final_url, src)).path for src in page.scripts],
        "patient_pixels_read": False,
        "package_transfer_started": False,
    }
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
