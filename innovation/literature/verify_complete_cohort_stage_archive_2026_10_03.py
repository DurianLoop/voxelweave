"""Bind terminal cohort, actual real-data replays, failed baseline and two readings."""
import ast, hashlib, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'literature/complete_cohort_stage_archive_manifest_2026-10-03.json'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()

def main():
    sys.stdout.reconfigure(encoding='utf-8');files=set();errors=[];external=[]
    def check(ok,msg):
        if not ok: errors.append(msg)
    def include(p):
        p=Path(p).resolve();check(p.is_file(),'Missing '+str(p))
        if p.is_file() and p.is_relative_to(ROOT): files.add(p)
    def bind(p,digest):
        include(p);check(Path(p).is_file() and sha(p)==digest,'Hash differs '+str(p))
        if Path(p).is_file() and not Path(p).resolve().is_relative_to(ROOT): external.append(dict(path=Path(p).relative_to(ROOT.parent).as_posix(),sha256=digest))
    cohort=ROOT/'experiments/vs_seg_full_volume_cohort';queue=ROOT/'experiments/vs_seg_full_volume_queue';contract=read(cohort/'run_contract.json');check(sha(cohort/'run_contract.json')=='061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5','Original contract changed')
    original=read(queue/'attempt_01.json');follow=read(ROOT/'experiments/vs_seg_selection_after_complete_queue/attempt_01.json')
    check(original['complete'] and original['active_stage']=='complete' and all(r['returncode']==0 for r in original['stages']),'Original complete/exit records differ')
    check(follow['complete'] and follow['active_stage']=='complete' and len(follow['stages'])==2 and all(r['returncode']==0 for r in follow['stages']),'Followup complete records differ')
    for item in contract['files']: bind(ROOT.parent/item['path'],item['sha256'])
    for stage in original['stages']: bind(ROOT/stage['log_file'],stage['log_sha256'])
    for item in follow['files']: bind(ROOT/item['path'],item['sha256'])
    count=0
    for patient in contract['main_roster']+contract['secondary_roster']:
        proof=read(cohort/f'verification_{patient}.json');check(not proof['errors'] and proof['reconstruction_pixels_independently_regenerated'] and proof['script_sha256']==sha(ROOT/'experiments/verify_vs_seg_full_volume_cohort.py'),'Whole patient proof differs '+patient);include(cohort/f'verification_{patient}.json')
        proofs={(x['condition'],x['prediction_sha256']) for x in proof['checked_conditions']};successful=[]
        for path in (cohort/'patients'/patient).glob('*_attempt_*.json'):
            r=read(path);include(path)
            if r.get('complete'): bind(ROOT/r['prediction_file'],r['prediction_sha256']);successful.append((r['condition'],r['prediction_sha256']));count+=1
        check(len(successful)==7 and set(successful)==proofs,'Seven-condition bindings differ '+patient)
    check(count==322 and len(contract['main_roster'])==45 and len(contract['secondary_roster'])==1,'Full322/45+1 denominator differs')
    ppath=ROOT/'experiments/vs_seg_complete_analysis_cpu/independent_all_frozen_estimates_replay.json';p=read(ppath);spath=ROOT/'experiments/vs_seg_selection_sensitivity/independent_real_all_endpoints_replay.json';s=read(spath)
    check(p['complete'] and not p['errors'] and p['replayed_endpoints']==58 and not p['fixed_joint_direction_supported'],'58 replay or primary failure differs');bind(queue/'completed_analysis.json',p['completed_analysis_sha256']);bind(cohort/'status.json',p['status_sha256']);bind(ROOT/'experiments/verify_vs_seg_complete_analysis_cpu.py',p['script_sha256']);bind(ROOT/'VS_SEG_COMPLETE_ANALYSIS_REPLAY_PLAN_2026-10-03.md',p['plan_sha256'])
    check(s['complete'] and not s['errors'] and s['endpoints_replayed']==112,'112 real replay differs');bind(ROOT/s['result_file'],s['result_sha256']);bind(ROOT/'experiments/verify_vs_seg_selection_real_cpu.py',s['verification_script_sha256'])
    for proof in (p,s):
        for record in proof['record_provenance']: bind(ROOT/record['file'],record['sha256'])
    pre=read(ROOT/'experiments/vs_seg_complete_analysis_preflight/attempt_01.json');check(pre['complete'] and pre['synthetic_only'] and not pre['patient_effects_read'] and not pre['errors'],'Known-answer preflight differs');bind(ROOT/'experiments/verify_vs_seg_complete_analysis_cpu.py',pre['verifier_sha256'])
    provenance=read(ROOT/'experiments/vs_seg_complete_analysis_cpu/human_report_provenance.json');bind(ppath,provenance['primary_proof_sha256']);bind(spath,provenance['selection_proof_sha256']);bind(ROOT/'experiments/report_vs_seg_complete_evidence.py',provenance['report_script_sha256'])
    for record in provenance['files']: bind(ROOT/record['path'],record['sha256'])
    add=ROOT/'experiments/residual_addback_cpu';a=read(add/'attempt_01.json');ap=read(add/'independent_algebra_and_roi_replay.json');check(a['complete'] and not a['errors'] and len(a['series'])==6 and sum(x['targets'] for x in a['series'])==297 and sum(x['development_gate_passed'] for x in a['series'])==2 and a['fixed_candidate_stopped'],'Fixed addback failure/denominator differs');check(ap['complete'] and not ap['errors'] and not a['new_neural_inferences'] and not a['task_inference_executed'],'Addback actual proof differs');bind(add/'attempt_01.json',ap['result_sha256']);bind(add/'run_contract.json',ap['run_contract_sha256']);bind(ROOT/'experiments/verify_residual_addback_cpu.py',ap['script_sha256'])
    for f in read(add/'run_contract.json')['files']: bind(ROOT.parent/f['path'],f['sha256'])
    ar=read(add/'report_provenance.json');bind(add/'attempt_01.json',ar['result_sha256']);bind(add/'independent_algebra_and_roi_replay.json',ar['proof_sha256']);bind(ROOT/'RESIDUAL_ADDBACK_CPU_RESULT_2026-10-03.md',ar['report_sha256']);bind(ROOT/'experiments/report_residual_addback_cpu.py',ar['script_sha256'])
    directory=ROOT/'literature/source_cache/task_utility_fulltexts_2026-10-03';reading=read(directory/'reading_provenance.json');routes=read(directory/'routes_attempt_01.json');html=read(directory/'benchmark_html_attempt_01.json');bind(directory/'routes_attempt_01.json',reading['routes_index_sha256']);bind(directory/'benchmark_html_attempt_01.json',reading['html_index_sha256']);bind(ROOT/reading['report'],reading['report_sha256']);bind(ROOT/'literature/fetch_task_utility_routes_2026_10_03.py',routes['script_sha256']);bind(ROOT/'literature/fetch_task_utility_benchmark_html_2026_10_03.py',html['script_sha256']);blocks=0
    for paper in reading['papers']:
        for key in ('raw','text','paragraph'): bind(directory/paper[key+'_file'],paper[key+'_sha256'])
        paragraphs=read(directory/paper['paragraph_file']);check(paper['actual_relevant_reading_completed'] and not paper['training_reproduced'] and not paper['supplementary_read'] and not paper['visual_figures_reviewed'],'Reading scope overstated')
        for start,finish in paper['paragraph_ranges_zero_based']: check(0<=start<=finish<len(paragraphs),'Reading interval out of range');blocks+=finish-start+1
    check(reading['new_fulltexts_read']==2 and blocks==139 and reading['new_pdfs']==0,'Two actual reading scope differs')
    search=ROOT/'literature/source_cache/task_utility_search_2026-10-03';index=read(search/'attempt_01.json');bind(ROOT/'literature/search_task_utility_2026_10_03.py',index['script_sha256']);bind(ROOT/'literature/2026-10-03_task_utility_search_plan.md',index['plan_sha256']);check(sum(x['returned'] for x in index['responses'])==26,'Bounded index title count differs')
    for response in index['responses']: bind(search/response['raw_file'],response['raw_sha256'])
    for folder in ('experiments/vs_seg_full_volume_queue','experiments/vs_seg_selection_after_complete_queue','experiments/vs_seg_complete_analysis_cpu','experiments/vs_seg_selection_sensitivity','experiments/vs_seg_complete_analysis_preflight','experiments/residual_addback_cpu','literature/source_cache/task_utility_search_2026-10-03','literature/source_cache/task_utility_fulltexts_2026-10-03'):
        for path in (ROOT/folder).iterdir():
            if path.is_file(): include(path)
    names=['README.md','EXPERIMENT_QUEUE.md','VS_SEG_FULL_VOLUME_COHORT_COMPLETE_RESULT_2026-10-02.md','VS_SEG_COMPLETE_ANALYSIS_REPLAY_PLAN_2026-10-03.md','VS_SEG_COMPLETE_EVIDENCE_RESULT_2026-10-03.md','VS_SEG_SELECTION_SENSITIVITY_REAL_RESULT_2026-10-03.md','FROZEN_TASK_EVALUATOR_FOLLOWUP_PREPARATION_2026-10-03.md','RESIDUAL_ADDBACK_CPU_PLAN_2026-10-03.md','RESIDUAL_ADDBACK_CPU_RESULT_2026-10-03.md','INNOVATION_DECISION_AFTER_COMPLETE_COHORT_2026-10-03.md','SESSION_VISIBLE_DIALOGUE_COMPLETE_COHORT_2026-10-03.md','SESSION_USER_PROVIDED_SUMMARY_COMPLETE_COHORT_2026-10-03.md','SESSION_UPDATE_COMPLETE_COHORT_2026-10-03.md','SESSION_HANDOFF_COMPLETE_COHORT_2026-10-03.md','experiments/verify_vs_seg_complete_analysis_cpu.py','experiments/preflight_vs_seg_complete_analysis_cpu.py','experiments/report_vs_seg_complete_evidence.py','experiments/residual_addback_cpu.py','experiments/verify_residual_addback_cpu.py','experiments/report_residual_addback_cpu.py','literature/2026-10-03_task_utility_search_plan.md','literature/2026-10-03_task_utility_fulltext_selection.md','literature/2026-10-03_task_utility_fulltext_reading.md','literature/search_task_utility_2026_10_03.py','literature/fetch_task_utility_routes_2026_10_03.py','literature/fetch_task_utility_benchmark_html_2026_10_03.py','literature/update_complete_cohort_entrypoints_2026_10_03.py','literature/verify_complete_cohort_all_archives_2026_10_03.py','literature/source_cache/complete_cohort_actual_process_observation_2026-10-03.json']
    for name in names: include(ROOT/name)
    include(Path(__file__))
    for path in files:
        if path.suffix=='.py': ast.parse(path.read_text(encoding='utf-8'))
    snapshot=read(ROOT/'literature/source_cache/complete_cohort_actual_process_observation_2026-10-03.json');check(snapshot['actual_terminal_polls'] and all(v==0 for v in snapshot['terminal_exit_codes'].values()) and not snapshot['scientific_goal_complete'],'Snapshot completion promoted to scientific goal')
    manifest=dict(scope='Terminal original45+1 all322 saved outputs,58+112 actual scalar estimates,all-six failed addback baseline,two read bodies,preparations and public dialogue',main_patients=45,secondary_patients=1,conditions=322,all_frozen_estimates_replayed=58,all_selection_endpoints_replayed=112,original_negative_claim_supported=False,addback_development_items=6,addback_missing_targets=297,addback_passed=2,new_bodies_read=2,new_related_blocks_read=139,new_pdfs=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,external_read_only_source_bindings=sorted({x['path']:x for x in external}.values(),key=lambda x:x['path']),files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)])
    if '--write' in sys.argv: MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else: check(MANIFEST.is_file() and read(MANIFEST)==manifest,'Current stage manifest stale')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('files','external_read_only_source_bindings')}|dict(files=len(files),errors=errors),ensure_ascii=False,indent=2));return int(bool(errors))

if __name__=='__main__': raise SystemExit(main())
