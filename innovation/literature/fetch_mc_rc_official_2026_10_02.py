"""Follow authenticated article reference DOI; metadata only."""
from __future__ import annotations
import json
import sys
from concurrent.futures import ThreadPoolExecutor
import fetch_cobrai_crossmoda_public_2026_10_02 as helper

ROOT=helper.ROOT
OUT=ROOT/'source_cache/mc_rc_official_2026-10-02'
PLAN=ROOT/'2026-10-02_mc_rc_official_adaptive_plan.md'

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=True);helper.OUT=OUT
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    targets=[('mc_rc_doi','html','https://doi.org/10.7937/HRZH-2N82'),
             ('mc_rc_models_zenodo','zenodo','https://zenodo.org/api/records/10363647')]
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(lambda t:helper.fetch(t,attempt),targets))
    result={'attempt':attempt,'script_sha256':helper.sha(__file__),'helper_sha256':helper.sha(helper.__file__),'plan_sha256':helper.sha(PLAN),'source_article_sha256':helper.sha(ROOT/'source_cache/cobrai_crossmoda_public_2026-10-02/kujawa_jats_attempt_01.response'),'scope':'authenticated article reference DOI landing page and model metadata; no images/labels/weights','responses':rows}
    (OUT/f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in rows:print(json.dumps({k:r.get(k) for k in ('key','http_status','final_url','error')},ensure_ascii=False))

if __name__=='__main__':main()
