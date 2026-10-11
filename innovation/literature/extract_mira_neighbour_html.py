"""Extract section-labelled text from archived arXiv HTML article bodies."""
from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_cache/mira_four_seed_fulltext_routes_2026-10-01"
DEST = ROOT / "extracted"
NAMES = ("mind_detail_arxiv_html", "structural_uncertainty_arxiv_html")
BLOCKS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "tr", "figcaption"}


class ArticleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.article_depth = 0
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "article" and not self.article_depth:
            self.article_depth = 1
            return
        if not self.article_depth:
            return
        if tag == "article":
            self.article_depth += 1
        if tag in {"script", "style", "nav"}:
            self.skip_depth += 1
        if not self.skip_depth and tag in BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if not self.article_depth:
            return
        if tag in {"script", "style", "nav"} and self.skip_depth:
            self.skip_depth -= 1
        if tag in BLOCKS and not self.skip_depth:
            self.parts.append("\n")
        if tag == "article":
            self.article_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.article_depth and not self.skip_depth and data.strip():
            self.parts.append(data)


def main() -> None:
    records = {}
    for name in NAMES:
        source = SOURCE / (name + ".html")
        target = DEST / (name + ".txt")
        if target.exists():
            raise FileExistsError(target)
        parser = ArticleText()
        parser.feed(source.read_text(encoding="utf-8"))
        lines = [" ".join(line.split()) for line in "".join(parser.parts).splitlines()]
        text = "\n".join(line for line in lines if line) + "\n"
        if len(text) < 10000:
            raise ValueError(f"Article extraction unexpectedly short: {name}")
        target.write_text(text, encoding="utf-8")
        records[name] = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                         "extracted_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                         "characters": len(text)}
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
