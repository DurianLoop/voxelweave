"""Public MC-RC nonpixel identity inventory from authenticated official links."""
from __future__ import annotations
import json
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import fetch_cobrai_crossmoda_public_2026_10_02 as helper

ROOT=helper.ROOT
OUT=ROOT/'source_cache/mc_rc_v2_identity_2026-10-02'
PLAN=ROOT.parent/'MC_RC_V2_NONPIXEL_IDENTITY_PLAN_2026-10-02.md'

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=True);helper.OUT=OUT
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    page=ROOT/'source_cache/mc_rc_official_2026-10-02/attempt_01.json'
    source=json.loads(page.read_text(encoding='utf-8'))['responses'][0]
    official_links=source['links']
    names={'overlap':'series_overlap_between_VS-MC-RC_and_-VS-SEG.csv','manifest':'Vestibular-Schwannoma-MC-RC_v2_20260604.tcia'}
    targets=[('series','json','https://services.cancerimagingarchive.net/nbia-api/services/v1/getSeries?'+urllib.parse.urlencode({'Collection':'Vestibular-Schwannoma-MC-RC','Modality':'MR'}))]
    for key,filename in names.items():
        urls=[u for u in official_links if u.endswith('/'+filename)]
        if len(urls)!=1:raise ValueError('Exactly one official link required: '+filename)
        targets.append((key,'metadata',urls[0]))
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(lambda t:helper.fetch(t,attempt),targets))
    result={'attempt':attempt,'script_sha256':helper.sha(__file__),'helper_sha256':helper.sha(helper.__file__),'plan_sha256':helper.sha(PLAN),'official_page_index_sha256':helper.sha(page),'scope':'nonpixel series JSON, CSV crosswalk, text manifest; no images/labels','responses':rows}
    (OUT/f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in rows:print(json.dumps({k:r.get(k) for k in ('key','http_status','bytes','error')},ensure_ascii=False))

if __name__=='__main__':main()
