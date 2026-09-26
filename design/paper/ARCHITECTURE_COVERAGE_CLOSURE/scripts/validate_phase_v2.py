from expanded_phase_v2 import *
def main():
 torch.set_num_threads(2);_,p11=wrappers();rows=[]
 for ds in ['fastmri','ixi']:
  r=next(r for r in read(B/'case_registry.json') if r['dataset']==ds);im=nib.load(ROOT/r['source']);v=im.get_fdata(dtype=np.float32)
  for m in ['ressrdiff','arssr']:
   net=load(ds,m)
   for phase in [0,2]:
    a=np.ascontiguousarray(v[:,:,r[f'phase{phase}']]);a=p11.nifti_roundtrip(a,im.affine,im.header) if ds=='ixi' else a;zs=np.array(r['targets'])-phase
    q=targets(net,m,a,zs);rng=torch.cuda.get_rng_state().clone()
    torch.manual_seed(20260914);orig=full(net,m,a);rng_ref=torch.cuda.get_rng_state()
    diff=float(abs(q-np.moveaxis(orig[:,:,zs],2,0)).max());same=bool(torch.equal(rng,rng_ref)) if m=='ressrdiff' else None
    row=dict(dataset=ds,model=m,phase=phase,case=r['case'],max_difference=diff,tolerance=.0001,sampler_rng_state_identical=same,script_sha256=sha(P/'scripts/expanded_phase_v2.py'))
    rows.append(row);write(P/'outputs/phase_v2_validation.json',rows);print(row,flush=True)
    assert diff<=.0001 and (same or m=='arssr'),row
   del net;gc.collect();torch.cuda.empty_cache()
 write(P/'outputs/phase_v2_authorization.json',dict(status='PASS',checks=len(rows),script_sha256=sha(P/'scripts/expanded_phase_v2.py')))
if __name__=='__main__':main()
