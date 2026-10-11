"""Archive the open PMC BioC full text of the neonatal T2 interpolation paper."""

from __future__ import annotations

import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache" / "verschuur_neonatal_t2_2022_bioc.xml"
INDEX = ROOT / "source_cache" / "verschuur_neonatal_t2_2022_index.json"
TEXT = ROOT / "extracted" / "verschuur_neonatal_t2_2022.txt"
URL = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC9314603/unicode"


def main() -> None:
    if any(path.exists() for path in (OUT, INDEX, TEXT)):
        raise FileExistsError("Refusing to overwrite prior full-text archive")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(urllib.request.Request(URL, headers={"User-Agent": "MRI-prior-art-audit/1.0"}), timeout=40) as response:
        raw = response.read(200_001)
        if response.status != 200 or len(raw) > 200_000:
            raise RuntimeError("Unexpected PMC full-text response")
    root = ET.fromstring(raw)
    passages = []
    for passage in root.findall(".//passage"):
        text = passage.findtext("text")
        if text:
            passages.append(text)
    if len(passages) < 40 or b"10.1111/jon.12985" not in raw:
        raise ValueError("Unexpected article or incomplete full text")
    OUT.write_bytes(raw)
    TEXT.write_text("\n\n".join(passages) + "\n", encoding="utf-8")
    result = {"url": URL, "file": OUT.relative_to(ROOT).as_posix(),
              "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
              "passages": len(passages),
              "extracted_text": TEXT.relative_to(ROOT).as_posix(),
              "extracted_sha256": hashlib.sha256(TEXT.read_bytes()).hexdigest()}
    INDEX.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
