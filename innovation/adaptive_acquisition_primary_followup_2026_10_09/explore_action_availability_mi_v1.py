"""Exact rational toy counterexample and independent information identities."""
import math,time
from itertools import combinations
from fractions import Fraction as Q
from collections import defaultdict
from pathlib import Path
from resource_guard_v1 import HERE,guard,entry,dump
def entropy(ps):return -math.fsum(float(p)*math.log(float(p)) for p in ps if p)
def marginal(rows,keys):
 r=defaultdict(Q)
 for row,p in rows:r[tuple(row[k] for k in keys)]+=p
 return dict(r)
def mi_entropy(rows,left,right):
 return entropy(marginal(rows,left).values())+entropy(marginal(rows,right).values())-entropy(marginal(rows,left+right).values())
def mi_kl(rows,left,right):
 a=marginal(rows,left);b=marginal(rows,right);j=marginal(rows,left+right);n=len(left)
 return math.fsum(float(p)*math.log(float(p/(a[k[:n]]*b[k[n:]]))) for k,p in j.items() if p)
def conditional(rows):
 wm=marginal(rows,('M',));total=[]
 for (m,),mass in wm.items():
  subset=[(v,p/mass) for v,p in rows if v['M']==m]
  total.append(float(mass)*mi_kl(subset,('A',),('X',)))
 return math.fsum(total)
started=time.perf_counter();before=guard(started);out=HERE/'action_availability_mi_attempt01';out.mkdir(exist_ok=False)
masks=list(combinations(range(6),3))
null=[(dict(M=m,X=x,A=a),Q(1,len(masks)*2*3)) for m in masks for x in (0,1) for a in m]
positive=[(dict(M=(0,1,2),X=x,A=x),Q(1,2)) for x in (0,1)]
fixed=[(dict(M=(0,1,2),X=x,A=a),Q(1,6)) for x in (0,1) for a in range(3)]
records=[]
for name,rows in [('availability_only',null),('image_signal_positive_control',positive),('fixed_mask_negative_control',fixed)]:
 assert sum(p for _,p in rows)==1
 for v,p in rows:assert v['A'] in v['M'] and p>0
 pairs={}
 for l,r in [(('A',),('M','X')),(('A',),('M',)),(('A',),('X',))]:
  e=mi_entropy(rows,l,r);k=mi_kl(rows,l,r);assert abs(e-k)<=1e-12
  pairs['I('+','.join(l)+';'+','.join(r)+')']=dict(entropy=e,KL=k)
 value=conditional(rows)
 rec=dict(name=name,rows=len(rows),MI_nats=pairs,conditional_I_A_X_given_M_nats=value,
  exact_joint=[dict(**v,probability_numerator=p.numerator,probability_denominator=p.denominator) for v,p in rows])
 records.append(rec)
assert abs(records[0]['MI_nats']['I(A;M,X)']['KL']-math.log(2))<1e-12
assert records[0]['conditional_I_A_X_given_M_nats']==0
assert abs(records[1]['conditional_I_A_X_given_M_nats']-math.log(2))<1e-12
assert records[2]['conditional_I_A_X_given_M_nats']==0
r=dict(complete=True,errors=[],records=records,all_predeclared_exact_distribution_gates_passed=True,
 source_bindings=[entry(Path(__file__)),entry(HERE/'CPU_EXPLORATION_PROTOCOL.md'),entry(HERE/'resource_guard_v1.py'),entry(HERE/'primary_html_attempt01/greedy/blocks.json.gz')],
 MRI_arrays_loaded=0,GT_arrays_loaded=0,GPU_calls=0,optimizer_updates=0,paper_experiments_reproduced=False,
 medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r)
print(__import__('json').dumps(dict(complete=True,records=[{k:v for k,v in x.items() if k!='exact_joint'} for x in records],elapsed_seconds=r['elapsed_seconds'])))
