"""Print source locations for the selected citation-screen candidates."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "search_snapshots/mira_four_seed_citations_2026-10-01/kuestner2024_citations.json"
IDS = {"W4414371023", "W7117964094", "W7152532020", "W4403204384"}


def main() -> None:
    works = json.loads(SOURCE.read_text(encoding="utf-8"))["results"]
    selected = []
    for work in works:
        if work["id"].rsplit("/", 1)[-1] not in IDS:
            continue
        selected.append({"id": work["id"], "title": work["display_name"],
                         "doi": work.get("doi"), "year": work.get("publication_year"),
                         "locations": [{"landing_page_url": item.get("landing_page_url"),
                                        "pdf_url": item.get("pdf_url"),
                                        "source": (item.get("source") or {}).get("display_name")}
                                       for item in work.get("locations", [])]})
    print(json.dumps(selected, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
