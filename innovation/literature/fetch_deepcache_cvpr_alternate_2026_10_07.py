"""Use an alternate official source after the arXiv PDF exceeded its acquisition cap."""
import json
from datetime import datetime, timezone
import fetch_incremental_inference_primary_2026_10_07 as original

def main():
    original.OUT=original.ROOT/'literature/source_cache/deepcache_cvpr_alternate_2026-10-07'
    original.OUT.mkdir(exist_ok=False,parents=True)
    result=original.acquire(('deepcache_cvpr','https://openaccess.thecvf.com/content/CVPR2024/html/Ma_DeepCache_Accelerating_Diffusion_Models_for_Free_CVPR_2024_paper.html'))
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=original.sha(__file__),
        imported_acquisition_script_sha256=original.sha(original.__file__),
        prior_failure='arXiv response read reached 32000001 bytes, exceeding fixed 32000000 cap; no PDF saved or read',
        system_proxy_unchanged=True,public_GET_only=True,new_papers_read=0,records=[result])
    (original.OUT/'acquisition_attempt02.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result.get(k) for k in ('key','complete','pdf_bytes','physical_pages','errors')}),flush=True)
    return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
