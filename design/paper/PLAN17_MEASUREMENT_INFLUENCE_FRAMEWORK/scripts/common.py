from pathlib import Path
import hashlib,json,datetime
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];PAPER=P.parent;OUT=P/'outputs'
SEED=20260911
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def save(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def fg(x):return np.abs(x)>.01*max(float(np.abs(x).max()),1e-6)
def avg(x,m):return float(np.mean(x[m],dtype=np.float64)) if m.any() else np.nan
def features(anchors):
 cv=[];ma=[];rm=[]
 for j in range(anchors.shape[2]-1):
  a,b=anchors[:,:,j],anchors[:,:,j+1];m=fg(a)|fg(b);d=a.astype(float)-b
  ma.append(avg(abs(d),m));rm.append(np.sqrt(avg(d*d,m)))
 for j in range(1,anchors.shape[2]-1):
  a=.5*(anchors[:,:,j-1].astype(float)+anchors[:,:,j+1])-anchors[:,:,j]
  cv.append(avg(abs(a),fg(anchors[:,:,j])))
 v=anchors[np.isfinite(anchors)&(abs(anchors)>0)]
 return {'anchor_cv':float(np.median(cv)),'adjacent_mae':float(np.median(ma)),'adjacent_rmse':float(np.median(rm)),'acquired_range':max(float(np.diff(np.percentile(v,[1,99]))[0]),1e-6)}
def metrics(a,b,y,m):
 ea=(a-y)[m].astype(float);eb=(b-y)[m].astype(float);d=ea-eb
 total=.5*np.mean(ea*ea+eb*eb);ob=.25*np.mean(d*d)
 return {'mae_a':float(np.mean(abs(ea))),'mae_b':float(np.mean(abs(eb))),'error':float(.5*(np.mean(abs(ea))+np.mean(abs(eb)))),'disagreement':float(np.mean(abs(d))),'variance':float(ob),'observable':float(ob/total) if total>0 else np.nan,'error_cosine':float(ea@eb/np.sqrt((ea@ea)*(eb@eb))),'total_energy':float(total)}
def specs():
 x=json.loads((P/'research_ledger.json').read_text(encoding='utf-8'))['primary_neural_checkpoint_bindings']
 return {(r['dataset'],r['model']):r for r in x}
def datasets():
 fast=(ROOT/'dataset/fastMRI_brain_T2/processed/splits/nifti_seed3407/test_cases.txt').read_text().split()
 meta=pd.read_csv(ROOT/'dataset/IXI/metadata/ixi_cases.csv').set_index('case_id')
 ixi=(ROOT/'dataset/IXI/splits/seed3407/test_cases.txt').read_text().split()
 return [('fastmri',c,ROOT/'dataset/fastMRI_brain_T2/processed/nifti'/(c+'.nii.gz')) for c in fast]+[('ixi',c,Path(str(meta.loc[c,'T2_path']))) for c in ixi]
def weights(z,grid):
 return np.array([np.prod([(z-b)/(a-b) for b in grid if b!=a]) for a in grid])
def interpolate(v,z,phase,method):
 left=phase+((z-phase)//4)*4;grid=[left,left+4] if method=='linear' else [left-4,left,left+4,left+8]
 assert min(grid)>=0 and max(grid)<v.shape[2]
 return sum(w*v[:,:,j].astype(float) for w,j in zip(weights(z,grid),grid))

