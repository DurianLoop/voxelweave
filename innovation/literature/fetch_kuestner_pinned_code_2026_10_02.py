"""Read DOI-linked author files at a fixed public commit; do not import them."""
from __future__ import annotations
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fetch_author_repo_and_mslesseg_2026_10_02 import fetch, ROOT

OUT=ROOT / 'source_cache/author_repo_and_mslesseg_2026-10-02'
COMMIT='ce0e6ede3682a6901bfdd6ddc85b44ef28e72f3a'
FILES=('ensemble/dataset/fastmri.py','ensemble/dataset/fastmri_dataloader_base.py','ensemble/dataset/transforms.py',
       'ensemble/dataset/config.yml','config/cnn.yml','config/modl.yml','config/unet.yml','config/vn.yml',
       'ensemble/models/losses.py')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    attempt=len(list(OUT.glob('pinned_code_attempt_*.json')))+1
    def get(path):
        row=fetch('kuestner_'+path.replace('/','_').replace('.','_'),'https://raw.githubusercontent.com/midas-tum/recon_uncertainty/'+COMMIT+'/'+path,attempt)
        row.update(repository_path=path,commit=COMMIT)
        return row
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows=list(pool.map(get,FILES))
    result={'attempt':attempt,'commit':COMMIT,'script_sha256':sha(__file__),'helper_sha256':sha(ROOT / 'fetch_author_repo_and_mslesseg_2026_10_02.py'),
            'foreign_code_imported_or_executed':False,'sources':rows}
    (OUT / f'pinned_code_attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for row in rows:
        print(json.dumps({k:row.get(k) for k in ('repository_path','http_status','bytes','raw_file','raw_sha256','error')},ensure_ascii=False))

if __name__=='__main__':
    main()
