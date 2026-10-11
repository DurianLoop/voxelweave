"""Static integrity and scope checks for this completed batch; no model or MR decoding."""
import ast,csv,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/direct_adaptation_and_identity_stage_manifest_2026-10-03.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def csvrows(p):
    with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def main():
    sys.stdout.reconfigure(encoding='utf-8');errors=[];files=set()
    def check(ok,msg):
        if not ok:errors.append(msg)
    def include(p):
        p=Path(p);check(p.is_file(),'Missing '+str(p))
        if p.is_file():files.add(p)
    def bind(p,expected):include(p);check(Path(p).is_file() and sha(p)==expected,'SHA '+str(p))
    head=ROOT/'literature/source_cache/mc_rc_next12_headers_2026-10-03';h=read(head/'attempt_01.json')
    label=ROOT/'experiments/mc_rc_next12_label_grid';r=read(label/'attempt_01.json');q=read(label/'independent_all1475_headers_and_25_labels_attempt_01.json')
    check(h['complete'] and r['complete'] and q['complete'] and not h['errors'] and not r['errors'] and not q['errors'],'Source/proof completion')
    check(len(h['series'])==len(r['series'])==25 and q['raw_dicom_headers_verified']==1475 and q['labels_verified']==25,'Source denominator')
    check(h['header_qualified_series']==22 and r['source_preflight_series_passed']==q['passed_series']==21 and len(q['patients'])==12,'Source positive and negative denominator')
    check(h['total_transfer_bytes']==302254256 and h['automatic_retries']==0 and not h['MR_pixel_array_decoded'],'Transfer role')
    check(not r['MR_pixel_arrays_decoded'] and not q['MR_pixel_arrays_decoded'] and not q['torch_imported'] and r['new_neural_forwards']==q['new_neural_forwards']==0,'No new model/MR array')
    bind(label/'attempt_01.json',q['label_result_sha256']);bind(head/'attempt_01.json',q['header_result_sha256']);bind(ROOT/'experiments/verify_mc_rc_next12_header_label.py',q['script_sha256'])
    bind(ROOT/'literature/download_mc_rc_next12_headers_2026_10_03.py',h['script_sha256']);bind(ROOT/'experiments/audit_mc_rc_next12_label_grid.py',r['script_sha256'])
    for x in h['source_bindings']+r['source_bindings']:bind(ROOT/x['path'],x['sha256'])
    for x in h['series']:bind(ROOT/x['transfer']['file'],x['transfer']['sha256']);bind(head/x['header_file'],x['header_sha256'])
    for x in r['series']:bind(ROOT/x['label_file'],x['label_sha256'])
    check({x['series_uid'] for x in r['series']}=={x['source']['SeriesInstanceUID'] for x in h['series']},'Exact source UID sets')
    rows=csvrows(label/'all25_source_qualification.csv');check(len(rows)==25 and sum(x['source_preflight_passed']=='True' for x in rows)==21,'CSV all25')
    prov=read(label/'report_provenance.json')
    for x in prov['outputs']:bind(ROOT/x['path'],x['sha256'])
    source=ROOT/'literature/source_cache/task_adaptation_direct_fulltexts_2026-10-03';reading=read(source/'reading_provenance.json')
    check(reading['new_primary_bodies_read']==3 and reading['new_primary_pdfs']==0 and reading['actual_focused_primary_anchors']==152,'Reading actual scope')
    bind(ROOT/reading['report'],reading['report_sha256']);bind(ROOT/'literature/register_task_adaptation_direct_reading_2026_10_03.py',reading['script_sha256'])
    for x in reading['papers']:
        for k in ('raw','block','text'):bind(source/x[k+'_file'],x[k+'_sha256'])
        blocks=read(source/x['block_file']);check(x['actual_read_blocks']==[dict(index=i,**blocks[i]) for i in x['actual_read_block_ids']],'Actual block anchors')
        check(x['actual_focused_primary_reading_completed'] and not x['author_experiments_independently_reproduced'] and not x['visual_figures_reviewed'] and not x['separate_supplement_read'],'Reading limits')
    for x in reading['source_manifests']:bind(source/x['file'],x['sha256'])
    xmlfetch=read(source/'attempt_01.json');check(not xmlfetch['papers'][0]['fulltext_acquired'] and xmlfetch['papers'][0]['error'],'XMLfront failure retained')
    htmlfail=read(source/'tumorsynth_public_html_attempt_02.json');htmlok=read(source/'tumorsynth_html_extraction_attempt_03.json')
    check(not htmlfail['fulltext_acquired'] and 'bs4' in htmlfail['error'] and htmlok['fulltext_acquired'] and htmlok['network_requests']==0,'bs4 failure and saved response extraction')
    table=read(source/'fibroid_table_aggregate_audit_attempt_01.json');check(table['complete'] and len(table['table1_comparisons'])==7,'CPU original table audit')
    bind(ROOT/reading['search_file'],reading['search_sha256']);search=read(ROOT/reading['search_file']);check(sum(len(x['items']) for x in search['responses'])==27,'Discovery duplicates denominator')
    idir=ROOT/'experiments/mc_rc_local_identity_audit';a=read(idir/'attempt_02.json');g=read(idir/'gap_stream_attempt_01.json');fail=read(idir/'failed_listing_attempt_01.json')
    check(a['complete'] and g['complete'] and not a['errors'] and not g['errors'] and not fail['complete'],'Identity attempts role')
    check(a['listed_files']==503812 and a['scanned_text_files']==23432 and a['scanned_text_bytes']==784587920 and len(a['focused_hits'])==114 and len(a['focused_requires_review'])==3,'Identity scan scope')
    bind(idir/a['listing_file'],a['listing_sha256']);bind(idir/fail['script_snapshot'],fail['script_sha256']);bind(idir/fail['stderr_file'],fail['stderr_sha256'])
    bind(idir/'attempt_02.json',g['prior_audit_sha256']);bind(ROOT/'experiments/audit_mc_rc_identity_gap_stream_2026_10_03.py',g['script_sha256'])
    check(len(g['streamed_texts'])==14 and g['scanned_bytes']==1453853303 and all(not x['patients'] for x in g['streamed_texts']),'Stream all14 scope')
    check(not a['complete_project_exposure_crosswalk_proven'] and not g['complete_project_exposure_crosswalk_proven'],'No global identity proof claim')
    role=ROOT/'experiments/mc_rc_predeclared_patient_allocation';p=read(role/'attempt_01.json');rs=csvrows(ROOT/p['csv_file'])
    bind(ROOT/p['csv_file'],p['csv_sha256']);bind(ROOT/'experiments/prepare_mc_rc_predeclared_patient_allocation_2026_10_03.py',p['script_sha256'])
    for x in p['source_bindings']:bind(ROOT/x['path'],x['sha256'])
    check(len(rs)==159 and len({x['patient'] for x in rs})==71 and len(p['manual_reviews'])==3,'All159 role coverage')
    expected=[x['patient'] for x in sorted(p['hashed_order'],key=lambda x:hashlib.sha256((p['hash_salt']+x['patient']).encode()).hexdigest())]
    check(expected[:4]==p['validation_candidate_patient_ids'] and expected[4:]==p['confirmation_reserved_candidate_patient_ids'],'Predeclared patient order')
    groups=[set(p[k]) for k in ('development_training_candidate_patient_ids','validation_candidate_patient_ids','confirmation_reserved_candidate_patient_ids')]
    check([len(x) for x in groups]==[11,4,8] and all(not groups[i]&groups[j] for i in range(3) for j in range(i)),'Patient role independence')
    check(not set.union(*groups)&set(p['shared_vs_seg_patient_ids_excluded']) and len(p['shared_vs_seg_patient_ids_excluded'])==58,'Shared full-patient exclusion')
    check(not p['final_scientific_split_activated'] and not p['selection_used_outcomes'] and p['scientific_confirmation_patients']==0 and not p['publication_claim_confirmed'],'Allocation not confirmation')
    for patient in {x['patient'] for x in rs}:check(len({x['patient_role'] for x in rs if x['patient']==patient})==1,'Same patient all times same role')
    folders=['experiments/mc_rc_next12_label_grid','experiments/mc_rc_local_identity_audit','experiments/mc_rc_predeclared_patient_allocation','literature/source_cache/mc_rc_next12_headers_2026-10-03','literature/source_cache/task_adaptation_direct_fulltexts_2026-10-03','literature/source_cache/task_adaptation_direct_search_2026-10-03']
    for folder in folders:
        for f in (ROOT/folder).rglob('*'):
            if f.is_file():include(f)
    names=['README.md','EXPERIMENT_QUEUE.md','MC_RC_NEXT12_IDENTITY_SOURCE_PLAN_2026-10-03.md','MC_RC_NEXT12_LABEL_GRID_ADDENDUM_2026-10-03.md','MC_RC_NEXT12_SOURCE_PREFLIGHT_RESULT_2026-10-03.md','MC_RC_LOCAL_IDENTITY_AUDIT_PLAN_2026-10-03.md','MC_RC_IDENTITY_GAP_STREAM_ADDENDUM_2026-10-03.md','MC_RC_LOCAL_IDENTITY_AND_ALLOCATION_RESULT_2026-10-03.md','INNOVATION_DECISION_AFTER_DIRECT_ADAPTATION_READING_2026-10-03.md','TASK_ADAPTATION_NEXT_TRIAL_PREPARATION_2026-10-03.md','SESSION_UPDATE_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md','SESSION_HANDOFF_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md','SESSION_VISIBLE_DIALOGUE_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md','SESSION_USER_PROVIDED_HANDOFF_DIRECT_ADAPTATION_2026-10-03.md','SESSION_FINAL_RECEIPT_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md']
    names+=['experiments/'+x for x in ('prepare_next12_source_scripts_2026_10_03.py','audit_mc_rc_next12_label_grid.py','verify_mc_rc_next12_header_label.py','report_mc_rc_next12_source_preflight_2026_10_03.py','audit_mc_rc_local_identity_2026_10_03.py','resume_mc_rc_identity_from_saved_listing_2026_10_03.py','audit_mc_rc_local_identity_attempt_02_2026_10_03.py','audit_mc_rc_identity_gap_stream_2026_10_03.py','prepare_mc_rc_predeclared_patient_allocation_2026_10_03.py')]
    names+=['literature/'+x for x in ('2026-10-03_task_adaptation_direct_search_plan.md','2026-10-03_task_adaptation_direct_selection.md','2026-10-03_task_adaptation_direct_fulltext_reading.md','search_task_adaptation_direct_2026_10_03.py','download_mc_rc_next12_headers_2026_10_03.py','fetch_task_adaptation_direct_2026_10_03.py','show_task_adaptation_blocks_2026_10_03.py','fetch_tumorsynth_public_html_2026_10_03.py','extract_tumorsynth_saved_html_attempt_03_2026_10_03.py','audit_fibroid_table_aggregates_2026_10_03.py','register_task_adaptation_direct_reading_2026_10_03.py')]
    for x in names:include(ROOT/x)
    include(Path(__file__));include(ROOT/'literature/finalize_direct_adaptation_identity_archive_2026_10_03.py');include(ROOT/'literature/repair_direct_adaptation_archive_checker_2026_10_03.py');include(ROOT/'literature/verify_direct_adaptation_stage_failed_attempt_01.py.txt');include(ROOT/'literature/direct_adaptation_archive_failure_provenance_2026-10-03.json');include(ROOT/'SESSION_ARCHIVE_VERIFICATION_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.json')
    for f in files:
        if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8'))
        if f.suffix=='.md':
            for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',f.read_text(encoding='utf-8')):
                if not target.startswith(('http://','https://','#','mailto:')):check((f.parent/target.split('#',1)[0]).exists(),'Broken link '+str(f)+': '+target)
    manifest=dict(scope='Three focused primary bodies/152 read anchors; fixed25 source production and independent all1475 header/all25 label reread; bounded local identity scope and retained failures; inactive predeclared all159 roles; complete session/preparation records.',new_primary_bodies_read=3,actual_read_anchors=152,new_neural_forwards=0,source_qualified_series=21,source_patients=12,patient_allocation_sizes=[11,4,8],scientific_confirmation_patients=0,publication_claim_confirmed=False,
                  files=[dict(path=f.relative_to(ROOT).as_posix(),bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(files)])
    if '--write' in sys.argv:OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:check(OUT.exists() and read(OUT)==manifest,'Stage manifest differs')
    print(json.dumps(dict(files=len(files),errors=errors,new_primary_bodies_read=3,source_qualified_series=21,new_neural_forwards=0,scientific_confirmation_patients=0),ensure_ascii=False));return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
