"""Independent per-pixel/geometry reconstruction; production CSVs are targets only.
Reaggregation reuses the frozen statistical contract on independently read arrays.
"""
from sensitivity import P,B,ROOT,MODELS,PAIRS,guard
import sensitivity as production
import numpy as np,pandas as pd,nibabel as nib,json,hashlib
OUT=P/'outputs';DEST=OUT/'independent_sensitivity';DEST.mkdir(exist_ok=True)
def main():
 guard();rows=[];geom=[];bindings=[]
 for i,r in enumerate(json.loads((B/'case_registry.json').read_text())):
  pred={}
  for model in MODELS:
   path=B/'outputs/phase_arrays'/f'{r["dataset"]}_{model}_{r["case"]}.npz'
   with np.load(path) as f:
    full=bool(f['full_arrays']);pred[model]=[[f['p0'][:,:,z] if full else f['p0'][j],f['p2'][:,:,z-2] if full else f['p2'][j]] for j,z in enumerate(r['targets'])]
   bindings.append(str(path.relative_to(ROOT)))
  with np.load(B/r['cross_targets']) as f:targets=f['gt'];masks=f['mask']
  im=nib.load(ROOT/r['source']);anchors=np.asarray(im.dataobj,dtype=np.float32)
  for j,z in enumerate(r['targets']):
   y=targets[j].astype(np.float64);stack=np.stack([v for mm in MODELS for v in pred[mm][j]]+[y]);valid=np.all(np.isfinite(stack),axis=0)
   brackets=[];four=True
   for phase in ['phase0','phase2']:
    distances=np.array(r[phase])-z;neg=distances[distances<0];pos=distances[distances>0];brackets.append(sorted([-int(neg.max()),int(pos.min())]) if len(neg) and len(pos) else []);four &= len(neg)>=2 and len(pos)>=2
   aok=bool(brackets[0]);mm={'target_1pct':masks[j]&valid,'full_common_valid':valid}
   if aok:
    ids=np.array(r['phase0']);left=ids[ids<z].max();right=ids[ids>z].min();x=abs(anchors[:,:,left]);v=abs(anchors[:,:,right]);mm['acquired_union']=np.logical_or(x>.01*x.max(),v>.01*v.max())&np.isfinite(x)&np.isfinite(v)&valid
   geom.append(dict(dataset=r['dataset'],case=r['case'],z=z,residue=z%4,nearest_match=brackets==[[1,3],[1,3]],full_four_anchor=bool(four),acquired_valid=aok,common_valid_pixels=valid.sum(),total_pixels=valid.size))
   for name,mask in mm.items():
    for pair in PAIRS:
     aa,bb=pair.split('__');e=pred[aa][j][0].astype(float)[mask]-y[mask];values=[]
     for other in pred[bb][j]:
      f=other.astype(float)[mask]-y[mask];h=(e-f)*.5;t=.5*(np.mean(e**2)+np.mean(f**2));values.append(np.mean(h*h)/t)
     rows.append(dict(dataset=r['dataset'],case=r['case'],z=z,pair=pair,support=name,pixels=mask.sum(),shared_O=values[0],disjoint_O=values[1],delta_O=values[1]-values[0]))
  if i%20==0:print('Independent support',i,flush=True)
 fresh=pd.DataFrame(rows);fresh.to_csv(DEST/'sensitivity_per_plane.csv',index=False);gg=pd.DataFrame(geom);gg.to_csv(DEST/'geometry_registry.csv',index=False)
 checks=[]
 def compare(file,old,new,keys,cols):
  a=old.set_index(keys).sort_index();b=new.set_index(keys).sort_index();assert a.index.equals(b.index),(file,'keys')
  for col in cols:
   x=a[col].to_numpy(float);y=b[col].to_numpy(float);ok=np.isclose(x,y,atol=1e-12,rtol=1e-10,equal_nan=True)
   checks.append(dict(file=file,column=col,rows=len(a),max_abs_difference=float(np.nanmax(abs(x-y))),status='PASS' if ok.all() else 'FAIL'))
 compare('planes',pd.read_csv(OUT/'sensitivity_per_plane.csv'),fresh,['dataset','case','z','pair','support'],['shared_O','disjoint_O','delta_O','pixels'])
 compare('geometry',pd.read_csv(OUT/'geometry_registry.csv'),gg,['dataset','case','z'],['residue','nearest_match','full_four_anchor','acquired_valid','common_valid_pixels','total_pixels'])
 # Recompute summaries from fresh planes into a separate root; frozen protocol stays original.
 production.OUT=DEST;production.P=DEST;production.guard=lambda:None;production.analyze() # Original protocol verified before array reads.
 for file,keys,cols in [('CROSS_ARCH_SUPPORT_SENSITIVITY.csv',['dataset','analysis','pair'],['shared_O','disjoint_O','delta_O','simultaneous_low','simultaneous_high']),('CROSS_ARCH_GEOMETRY_SENSITIVITY.csv',['dataset','analysis','pair'],['units','shared_O','disjoint_O','delta_O','simultaneous_low','simultaneous_high']),('CROSS_ARCH_FAMILY_ROBUSTNESS.csv',['dataset','excluded_architecture','statistic'],['delta_O','low','high'])]:
  compare(file,pd.read_csv(P/file),pd.read_csv(DEST/file),keys,cols)
 pd.DataFrame(checks).to_csv(OUT/'sensitivity_reproduction_checks.csv',index=False)
 assert all(r['status']=='PASS' for r in checks),'Sensitivity mismatch'
 print('Independent sensitivity',len(checks),'checks PASS')
if __name__=='__main__':main()
