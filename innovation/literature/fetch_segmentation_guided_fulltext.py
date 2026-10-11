"""Fetch the public arXiv HTML for the task-aware MRI reconstruction comparator."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache" / "segmentation_guided_mri_2026-10-01"
URL = "https://arxiv.org/html/2407.18026"


class Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.suppressed = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in ("script", "style", "nav"):
            self.suppressed += 1
        elif tag in ("p", "h1", "h2", "h3", "li", "tr", "section"):
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "nav") and self.suppressed:
            self.suppressed -= 1
        elif tag in ("p", "h1", "h2", "h3", "li", "tr", "section"):
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.suppressed:
            self.parts.append(data)


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite prior result")
    OUT.mkdir(parents=True)
    report: dict = {"url": URL}
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        request = urllib.request.Request(URL, headers={"User-Agent": "MRI-literature-audit/1.0"})
        with opener.open(request, timeout=40) as response:
            raw = response.read(8_000_001)
            report["http_status"] = response.status
            report["content_type"] = response.headers.get("Content-Type")
        if len(raw) > 8_000_000 or b"<html" not in raw[:1000].lower():
            raise ValueError("Response not a bounded HTML document")
        (OUT / "article.html").write_bytes(raw)
        parser = Text()
        parser.feed(raw.decode("utf-8", "replace"))
        extracted = " ".join(" ".join(parser.parts).split())
        (OUT / "article.txt").write_text(extracted + "\n", encoding="utf-8")
        report.update({"html_bytes": len(raw), "html_sha256": hashlib.sha256(raw).hexdigest(),
                       "text_characters": len(extracted), "text_sha256": hashlib.sha256(extracted.encode()).hexdigest()})
    except urllib.error.HTTPError as error:
        report["http_status"] = error.code
        report["error_type"] = "HTTPError"
    except Exception as error:
        report["error_type"] = type(error).__name__
    (OUT / "index.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
