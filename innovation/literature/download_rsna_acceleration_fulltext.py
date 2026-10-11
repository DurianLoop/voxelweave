"""Archive the accessible PMC full text for a focused MIRA prior-art check."""
from __future__ import annotations

import hashlib
import html
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC9745443/"
RAW = ROOT / "source_cache/rsna_acceleration_limits_2022_pmc.html"
TEXT = ROOT / "extracted/rsna_acceleration_limits_2022_pmc.txt"
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class ArticleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.article_depth = 0
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "article" and self.article_depth == 0:
            self.article_depth = 1
        elif self.article_depth and tag not in VOID_TAGS:
            self.article_depth += 1
        if self.article_depth and tag in {"script", "style", "svg"}:
            self.skip_depth += 1
        if self.article_depth and tag in {"h1", "h2", "h3", "h4", "p", "li", "table", "tr", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self.article_depth and tag in {"h1", "h2", "h3", "h4", "p", "li", "tr"}:
            self.parts.append("\n")
        if self.article_depth and tag in {"script", "style", "svg"} and self.skip_depth:
            self.skip_depth -= 1
        if self.article_depth:
            self.article_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.article_depth and not self.skip_depth:
            self.parts.append(data)


def main() -> None:
    if RAW.exists() or TEXT.exists():
        raise FileExistsError("Refusing to overwrite full-text evidence")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(URL, headers={"User-Agent": "MRI-MIRA-prior-art-screen/1.0"})
    with opener.open(request, timeout=40) as response:
        raw = response.read()
        if response.status != 200 or b"<article" not in raw:
            raise ValueError("PMC response lacks article full text")
    parser = ArticleText()
    parser.feed(raw.decode("utf-8", "replace"))
    lines = [" ".join(line.split()) for line in html.unescape("".join(parser.parts)).splitlines()]
    extracted = "\n".join(line for line in lines if line)
    if len(extracted) < 10000:
        raise ValueError(f"Unexpectedly short extraction: {len(extracted)}")
    RAW.write_bytes(raw)
    TEXT.write_text(extracted + "\n", encoding="utf-8")
    print({"url": URL, "html_bytes": len(raw), "html_sha256": hashlib.sha256(raw).hexdigest(),
           "extracted_characters": len(extracted),
           "text_sha256": hashlib.sha256(TEXT.read_bytes()).hexdigest()})


if __name__ == "__main__":
    main()
