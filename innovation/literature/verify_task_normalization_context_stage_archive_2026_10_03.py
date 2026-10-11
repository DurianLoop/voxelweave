"""Static audit of three new bodies, two saved-output studies and preparations."""
import ast,csv,hashlib,json,re,sys
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/task_normalization_context_stage_archive_manifest_2026-10-03.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as stream:
  for b in iter(lambda:stream.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');files=set();errors=[]
 def check(ok,msg):
  if not ok:errors.append(msg)
 def include(p):
  p=Path(p);check(p.is_file(),'Missing '+str(p))
  if p.is_file():files.add(p)
 def bind(p,digest):include(p);check(Path(p).is_file() and sha(p)==digest,'SHA differs '+str(p))
 src=ROOT/'literature/source_cache/task_normalization_context_fulltexts_2026-10-03';reading=read(src/'reading_provenance.json');fetch=read(src/'attempt_01.json')
 bind(src/'attempt_01.json',reading['fetch_manifest_sha256']);bind(ROOT/reading['report'],reading['report_sha256']);check(len(reading['papers'])==3 and reading['actual_focused_primary_anchors']==194 and reading['new_pdfs']==0,'Reading denominator differs')
 bind(ROOT/'literature/register_task_normalization_context_reading_2026_10_03.py',reading['script_sha256']);bind(ROOT/'literature/fetch_task_normalization_context_2026_10_03.py',fetch['script_sha256']);bind(ROOT/'literature/2026-10-03_task_normalization_context_selection.md',fetch['selection_sha256'])
 for paper in reading['papers']:
  for key in ('raw','block','text'):bind(src/paper[key],paper[key+'_sha256'])
  tree=ET.parse(src/paper['raw']);article=tree.getroot().find('.//article');check(article is not None and article.find('body') is not None,'Body absent')
  if article is not None:check(paper['doi'].casefold() in [''.join(e.itertext()).casefold() for e in article.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi'],'DOI differs')
  blocks=read(src/paper['block'])
  for a in paper['anchors']:check(blocks[a['index']]=={k:a[k] for k in ('tag','text')},'Reading anchor differs')
  check(paper['actual_relevant_body_reading_completed'] and not paper['visual_figures_reviewed'] and not paper['author_experiments_independently_reproduced'] and not paper['supplementary_material_read'],'Reading scope overstated')
 for search in reading['searches']:bind(ROOT/search['path'],search['sha256'])
 first=read(ROOT/'literature/source_cache/task_normalization_context_search_2026-10-03/attempt_01.json');check(len(first['responses'])==4 and all('503' in x.get('error','') for x in first['responses']),'First failures not retained')
 second=read(ROOT/'literature/source_cache/task_normalization_context_search_2026-10-03/network_fallback_attempt_01.json')
 for x in second['responses']:
  if 'raw_file' in x:bind(ROOT/'literature/source_cache/task_normalization_context_search_2026-10-03'/x['raw_file'],x['sha256'])
 narrow=read(ROOT/'literature/source_cache/task_normalization_context_ncbi_2026-10-03/attempt_01.json');check(sum(len(x.get('items',[])) for x in narrow['responses'])==26,'Narrow title rows differ')
 for x in narrow['responses']:
  for key in ('raw','summary'):
   if key+'_file' in x:bind(ROOT/'literature/source_cache/task_normalization_context_ncbi_2026-10-03'/x[key+'_file'],x[key+'_sha256'])
 for folder,script in [('anchor_pilot_boundary_decomposition_cpu','anchor_pilot_boundary_decomposition_cpu.py'),('anchor_pilot_output_domain_audit_cpu','anchor_pilot_output_domain_audit_cpu.py')]:
  p=ROOT/'experiments'/folder;r=read(p/'attempt_01.json');prov=read(p/'report_provenance.json');check(r['complete'] and not r['errors'] and r['new_neural_forwards']==0 and not r['torch_imported'] and not r['publication_claim_confirmed'],'CPU scalar/output audit role differs')
  bind(ROOT/'experiments'/script,r['script_sha256']);bind(p/'attempt_01.json',prov['result_sha256'])
  plan=ROOT/('ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_CPU_PLAN_2026-10-03.md' if folder=='anchor_pilot_boundary_decomposition_cpu' else 'ANCHOR_PILOT_OUTPUT_DOMAIN_AUDIT_CPU_PLAN_2026-10-03.md');bind(plan,r['plan_sha256'])
  for x in r['source_bindings']:bind(ROOT/x['path'],x['sha256'])
  for x in prov['outputs']:bind(ROOT/x['path'],x['sha256'])
  if folder=='anchor_pilot_boundary_decomposition_cpu':
   q=read(p/'independent_partition_and_csv_verification.json');bind(p/'attempt_01.json',q['result_sha256']);bind(ROOT/'experiments/verify_anchor_pilot_boundary_decomposition_cpu.py',q['script_sha256']);check(q['complete'] and not q['errors'] and q['paired_rows_verified']==108 and q['summaries_verified']==36,'Exact partition proof differs')
  else:
   check(r['xor_domain_counts_verified']==54 and r['label_domain_comparisons']==108 and [x['changed_prediction_voxels'] for x in r['selected_fixed_post_missing_output_changes']]==[288,593,186],'Actual missing prediction response differs')
   bind(ROOT/'experiments/anchor_bandwidth_task_cpu_pilot/independent_inputs_and_all36_estimates.json',r['input_proof_sha256'])
 spec=read(ROOT/'experiments/task_input_contract_matrix_preparation_2026-10-03.json');check(spec['status']=='design_prepared_not_executed_not_frozen' and spec['gpu_jobs_started']==0 and spec['first_matrix_models']==6 and spec['evaluation_cells_per_qualified_cohort']==30,'GPU design overstated')
 for folder in ('literature/source_cache/task_normalization_context_search_2026-10-03','literature/source_cache/task_normalization_context_ncbi_2026-10-03','literature/source_cache/task_normalization_context_fulltexts_2026-10-03','experiments/anchor_pilot_boundary_decomposition_cpu','experiments/anchor_pilot_output_domain_audit_cpu'):
  for p in (ROOT/folder).iterdir():
   if p.is_file():include(p)
 for name in ('README.md','EXPERIMENT_QUEUE.md','SESSION_VISIBLE_DIALOGUE_ORDER_RISK_AND_PHASE_2026-10-03.md','SESSION_USER_PROVIDED_COMPLETED_QUEUES_CHECKPOINT_2026-10-03.md','SESSION_UPDATE_ORDER_RISK_AND_PHASE_2026-10-03.md','SESSION_HANDOFF_ORDER_RISK_AND_PHASE_2026-10-03.md','INNOVATION_DECISION_AFTER_POST_TASK_AND_PHASE_2026-10-03.md','POST_TASK_AND_PHASE_NEXT_VALIDATION_PREPARATION_2026-10-03.md','ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_COUNT_CORRECTION_2026-10-03.md','experiments/task_input_contract_matrix_preparation_2026-10-03.json','literature/search_task_normalization_context_2026_10_03.py','literature/search_task_normalization_context_ncbi_2026_10_03.py','literature/prepare_order_risk_and_phase_entries_2026_10_03.py'):include(ROOT/name)
 include(Path(__file__))
 for path in files:
  if path.suffix=='.py':ast.parse(path.read_text(encoding='utf-8'))
  if path.suffix=='.md':
   for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
    if not target.startswith(('http://','https://','#','mailto:')):check((path.parent/target.split('#')[0]).exists(),'Broken link '+str(path)+': '+target)
 manifest=dict(scope='Additional three DOI-authenticated focused bodies; two post-hoc saved-count/prediction studies; current session and future design.',new_primary_bodies_read=3,focused_primary_anchors=194,new_pdfs=0,new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False,files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(files)])
 if '--write' in sys.argv:OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else:check(OUT.exists() and read(OUT)==manifest,'Additional stage manifest stale')
 print(json.dumps({k:v for k,v in manifest.items() if k!='files'}|dict(files=len(files),errors=errors),ensure_ascii=False));return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
