"""Fetch the exact MSI linked on IBM's public Aspera downloads page."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PAGE = ROOT / "literature" / "source_cache" / "ibm_aspera_downloads_2026-10-01" / "page.html"
OUT = ROOT / "tools" / "ibm_aspera_connect_4.2.19.956"
NAME = "ibm-aspera-connect_4.2.19.956-HEAD_win32_AMD64.msi"
EXPECTED_BYTES = 53_911_552


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    links = Links()
    links.feed(SOURCE_PAGE.read_text(encoding="utf-8"))
    matches = [url for url in links.links if url.endswith("/" + NAME)]
    if len(matches) != 1 or not matches[0].startswith("https://d3gcli72yxqn2z.cloudfront.net/downloads/connect/latest/bin/"):
        raise ValueError("Official IBM link not uniquely found")
    url = matches[0]
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
    with opener.open(request, timeout=90) as response:
        declared = int(response.headers.get("Content-Length", "0"))
        if response.status != 200 or declared != EXPECTED_BYTES:
            raise RuntimeError("Unexpected MSI response size or status")
        data = response.read(EXPECTED_BYTES + 1)
    if len(data) != EXPECTED_BYTES or data[:8] != bytes.fromhex("d0cf11e0a1b11ae1"):
        raise ValueError("Incomplete or non-MSI download")
    OUT.mkdir(parents=True)
    path = OUT / NAME
    path.write_bytes(data)
    result = {"source_page": SOURCE_PAGE.relative_to(ROOT).as_posix(),
              "url": url, "file": path.relative_to(ROOT).as_posix(),
              "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
              "installed": False, "executed": False}
    (OUT / "source.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
