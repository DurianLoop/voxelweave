"""Fetch only the exact ranker.py path documented by the pinned README."""
import sys,time,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
from fetch_pinned_vinn_code import get

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    previous=HERE/'lesion_ranker_entry_attempt01/receipt.json';r=read(previous)
    assert r['complete'] and not r['errors']
    for b in r['records']:bind(b['source_binding'])
    commit=r['pinned_commit'];assert commit=='ecd3b9bdadc40877b9832ea49b5c82d5e27e7d14'
    text=(HERE/'lesion_ranker_entry_attempt01/README_source.md').read_text(encoding='utf-8');assert 'ranker.py' in text
    out=HERE/'lesion_ranker_source_attempt01';out.mkdir(exist_ok=False)
    result=dict(complete=False,errors=[],pinned_commit=commit,actual_source_reading_completed=False,
                author_code_imported=False,author_code_executed=False,medical_arrays_loaded=0)
    dest=out/'ranker.py';url='https://raw.githubusercontent.com/Pediatric-Accelerated-Intelligence-Lab/BraTS-Unofficial-Ranker/'+commit+'/ranker.py'
    try:
        get(url,dest);assert dest.stat().st_size<=200000
        result.update(complete=True,url=url,source_binding=entry(dest),lines=len(dest.read_text(encoding='utf-8').splitlines()))
    except Exception as exc:result['errors'].append(type(exc).__name__+': '+str(exc))
    result.update(elapsed_seconds=time.perf_counter()-started,
                  source_bindings=[entry(p) for p in [Path(__file__),HERE/'LESION_RANKER_SOURCE_PROTOCOL.md',previous,HERE/'lesion_ranker_entry_attempt01/README_source.md']])
    dump(out/'receipt.json',result);resource_guard()
    assert time.perf_counter()-started<90 and sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(result),flush=True);return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
