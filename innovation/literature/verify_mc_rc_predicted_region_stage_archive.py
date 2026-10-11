"""Static completed evidence audit; never inspect live native or main-cohort scores."""
import hashlib,json,re,sys,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'literature/mc_rc_predicted_region_stage_archive_manifest_2026-10-03.json'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');errors=[];files={Path(__file__),ROOT/'README.md',ROOT/'EXPERIMENT_QUEUE.md'}
 def check(ok,msg):
  if not ok: errors.append(msg)
 def bind(p,expected):
  p=Path(p).resolve();ok=p.is_relative_to(ROOT) and p.is_file();check(ok,'Missing/outside file '+str(p))
  if ok: files.add(p);check(sha(p)==expected,'Hash lineage differs '+p.relative_to(ROOT).as_posix())
 def include(p):
  p=Path(p);check(p.is_file(),'Missing required stage file '+str(p))
  if p.is_file(): files.add(p)
 for folder,proof_name in [('mc_rc_observed_region_propagation','independent_raw_label_roi_verification.json'),('mc_rc_frozen_predicted_region_cpu','independent_observed_input_roi_and_model_replay.json')]:
  directory=ROOT/'experiments'/folder;r=read(directory/'attempt_01.json');c=read(directory/'run_contract.json');p=read(directory/proof_name)
  check(r['complete'] and not r['errors'] and not p['errors'],folder+' not complete/verified')
  bind(directory/'run_contract.json',r['run_contract_sha256']);bind(directory/'attempt_01.json',p['result_sha256']);bind(ROOT/('experiments/verify_'+folder+'.py'),p['verification_script_sha256'])
  check(len(r['series'])==15 and r['scientific_independent_validation_patients']==0 and not r['publication_claim_confirmed'] and not r['gpu_used'],folder+' scope promoted')
  for entry in c['files']: bind(ROOT/entry['path'],entry['sha256'])
  for item in directory.iterdir():
   if item.is_file(): include(item)
  if 'frozen' in folder:
   check(p['counts']==dict(series=15,patients=8,fresh_neural_replays=15,raw_headers_checked=1069,genuine_observed_arrays_decoded=268,missing_targets=759,strategies_per_target=6),'Predicted verification coverage differs')
   check(not r['strict_all_series_primary_gate_passed'] and all(not row['primary_gate_passed'] for row in r['series']),'Fixed predicted failure lost')
   for row in r['series']:
    bind(ROOT/row['prediction_file'],row['prediction_sha256']);bind(ROOT/row['primary_roi_file'],row['primary_roi_sha256'])
  else: check(r['strict_all_series_geometric_gate_passed'],'Ideal geometric outcome differs')
 directory=ROOT/'experiments/mc_rc_source_denominator_correction';r=read(directory/'attempt_01.json');include(directory/'attempt_01.json')
 for entry in r['files']: bind(ROOT/entry['path'],entry['sha256'])
 proof_dirs=['mc_rc_native_t2_label_gate','mc_rc_004_006_native_label_gate','mc_rc_007_010_native_label_gate'];eligible=set()
 for name in proof_dirs:
  p=read(ROOT/'experiments'/name/'independent_raw_geometry_grid_verification.json');check(not p['errors'],'Source proof errors '+name);eligible.update(row['uid'] for row in p['series'] if row['source_preflight_passed'])
 cases=r['cases'];found={row['uid'] for row in cases};old={row['uid'] for row in read(ROOT/'experiments/mc_rc_frozen_predicted_region_cpu/run_contract.json')['cases']}
 check(r['complete'] and not r['errors'] and len(r['all_source_qualification'])==24 and found==eligible and len(found)==16 and len({row['patient'] for row in cases})==8,'Corrected authoritative roster differs')
 check(found-old==set(r['omitted_uids'])=={'1.3.6.1.4.1.14519.5.2.1.213711595575218613093188251544325434833'} and not old-found,'Omission correction differs')
 check(not r['MR_pixels_decoded'] and not r['new_label_arrays_decoded'],'Denominator audit scope differs')
 directory=ROOT/'literature/source_cache/predicted_region_search_2026-10-03';r=read(directory/'attempt_01.json');include(directory/'attempt_01.json');bind(ROOT/'literature/search_predicted_region_followup_2026_10_03.py',r['script_sha256']);bind(ROOT/'literature/2026-10-03_predicted_region_followup_search_plan.md',r['plan_sha256'])
 check([row['returned'] for row in r['responses']]==[12,12,5,12] and all('error' not in row for row in r['responses']),'Index scope differs')
 for row in r['responses']:
  bind(directory/row['raw_file'],row['raw_sha256']);payload=read(directory/row['raw_file']);check(len(payload['resultList']['result'])==row['returned'],'Raw search count differs')
 directory=ROOT/'literature/source_cache/predicted_region_fulltexts_2026-10-03';r=read(directory/'attempt_01.json');reading=read(directory/'reading_provenance.json');include(directory/'reading_provenance.json');bind(directory/'attempt_01.json',reading['acquisition_index_sha256']);bind(ROOT/'literature/fetch_predicted_region_fulltexts_2026_10_03.py',r['script_sha256']);bind(ROOT/'literature/2026-10-03_predicted_region_fulltext_selection.md',r['plan_sha256'])
 check(reading['new_fulltexts_read']==3 and len(r['papers'])==3,'Fulltext scope differs')
 paragraphs=0
 for paper in r['papers']:
  bind(directory/paper['raw_file'],paper['raw_sha256']);bind(directory/paper['text_file'],paper['text_sha256']);xml=ET.parse(directory/paper['raw_file']).getroot();article=xml if xml.tag=='article' else xml.find('.//article');check(article is not None and article.find('body') is not None,'Missing fulltext body')
  doi=[ ''.join(e.itertext()).lower() for e in article.findall('.//article-id') if e.get('pub-id-type')=='doi'];check(paper['expected_doi'].lower() in doi,'DOI identity differs')
  record=next(x for x in reading['papers'] if x['doi']==paper['expected_doi']);check(record['actual_reading_completed'] and not record['training_reproduced'],'Actual reading role differs');bind(ROOT.parent/record['text_file'],record['text_sha256']);bind(ROOT.parent/record['raw_file'],record['raw_sha256'])
  indices=[int(x) for x in re.findall(r'^\[(\d+) [^]]+\]',(directory/paper['text_file']).read_text(encoding='utf-8'),re.M)];check(indices==list(range(paper['paragraphs'])),'Extracted paragraph indices differ')
  for start,end in record['paragraph_ranges_zero_based']: check(0<=start<=end<len(indices),'Reading interval invalid');paragraphs+=end-start+1
 check(paragraphs==372,'Actual relevant reading denominator differs');include(ROOT/reading['report']);include(ROOT/reading['previous_pdf_method_page_visually_rechecked'])
 snapshot_path=ROOT/'literature/source_cache/mc_rc_predicted_native_queue_observation_2026-10-03.json';snapshot=read(snapshot_path);include(snapshot_path)
 check(snapshot['historical_snapshot_only'] and snapshot['actual_poll_before_snapshot'] and snapshot['original_session']==83910 and snapshot['native_session']==80884 and not snapshot['scientific_goal_complete'],'Historical live snapshot promoted')
 old_policy=read(ROOT/'experiments/mc_rc_visible_joint_development_diagnostic/attempt_01.json');check(not old_policy['fixed_visible_joint_diagnostic_gate_passed'] and not old_policy['original_raw_development_gate_passed'],'Old failed policy restored')
 names=['MC_RC_OBSERVED_REGION_PROPAGATION_PLAN_2026-10-03.md','MC_RC_OBSERVED_REGION_PROPAGATION_RESULT_2026-10-03.md','MC_RC_FROZEN_PREDICTED_REGION_CPU_PLAN_2026-10-03.md','MC_RC_FROZEN_PREDICTED_REGION_CPU_RESULT_2026-10-03.md','MC_RC_SOURCE_DENOMINATOR_CORRECTION_PLAN_2026-10-03.md','MC_RC_SOURCE_DENOMINATOR_CORRECTION_RESULT_2026-10-03.md','MC_RC_NATIVE_COMPETENCE_CPU_PLAN_2026-10-03.md','MC_RC_NEXT_REPRESENTATION_AND_ACTION_PREPARATION_2026-10-03.md','INNOVATION_DECISION_AFTER_PREDICTED_REGION_2026-10-03.md','SESSION_IMPORTED_CHECKPOINT_PREDICTED_REGION_2026-10-03.md','SESSION_UPDATE_MC_RC_PREDICTED_REGION_2026-10-03.md','SESSION_VISIBLE_DIALOGUE_MC_RC_PREDICTED_REGION_2026-10-03.md','SESSION_HANDOFF_MC_RC_PREDICTED_NATIVE_QUEUE_ACTIVE_2026-10-03.md','experiments/mc_rc_source_denominator_correction.py','experiments/mc_rc_native_competence_cpu.py','experiments/verify_mc_rc_native_competence_cpu.py','experiments/mc_rc_native_competence_queue.py','literature/verify_mc_rc_predicted_region_all_archives_2026_10_03.py']
 for name in names: include(ROOT/name)
 manifest=dict(scope='completed old15 ideal/predicted evidence, corrected source roster, three fulltext readings and preparation; excludes live native/main-cohort outputs',new_fulltexts_read=3,related_paragraphs_read=paragraphs,new_pdfs=0,index_records=41,old_frozen_series=15,current_qualified_series=16,development_patients=8,primary_predicted_gate_passed_series=0,scientific_independent_validation_patients=0,publication_claim_confirmed=False,files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)])
 if '--write' in sys.argv: MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else: check(MANIFEST.is_file() and read(MANIFEST)==manifest,'Stage manifest stale')
 print(json.dumps({k:v for k,v in manifest.items() if k!='files'}|dict(files=len(files),errors=errors),ensure_ascii=False,indent=2));return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
