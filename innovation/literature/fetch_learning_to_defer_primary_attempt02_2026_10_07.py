"""Use verified public title routes, retaining the wrong-ID and page-budget failures."""
import concurrent.futures,json,sys
from datetime import datetime,timezone
import fetch_learning_to_defer_primary_2026_10_07 as previous
ROOT=previous.ROOT
OUT=ROOT/'literature/source_cache/learning_to_defer_primary_attempt02_2026-10-07'
PAPERS=[('mozannar_sontag_pmlr_2020','PMLR119:mozannar20b','https://proceedings.mlr.press/v119/mozannar20b/mozannar20b.pdf'),
        ('madras_2018_verified','1711.06664','https://arxiv.org/pdf/1711.06664')]
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);previous.OUT=OUT
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(previous.fetch,PAPERS))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,script_sha256=previous.sha(__file__),papers=results,
           original_failures_preserved=True,original_wrong_identifier='1711.06646',correct_identifier='1711.06664',
           source_bindings=[dict(path='literature/fetch_learning_to_defer_primary_2026_10_07.py',sha256=previous.sha(previous.__file__)),
               dict(path='literature/2026-10-07_learning_to_defer_route_correction.md',sha256=previous.sha(ROOT/'literature/2026-10-07_learning_to_defer_route_correction.md'))],
           actual_new_fulltexts_read=0,actual_training_updates=0,actual_gpu_updates=0)
    for p in results:
        if not p['fulltext_acquired']:continue
        pages=json.loads((OUT/p['key']/p['index_file']).read_text(encoding='utf-8'));first=' '.join(pages[0]['text'].lower().split())
        title='consistent estimators for learning to defer to an expert' if p['key'].startswith('mozannar') else 'predict responsibly: improving fairness and accuracy by learning to defer'
        p['expected_title_verified']=title in first
        assert p['expected_title_verified'],'Corrected PDF title mismatch'
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps([{k:p.get(k) for k in ['key','fulltext_acquired','physical_pages','expected_title_verified','error']} for p in results]),flush=True)
    return int(not all(p['fulltext_acquired'] for p in results))
if __name__=='__main__':raise SystemExit(main())
