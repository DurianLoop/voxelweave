"""Independent raw-cell and recorded-numeric arithmetic, no model or medical rerun."""
import re,gzip,json,time
from html.parser import HTMLParser
from decimal import Decimal as D
from pathlib import Path
from resource_guard_v1 import HERE,ROOT,guard,entry,bind,read,dump
class Visible(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.skip=0;self.parts=[]
 def handle_starttag(self,tag,attrs):
  if tag=='annotation':self.skip+=1
 def handle_endtag(self,tag):
  if tag=='annotation':self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
def native_rows(p,ident):
 s=gzip.decompress(p.read_bytes()).decode('utf-8');m=re.search(r'<table\b[^>]*\bid="'+re.escape(ident)+r'"[^>]*>',s);assert m
 end=s.index('</table>',m.end());rows=[]
 for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',s[m.end():end],re.S):
  cells=[]
  for cell in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',row,re.S):
   v=Visible();v.feed(cell);cells.append(' '.join(''.join(v.parts).split()))
  if cells:rows.append(cells)
 assert rows;return rows
start=time.perf_counter();before=guard(start);prep=ROOT/'six_resolution_training_preparation_2026_10_09';sources=[]
def receipt(p,complete=True):
 v=read(p);sources.append(entry(p));assert v['complete']==complete and bool(v['errors'])==(not complete)
 for b in v.get('source_bindings',[]):bind(b)
 return v
t=receipt(HERE/'foundation_table_arithmetic_attempt01/receipt.json')
for ident,rows in t['native_HTML_cells'].items():
 folder=HERE/('foundation_primary_html_attempt01/swin_pretraining' if ident.startswith('swin_') else 'brainsegfounder_identity_html_attempt02')
 rawid=ident.removeprefix('swin_');p=folder/'primary.html.gz';sources.append(entry(p));assert native_rows(p,rawid)==rows
for v in t['fold_means']:
 computed=sum(D(z) for z in v['values'])/5;delta=D(v['reported_mean'])-computed
 assert computed==D(v['mean_from_printed_values']) and delta==D(v['reported_minus_computed'])
 assert (abs(delta)>D(v['rounding_bound']))==v['discrepancy_exceeds_printed_rounding']
assert sum(v['total'] for v in t['Swin_pretraining_counts'])==5010 and sum(v['train'] for v in t['Swin_pretraining_counts'])==4761 and sum(v['validation'] for v in t['Swin_pretraining_counts'])==249
assert 5050-5010==t['Swin_reported_total_minus_table_sum']==40
failed=receipt(prep/'stable_reduction_model_cpu_attempt01/receipt.json',False);adam=receipt(prep/'stable_reduction_adam_attribution_attempt01/receipt.json')
assert len(failed['steps'])==1 and failed['CPU_optimizer_updates']==2 and adam['CPU_optimizer_updates']==2
assert adam['max_errors']==failed['steps'][0]['max_errors'] and len(adam['coordinates'])==54 and adam['max_errors']['parameter']>3e-6
for row in adam['coordinates']:
 a,b=row['branches'];assert abs(a['updated']-b['updated'])==row['parameter_error']
 for v in row['branches']:
  g=v['gradient'];pred=v['initial']*(1-1e-8)-1e-4*g/(abs(g)+1e-8)
  assert abs(pred-v['predicted_updated_double'])<1e-12 and abs(pred-v['updated'])<=3e-6 and v['step']==1
assert max(adam['coordinates'],key=lambda v:v['parameter_error'])==adam['worst_coordinate'] and adam['worst_coordinate']['gradient_signs']==[1,1]
cpu=receipt(prep/'high_precision_model_cpu_attempt01/receipt.json');gpu=receipt(prep/'high_precision_model_gpu_attempt04/receipt.json');pool=receipt(prep/'disjoint_pool_cpu_attempt01/receipt.json')
assert cpu['CPU_optimizer_updates']==4 and gpu['synthetic_CPU_optimizer_updates']==gpu['synthetic_GPU_optimizer_updates']==2
for r in (cpu,gpu):
 assert len(r['steps'])==2 and r['initial_state_sha256']==failed['initial_state_sha256'] and r['input_sha256']==failed['input_sha256'] and r['synthetic_target_sha256']==failed['synthetic_target_sha256']
 for step in r['steps']:
  rows=step['all54_parameters'];assert len(rows)==len({v['name'] for v in rows})==54
  fields=[f for v in rows for f in v['optimizer_fields']];assert len(fields)==step['optimizer_fields_compared']==162
  assert step['max_errors']['loss']==abs(step['loss_values'][0]-step['loss_values'][1])
  for label,key in (('gradient','gradient_error'),('parameter','parameter_error')):assert step['max_errors'][label]==max(v[key] for v in rows)
  assert step['max_errors']['optimizer_state']==max(v['max_error'] for v in fields)
  assert max(step['max_errors'].values())<=3e-6 and step['binary_disagreements']==0
  assert all({v['field'] for v in row['optimizer_fields']}=={'step','exp_avg','exp_avg_sq'} for row in rows)
assert len(pool['records'])==6 and all(v['output_max_error']==v['input_VJP_max_error']==0 and v['tie_selection_bitwise_equal'] for v in pool['records'])
assert gpu['CUDA_VISIBLE_DEVICES_after_CPU_imports']=='-1' and gpu['CUDA_VISIBLE_DEVICES_at_GPU_admission']=='0'
assert gpu['resources_after']['GPU_peak_reserved_bytes']<=2500000000 and gpu['resources_after']['GPU_free_bytes']>=4000000000 and gpu['resources_after']['GPU_allocator_max_bytes']<=2400000000
for r in (failed,adam,cpu,gpu):assert r['MRI_arrays_loaded']==r['GT_arrays_loaded']==0 and not r['medical_effect_scored'] and not r['publication_claim_confirmed']
v2=receipt(prep/'high_precision_model_gpu_attempt02/receipt.json',False);v3=receipt(prep/'high_precision_model_gpu_attempt03/receipt.json',False)
for v in (v2,v3):assert v['synthetic_CPU_optimizer_updates']==v['synthetic_GPU_optimizer_updates']==0
assert not v2['CUDA_initialized'] and 'deterministic' in v3['errors'][0]
reading=receipt(HERE/'foundation_reading_scope_attempt01/receipt.json');assert reading['recovered_original_foundation_reading_chunks']==2 and reading['Swin_omitted_algorithm_lines_actually_read_and_verified']==22 and not reading['Greedy_author_code_executed']
out=HERE/'independent_round51_audit_attempt02';out.mkdir(exist_ok=False)
r=dict(complete=True,errors=[],source_bindings=[entry(Path(__file__)),entry(HERE/'resource_guard_v1.py')]+sources,
 original_HTML_table_cells_independently_reparsed=True,all_displayed_fold_arithmetic_independently_verified=True,
 stable_reduction_failure_preserved=True,all54_Adam_coordinates_and_formulas_audited=True,
 high_precision_CPU_and_GPU_two_step_receipt_arithmetic_verified=True,new_model_rerun=False,
 deterministic_pool_six_records_verified=True,original_FP32_production_qualified=False,
 known_recorded_round51_CPU_optimizer_updates=10,known_recorded_round51_GPU_optimizer_updates=2,
 GPU_v1_exact_runtime_optimizer_count_not_recoverable=True,total_round51_updates_claimed_exact=False,
 new_medical_training_launched=False,MRI_arrays_loaded=0,GT_arrays_loaded=0,additional_optimizer_updates_in_audit=0,
 medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(start),elapsed_seconds=time.perf_counter()-start)
dump(out/'receipt.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_bindings','resources_before','resources_after')}))
