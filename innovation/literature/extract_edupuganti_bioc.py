"""Create a readable, section-labelled extraction of archived BioC XML."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_cache/edupuganti_mri_uq_2020_bioc.xml"
OUT = ROOT / "extracted/edupuganti_mri_uq_2020_bioc.txt"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    root = ET.parse(SOURCE).getroot()
    passages = root.findall(".//passage")
    if len(passages) < 100:
        raise ValueError("Expected complete article passages")
    lines = []
    for passage in passages:
        metadata = {item.get("key"): item.text or "" for item in passage.findall("infon")}
        body = passage.findtext("text") or ""
        if not body.strip():
            continue
        label = metadata.get("section_type") or metadata.get("type") or "passage"
        lines.append(f"[{label}] {body.strip()}")
    OUT.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    print(f"passages={len(passages)} extracted={len(lines)} bytes={OUT.stat().st_size}")


if __name__ == "__main__":
    main()
