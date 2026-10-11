"""Static provenance, denominators and scope checks for this batch; no model evaluation."""
import ast,csv,json,hashlib,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/sparse_task_training_stage_manifest_2026-10-03.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');errors=[];files=set()
    def check(ok,message):
        if not ok:errors.append(message)
    def include(p):
        p=Path(p);check(p.is_file(),'Missing '+str(p))
        if p.is_file():files.add(p)
    def bind(p,digest):include(p);check(Path(p).is_file() and sha(p)==digest,'SHA '+str(p))
    prepfile=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json';prep=read(prepfile);check(prep['complete'] and not prep['errors'] and len(prep['cases'])==19,'Current 19 source cases')
    counts=prep['counts'];check([counts[k]['qualified_series'] for k in ('development_training_candidate','validation_candidate','confirmation_reserved_candidate')]==[19,9,12],'Current 40 qualified series')
    check(prep['patient_roles_unchanged'] and not prep['final_scientific_split_activated'],'Roles unchanged/inactive scientific split');bind(ROOT/prep['csv_file'],prep['csv_sha256']);bind(ROOT/'experiments/prepare_mc_rc_current_development_cases_2026_10_03.py',prep['script_sha256'])
    with (ROOT/prep['csv_file']).open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    check(len(rows)==159 and len({c['patient'] for c in prep['cases']})==11,'159 role rows/11 developers')
    for patient in {x['patient'] for x in rows}:check(len({x['patient_role'] for x in rows if x['patient']==patient})==1,'Same patient role '+patient)
    ip=ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json';p=read(ip);qp=ip.parent/'independent_all19_observed_inputs_and_label_axes_attempt_01.json';q=read(qp)
    check(p['complete'] and q['complete'] and not p['errors'] and not q['errors'],'Input production/proof complete');check(q['observed_dicom_planes_verified']==354 and q['sparse_inputs_verified']==76 and q['labels_verified']==19,'Input proof denominator');check(p['saved_observed_bytes']==116973848,'Saved observed packages')
    bind(ip,q['result_sha256']);bind(prepfile,p['preparation_sha256']);bind(ROOT/'experiments/verify_mc_rc_development_training_input_cpu.py',q['script_sha256']);bind(ROOT/'experiments/audit_mc_rc_development_training_input_cpu.py',p['script_sha256']);bind(ROOT/'experiments/mc_rc_observed_only_training_input.py',p['loader_sha256'])
    for x in p['series']:bind(ROOT/x['observed_package'],x['observed_package_sha256'])
    check(not p['non_observed_MR_pixels_decoded'] and not q['non_observed_MR_pixels_decoded'] and not p['torch_imported'] and not q['torch_imported'],'Only observed production/proof input')
    lit=ROOT/'literature/source_cache/sparse_task_joint_fulltexts_2026-10-03';reading=read(lit/'reading_provenance.json');check(reading['new_primary_bodies_read']==4 and reading['actual_focused_primary_anchors']==393 and reading['new_primary_pdfs']==0,'Reading 4/393/PDF0');bind(ROOT/reading['report'],reading['report_sha256']);bind(ROOT/reading['search_file'],reading['search_sha256']);bind(ROOT/'literature/register_sparse_task_joint_reading_2026_10_03.py',reading['script_sha256'])
    for paper in reading['papers']:
        for k in ('raw','block','text'):bind(lit/paper[k+'_file'],paper[k+'_sha256'])
        blocks=read(lit/paper['block_file']);check(paper['actual_read_blocks']==[dict(index=i,**blocks[i]) for i in paper['actual_read_block_ids']],'Read anchors '+paper['key']);check(not paper['author_experiments_independently_reproduced'] and not paper['visual_figures_reviewed'] and not paper['separate_supplement_read'],'Reading bounds '+paper['key'])
    for x in reading['source_manifests']:bind(lit/x['file'],x['sha256'])
    check(not read(lit/'lge_sr_extra_attempt_01.json')['fulltext_acquired'] and read(lit/'lge_sr_public_html_attempt_02.json')['fulltext_acquired'],'LGE failed XML and successful HTML retained');acq=read(lit/'attempt_01.json');snapshot=ROOT/'literature/source_cache/sparse_task_entry_snapshot_2026-10-03';bind(snapshot/'selection_before_addendum.md',acq['selection_sha256'])
    n=read(snapshot/'provenance.json')
    for x in n['snapshots']:bind(ROOT/x['snapshot'],x['sha256'])
    neural_calls=0
    for folder,script in [('mc_rc_sparse_task_training_cpu_pilot','run_mc_rc_sparse_task_training_cpu_pilot.py'),('mc_rc_single_developer_fit_diagnostic_cpu','run_mc_rc_single_developer_fit_diagnostic_cpu.py')]:
        rp=ROOT/'experiments'/folder/'attempt_01.json';r=read(rp);proof=read(rp.parent/'independent_metrics_and_checkpoint_attempt_01.json');check(r['complete'] and proof['complete'] and not r['errors'] and not proof['errors'],'Training/proof complete '+folder);check(r['updates_completed']==4000 and not r['pretrained_weights_loaded'],'From scratch fixed budget '+folder);check(not r['gpu_initialized'] and not proof['gpu_initialized'] and not r['validation_or_confirmation_patients_opened'] and not r['native_hidden_MR_pixels_decoded'],'CPU/development input scope '+folder)
        bind(rp,proof['result_sha256']);bind(ROOT/'experiments'/script,r['script_sha256']);bind(ROOT/'experiments/mc_rc_sparse_task_cpu_pilot_support.py',r['support_sha256']);bind(ROOT/r['protocol_file'],r['protocol_sha256']);bind(ROOT/r['checkpoint_file'],r['checkpoint_sha256']);bind(ROOT/'experiments'/('verify_mc_rc_sparse_task_training_cpu_pilot.py' if folder=='mc_rc_sparse_task_training_cpu_pilot' else 'verify_mc_rc_single_developer_fit_diagnostic_cpu.py'),proof['script_sha256'])
        for e in r['evaluations']:bind(ROOT/e['prediction_file'],e['prediction_file_sha256'])
        check(r['scientific_confirmation_patients']==proof['scientific_confirmation_patients']==0 and not r['publication_claim_confirmed'] and not proof['publication_claim_confirmed'],'No scientific confirmation '+folder);neural_calls+=r['neural_forward_calls']+proof['neural_forward_calls']
        if folder=='mc_rc_sparse_task_training_cpu_pilot':check(not r['capability_gate_passed'] and 'VS-MC-RC-013' not in r['training_patient_ids'] and sum(r['training_sampling_counts'].values())==4000 and proof['checkpoint_replayed_planes']==12,'Failed pilot/exclusion/replay')
        else:check(not r['fit_gate_passed'] and r['training_patient_ids']==['VS-MC-RC-012'] and len(proof['checkpoint_replayed_planes'])==3,'Failed single-case fit/replay')
    check(neural_calls==13779,'Total neural forward calls');report=read(ROOT/'experiments/mc_rc_sparse_task_training_cpu_pilot/report_provenance.json');bind(ROOT/report['report'],report['report_sha256'])
    for x in report['source_bindings']:bind(ROOT/x['path'],x['sha256'])
    figure=read(ROOT/'figures/mc_rc_sparse_task_cpu_pilot/provenance.json')
    for x in figure['outputs']:bind(ROOT/x['path'],x['sha256'])
    folders=['experiments/mc_rc_current_development_input_preparation','experiments/mc_rc_development_training_input_cpu','experiments/mc_rc_sparse_task_training_cpu_pilot','experiments/mc_rc_single_developer_fit_diagnostic_cpu','literature/source_cache/sparse_task_joint_fulltexts_2026-10-03','literature/source_cache/sparse_task_joint_search_2026-10-03','literature/source_cache/sparse_task_entry_snapshot_2026-10-03','figures/mc_rc_sparse_task_cpu_pilot']
    for folder in folders:
        for f in (ROOT/folder).rglob('*'):
            if f.is_file():include(f)
    names=['README.md','EXPERIMENT_QUEUE.md','MC_RC_DEVELOPMENT_INPUT_CPU_PLAN_2026-10-03.md','MC_RC_DEVELOPMENT_INPUT_CPU_RESULT_2026-10-03.md','MC_RC_SPARSE_TASK_TRAINING_CPU_PILOT_PLAN_2026-10-03.md','MC_RC_SINGLE_DEVELOPER_FIT_DIAGNOSTIC_PLAN_2026-10-03.md','MC_RC_SPARSE_TASK_TRAINING_CPU_RESULT_2026-10-03.md','INNOVATION_DECISION_AFTER_SPARSE_TASK_TRAINING_2026-10-03.md','SPARSE_TASK_CAPABILITY_AND_MATRIX_NEXT_PREPARATION_2026-10-03.md','SESSION_USER_PROVIDED_SUMMARY_SPARSE_TASK_2026-10-03.md','SESSION_VISIBLE_DIALOGUE_SPARSE_TASK_2026-10-03.md','SESSION_UPDATE_SPARSE_TASK_TRAINING_2026-10-03.md','SESSION_HANDOFF_SPARSE_TASK_TRAINING_2026-10-03.md','SESSION_FINAL_RECEIPT_SPARSE_TASK_2026-10-03.md']
    names+=['experiments/'+x for x in ('prepare_mc_rc_current_development_cases_2026_10_03.py','mc_rc_observed_only_training_input.py','audit_mc_rc_development_training_input_cpu.py','verify_mc_rc_development_training_input_cpu.py','mc_rc_sparse_task_cpu_pilot_support.py','run_mc_rc_sparse_task_training_cpu_pilot.py','verify_mc_rc_sparse_task_training_cpu_pilot.py','run_mc_rc_single_developer_fit_diagnostic_cpu.py','verify_mc_rc_single_developer_fit_diagnostic_cpu.py','plot_mc_rc_sparse_task_development_diagnosis_cpu.py','report_mc_rc_sparse_task_training_cpu_results.py')]
    names+=['literature/'+x for x in ('2026-10-03_sparse_task_joint_search_plan.md','2026-10-03_sparse_task_joint_selection.md','2026-10-03_sparse_task_joint_fulltext_reading.md','prepare_sparse_task_joint_search_2026_10_03.py','prepare_sparse_task_joint_fulltexts_2026_10_03.py','search_sparse_task_joint_2026_10_03.py','fetch_sparse_task_joint_fulltexts_2026_10_03.py','show_sparse_task_joint_blocks_2026_10_03.py','fetch_lge_superresolution_extra_2026_10_03.py','fetch_lge_sr_public_html_attempt_02_2026_10_03.py','register_sparse_task_joint_reading_2026_10_03.py','prepare_sparse_task_archive_navigation_2026_10_03.py','finalize_sparse_task_session_archive_2026_10_03.py')]
    for name in names:include(ROOT/name)
    include(Path(__file__))
    for f in files:
        if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8'))
        if f.suffix=='.md':
            for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',f.read_text(encoding='utf-8')):
                if not target.startswith(('http://','https://','#','mailto:')):check((f.parent/target.split('#',1)[0]).exists(),'Broken link '+str(f)+': '+target)
    manifest=dict(scope='Four primary research bodies and 393 actual text anchors; current40 qualification/19 developer observed-only packages; two failed task capability trainings, 8000updates, independent metrics and 15 plane replay; complete visible dialogue/preparation/provenance.',new_primary_bodies_read=4,actual_read_anchors=393,current_qualified_series=40,developer_input_series=19,new_training_updates=8000,new_neural_forward_calls=13779,scientific_confirmation_patients=0,publication_claim_confirmed=False,files=[dict(path=f.relative_to(ROOT).as_posix(),bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(files)])
    if '--write' in sys.argv:OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:check(OUT.exists() and read(OUT)==manifest,'Stage manifest differs')
    print(json.dumps(dict(files=len(files),errors=errors,new_primary_bodies_read=4,new_training_updates=8000,new_neural_forward_calls=13779,scientific_confirmation_patients=0),ensure_ascii=False));return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
