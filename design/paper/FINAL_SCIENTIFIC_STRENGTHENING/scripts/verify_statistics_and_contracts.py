"""Implementation checks, not new scientific analyses."""
from common import *
from audit_statistics import rho,weighted_rho,partial,weighted_partial,simultaneous
from acquired_probe import inputs,conditions,compute

def main():
 guard();rng=np.random.default_rng(18101);n=8;k=12;case=np.repeat(np.arange(n),k);x=rng.normal(size=n*k);y=.3*x+rng.normal(size=n*k);geo=np.tile(np.array([[3,1],[5,1],[3,1],[5,1]]),(n*3,1));idx=rng.integers(0,n,(8,n));w=np.stack([np.bincount(i,minlength=n)[case] for i in idx])
 wr=weighted_rho(x,y,w);wp=weighted_partial(x,y,geo,case,w);errors=[]
 for j,draw in enumerate(idx):
  ii=np.concatenate([np.flatnonzero(case==c) for c in draw]);newcase=np.repeat(np.arange(n),k);errors.extend([abs(float(rho(x[ii],y[ii]))-wr[j]),abs(partial(x[ii],y[ii],geo[ii],newcase)-wp[j])])
 assert max(errors)<1e-12
 iv,valid=simultaneous([0,1],np.column_stack([rng.normal(0,.1,5000),np.ones(5000)]));assert np.array_equal(iv[1],[1,1]) and valid==5000
 r=read(P/'case_registry.json')[0];z=r['central_target'];pool,lo,scale,mask=inputs(P/'inputs'/f'{r["dataset"]}_{r["case"]}_z{z}.npz');assert z not in pool
 a=conditions(pool,z,REF)[0];b=conditions(pool,z,REF)[0];assert np.array_equal(a,b)
 # Targets are held in another file and never passed into acquired_probe inputs/conditions.
 code=(P/'scripts/acquired_probe.py').read_text();assert "P/'targets'" not in code and 'nib.load' not in code
 import torch
 torch.set_num_threads(2)
 class Mock:
  device=torch.device('cpu')
  def model(self,t):return torch.zeros_like(t[:,:1])
 data=compute(Mock(),P/'inputs'/f'{r["dataset"]}_{r["case"]}_z{z}.npz',z)
 assert data['response'].shape[:4]==(4,9,2,4) and np.isfinite(data['response']).all()
 write(OUT/'implementation_verification.json',{'weighted_statistics_max_error':max(errors),'constant_bootstrap_interval_handled':True,'target_absent_from_physical_pool':True,'deterministic_condition':True,'probe_module_has_no_target_file_access':True,'interpretation':'These tests cannot prove arbitrary imported model code is leak-free; preprocessing and model source are separately hashed and inspected.'})
 print('Implementation checks passed',max(errors))
if __name__=='__main__':main()
