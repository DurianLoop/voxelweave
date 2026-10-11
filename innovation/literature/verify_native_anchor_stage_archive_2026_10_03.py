"""Static completed native/QDA/readings; exclude live original and followup outputs."""
import ast,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];MANIFEST=ROOT/'literature/native_anchor_stage_archive_manifest_2026-10-03.json'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''): h.update(block)
 return h.hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');errors=[];files=set()
 def check(ok,msg):
  if not ok: errors.append(msg)
 def include(p):
  p=Path(p).resolve();check(p.is_relative_to(ROOT) and p.is_file(),'Missing/outside stage evidence '+str(p))
  if p.is_file() and p.is_relative_to(ROOT): files.add(p)
 def bind(p,expected): include(p);check(Path(p).is_file() and sha(p)==expected,'Frozen hash differs '+str(p))
 for directory,proof_name,expected in [('mc_rc_native_competence_cpu','independent_native_model_and_roi_replay.json',17),('mc_rc_anchor_qda_cpu','independent_anchor_qda_replay.json',4)]:
  out=ROOT/'experiments'/directory;r=read(out/'attempt_01.json');c=read(out/'run_contract.json');p=read(out/proof_name);check(r['complete'] and not r['errors'] and not p['errors'] and len(r['series'])==16,'Complete model proof differs '+directory);bind(out/'attempt_01.json',p['result_sha256']);bind(out/'run_contract.json',p['run_contract_sha256']);check(r['run_contract_sha256']==sha(out/'run_contract.json'),'Result contract differs');check(p['counts']['series']==16 and p['counts']['patients']==8 and p['counts']['missing_targets']==864,'Whole source denominator differs')
  for f in c['files']: bind(ROOT/f['path'],f['sha256'])
  for path in out.iterdir():
   if path.is_file(): include(path)
  summary=read(out/'descriptive_summary.json')
  for f in summary['files']: bind(ROOT/f['path'],f['sha256'])
  if directory=='mc_rc_native_competence_cpu':
   check(p['counts']['fresh_neural_replays']==17 and p['counts']['raw_native_arrays_decoded']==1213,'All native replay count differs');check(abs(summary['patient_equal_missing_dice_native_minus_sparse']-r['patient_equal_missing_dice_native_minus_sparse'])<1e-12,'Frozen descriptive native endpoint differs')
   for name in ('native','sparse'): check(summary['conditions'][name]['roi_gate_passed_series']==0,'Native/sparse failure rescued')
   check(summary['omitted_source']['ideal_gate_passed'] and summary['omitted_source']['missing_targets']==105,'Omitted002 ideal source differs')
  else:
   check(p['counts']['methods']==4 and p['counts']['fresh_anchor_classifications']==1216 and len(r['folds'])==8,'All QDA replay count differs');check(not r['hidden_MR_pixel_arrays_decoded'] and not r['missing_label_used_for_training'],'Forbidden new input role')
   for method in c['methods']: check(r['summary'][method]['roi_gate_passed']==0 and summary['methods'][method]['roi_gate_passed']==0,'QDA fixed failure rescued')
   for fold in r['folds']: check(len(fold['training_patients'])==7 and fold['patient'] not in fold['training_patients'],'QDA whole-patient exclusion differs');bind(ROOT/fold['model_file'],fold['model_sha256'])
  check(not r['gpu_used'] and r['scientific_independent_validation_patients']==0 and not r['publication_claim_confirmed'],'Model replay promoted to science claim')
 search=ROOT/'literature/source_cache/anchor_representation_search_2026-10-03';s=read(search/'attempt_01.json');bind(ROOT/'literature/search_anchor_representation_2026_10_03.py',s['script_sha256']);bind(ROOT/'literature/2026-10-03_anchor_representation_search_plan.md',s['plan_sha256']);count=0
 for response in s['responses']:
  bind(search/response['raw_file'],response['raw_sha256']);payload=read(search/response['raw_file']);check(len(payload['resultList']['result'])==response['returned'],'Index response count differs');count+=response['returned']
 directory=ROOT/'literature/source_cache/anchor_representation_fulltexts_2026-10-03';reading=read(directory/'reading_provenance.json');r=read(directory/'attempt_01.json');alternate=read(directory/'html_alternate_attempt_01.json');bind(directory/'attempt_01.json',reading['acquisition_index_sha256']);bind(directory/'html_alternate_attempt_01.json',reading['html_index_sha256']);bind(ROOT/'literature/fetch_anchor_representation_fulltexts_2026_10_03.py',r['script_sha256']);bind(ROOT/'literature/fetch_anchor_representation_html_2026_10_03.py',alternate['script_sha256']);bind(ROOT/'literature/2026-10-03_anchor_representation_fulltext_selection.md',r['plan_sha256']);historical=read(directory/'historical_forest_attempt_01.json');bind(directory/historical['raw_file'],historical['raw_sha256']);count+=len(historical['items']);check(count==55 and reading['new_fulltexts_read']==3 and reading['new_pdfs']==0,'Reading/index scope differs');segments=0
 for paper in reading['papers']:
  bind(directory/paper['raw_file'],paper['raw_sha256']);bind(directory/paper['text_file'],paper['text_sha256']);indices=[int(x) for x in re.findall(r'^\[(\d+) [^]]+\]',(directory/paper['text_file']).read_text(encoding='utf-8'),re.M)];check(indices==list(range(len(indices))),'Paragraph sequence differs')
  for a,b in paper['paragraph_ranges_zero_based']: check(0<=a<=b<len(indices),'Invalid reading interval');segments+=b-a+1
  check(paper['actual_relevant_reading_completed'] and not paper['training_reproduced'] and not paper['supplementary_read'] and not paper['visual_figures_reviewed'],'Reading boundary promoted')
 check(segments==256,'Actual read segment denominator differs');include(ROOT/reading['report'])
 for path in directory.iterdir():
  if path.is_file(): include(path)
 for folder in ('experiments/mc_rc_native_competence_queue','experiments/mc_rc_anchor_qda_queue','experiments/mc_rc_anchor_qda_preflight','literature/source_cache/entry_encoding_fix_2026-10-03'):
  for path in (ROOT/folder).iterdir():
   if path.is_file(): include(path)
 check(not read(ROOT/'experiments/mc_rc_anchor_qda_preflight/attempt_01.json')['errors'],'Synthetic preflight differs')
 names=['README.md','EXPERIMENT_QUEUE.md','MC_RC_NATIVE_COMPETENCE_CPU_RESULT_2026-10-03.md','MC_RC_ANCHOR_QDA_CPU_PLAN_2026-10-03.md','MC_RC_ANCHOR_QDA_CPU_RESULT_2026-10-03.md','INNOVATION_DECISION_AFTER_NATIVE_AND_QDA_2026-10-03.md','MC_RC_NEXT_EVIDENCE_PREPARATION_AFTER_NATIVE_2026-10-03.md','VS_SEG_SELECTION_REAL_REPLAY_PLAN_2026-10-03.md','SESSION_IMPORTED_CHECKPOINT_NATIVE_AND_ANCHOR_2026-10-03.md','SESSION_VISIBLE_DIALOGUE_NATIVE_AND_ANCHOR_2026-10-03.md','SESSION_UPDATE_NATIVE_AND_ANCHOR_2026-10-03.md','SESSION_HANDOFF_NATIVE_AND_ANCHOR_ORIGINAL_QUEUE_ACTIVE_2026-10-03.md','experiments/report_mc_rc_native_competence_cpu.py','experiments/mc_rc_anchor_qda_cpu.py','experiments/verify_mc_rc_anchor_qda_cpu.py','experiments/mc_rc_anchor_qda_queue.py','experiments/preflight_mc_rc_anchor_qda_cpu.py','experiments/report_mc_rc_anchor_qda_cpu.py','experiments/verify_vs_seg_selection_real_cpu.py','experiments/vs_seg_selection_after_complete_queue.py','literature/update_native_anchor_entrypoints_2026_10_03.py','literature/verify_native_anchor_all_archives_2026_10_03.py']
 for name in names: include(ROOT/name)
 include(Path(__file__));include(ROOT/'SESSION_USER_PROVIDED_SUMMARY_NATIVE_AND_ANCHOR_2026-10-03.md');snapshot_path=ROOT/'literature/source_cache/native_anchor_queue_observation_2026-10-03.json';include(snapshot_path);snapshot=read(snapshot_path);check(snapshot['historical_snapshot_only'] and snapshot['actual_poll_before_snapshot'] and not snapshot['scientific_goal_complete'] and snapshot['original_session']==83910 and snapshot['followup_session']==56604 and snapshot['native_actual_exit_code']==0 and snapshot['anchor_actual_exit_code']==0,'Historical process snapshot promoted')
 for path in files:
  if path.suffix=='.py': ast.parse(path.read_text(encoding='utf-8'))
 manifest=dict(scope='completed native16/QDA16 mathematical and raw-input proofs, three readings, entry repair, preparations and visible dialogue; excludes live original45/followup outputs',qualified_series=16,development_patients=8,missing_targets=864,native_neural_replays=17,QDA_anchor_classifications=1216,native_roi_passed=0,sparse_roi_passed=0,joint_QDA_roi_passed=0,new_fulltexts_read=3,index_records=55,related_segments_read=256,new_pdfs=0,scientific_independent_validation_patients=0,publication_claim_confirmed=False,files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)])
 if '--write' in sys.argv: MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else: check(MANIFEST.is_file() and read(MANIFEST)==manifest,'Stage manifest stale')
 print(json.dumps({k:v for k,v in manifest.items() if k!='files'}|dict(files=len(files),errors=errors),ensure_ascii=False,indent=2));return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
