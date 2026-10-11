"""Verify local paper evidence and Markdown links; generate its hash manifest."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent
LITERATURE = ROOT / "literature"
MANIFEST = LITERATURE / "archive_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archived(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


sources = json.loads((LITERATURE / "2026-09-30_sources.json").read_text(encoding="utf-8"))
downloads = json.loads((LITERATURE / "new_pdf_manifest.json").read_text(encoding="utf-8"))
by_name = {
    Path(entry["local_pdf"]).name: {
        "source_url": entry["source_url"], "original_path": entry["local_pdf"],
        "registered_sha256": entry["sha256"],
    }
    for entry in sources["entries"] if "local_pdf" in entry
}
for entry in downloads:
    by_name[Path(entry["path"]).name] = {
        "source_url": f"https://arxiv.org/abs/{entry['arxiv']}",
        "original_path": entry["path"], "registered_sha256": entry["sha256"],
    }
by_hash = {entry["registered_sha256"]: entry for entry in by_name.values()}

errors: list[str] = []
papers = []
for path in sorted(LITERATURE.glob("*.pdf")):
    entry = {"archive_path": archived(path), "bytes": path.stat().st_size,
             "sha256": sha256(path)}
    provenance = by_name.get(path.name)
    if provenance:
        entry.update(provenance)
        if entry["sha256"] != provenance["registered_sha256"]:
            errors.append(f"PDF hash differs from source record: {path.name}")
    else:
        original = ROOT.parent / "docx" / "experiment_notes" / "reading" / path.name
        if original.is_file() and sha256(original) == entry["sha256"]:
            entry["original_path"] = original.relative_to(ROOT.parent).as_posix()
        else:
            errors.append(f"Original PDF missing or differs: {path.name}")
        if entry["sha256"] in by_hash:
            entry["source_url"] = by_hash[entry["sha256"]]["source_url"]
    papers.append(entry)
for name in by_name:
    if not (LITERATURE / name).is_file():
        errors.append(f"Missing registered PDF: {name}")

evidence = []
for folder in ("extracted", "search_snapshots", "source_cache"):
    for path in sorted((LITERATURE / folder).rglob("*")):
        if path.is_file():
            evidence.append({"archive_path": archived(path), "bytes": path.stat().st_size,
                             "sha256": sha256(path)})

for entry in sources["search_snapshots"]:
    path = LITERATURE / "search_snapshots" / Path(entry["path"]).name
    if not path.is_file() or sha256(path) != entry["sha256"]:
        errors.append(f"Search snapshot missing or changed: {path.name}")

link_count = 0
for page in ROOT.rglob("*.md"):
    relative = page.relative_to(ROOT)
    if relative.parts[0] == "tools" or relative.parts[:2] == ("literature", "source_cache"):
        continue
    for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
        if target.startswith(("https://", "http://", "mailto:", "#")):
            continue
        local = (page.parent / unquote(target.split("#", 1)[0])).resolve()
        link_count += 1
        if not local.exists():
            errors.append(f"Broken local link in {archived(page)}: {target}")

result = {"scope": "archived primary PDFs and reading evidence",
          "papers": papers, "evidence_files": evidence}
if "--write" in sys.argv:
    MANIFEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
elif not MANIFEST.is_file() or json.loads(MANIFEST.read_text(encoding="utf-8")) != result:
    errors.append("archive_manifest.json is absent or out of date")

print(json.dumps({"pdfs": len(papers), "evidence_files": len(evidence),
                  "local_links_checked": link_count, "errors": errors},
                 ensure_ascii=False, indent=2))
sys.exit(bool(errors))
