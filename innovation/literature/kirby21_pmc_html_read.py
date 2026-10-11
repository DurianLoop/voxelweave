"""Archive and extract the public PMC HTML for the Kirby21 data paper."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/kirby21_pmc_html_2026-10-01"
URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC3020263/"


class Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            value = " ".join(data.split())
            if value:
                self.parts.append(value)


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite article read")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(URL, headers={"User-Agent": "MRI-literature-audit/1.0"})
    with opener.open(request, timeout=30) as response:
        status, final_url = response.status, response.url
        raw = response.read(3_000_001)
    if status != 200 or len(raw) > 3_000_000:
        raise ValueError("Unexpected article response")
    (OUT / "article.html").write_bytes(raw)
    parser = Text()
    parser.feed(raw.decode("utf-8", errors="replace"))
    text = "\n".join(parser.parts) + "\n"
    (OUT / "article_extracted.txt").write_text(text, encoding="utf-8")
    index = {"url": URL, "final_url": final_url, "status": status,
             "html_bytes": len(raw), "html_sha256": hashlib.sha256(raw).hexdigest(),
             "extracted_bytes": len(text.encode("utf-8")),
             "extracted_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
