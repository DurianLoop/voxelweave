"""Create a separate acquisition from the verified official NeurIPS Paper link."""
import ast
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    identity=ROOT/'literature/source_cache/blindspot_dependence_primary_2026-10-08/noise2same_official_identity_attempt01.json'
    record=json.loads(identity.read_text(encoding='utf-8'))
    assert record['complete'] and not record['errors'] and record['matched_title']=='Noise2Same: Optimizing A Self-Supervised Bound for Image Denoising'
    urls=[u for u in record['actual_public_PDF_links'] if u.endswith('-Paper.pdf')]
    assert len(urls)==1
    old=ROOT/'literature/fetch_distortion_perception_primary_2026_10_08.py'
    dest=ROOT/'literature/fetch_noise2same_official_primary_2026_10_08.py'
    assert not dest.exists()
    s=old.read_text(encoding='utf-8')
    a="    for key, url in (('perception_distortion', 'https://arxiv.org/pdf/1711.06077'),\n                     ('rate_distortion_perception', 'https://arxiv.org/pdf/1901.07821')):"
    b="    for key, url in (('noise2same_verified', '"+urls[0]+"'),):"
    assert s.count(a)==1
    s=s.replace(a,b)
    assert s.count('distortion_perception_primary_2026-10-08')==1
    s=s.replace('distortion_perception_primary_2026-10-08','blindspot_dependence_primary_2026-10-08/noise2same_official_attempt01')
    assert s.count('2026-10-08_distortion_perception_primary_protocol.md')==1
    s=s.replace('2026-10-08_distortion_perception_primary_protocol.md','BLINDSPOT_PRIMARY_IDENTITY_CORRECTION_2026-10-08.md')
    ast.parse(s)
    with dest.open('x',encoding='utf-8') as f:
        f.write(s)
    print(json.dumps(dict(complete=True,official_verified_URL=urls[0],medical_arrays_loaded=0)),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
