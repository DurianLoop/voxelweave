"""Audit finished experiments, primary-body reading, figures and session records."""
import ast,csv,json,hashlib,re,sys
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/order_risk_and_phase_stage_archive_manifest_2026-10-03.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as stream:
  for block in iter(lambda:stream.read(1048576),b''):h.update(block)
 return h.hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');files=set();external={};errors=[]
 def check(ok,label):
  if not ok:errors.append(label)
 def include(p):
  p=Path(p).resolve();check(p.is_file(),'Missing '+str(p))
  if p.is_file() and p.is_relative_to(ROOT):files.add(p)
 def bind(p,digest):
  include(p);check(Path(p).is_file() and sha(p)==digest,'SHA differs '+str(p))
  if Path(p).is_file() and not Path(p).resolve().is_relative_to(ROOT):external[str(Path(p).resolve())]=digest
 def contract(folder):
  p=ROOT/'experiments'/folder/'run_contract.json';include(p)
  for f in read(p)['files']:bind(ROOT.parent/f['path'],f['sha256'])
 def complete(folder,proofname):
  p=ROOT/'experiments'/folder;r=read(p/'attempt_01.json');q=read(p/proofname);check(r['complete'] and q['complete'] and not r['errors'] and not q['errors'],'Complete/proof differs '+folder);bind(p/'attempt_01.json',q['result_sha256']);contract(folder);check(not r['publication_claim_confirmed'],'Scientific claim overstated '+folder);return p,r,q
 risk,riskr,riskp=complete('observable_order_risk_cpu','independent_observables_and_rankings.json');check(len(riskr['patients'])==45 and riskp['old_analytic_volumes_replayed']==180 and riskp['policies_checked']==6 and riskp['random_same_budget_draws_checked']==5000 and riskp['main_fixed_candidate_stopped'] and riskp['patients_meeting_both_label_guard']==16,'Risk fixed denominator/gate differs');bind(ROOT/'experiments/verify_observable_order_risk_cpu.py',riskp['script_sha256'])
 for x in riskr['patients']:bind(ROOT/x['file'],x['sha256'])
 rp=read(risk/'report_provenance.json');bind(ROOT/'experiments/report_observable_order_risk_cpu.py',rp['script_sha256']);bind(ROOT/rp['report'],rp['report_sha256']);bind(ROOT/rp['csv'],rp['csv_sha256'])
 post,postr,postp=complete('vs_seg_post_resize_task_cpu','independent_all_tasks_and_estimates.json');check(len(postr['patients'])==45 and len(postr['analysis'])==len(postp['endpoints'])==18 and postr['new_neural_forwards']==45,'Post all45/18 differs');bind(ROOT/'experiments/verify_vs_seg_post_resize_task_cpu.py',postp['script_sha256'])
 for x in postr['patients']:
  bind(ROOT/x['record_file'],x['record_sha256']);bind(ROOT/x['verification_file'],x['verification_sha256']);record=read(ROOT/x['record_file']);bind(ROOT/record['prediction_file'],record['prediction_sha256']);check(record['complete'] and not record['cuda_initialized'],'Post GPU/completion differs')
 pr=read(post/'report_provenance.json');bind(ROOT/'experiments/report_vs_seg_post_resize_task_cpu.py',pr['script_sha256'])
 for x in pr['outputs']:bind(ROOT/x['path'],x['sha256'])
 with (post/'all18_descriptive_task_endpoints.csv').open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.DictReader(stream))
 check(len(rows)==18 and all(float(x['mean_difference'])==y['estimate']['mean_difference'] for x,y in zip(rows,postr['analysis'])),'All18 CSV actual values differ')
 phase,phaser,phasep=complete('anchor_bandwidth_diagnostic_cpu','independent_gradient_and_identities.json');check(len(phaser['patients'])==45 and phasep['old_analytic_volumes_replayed']==90 and phasep['total_intervals']==855 and len(phaser['analysis'])==4,'Bandwidth denominator differs');bind(ROOT/'experiments/verify_anchor_bandwidth_diagnostic_cpu.py',phasep['script_sha256'])
 for x in phaser['patients']:bind(ROOT/x['file'],x['sha256'])
 ap=read(phase/'report_provenance.json');bind(ROOT/'experiments/report_anchor_bandwidth_and_normalization_cpu.py',ap['script_sha256'])
 for x in ap['outputs']:bind(ROOT/x['path'],x['sha256'])
 first=ROOT/'experiments/anchor_normalization_control_cpu';second=ROOT/'experiments/anchor_normalization_control_cpu_attempt_02';a,b=read(first/'attempt_01.json'),read(second/'attempt_01.json');check(not a['complete'] and a['errors']==['AssertionError: '] and len(a['patients'])==3,'First normalization failure not preserved');check(b['complete'] and not b['errors'] and b['torch_imported'] and not b['cuda_initialized'] and b['all_six_fixed_stats_missing_and_tail_bitwise_equal'],'Actual repaired normalizer state differs');contract(first.name);contract(second.name);bind(first/'attempt_01.json',ap['normalizer_first_failure_sha256']);bind(second/'attempt_01.json',ap['normalizer_result_sha256'])
 pilot,pilotr,pilotp=complete('anchor_bandwidth_task_cpu_pilot','independent_inputs_and_all36_estimates.json');check(len(pilotr['patients'])==12 and pilotp['normalized_inputs_replayed']==12 and pilotp['fixed_missing_identities_verified']==6 and pilotp['task_analysis_endpoints_verified']==36 and pilotp['saved_prediction_proofs_verified']==12,'Pilot whole12 input/36 estimate coverage differs');bind(ROOT/'experiments/verify_anchor_bandwidth_task_pilot_final.py',pilotp['script_sha256'])
 for x in pilotr['patients']:
  bind(ROOT/x['file'],x['sha256']);bind(ROOT/x['verification_file'],x['verification_sha256']);v=read(ROOT/x['file']);bind(ROOT/v['prediction_file'],v['prediction_sha256'])
 pp=read(pilot/'report_provenance.json');bind(ROOT/'experiments/report_anchor_bandwidth_task_cpu_pilot.py',pp['script_sha256'])
 for x in pp['outputs']:bind(ROOT/x['path'],x['sha256'])
 anchors=0
 for folder in ('bandwidth_consistency_fulltexts_2026-10-03','phase_direct_neighbour_fulltexts_2026-10-03'):
  src=ROOT/'literature/source_cache'/folder;reading=read(src/'reading_provenance.json');fetch=read(src/'attempt_01.json');bind(src/'attempt_01.json',reading['fetch_manifest_sha256']);bind(ROOT/reading['report'],reading['report_sha256']);anchors+=reading['actual_focused_primary_anchors']
  for paper in reading['papers']:
   for key in ('raw','block','text'):bind(src/paper[key],paper[key+'_sha256'])
   tree=ET.parse(src/paper['raw']);article=tree.getroot() if tree.getroot().tag=='article' else tree.getroot().find('.//article');check(article is not None and article.find('body') is not None,'Actual body missing');check(paper['doi'].strip().casefold() in [''.join(e.itertext()).strip().casefold() for e in article.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi'],'Primary DOI identity differs '+paper['key']);blocks=read(src/paper['block'])
   for a in paper['anchors']:check(blocks[a['index']]=={k:a[k] for k in ('tag','text')},'Actual reading anchor differs')
   check(paper['actual_relevant_body_reading_completed'] and not paper['author_experiments_independently_reproduced'] and not paper['visual_figures_reviewed'] and not paper['supplementary_material_read'],'Reading scope overstated')
  search=ROOT/'literature'/reading['search_manifest'];bind(search,reading['search_manifest_sha256']);s=read(search)
  for response in s['responses']:bind(search.parent/response['raw_file'],response['raw_sha256'])
 check(anchors==221,'Five body focused anchor count differs')
 for name,snapshot in [('figure_provenance.json','plot_script_attempt_01.py'),('figure_provenance_attempt_02.json',None)]:
  v=read(post/name);bind(post/snapshot if snapshot else ROOT/'experiments/plot_post_task_and_bandwidth_cpu.py',v['script_sha256'])
  for x in v['outputs']:bind(ROOT/x['path'],x['sha256'])
 qa=read(post/'figure_visual_review_attempt_02.json');check(qa['actual_image_viewed'] and qa['visual_review_passed'] and qa['reviewed_png_sha256']==read(post/'figure_provenance_attempt_02.json')['outputs'][0]['sha256'],'Actual final figure review absent')
 names=['README.md','EXPERIMENT_QUEUE.md','SESSION_VISIBLE_DIALOGUE_ORDER_RISK_AND_PHASE_2026-10-03.md','SESSION_IMPORTED_CHECKPOINT_ORDER_RISK_AND_PHASE_2026-10-03.md','SESSION_USER_PROVIDED_SUMMARY_ORDER_RISK_AND_PHASE_2026-10-03.md','SESSION_UPDATE_ORDER_RISK_AND_PHASE_2026-10-03.md','SESSION_HANDOFF_ORDER_RISK_AND_PHASE_2026-10-03.md','INNOVATION_DECISION_AFTER_POST_TASK_AND_PHASE_2026-10-03.md','POST_TASK_AND_PHASE_NEXT_VALIDATION_PREPARATION_2026-10-03.md','OBSERVABLE_ORDER_RISK_CPU_RESULT_2026-10-03.md','ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_PLAN_2026-10-03.md','ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_RESULT_2026-10-03.md','ANCHOR_NORMALIZATION_CONTROL_CPU_PLAN_2026-10-03.md','ANCHOR_NORMALIZATION_CONTROL_CPU_REPAIR_2026-10-03.md','ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md','ANCHOR_BANDWIDTH_TASK_CPU_PILOT_PLAN_2026-10-03.md','ANCHOR_BANDWIDTH_TASK_CPU_PILOT_RESULT_2026-10-03.md','VS_SEG_POST_RESIZE_TASK_CPU_RESULT_2026-10-03.md']
 for name in names:include(ROOT/name)
 for folder in ('experiments/observable_order_risk_cpu','experiments/vs_seg_post_resize_task_cpu','experiments/anchor_bandwidth_diagnostic_cpu','experiments/anchor_normalization_control_cpu','experiments/anchor_normalization_control_cpu_attempt_02','experiments/anchor_bandwidth_task_cpu_pilot','literature/source_cache/bandwidth_consistency_search_2026-10-03','literature/source_cache/bandwidth_consistency_fulltexts_2026-10-03','literature/source_cache/acquired_synthesized_phase_search_2026-10-03','literature/source_cache/phase_direct_neighbour_fulltexts_2026-10-03','literature/source_cache/order_risk_and_phase_entry_snapshot_2026-10-03'):
  for p in (ROOT/folder).iterdir():
   if p.is_file():include(p)
 for p in (ROOT/'literature').glob('*2026_10_03.py'):
  if any(w in p.name for w in ('bandwidth','phase','order_risk')):include(p)
 for name in ('prepare_anchor_normalization_repair.py','anchor_normalization_control_cpu.py','anchor_normalization_control_cpu_attempt_02.py','verify_anchor_bandwidth_task_cpu.py','anchor_bandwidth_task_cpu_pilot.py'):include(ROOT/'experiments'/name)
 include(Path(__file__))
 for p in files:
  if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
  if p.suffix=='.md':
   for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
    if not target.startswith(('https://','http://','#','mailto:')):check((p.parent/target.split('#')[0]).exists(),'Broken link '+str(p)+': '+target)
 manifest=dict(scope='Completed all45 post task, observable-risk failure, all45 phase diagnostic, first/repaired normalizer pilot, complete3x4 anchors task with input/scalar proofs, five focused primary bodies and session records.',post_patients=45,post_endpoints=18,risk_patients=45,phase_intervals=855,pilot_patients=3,pilot_conditions=12,pilot_endpoints=36,new_primary_bodies_read=5,focused_primary_anchors=221,new_pdfs=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,scientific_goal_complete=False,files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)],external_read_only_bindings=[dict(path=k,sha256=v) for k,v in sorted(external.items())])
 if '--write' in sys.argv:OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else:check(OUT.exists() and read(OUT)==manifest,'Stage manifest stale')
 print(json.dumps({k:v for k,v in manifest.items() if k not in ('files','external_read_only_bindings')}|dict(files=len(files),errors=errors),ensure_ascii=False));return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
