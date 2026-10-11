"""Static archive audit; exclude every mutable file in the live task queue."""
import ast,csv,hashlib,json,re,sys
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/resampling_order_stage_archive_manifest_2026-10-03.json'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as stream:
  for block in iter(lambda:stream.read(1048576),b''): h.update(block)
 return h.hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');files=set();errors=[];external=[]
 def check(ok,label):
  if not ok: errors.append(label)
 def include(p):
  p=Path(p).resolve();check(p.is_file(),'Missing '+str(p))
  if p.is_file() and p.is_relative_to(ROOT): files.add(p)
 def bind(p,digest):
  include(p);check(Path(p).is_file() and sha(p)==digest,'Hash differs '+str(p))
  if Path(p).is_file() and not Path(p).resolve().is_relative_to(ROOT): external.append(dict(path=Path(p).relative_to(ROOT.parent).as_posix(),sha256=digest))
 analytic=ROOT/'experiments/vs_seg_resampling_order_cpu';result=read(analytic/'attempt_01.json');proof=read(analytic/'independent_replay_attempt_01.json');contract=read(analytic/'run_contract.json')
 check(result['complete'] and not result['errors'] and proof['complete'] and not proof['errors'],'All45 analytic completion/proof differs');check(len(result['patients'])==len(proof['patients'])==45 and result['total_targets']==proof['total_targets']==2565,'Analytic denominator differs');check(len(result['analysis'])==len(proof['endpoints'])==36,'All36 endpoint proof differs');bind(analytic/'attempt_01.json',proof['result_sha256']);bind(analytic/'run_contract.json',proof['run_contract_sha256']);bind(ROOT/'experiments/verify_vs_seg_resampling_order_cpu.py',proof['script_sha256']);check(contract['original_contract_sha256']=='061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5','Original contract identity differs');bind(ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json',contract['original_contract_sha256'])
 for record in contract['files']: bind(ROOT.parent/record['path'],record['sha256'])
 for record in result['patients']: bind(ROOT/record['file'],record['sha256'])
 check(result['existing_analytic_volumes_bitwise_replayed']==proof['existing_analytic_volumes_replayed']==180 and result['new_post_volumes_constructed']==proof['new_post_volumes_replayed']==90,'180/90 replay coverage differs')
 check(result['clipping']==proof['clipping'] and all(v['changed_pixels']==0 and v['changed_planes']==0 for k in result['clipping'].values() for v in k.values()),'Actual clipping differs');check(result['order_above_linear_tolerance']==proof['order_above_linear_tolerance']=={'linear':0,'pchip':45},'Linear/PCHIP explanatory gate differs')
 report=read(analytic/'report_provenance.json');bind(ROOT/'experiments/report_vs_seg_resampling_order_cpu.py',report['script_sha256']);bind(ROOT/'VS_SEG_RESAMPLING_ORDER_CPU_RESULT_2026-10-03.md',report['report_sha256']);bind(analytic/'all36_descriptive_endpoints.csv',report['csv_sha256']);bind(analytic/'attempt_01.json',report['result_sha256']);bind(analytic/'independent_replay_attempt_01.json',report['proof_sha256'])
 with (analytic/'all36_descriptive_endpoints.csv').open(encoding='utf-8-sig',newline='') as stream: csvrows=list(csv.DictReader(stream))
 check(len(csvrows)==36,'CSV endpoint count differs')
 for a,b in zip(csvrows,result['analysis']):
  check(all(a[k]==b[k] for k in ('kernel','region','weighting','comparison')) and float(a['mean_difference'])==b['estimate']['mean_difference'],'CSV endpoint values differ')
 first=read(analytic/'figure_provenance.json');second=read(analytic/'figure_provenance_attempt_02.json');qa=read(analytic/'figure_visual_review_attempt_02.json')
 bind(analytic/'plot_script_attempt_01.py',first['script_sha256']);bind(ROOT/'experiments/plot_vs_seg_resampling_order_cpu.py',second['script_sha256']);check(qa['visual_review_completed'] and qa['reviewed_png_sha256']==second['outputs'][0]['sha256'],'Second actual visual review absent')
 for figure in (first,second):
  bind(analytic/'attempt_01.json',figure['result_sha256']);bind(analytic/'independent_replay_attempt_01.json',figure['proof_sha256'])
  for output in figure['outputs']: bind(ROOT/output['path'],output['sha256'])
 source=ROOT/'literature/source_cache/resampling_order_fulltexts_2026-10-03';reading=read(source/'reading_provenance.json');fetch=read(source/'attempt_01.json');bind(source/'attempt_01.json',reading['fetch_manifest_sha256']);bind(ROOT/reading['report'],reading['report_sha256']);bind(ROOT/'literature/register_resampling_order_reading_2026_10_03.py',reading['script_sha256']);bind(ROOT/'literature/fetch_resampling_order_fulltexts_2026_10_03.py',fetch['script_sha256']);bind(ROOT/'literature/2026-10-03_resampling_order_fulltext_selection.md',fetch['plan_sha256']);anchors=0
 for paper in reading['papers']:
  for key in ('raw','block','text'): bind(source/paper[key+'_file'],paper[key+'_sha256'])
  blocks=read(source/paper['block_file']);tree=ET.parse(source/paper['raw_file']);article=tree.getroot().find('.//article');article=tree.getroot() if tree.getroot().tag=='article' else article
  check(article is not None and article.find('body') is not None,'Authentic body absent');dois=[''.join(e.itertext()) for e in article.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi'];check(paper['doi'] in dois,'Body DOI mismatch')
  for anchor in paper['anchors']: check(0<=anchor['index']<len(blocks) and blocks[anchor['index']]=={k:anchor[k] for k in ('tag','text')},'Actual body anchor differs');anchors+=1
  check(paper['actual_relevant_body_reading_completed'] and not paper['training_or_phantom_results_independently_reproduced'] and not paper['visual_figures_reviewed'] and not paper['supplementary_material_read'],'Reading scope overstated')
 check(reading['new_primary_bodies_read']==3 and reading['new_pdfs']==0 and anchors==reading['actual_focused_primary_anchors']==88,'Three body/88 anchor scope differs');check(reading['returned_title_rows']==41 and reading['unique_normalized_titles']==39,'Title scope differs')
 for search in reading['search_bindings']:
  index=ROOT/'literature'/search['path'];bind(index,search['sha256']);data=read(index)
  for response in data['responses']: bind(index.parent/response['raw_file'],response['raw_sha256'])
  script='search_resampling_order_2026_10_03.py' if 'resampling_order_search' in search['path'] else 'search_pchip_order_prior_art_2026_10_03.py';bind(ROOT/'literature'/script,data['script_sha256'])
 failed=ROOT/'literature'/reading['unobtained_fourth_body']['path'];bind(failed,reading['unobtained_fourth_body']['sha256']);unobtained=read(failed);bind(ROOT/'literature/fetch_t2_tumor_processing_fulltext_2026_10_03.py',unobtained['script_sha256']);bind(failed.parent/unobtained['raw_file'],unobtained['raw_sha256']);check(not unobtained['fulltext_acquired'] and not reading['unobtained_fourth_body']['counted_as_fulltext'],'Absent fourth body counted');check('does not allow downloading of the full text in XML form' in (failed.parent/unobtained['raw_file']).read_text(encoding='utf-8'),'Publisher XML restriction not recorded')
 # The live queue is excluded except its fixed, already-created contract.
 task=ROOT/'experiments/vs_seg_post_resize_task_cpu';taskcontract=read(task/'run_contract.json');include(task/'run_contract.json');check(taskcontract['main_roster']==contract['main_roster'] and taskcontract['condition']=='post_resize_pchip' and taskcontract['post_result_development'] and taskcontract['new_method_confirmation_patients']==0,'New fixed45 task role differs')
 for f in taskcontract['files']: bind(ROOT.parent/f['path'],f['sha256'])
 names=['README.md','EXPERIMENT_QUEUE.md','VS_SEG_RESAMPLING_ORDER_CPU_PLAN_2026-10-03.md','VS_SEG_RESAMPLING_ORDER_CPU_RESULT_2026-10-03.md','VS_SEG_POST_RESIZE_TASK_CPU_PLAN_2026-10-03.md','INNOVATION_DECISION_AFTER_RESAMPLING_ORDER_2026-10-03.md','RESAMPLING_ORDER_NEXT_VALIDATION_PREPARATION_2026-10-03.md','SESSION_FAILURES_RESAMPLING_ORDER_2026-10-03.md','SESSION_USER_PROVIDED_SUMMARY_RESAMPLING_ORDER_2026-10-03.md','SESSION_VISIBLE_DIALOGUE_RESAMPLING_ORDER_2026-10-03.md','SESSION_UPDATE_RESAMPLING_ORDER_2026-10-03.md','SESSION_HANDOFF_RESAMPLING_ORDER_TASK_QUEUE_ACTIVE_2026-10-03.md','literature/source_cache/resampling_order_actual_process_observation_2026-10-03.json','literature/verify_resampling_order_all_archives_2026_10_03.py']
 for name in names: include(ROOT/name)
 include(ROOT/'SESSION_ARCHIVE_VERIFICATION_RESAMPLING_ORDER_2026-10-03.json');include(ROOT/'literature/source_cache/resampling_order_actual_process_observation_2026-10-03_attempt_02.json')
 audit=read(ROOT/'SESSION_ARCHIVE_VERIFICATION_RESAMPLING_ORDER_2026-10-03.json');check(audit['all_checks_passed'] and audit['status']=='complete' and len(audit['records'])==30 and all(r['returncode']==0 for r in audit['records']) and not audit['scientific_goal_complete'],'Actual30 static audit differs')
 for folder in ('experiments/vs_seg_resampling_order_cpu','literature/source_cache/resampling_order_search_2026-10-03','literature/source_cache/resampling_order_fulltexts_2026-10-03','literature/source_cache/pchip_order_prior_art_2026-10-03','literature/source_cache/t2_tumor_processing_fulltext_2026-10-03'):
  for p in (ROOT/folder).iterdir():
   if p.is_file(): include(p)
 include(Path(__file__))
 for p in files:
  if p.suffix=='.py': ast.parse(p.read_text(encoding='utf-8'))
  if p.suffix=='.md':
   for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
    if not target.startswith(('https://','http://','#','mailto:')): check((p.parent/target.split('#')[0]).exists(),'Broken link '+str(p)+': '+target)
 snapshot=read(ROOT/'literature/source_cache/resampling_order_actual_process_observation_2026-10-03.json');check(snapshot['terminal_exit_codes']=={'resampling_order_producer_5040':0,'independent_analytic_verifier_68788':0} and not snapshot['scientific_goal_complete'],'Actual analytic terminal state differs')
 manifest=dict(scope='Static completed analytic all45/all36, three body readings and actual public-dialogue checkpoint. Live post-task outputs excluded; fixed task contract included.',main_patients=45,missing_targets=2565,analytic_endpoint_replays=36,existing_volumes_replayed=180,new_post_volumes_replayed=90,new_primary_bodies_read=3,actual_reading_anchors=88,title_rows=41,unique_titles=39,new_pdfs=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,live_task_outputs_included=False,files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)],external_read_only_source_bindings=sorted({v['path']:v for v in external}.values(),key=lambda x:x['path']))
 if '--write' in sys.argv: OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else: check(OUT.exists() and read(OUT)==manifest,'Current static stage manifest stale')
 print(json.dumps({k:v for k,v in manifest.items() if k not in ('files','external_read_only_source_bindings')}|dict(files=len(files),errors=errors),ensure_ascii=False));return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
