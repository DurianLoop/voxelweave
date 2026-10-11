"""Extract relevant text and link targets from archived NITRC project HTML."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin


PAGE = Path(__file__).resolve().parent / "source_cache/kirby21_public_metadata_2026-10-01/nitrc_project.html"
BASE = "https://www.nitrc.org/projects/multimodal/"
TERMS = ("reproduc", "repeat", "t2", "multi", "license", "files", "download", "access", "landman")


class Extractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.link: str | None = None
        self.fragments: list[str] = []
        self.rows: list[tuple[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.link = dict(attrs).get("href")
            self.fragments = []

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            if self.link is not None:
                self.fragments.append(value)
            elif any(term in value.lower() for term in TERMS):
                self.rows.append((value[:320], None))

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.link is not None:
            label = " ".join(self.fragments)
            if any(term in label.lower() for term in TERMS) or any(
                term in self.link.lower() for term in ("frs", "license", "download")):
                self.rows.append((label[:320], urljoin(BASE, self.link)))
            self.link = None
            self.fragments = []


if __name__ == "__main__":
    parser = Extractor()
    parser.feed(PAGE.read_text(encoding="utf-8", errors="replace"))
    for label, link in parser.rows:
        print(label, f"=> {link}" if link else "")
