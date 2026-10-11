"""Archive exact PMC/BioC full text for the Edupuganti MRI UQ paper."""
from __future__ import annotations

import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/edupuganti_mri_uq_2020_bioc.xml"
URL = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC7837266/unicode"


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite archived full text")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(URL, headers={"User-Agent": "MRI-literature-audit/1.0"})
    with opener.open(request, timeout=45) as response:
        raw = response.read()
        if response.status != 200 or len(raw) < 5000:
            raise RuntimeError("Missing expected BioC full text")
    tree = ET.fromstring(raw)
    if len(tree.findall(".//passage")) < 100 or b"10.1109/TMI.2020.3025065" not in raw:
        raise ValueError("Response does not contain the expected full article")
    OUT.write_bytes(raw)
    print(json.dumps({"url": URL, "path": OUT.relative_to(ROOT).as_posix(),
                      "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
