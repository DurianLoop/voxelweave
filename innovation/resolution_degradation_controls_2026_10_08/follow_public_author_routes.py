"""Bounded exact DOI metadata from a new public index; no full-text or patient-data claims."""
import sys,time,json,gzip,hashlib,urllib.parse
from pathlib import Path
import requests
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard
DOIS=['10.1016/j.jneumeth.2026.110834','10.1109/tmi.2026.3662706','10.1016/j.compmedimag.2026.102786']


def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    journal=HERE/'full_real_pipeline_attempt01/fields.jsonl.gz'
    def guard():
        resource_guard();assert time.perf_counter()-started<180
        size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        reserve=max(0,1_500_000-journal.stat().st_size)+150_000+100_000
        assert size+reserve+100_000<5_000_000,'Preserve live full-pipeline and audit capacity'
    guard();out=HERE/'public_author_routes_attempt01';out.mkdir(exist_ok=False)
    s=requests.Session();s.trust_env=False
    s.headers['User-Agent']='MRI-research-public-literature-audit/1.0'
    sources=[Path(__file__),HERE/'PUBLIC_AUTHOR_ROUTE_FOLLOWUP_PROTOCOL_TURN29.md',
             ROOT/'literature/2026-10-07_recent_thickslice_primary_availability_result.md',
             ROOT/'literature/2026-10-07_action_utility_followup_reading.md',
             ROOT/'literature/2026-10-08_relative_utility_collision_recheck.md']
    result=dict(complete=False,errors=[],records=[],exact_DOIs=DOIS,
                new_maintexts_retrieved=0,new_maintexts_actually_read=0,
                new_patient_medical_effects=0,confirmation_patients_opened=False,
                user_data_sent=False,public_GETs_only=True,goal_status='active')
    for i,doi in enumerate(DOIS):
        guard();url='https://api.openalex.org/works/https://doi.org/'+urllib.parse.quote(doi,safe='/')
        record=dict(doi_requested=doi,request_url=url,actually_read_maintext=False)
        at=time.perf_counter()
        try:
            response=s.get(url,timeout=30,stream=True)
            record['HTTP_status']=response.status_code;body=b''
            for part in response.iter_content(16384):
                body+=part;assert len(body)<=500_000,'Response-byte bound exceeded'
            response.close()
            p=out/f'openalex_{i:02d}.json.gz';packed=gzip.compress(body,mtime=0)
            assert sum(x.stat().st_size for x in out.glob('*.gz'))+len(packed)<=80_000
            with p.open('xb') as f:f.write(packed)
            record.update(raw_response_gzip=entry(p),uncompressed_bytes=len(body),
                          uncompressed_sha256=hashlib.sha256(body).hexdigest())
            response.raise_for_status();q=json.loads(body)
            assert q.get('doi','').lower()=='https://doi.org/'+doi.lower(),'DOI identity mismatch'
            record.update(exact_DOI_confirmed=True,title=q.get('title'),work_id=q.get('id'),
                publication_date=q.get('publication_date'),open_access=q.get('open_access'),
                best_oa_location=q.get('best_oa_location'),primary_location=q.get('primary_location'),
                locations=q.get('locations'),metadata_only=True)
        except Exception as exc:
            record['error']=type(exc).__name__+': '+str(exc)
            result['errors'].append(dict(doi=doi,error=record['error']))
        record['elapsed_seconds']=time.perf_counter()-at;result['records'].append(record)
        print(json.dumps(record,ensure_ascii=False),flush=True)
    result.update(complete=len(result['records'])==3,elapsed_seconds=time.perf_counter()-started,
                  source_bindings=[entry(p) for p in sources])
    dump(out/'receipt.json',result);guard()
    print(json.dumps({k:v for k,v in result.items() if k not in ['records','source_bindings']},ensure_ascii=False),flush=True)
    return int(bool(result['errors']))


if __name__=='__main__':raise SystemExit(main())
