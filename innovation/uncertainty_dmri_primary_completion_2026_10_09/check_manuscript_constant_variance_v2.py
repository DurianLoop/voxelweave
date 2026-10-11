"""Version-specific literal equation check, not author implementation or medical replication."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import sys,json,time
from fractions import Fraction
from pathlib import Path
import numpy as np
from fetch_arxiv_maintext import guard,entry,dump,DOM
HERE=Path(__file__).resolve().parent
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();guard()
 p=HERE/'arxiv_html_attempt01/maintext.html';dom=DOM();dom.feed(p.read_text(encoding='utf-8'))
 eq=next(n for n in dom.root.nodes() if n.attrs.get('id')=='S3.EGx6')
 tex=[n.attrs['alttext'] for n in eq.nodes() if n.tag=='math' and n.attrs.get('id') in ('S3.E20.m2','S3.E21.m2','S3.E22.m2')]
 assert len(tex)==3 and 'J-1' in tex[0] and 'J-1' in tex[1] and '\\frac{1}{J}' in tex[2]
 rows=[];T,J=200,10
 for constant in (0,1,2):
  g=np.full((T,J),constant,dtype=np.float64);mu=g.mean(axis=1)
  parameter=float(np.mean(mu**2)-(g.sum()/((J-1)*T))**2)
  intrinsic=float(np.sum(g**2)/((J-1)*T)-np.mean(mu**2))
  cp=Fraction(constant)**2-(Fraction(J*constant,J-1))**2;ci=Fraction(J*constant*constant,J-1)-Fraction(constant)**2
  assert abs(parameter-float(cp))<1e-12 and abs(intrinsic-float(ci))<1e-12
  empirical_parameter=float(np.var(mu,ddof=0));empirical_intrinsic=float(np.mean(np.var(g,axis=1,ddof=0)))
  assert empirical_parameter==empirical_intrinsic==0
  rows.append(dict(constant=constant,literal_eq20_parameter=parameter,literal_eq21_intrinsic=intrinsic,literal_total=parameter+intrinsic,exact_parameter=str(cp),exact_intrinsic=str(ci),exact_total=str(cp+ci),empirical_distribution_parameter=empirical_parameter,empirical_distribution_intrinsic=empirical_intrinsic))
 assert rows[1]['literal_eq20_parameter']<0 and rows[1]['literal_total']<0
 r=dict(complete=True,errors=[],version='1907.13418v1 HTML',equation_id='S3.EGx6',literal_math_alttext=tex,T=T,J=J,constant_cases=rows,nonzero_constant_literal_equations_fail_zero_nonnegative_variance=True,independent_Fraction_matches_float64=True,empirical_definition_not_claimed_as_unbiased_population_estimator=True,author_code_executed=False,final_publisher_equations_checked=False,clinical_or_MRI_effect_tested=False,publication_claim_confirmed=False,goal_status='active',source_bindings=[entry(p),entry(Path(__file__)),entry(HERE/'MATH_SANITY_PROTOCOL.md')],elapsed_seconds=time.perf_counter()-started)
 out=HERE/'constant_variance_attempt02';out.mkdir(exist_ok=False);dump(out/'receipt.json',r);guard();assert time.perf_counter()-started<60
 print(json.dumps(r,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
