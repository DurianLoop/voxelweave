"""Archive the public IBM Aspera downloads page and extract link targets."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache" / "ibm_aspera_downloads_2026-10-01"
URL = "https://www.ibm.com/products/aspera/downloads"


class Hrefs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(urllib.request.Request(URL, headers={"User-Agent": "MRI-source-audit/1.0"}), timeout=40) as response:
        raw = response.read(1_000_001)
        if response.status != 200 or len(raw) > 1_000_000:
            raise RuntimeError("Unexpected IBM downloads page")
    parser = Hrefs()
    parser.feed(raw.decode("utf-8", "replace"))
    selected = sorted({href for href in parser.hrefs
                       if any(term in href.lower() for term in ("aspera", "connect", "download", "windows"))})
    OUT.mkdir(parents=True)
    (OUT / "page.html").write_bytes(raw)
    result = {"url": URL, "bytes": len(raw),
              "sha256": hashlib.sha256(raw).hexdigest(),
              "all_href_count": len(parser.hrefs), "selected_links": selected}
    (OUT / "index.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
