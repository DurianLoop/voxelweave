"""Derive acquisition attempt04 from verified official search; preserve failures."""
import ast,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'literature/fetch_pareto_testing_primary_2026_10_07.py'
NEW=ROOT/'literature/fetch_verified_pareto_testing_primary_2026_10_07.py'
SEARCH=ROOT/'literature/source_cache/pareto_testing_official_search_2026-10-07/search_attempt03.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not NEW.exists()
    q=json.loads(SEARCH.read_text(encoding='utf-8'));assert q['complete'] and not q['errors']
    url=q['matches'][0]['official_abs_urls'][0];assert url=='https://arxiv.org/abs/2210.07913'
    source=BASE.read_text(encoding='utf-8')
    old="OUT=ROOT/'literature/source_cache/pareto_testing_primary_2026-10-07'"
    new="OUT=ROOT/'literature/source_cache/pareto_testing_verified_primary_2026-10-07'"
    assert source.count(old)==1;source=source.replace(old,new)
    old="('https://proceedings.mlr.press/v206/laufer-goldshtein23a.html','https://arxiv.org/abs/2210.07998')"
    assert source.count(old)==1;source=source.replace(old,repr((url,)))
    old="expected_title=TITLE,identity_attempts=[],reading_performed=False,visual_review_performed=False)"
    new="expected_title=TITLE,identity_attempts=[],reading_performed=False,visual_review_performed=False,\n        source_bindings=[dict(path='literature/source_cache/pareto_testing_official_search_2026-10-07/search_attempt03.json',sha256='"+sha(SEARCH)+"')])"
    assert source.count(old)==1;source=source.replace(old,new);ast.parse(source)
    with NEW.open('x',encoding='utf-8',newline='\n') as s:s.write(source)
    print(json.dumps(dict(complete=True,new_source_sha256=sha(NEW),official_identity_url=url)));return 0
if __name__=='__main__':raise SystemExit(main())
