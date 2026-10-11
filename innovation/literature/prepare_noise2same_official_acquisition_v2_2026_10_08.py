"""Separate 10MB acquisition after verified 9,591,234-byte official PDF metadata."""
import ast
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    folder=ROOT/'literature/source_cache/blindspot_dependence_primary_2026-10-08'
    observed=json.loads((folder/'noise2same_public_response_diagnostic_attempt01.json').read_text(encoding='utf-8'))
    assert observed['http_status']==200 and observed['PDF_magic_matched'] and int(observed['content_length'])==9591234
    old=ROOT/'literature/fetch_noise2same_official_primary_2026_10_08.py'
    dest=ROOT/'literature/fetch_noise2same_official_primary_v2_2026_10_08.py'
    assert not dest.exists()
    text=old.read_text(encoding='utf-8')
    for a,b in (('noise2same_official_attempt01','noise2same_official_attempt02'),
                ('response.read(8_000_001)','response.read(10_000_001)'),
                ('len(data) <= 8_000_000','len(data) <= 10_000_000'),
                ('BLINDSPOT_PRIMARY_IDENTITY_CORRECTION_2026-10-08.md','BLINDSPOT_PRIMARY_RESOURCE_AMENDMENT_2026-10-08.md')):
        assert text.count(a)==1,a
        text=text.replace(a,b)
    ast.parse(text)
    with dest.open('x',encoding='utf-8') as f:
        f.write(text)
    print(json.dumps(dict(complete=True,verified_official_PDF_bytes=9591234,new_acquisition_limit=10000000,
                          new_archival_stage_limit=25000000,medical_arrays_loaded=0)),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
