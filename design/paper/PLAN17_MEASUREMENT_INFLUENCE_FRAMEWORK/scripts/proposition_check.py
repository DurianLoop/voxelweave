from common import *
def main():
 rng=np.random.default_rng(SEED);d=6;n=100000;A=np.diag(np.linspace(.4,1.4,d));bias_a=np.linspace(.1,.3,d);bias_b=np.linspace(.2,.4,d)
 rows=[]
 for label,B in [('aligned',A),('orthogonal',np.roll(A,1,axis=0)),('opposed',-A)]:
  for corr in [-.5,0,.5,1.]:
   xi=rng.normal(size=(n,d));eta=rng.normal(size=(n,d));same=corr*xi+np.sqrt(1-corr*corr)*eta
   ea=bias_a+xi@A.T;eb=bias_b+same@B.T
   kappa=corr*np.trace(A@B.T);T=.5*(bias_a@bias_a+bias_b@bias_b+np.trace(A@A.T)+np.trace(B@B.T))
   expected_inner=bias_a@bias_b+kappa;expected_D=2*T-2*expected_inner
   inner=(ea*eb).sum(axis=1);D=((ea-eb)**2).sum(axis=1)
   err_inner=abs(inner.mean()-expected_inner);err_D=abs(D.mean()-expected_D)
   passed=err_inner<5*inner.std(ddof=1)/np.sqrt(n)+1e-12 and err_D<5*D.std(ddof=1)/np.sqrt(n)+1e-12
   rows.append({'sensitivity':label,'cross_correlation':corr,'kappa':kappa,'theory_inner':expected_inner,'mc_inner':inner.mean(),'theory_disagreement_energy':expected_D,'mc_disagreement_energy':D.mean(),'ratio_of_expectations_observable':expected_D/(4*T),'pass_5_standard_errors':passed})
 # Verify embedded cosine differs from mean shared-anchor cosine when unshared
 # anchors have nonzero energy. This catches the prior manuscript definition bug.
 ra={0:np.array([1.,0.]),1:np.array([0.,3.])};rb={0:np.array([1.,0.]),2:np.array([0.,4.])}
 embedded=sum(ra[j]@rb[j] for j in ra.keys()&rb.keys())/np.sqrt(sum(v@v for v in ra.values())*sum(v@v for v in rb.values()))
 assert abs(embedded-1/np.sqrt(170))<1e-12 and embedded!=1
 assert all(r['pass_5_standard_errors'] for r in rows)
 pd.DataFrame(rows).to_csv(OUT/'proposition_numerical_check.csv',index=False)
 save('proposition_verification.json',{'settings':len(rows),'draws_per_setting':n,'all_mc_checks_pass':True,'embedded_cosine_check':embedded,'mean_shared_only_cosine_counterexample':1,'natural_image_generalization':False})
 print('E01: all 12 covariance settings pass; embedded cosine counterexample verified')
if __name__=='__main__':main()

