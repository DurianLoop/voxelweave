"""Save two previously acquired method pages for bounded reread, not new papers."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'literature/source_cache/learning_to_defer_primary_attempt02_2026-10-07'
OUT=ROOT/'literature/source_cache/downstream_feature_cost_primary_2026-10-08'


def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    records=[];bindings=[]
    for key,number in (('madras_2018_verified',3),('mozannar_sontag_pmlr_2020',2)):
        path=BASE/key/'physical_pages.json'
        data=json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data,dict):
            pages=data.get('pages') or data.get('records') or data.get('physical_pages')
        else:pages=data
        assert isinstance(pages,list),(key,list(data) if isinstance(data,dict) else type(data).__name__)
        selected=[v for v in pages if v.get('physical_page',v.get('page'))==number]
        assert len(selected)==1,(key,pages[0].keys())
        text=selected[0].get('text') or selected[0].get('page_text')
        assert isinstance(text,str) and len(text)>100
        bindings.append(entry(path))
        records.append(dict(key=key,physical_page=number,text=text,text_actually_reread=False))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[entry(Path(__file__))]+bindings,
        records=records,new_primary_papers_read=0,new_primary_pages_read=0,old_method_pages_prepared=2,
        extraction_is_not_reading=True,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    with (OUT/'old_deferral_method_reread_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    for row in records:print(json.dumps(row,ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
