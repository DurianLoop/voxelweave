"""Bounded local text/name identity audit; never open images or checkpoints."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import csv,hashlib,json,re,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parent
OUT=ROOT/'experiments/mc_rc_local_identity_audit'
TEXT_EXT={'.py','.md','.txt','.json','.jsonl','.csv','.tsv','.yaml','.yml','.toml','.ini','.response'}
IDRE=re.compile(r'(?<![A-Za-z0-9-])VS-(?:MC-RC|SEG)-\d{3}(?![A-Za-z0-9-])')
UIDRE=re.compile(r'(?<![\d.])(?:\d+\.){3,}\d+(?![\d.])')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def classify(rel):
    low=rel.lower()
    if low.startswith('innovation/literature/source_cache/'):
        return 'public_metadata_or_source_preflight_or_archive_snapshot'
    if low.startswith('innovation/experiments/'):
        folder=low.split('/')[2]
        if low.endswith('.py'):return 'code_definition_no_execution_inferred'
        if any(x in folder for x in ('header','label_grid','label_gate','source_roles','source_preparation','identity_audit')):
            return 'source_or_label_preflight_not_model_effect'
        return 'experiment_record_requires_role_review'
    if low.startswith('innovation/data/'):
        return 'source_payload_name_only_not_model_effect'
    if low.startswith('innovation/'):
        if low.endswith('.py'):return 'code_definition_no_execution_inferred'
        if 'manifest' in low:return 'archive_index_not_model_effect'
        return 'research_document_requires_role_review'
    return 'other_project_record_requires_role_review'
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();OUT.mkdir(exist_ok=True)
    api_path=ROOT/'literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response';api=read(api_path)
    prep_path=ROOT/'experiments/mc_rc_source_roles_metadata_preparation/attempt_01.json';prep=read(prep_path)
    ids={x['PatientID'] for x in api};uid_to_id={}
    for x in api:
        for k in ('StudyInstanceUID','SeriesInstanceUID'):
            uid_to_id.setdefault(x[k],set()).add(x['PatientID'])
    assert all(len(v)==1 for v in uid_to_id.values())
    focused={'VS-MC-RC-'+x for x in ('011','012','013','015','019','020','022','024','025','026','027','028','029','030','031')}
    roots=['baseline','design','pre','processing','docx','handoff_hat_smamba_evidence_2026-09-16','exports','migration_2026-09-26','temp','innovation','dataset']
    args=['rg','--files','-uuu']+[x for x in roots if (PROJECT/x).exists()]
    args += ['--glob','!**/.git/**','--glob','!**/.codex/**','--glob','!**/.agents/**','--glob','!**/tools/**','--glob','!**/vendor/**','--glob','!**/node_modules/**','--glob','!**/__pycache__/**','--glob','!**/test*/**','--glob','!**/test*','--glob','!**/*test115*/**','--glob','!dataset/IXI/**','--glob','!innovation/experiments/mc_rc_local_identity_audit/**']
    from types import SimpleNamespace
    result=SimpleNamespace(stdout=(OUT/'rg_file_listing_attempt_01.txt').read_bytes())
    assert len(result.stdout)<64_000_000
    listing=result.stdout.decode('utf-8').splitlines();r=dict(created_utc=datetime.now(timezone.utc).isoformat(),resources=resources,
        script_sha256=sha(__file__),plan_sha256=sha(ROOT/'MC_RC_LOCAL_IDENTITY_AUDIT_PLAN_2026-10-03.md'),api_sha256=sha(api_path),preparation_sha256=sha(prep_path),
        command=args,listing_file='rg_file_listing_attempt_01.txt',listing_sha256=sha(OUT/'rg_file_listing_attempt_01.txt'),listed_files=len(listing),
        api_patients=len(ids),api_mc_rc_patients=len([x for x in ids if x.startswith('VS-MC-RC-')]),shared_vs_seg_excluded_ids=prep['api_shared_patient_ids'],
        focused_patient_ids=sorted(focused),scanned_text_files=0,scanned_text_bytes=0,name_only_files=0,coverage_gaps=[dict(path='temp/skill_install_tmp/codex/skill-install-ykexumxq',reason='Inaccessible during rg enumeration; first failure and stderr retained')],excluded_names_before_content_read=[],hits=[],complete=False,errors=[],
        scope='Audited local text and file names; binary contents and inaccessible/excluded paths not assessed',
        complete_project_exposure_crosswalk_proven=False,external_model_training_identity_verified=False,cross_dataset_identity_linkage_proven=False,
        MR_pixels_decoded=False,new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(OUT/'attempt_02.json',r)
    try:
        for ix,item in enumerate(listing):
            if ix%1000==0:resource_gate()
            path=PROJECT/item;rel=path.relative_to(PROJECT).as_posix();parts=rel.lower().split('/')
            if any(p.startswith('test') or 'test115' in p for p in parts) or rel.lower().startswith('dataset/ixi/'):
                r['excluded_names_before_content_read'].append(rel);continue
            name_ids=set(IDRE.findall(rel))&ids;name_uids=set(UIDRE.findall(rel))&set(uid_to_id)
            mentions=set(name_ids)|{next(iter(uid_to_id[u])) for u in name_uids};content_matches=[];content_uids=set();file_sha=None
            if path.suffix.lower() in TEXT_EXT:
                size=path.stat().st_size
                if size>16_000_000:r['coverage_gaps'].append(dict(path=rel,reason='Text exceeds 16 MB cap',bytes=size))
                else:
                    data=path.read_bytes();file_sha=hashlib.sha256(data).hexdigest()
                    try:text=data.decode('utf-8-sig')
                    except UnicodeDecodeError:
                        try:text=data.decode('gb18030')
                        except UnicodeDecodeError:r['coverage_gaps'].append(dict(path=rel,reason='Unrecognized text encoding',bytes=size));text=''
                    r['scanned_text_files']+=1;r['scanned_text_bytes']+=size
                    content_ids=set(IDRE.findall(text))&ids;content_uids=set(UIDRE.findall(text))&set(uid_to_id)
                    mentions|=content_ids|{next(iter(uid_to_id[u])) for u in content_uids}
                    for pat in sorted(mentions&focused):
                        evidence=[]
                        for match in IDRE.finditer(text):
                            if match.group()==pat:evidence.append(text[max(0,match.start()-100):min(len(text),match.end()+150)].replace('\n',' '))
                            if len(evidence)==3:break
                        if not evidence:
                            for u in sorted(content_uids):
                                if pat in uid_to_id[u]:
                                    where=text.find(u);evidence.append(text[max(0,where-100):where+len(u)+150].replace('\n',' '))
                                    if len(evidence)==3:break
                        content_matches.append(dict(patient=pat,contexts=evidence))
            else:r['name_only_files']+=1
            if mentions:r['hits'].append(dict(path=rel,classification=classify(rel),content_sha256=file_sha,patients=sorted(mentions),name_patient_ids=sorted(name_ids),name_uids=sorted(name_uids),content_uid_count=len(content_uids),focused_contexts=content_matches))
        r['focused_hits']=[x for x in r['hits'] if set(x['patients'])&focused]
        r['focused_requires_review']=[x for x in r['focused_hits'] if 'requires_role_review' in x['classification']]
        r['complete']=True
    except Exception as exc:r['errors'].append(type(exc).__name__+': '+str(exc))
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_02.json',r)
    write(OUT/'focused15_review_queue_attempt_02.json',dict(coverage_gaps=r['coverage_gaps'],focused_hits=r.get('focused_hits',[]),requires_review=r.get('focused_requires_review',[])))
    print(json.dumps({k:r.get(k) for k in ('complete','errors','listed_files','api_patients','api_mc_rc_patients','scanned_text_files','scanned_text_bytes','name_only_files','coverage_gaps')},ensure_ascii=False))
    print(json.dumps(dict(all_hit_files=len(r['hits']),focused_hit_files=len(r.get('focused_hits',[])),focused_requires_review=[x['path'] for x in r.get('focused_requires_review',[])]),ensure_ascii=False))
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
