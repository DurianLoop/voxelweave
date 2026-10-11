"""Separate source-table parser and receipt arithmetic audit; no model rerun."""
import sys,gzip,json,math,time,re
from html.parser import HTMLParser
from decimal import Decimal as D
from fractions import Fraction as Q
from collections import defaultdict
from pathlib import Path
from resource_guard_v1 import HERE,ROOT,guard,read,entry,bind,dump
class Tables(HTMLParser):
 def __init__(self,wanted):
  super().__init__(convert_charrefs=True);self.wanted=wanted;self.table=False;self.rows=[];self.row=None;self.cell=None;self.skip=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='table' and a.get('id')==self.wanted:self.table=True
  if not self.table:return
  if tag=='tr':self.row=[]
  if tag in ('td','th'):self.cell=[]
  if tag=='annotation':self.skip+=1
 def handle_data(self,data):
  if self.table and self.cell is not None and not self.skip:self.cell.append(data)
 def handle_endtag(self,tag):
  if not self.table:return
  if tag=='annotation':self.skip-=1
  if tag in ('td','th') and self.cell is not None:
   self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
  if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
  if tag=='table':self.table=False
def table(name,ident):
 p=HERE/'primary_html_attempt01'/name/'primary.html.gz';parser=Tables(ident);parser.feed(gzip.decompress(p.read_bytes()).decode('utf-8'))
 assert parser.rows;return parser.rows,entry(p)
def number(s):
 x=re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',s);assert x,s;return D(x[0])
def rows_by_label(rows):return {row[0]:row for row in rows if row}
started=time.perf_counter();before=guard(started);out=HERE/'independent_primary_cpu_audit_attempt01';out.mkdir(exist_ok=False)
sources=[]
def inspected(p):
 v=read(p);sources.append(entry(p));assert v['complete'] and not v['errors']
 for b in v.get('source_bindings',[]):bind(b)
 return v
t=inspected(HERE/'primary_table_arithmetic_attempt01/receipt.json')
ot,source=table('openmasc','S4.T3.12.1');sources.append(source);o=rows_by_label(ot)
assert 'Ours' in o;full=o['Ours'];assert number(full[1])==D('.777') and number(full[2])==D('27.62')
labels=['w/o Active Acq. (Rand†)','w/o Active Acq. (Equi)','w/o DCR','w/o PPO-DCR Co-train']
for result,label in zip(t['OpenMASC'],labels):
 assert D(result['delta_SSIM'])==number(full[1])-number(o[label][1])
 assert D(result['delta_PSNR_dB'])==number(full[2])-number(o[label][2])
gt,source=table('greedy','A2.T4.5');sources.append(source);g=rows_by_label(gt)
for i,result in enumerate(t['Greedy'],1):
 assert D(result['greedy_minus_test_GT_NA_oracle'])==number(g['Greedy'][i])-number(g['NA Oracle'][i])
 gamma=next(row for label,row in g.items() if 'γ' in label)
 assert D(result['gamma09_minus_greedy'])==number(gamma[i])-number(g['Greedy'][i])
ft,source=table('active_fewshot','S4.T1.2.1');sources.append(source);f=rows_by_label(ft)
for i,result in enumerate(t['active_fewshot']):
 col=(i+1)*3
 assert D(result['proposed_minus_random_percentage_points'])==number(f['Proposed'][col])-number(f['Random'][col])
 assert D(result['proposed_minus_DVRL_percentage_points'])==number(f['Proposed'][col])-number(f['DVRL'][col])
 assert result['support_plus_reward_validation_label_slots']==result['K']+8 and not result['unique_subject_annotation_count_confirmed']
ct,source=table('greedy','A2.T3.5');sources.append(source);c=rows_by_label(ct)
for result in t['approximate_training_cost']:
 offset=1 if result['horizon']=='base' else 3
 for key,col in [('greedy_approximate_GPU_days',offset),('nongreedy_approximate_GPU_days',offset+1)]:
  raw=c[result['dataset'].title()][col];ns=re.findall(r'\d+(?:\.\d+)?',raw);assert len(ns)==2,raw
  assert D(result[key])==D(ns[0])*D(ns[1])
mi=inspected(HERE/'action_availability_mi_attempt01/receipt.json')
for rec in mi['records']:
 rows=rec['exact_joint'];joint=defaultdict(Q);pa=defaultdict(Q);ps=defaultdict(Q)
 for v in rows:
  p=Q(v['probability_numerator'],v['probability_denominator']);key=(tuple(v['M']),v['X']);joint[(v['A'],key)]+=p;pa[v['A']]+=p;ps[key]+=p
 assert sum(joint.values())==1
 direct=math.fsum(float(p)*math.log(float(p/(pa[a]*ps[s]))) for (a,s),p in joint.items())
 assert abs(direct-rec['MI_nats']['I(A;M,X)']['KL'])<1e-12
 conditional=0.;masses=defaultdict(Q)
 for s,p in ps.items():masses[s[0]]+=p
 for m,mass in masses.items():
  j=defaultdict(Q);ax=defaultdict(Q);xx=defaultdict(Q)
  for (a,(mask,x)),p in joint.items():
   if mask==m:j[(a,x)]+=p/mass;ax[a]+=p/mass;xx[x]+=p/mass
  conditional+=float(mass)*math.fsum(float(p)*math.log(float(p/(ax[a]*xx[x]))) for (a,x),p in j.items())
 assert abs(conditional-rec['conditional_I_A_X_given_M_nats'])<1e-12
prep=ROOT/'six_resolution_training_preparation_2026_10_09'
norm=inspected(prep/'stable_norm_math_v2_attempt01/receipt.json')
assert norm['optimizer_updates']==norm['MRI_arrays_loaded']==norm['GT_arrays_loaded']==0 and not norm['CUDA_initialized']
assert max(norm['double_equation_errors'].values())<=3e-6 and max(norm['FP32_cast_output_dx_dgamma_dbeta_errors'])<=3e-6
for row in norm['finite_difference']:
 assert [v['h'] for v in row['checks']]==[1e-3,1e-4,1e-5]
 for v in row['checks']:
  assert (v['plus']-v['minus'])/(2*v['h'])==v['derivative']
  assert abs(v['derivative']-row['analytical'])==v['analytic_error']
 assert row['checks'][-1]['analytic_error']<=1e-8
 if row['parameter']=='input':assert row['checks'][1]['analytic_error']<=row['checks'][0]['analytic_error']*.05+1e-9
failed=read(prep/'gin_cpu_reference_verification_attempt02/receipt.json');sources.append(entry(prep/'gin_cpu_reference_verification_attempt02/receipt.json'))
assert not failed['complete'] and failed['errors'] and failed['CPU_optimizer_updates']==2 and len(failed['steps'])==1
for b in failed['source_bindings']:bind(b)
step=failed['steps'][0];assert len(step['all54_parameters'])==54 and step['optimizer_fields_compared']==162
assert step['max_errors']['parameter']>3e-6 and all(v<=3e-6 for k,v in step['max_errors'].items() if k!='parameter')
adam=inspected(prep/'synthetic_adam_attribution_attempt01/receipt.json')
assert adam['CPU_optimizer_updates']==2 and adam['max_errors']==step['max_errors'] and len(adam['coordinates'])==54
assert adam['all54_parameter_gradient_and162_state_error_rows_reproduced_exactly'] and not adam['original_parameter_gate_passed']
max_predict=0.
for row in adam['coordinates']:
 assert len(row['coordinate'])==len(row['shape'])
 for v in row['branches']:
  g0=v['gradient'];predict=v['initial']*(1-1e-8)-1e-4*g0/(abs(g0)+1e-8)
  assert abs(predict-v['predicted_updated_double'])<1e-12 and abs(predict-v['updated'])<=3e-6
  assert v['step']==1 and v['all_parameter_predicted_max_error']<=3e-6
  max_predict=max(max_predict,v['all_parameter_predicted_max_error'])
 assert abs(row['branches'][0]['updated']-row['branches'][1]['updated'])==row['parameter_error']
 assert abs(row['branches'][0]['gradient']-row['branches'][1]['gradient'])==row['coordinate_gradient_difference']
assert max_predict==adam['independent_double_AdamW_max_prediction_error']
worst=max(adam['coordinates'],key=lambda v:v['parameter_error']);assert worst==adam['worst_coordinate'] and worst['gradient_signs']==[1,1]
result=dict(complete=True,errors=[],source_bindings=[entry(Path(__file__)),entry(HERE/'resource_guard_v1.py')]+sources,
 native_HTML_table_cells_independently_parsed=dict(OpenMASC=ot,Greedy=gt,active_fewshot=ft,policy_training_cost=ct),
 all_reported_arithmetic_bound_to_exact_primary_cells=True,MI_exact_joint_independently_recomputed=True,
 norm_equations_and_finite_difference_record_arithmetic_verified=True,norm_model_rerun=False,
 failed_two_step_protocol_stopped_after_step0_verified=True,failed_parameter_gate_preserved=True,
 Adam_all54_coordinates_and_scalar_formulas_audited=True,additional_CPU_optimizer_updates_in_this_audit=0,
 total_round50_synthetic_CPU_optimizer_updates=4,medical_or_GPU_updates=0,MRI_arrays_loaded=0,GT_arrays_loaded=0,
 medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('source_bindings','native_HTML_table_cells_independently_parsed','resources_before','resources_after')}))
