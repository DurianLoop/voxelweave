"""Close oversized text gaps with bounded streaming and retained limits."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import hashlib,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parent;OUT=ROOT/'experiments/mc_rc_local_identity_audit'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();audit=read(OUT/'attempt_02.json')
    api=read(ROOT/'literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response')
    ids={x['PatientID'].encode() for x in api};uids={x[k].encode():x['PatientID'] for x in api for k in ('SeriesInstanceUID','StudyInstanceUID')}
    overlap=max(map(len,uids))+16;idre=re.compile(rb'(?<![A-Za-z0-9-])VS-(?:MC-RC|SEG)-\d{3}(?![A-Za-z0-9-])');uidre=re.compile(rb'(?<![\d.])(?:\d+\.){3,}\d+(?![\d.])')
    gaps=[x for x in audit['coverage_gaps'] if x['reason']=='Text exceeds 16 MB cap'];expected=sum(x['bytes'] for x in gaps)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),prior_audit_sha256=sha(OUT/'attempt_02.json'),plan_sha256=sha(ROOT/'MC_RC_IDENTITY_GAP_STREAM_ADDENDUM_2026-10-03.md'),
           complete=False,errors=[],expected_bytes=expected,max_total_bytes=3_000_000_000,chunk_bytes=65536,boundary_overlap_bytes=overlap,scanned_bytes=0,streamed_texts=[],nontext_signatures=[],excluded_scope=[],
           external_identity_proven=False,complete_project_exposure_crosswalk_proven=False,new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    path=OUT/'gap_stream_attempt_01.json';assert not path.exists()
    try:
        assert expected<=r['max_total_bytes']
        for x in gaps:
            resource_gate();p=PROJECT/x['path'];assert p.is_relative_to(PROJECT) and p.suffix=='.csv' and not any(y.lower().startswith('test') for y in p.relative_to(PROJECT).parts)
            h=hashlib.sha256();found=set();founduids=set();tail=b'';total=0
            with p.open('rb') as f:
                for chunk in iter(lambda:f.read(65536),b''):
                    h.update(chunk);total+=len(chunk);merged=tail+chunk
                    found.update(set(idre.findall(merged))&ids);founduids.update(set(uidre.findall(merged))&set(uids));tail=merged[-overlap:]
            assert total==x['bytes'];r['scanned_bytes']+=total
            row=dict(path=x['path'],bytes=total,sha256=h.hexdigest(),patients=sorted({x.decode() for x in found}|{uids[u] for u in founduids}),exact_uid_count=len(founduids))
            r['streamed_texts'].append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
        for x in audit['coverage_gaps']:
            if x['reason']=='Unrecognized text encoding':
                p=PROJECT/x['path']
                with p.open('rb') as f:first=f.read(512)
                r['nontext_signatures'].append(dict(path=x['path'],bytes=p.stat().st_size,sha256=sha(p),first16_hex=first[:16].hex(),pdf_magic=first.startswith(b'%PDF'),zip_magic=first.startswith(b'PK'),original_purpose='Prior public source access / failed label metadata retrieval; not a task-model output'))
            elif x['reason'].startswith('Inaccessible'):r['excluded_scope'].append(dict(**x,classification='Temporary skill installer excluded; permissions unchanged; no contents verified'))
        r['complete']=r['scanned_bytes']==expected
    except Exception as exc:r['errors'].append(type(exc).__name__+': '+str(exc))
    r['finished_utc']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in r.items() if k not in ('streamed_texts','nontext_signatures')},ensure_ascii=False));return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
