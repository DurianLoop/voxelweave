"""Static complete-stage proof: primary reading, exact scalar exports and raw-source lineage."""
import ast,csv,hashlib,json,math,re,sys
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/stats_swap_and_source_stage_archive_manifest_2026-10-03.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as s:
        for b in iter(lambda:s.read(1048576),b''):h.update(b)
    return h.hexdigest()
def csvrows(p):
    with Path(p).open(encoding='utf-8',newline='') as s:return list(csv.DictReader(s))
def fscore(m):return Fraction(2*m['tp'],2*m['tp']+m['fp']+m['fn']) if m['dice'] is not None else None
def main():
    sys.stdout.reconfigure(encoding='utf-8');files=set();errors=[]
    def check(ok,msg):
        if not ok:errors.append(msg)
    def include(p):
        p=Path(p);check(p.is_file(),'Missing '+str(p))
        if p.is_file():files.add(p)
    def bind(p,d):
        include(p);check(Path(p).is_file() and sha(p)==d,'SHA '+str(p))
    def close(a,b,msg):check(a==b if a is None or b is None else math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-12),msg)
    def csvvalue(a,b,msg):
        if a is None:check(b=='',msg)
        elif isinstance(a,(int,float,Fraction)) and not isinstance(a,bool):close(a,float(b),msg)
        else:check(str(a)==b,msg)
    # Reading attestation binds exact pages and actual three PNG inspections.
    src=ROOT/'literature/source_cache/masked_normalization_primary_2026-10-03';rr=read(src/'reading_provenance.json');ext=read(src/'extraction_attempt_03.json')
    bind(src/'extraction_attempt_03.json',rr['extraction_manifest_sha256']);bind(ROOT/rr['report'],rr['report_sha256']);bind(ROOT/'literature/register_masked_normalization_reading_2026_10_03.py',rr['script_sha256'])
    check(rr['new_public_primary_pdfs']==3 and rr['actual_pdf_page_anchors']==28 and rr['actual_visual_pages_reviewed']==3 and rr['visual_review_completed'],'Reading scope')
    ranges={'region_normalization':list(range(1,9)),'partial_convolution':[3,5,6,7,8,9,12,13,14],'normalization_equivariance':list(range(1,11))+[21]}
    for x in rr['papers']:
        for k in ('pdf','text','pages'):bind(src/x[k],x[k+'_sha256'])
        check((src/x['pdf']).read_bytes().startswith(b'%PDF'),'PDF magic')
        pages=read(src/x['pages']);check(x['actual_read_pages']==ranges[x['key']] and x['actual_page_anchors']==[p for p in pages if p['page'] in ranges[x['key']]],'Read page scope')
        bind(src/x['visual_png'],x['visual_png_sha256']);check(x['actual_focused_primary_reading_completed'] and not x['author_experiments_independently_reproduced'] and not x['separate_supplement_read'],'Reading role')
    for x in rr['retained_failures']:bind(src/x['file'],x['sha256'])
    # Pilot complete all30/all72; exports are checked from saved exact confusion counts.
    pilot=ROOT/'experiments/task_stats_swap_cpu_pilot';r=read(pilot/'attempt_01.json');q=read(pilot/'independent_inputs_domains_and_all30_estimates.json');c=read(pilot/'run_contract.json')
    check(r['complete'] and q['complete'] and not r['errors'] and not q['errors'] and r['new_neural_forwards']==6 and q['paired_endpoints_verified']==30 and q['domain_confusion_cells_verified']==72,'Pilot completion')
    bind(pilot/'attempt_01.json',q['result_sha256']);bind(ROOT/'experiments/verify_task_stats_swap_cpu_pilot.py',q['script_sha256']);bind(pilot/'run_contract.json',r['run_contract_sha256'])
    for x in c['files']:bind(ROOT.parent/x['path'],x['sha256'])
    records={}
    for e in r['patients']:
        bind(ROOT/e['file'],e['sha256']);bind(ROOT/e['verification_file'],e['verification_sha256']);x=read(ROOT/e['file']);bind(ROOT/x['prediction_file'],x['prediction_sha256'])
        records.setdefault(x['patient'],{})[x['condition']]=x
        for name,d in x['diagonals'].items():records[x['patient']][name+'_'+name+'stats']=d
    erows=csvrows(pilot/'all30_endpoints.csv');prows=csvrows(pilot/'all90_patient_differences.csv');check(len(erows)==30 and len(prows)==90,'Pilot export denominators')
    for a,b in zip(r['analysis'],erows):
        for key in ('reference','domain','comparison','original_denominator','defined_n','mean'):csvvalue(a[key],b[key],'Endpoint CSV')
        check(','.join(a['undefined_patients'])==b['undefined_patients'],'Undefined CSV')
    expected=[{k:e[k] for k in ('reference','domain','comparison')}|p for e in r['analysis'] for p in e['patient_differences']]
    for a,b in zip(expected,prows):
        for k,v in a.items():csvvalue(v,b[k],'Patient CSV')
    counts=csvrows(pilot/'all72_acquisition_domain_counts.csv');diffs=csvrows(pilot/'all90_acquisition_domain_differences.csv');check(len(counts)==72 and len(diffs)==90,'Acquisition export denominator')
    for x in counts:
        m=records[x['patient']][x['condition']]['domain_confusion'][x['reference']][x['domain']]
        for k,v in m.items():csvvalue(v,x[k],'Acquisition count CSV')
    for x in diffs:
        v={name:fscore(row['domain_confusion'][x['reference']][x['domain']]) for name,row in records[x['patient']].items()}
        if x['comparison']=='normalization_image_interaction':d=(v['post_poststats']-v['post_rawstats'])-(v['raw_poststats']-v['raw_rawstats']) if all(a is not None for a in v.values()) else None
        else:left,right=x['comparison'].split('-');d=v[left]-v[right] if v[left] is not None and v[right] is not None else None
        csvvalue(d is not None,x['defined'],'Acquisition defined');csvvalue(d,x['difference'],'Acquisition difference')
    for folder,proofname,script in [('full45_normalization_drift_cpu','independent_scalar_csv_and_correlations.json','verify_full45_normalization_drift_cpu.py'),('mc_rc_011_013_label_grid','independent_all230_headers_and_5_labels_attempt_02.json','verify_mc_rc_011_013_header_label.py')]:
        p=ROOT/'experiments'/folder;r=read(p/'attempt_01.json');q=read(p/proofname);check(r['complete'] and q['complete'] and not r['errors'] and not q['errors'] and q['new_neural_forwards']==0 and q['scientific_confirmation_patients']==0 and not q['publication_claim_confirmed'],'New CPU completion')
        bind(p/'attempt_01.json',q.get('result_sha256',q.get('label_result_sha256')));bind(ROOT/'experiments'/script,q['script_sha256'])
        for b in r.get('source_bindings',[]):bind(ROOT/b['path'],b['sha256'])
        if folder=='full45_normalization_drift_cpu':
            check(q['patients_verified']==45 and q['domain_moment_cells_verified']==270 and q['manual_correlations_verified']==12 and q['csv_rows_verified']==45,'All45 denominator')
            c=read(p/'run_contract.json');bind(p/'run_contract.json',r['run_contract_sha256'])
            for b in c['files']:bind(ROOT.parent/b['path'],b['sha256'])
            for e in r['patients']:
                bind(ROOT/e['file'],e['sha256']);x=read(ROOT/e['file'])
                for b in x['source_bindings']:bind(ROOT/b['path'],b['sha256'])
            bind(ROOT/r['csv_file'],r['csv_sha256']);check(len(csvrows(p/'all12_descriptive_associations.csv'))==12,'Associations exported')
        else:
            check(q['raw_dicom_headers_verified']==230 and q['labels_verified']==5 and q['passed_series']==3,'Source denominator')
            head=ROOT/'literature/source_cache/mc_rc_011_013_headers_2026-10-03';h=read(head/'attempt_01.json');bind(head/'attempt_01.json',q['header_result_sha256'])
            check(h['complete'] and not h['errors'] and h['total_transfer_bytes']==75590775 and len(h['series'])==5 and h['automatic_retries']==0 and not h['MR_pixel_array_decoded'],'Source transfer role')
            for x in h['series']:bind(ROOT/x['transfer']['file'],x['transfer']['sha256']);bind(head/x['header_file'],x['header_sha256'])
            for x in r['series']:bind(ROOT/x['label_file'],x['label_sha256'])
            failed=read(p/'independent_all230_headers_and_5_labels.json');check(not failed['complete'] and bool(failed['errors']),'First proof retained');bind(p/'verifier_failed_attempt_01.py.txt',failed['script_sha256'])
            check(len(csvrows(p/'all5_source_qualification.csv'))==5,'All source CSV')
    role=read(ROOT/'experiments/mc_rc_source_roles_metadata_preparation/attempt_01.json');check(role['catalogue_candidate_patients']==71 and role['catalogue_candidate_series']==159 and role['remaining_catalogue_candidate_patients']==63 and role['remaining_catalogue_candidate_series']==138 and role['qualified_scientific_confirmation_patients']==0 and not role['complete_project_exposure_crosswalk_proven'],'Role preparation denominator')
    for b in role['source_bindings']:bind(ROOT/b['path'],b['sha256'])
    bind(ROOT/role['csv_file'],role['csv_sha256']);check(len(csvrows(ROOT/role['csv_file']))==159,'Role CSV')
    for folder,producer in [('task_stats_swap_cpu_pilot','report_task_stats_swap_cpu_pilot.py'),('full45_normalization_drift_cpu','report_full45_normalization_drift_cpu.py'),('mc_rc_011_013_label_grid','report_mc_rc_011_013_source_preflight.py')]:
        p=ROOT/'experiments'/folder;v=read(p/'report_provenance.json');bind(ROOT/'experiments'/producer,v['script_sha256'])
        for e in v['outputs']:bind(ROOT/e['path'],e['sha256'])
    for folder in ('experiments/task_stats_swap_cpu_pilot','experiments/full45_normalization_drift_cpu','experiments/mc_rc_source_roles_metadata_preparation','experiments/mc_rc_011_013_label_grid','literature/source_cache/masked_normalization_primary_2026-10-03','literature/source_cache/masked_normalization_restoration_search_2026-10-03','literature/source_cache/mc_rc_011_013_headers_2026-10-03','literature/source_cache/stats_swap_and_source_entry_snapshot_2026-10-03'):
        for p in (ROOT/folder).iterdir():
            if p.is_file():include(p)
    names=['README.md','EXPERIMENT_QUEUE.md','TASK_STATS_SWAP_CPU_PILOT_PLAN_2026-10-03.md','TASK_STATS_SWAP_CPU_PILOT_RESULT_2026-10-03.md','FULL45_NORMALIZATION_DRIFT_CPU_PLAN_2026-10-03.md','FULL45_NORMALIZATION_DRIFT_CPU_RESULT_2026-10-03.md','MC_RC_SOURCE_ROLE_METADATA_PREPARATION_PLAN_2026-10-03.md','MC_RC_011_013_HEADER_AND_LABEL_PLAN_2026-10-03.md','MC_RC_011_013_SOURCE_PREFLIGHT_RESULT_2026-10-03.md','INNOVATION_DECISION_AFTER_STATS_SWAP_2026-10-03.md','STATS_SWAP_AND_SOURCE_NEXT_PREPARATION_2026-10-03.md','SESSION_USER_PROVIDED_SUMMARY_STATS_SWAP_2026-10-03.md','SESSION_VISIBLE_DIALOGUE_STATS_SWAP_AND_SOURCE_2026-10-03.md','SESSION_UPDATE_STATS_SWAP_AND_SOURCE_2026-10-03.md','SESSION_HANDOFF_STATS_SWAP_AND_SOURCE_2026-10-03.md','SESSION_FINAL_RECEIPT_STATS_SWAP_AND_SOURCE_2026-10-03.md']
    names += ['experiments/'+n for n in ('task_stats_swap_cpu_pilot.py','verify_task_stats_swap_cpu_pilot.py','report_task_stats_swap_cpu_pilot.py','full45_normalization_drift_cpu.py','verify_full45_normalization_drift_cpu.py','report_full45_normalization_drift_cpu.py','prepare_mc_rc_source_roles_metadata.py','audit_mc_rc_011_013_label_grid.py','verify_mc_rc_011_013_header_label.py','report_mc_rc_011_013_source_preflight.py')]
    names += ['literature/'+n for n in ('2026-10-03_masked_normalization_primary_reading.md','register_masked_normalization_reading_2026_10_03.py','fetch_masked_normalization_primary_2026_10_03.py','extract_masked_normalization_primary_attempt_02_2026_10_03.py','search_masked_normalization_restoration_2026_10_03.py','download_mc_rc_011_013_headers_2026_10_03.py','prepare_stats_swap_and_source_entries_2026_10_03.py')]
    for n in names:include(ROOT/n)
    include(Path(__file__))
    for p in files:
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
        if p.suffix=='.md':
            for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if not target.startswith(('https://','http://','#','mailto:')):check((p.parent/target.split('#',1)[0]).exists(),'Broken link '+str(p)+': '+target)
    manifest=dict(scope='Complete six crossed CPU forwards and all30/72 pilot, three primary PDFs/28 read pages/3 visual pages, all45 statistics without forwards, exact-UID source roles and fixed three-patient five-series raw/header/label preflight, retained failures, session/navigation.',
                  new_primary_pdfs=3,actual_read_pdf_page_anchors=28,actual_visual_pages=3,stage_new_neural_forwards=6,continuation_new_neural_forwards=0,full45_replayed_old_arrays=90,
                  source_dicom_headers=230,source_labels=5,passed_source_series=3,scientific_confirmation_patients=0,publication_claim_confirmed=False,
                  files=[dict(path=Path(ospath).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files) for ospath in [__import__('os').path.relpath(p,ROOT)]])
    if '--write' in sys.argv:OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:check(OUT.exists() and read(OUT)==manifest,'Current stage manifest stale')
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'}|dict(files=len(files),errors=errors),ensure_ascii=False));return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
