"""One alternate public full-text endpoint; no repeated NCBI request or automatic retry."""
import json,sys,time
from pathlib import Path
from datetime import datetime,timezone
from retrieve_stronger_adaptation_primary import fetch,OUT,ROOT,sha,dump,resource_guard
from retrieve_adaptation_fulltexts_addendum import blocks_xml
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    r=fetch('bigaug_europepmc_jats','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7393676/fullTextXML','.xml')
    if r['complete']:
        blocks=blocks_xml(ROOT/r['file']);assert blocks
        assert any('Generalizing deep learning for medical image segmentation to unseen domains via deep stacked transformation'.lower() in b['text'].lower() for b in blocks)
        p=OUT/'bigaug_europepmc_jats_blocks.json';dump(p,blocks)
        r.update(extracted_file=p.relative_to(ROOT).as_posix(),extracted_sha256=sha(p),extracted_blocks=len(blocks))
    r.update(created_utc=datetime.now(timezone.utc).isoformat(),automatic_retries=False,actual_reading_completed=False,
        original_NCBI_429_unchanged=True,medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0)
    dump(OUT/'bigaug_europepmc_receipt.json',r);print(json.dumps(r),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
