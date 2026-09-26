"""Freeze assets and geometry/masks only; no predictor outcomes or summaries."""
from pathlib import Path
import hashlib,json,datetime,shutil,sys
import numpy as np,pandas as pd,nibabel as nib

P=Path(__file__).resolve().parents[1];PAPER=P.parent;ROOT=PAPER.parents[1]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def fg(x):return abs(x)>.01*max(float(abs(x).max()),1e-6)
def pick(a,n):
 if len(a)<=n:return list(a)
 ids=[]
 for x in np.linspace(0,len(a)-1,n+2)[1:-1]:
  i=int(round(x))
  while i in ids and i+1<len(a):i+=1
  ids.append(i)
 return [a[i] for i in sorted(set(ids))]
def balanced(a,case):
 n1=2+int(sum(map(ord,case))%2==0)
 return sorted(pick([z for z in a if z%4==1],n1)+pick([z for z in a if z%4==3],5-n1))
def main():
 if (P/'freeze.json').exists():raise SystemExit('Freeze already exists; never overwrite.')
 for n in ['inputs','targets','outputs','logs','figures','original_snapshot']:(P/n).mkdir(exist_ok=True)
 original=[]
 for tree in [PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER',PAPER/'TMI/TMI_ARCH_GENERALIZED']:
  for f in tree.rglob('*'):
   if f.is_file():
    rel=f.relative_to(ROOT);dst=P/'original_snapshot'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dst);original.append({'path':rel.as_posix(),'sha256':sha(f)})
 for f in [ROOT/'README.md',PAPER/'README.md',PAPER/'CVPR/README.md']:
  rel=f.relative_to(ROOT);dst=P/'original_snapshot'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dst);original.append({'path':rel.as_posix(),'sha256':sha(f)})
 write(P/'original_manifest.json',original)
 old=PAPER/'PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK';ledger=json.loads((old/'research_ledger.json').read_text(encoding='utf-8'))
 specs=ledger['primary_neural_checkpoint_bindings'];write(P/'model_registry.json',specs)
 sources=set();sources.update(ROOT/x['checkpoint'] for x in specs)
 for r in ledger['ningxia_primary_influence_checkpoint_bindings']:
  sources.add(ROOT/r['checkpoint'])
 for name in ['research_ledger.json','experiment_registry.csv','research_audit.md','HOSTILE_REVIEW_ZH.md','claim_evidence_matrix.md']:sources.add(old/name)
 for s in ['mira.py','nonself_sensitivity.py','figures.py','qualitative.py']:sources.add(old/'scripts'/s)
 # Preserve raw scientific records and executable preprocessing, not summary claims alone.
 for base in [PAPER/'ARCHIVE',PAPER/'CVPR/archive',PAPER/'PLAN13_EVIDENCE_UPGRADE',PAPER/'PLAN14_SCIENTIFIC_STRENGTHENING',PAPER/'PLAN15_BASELINE_INTEGRATION',old]:
  for f in base.rglob('*'):
   if f.is_file() and f.suffix.lower() in {'.py','.csv','.json','.npz'} and not any(x in f.parts for x in ['original_snapshot','delivery']):sources.add(f)
 packages=['baseline/fastmri_brain_hat_2p5d','baseline/fastmri_brain_swinir_2p5d','baseline/ixi_hat_2p5d','baseline/ixi_swinir_2p5d','baseline/ixi_i3net','baseline/ixi_arssr','baseline/ixi_cycleinr','pre/ixi_diffusion','pre/basicsr']
 for name in packages:
  for f in (ROOT/name).rglob('*.py'):
   if 'runs' not in f.parts:sources.add(f)
 manifest=pd.read_csv(PAPER/'CVPR/archive/CVPR_UPGRADE/DATA_MANIFEST.csv');historical=manifest[(manifest.factor==4)&manifest.architecture.isin(['hat','swinir'])]
 for r in historical.itertuples():sources.update([Path(r.source_file),Path(r.ground_truth_file)])
 historical.to_csv(P/'historical_case_registry.csv',index=False)
 meta=pd.read_csv(ROOT/'dataset/IXI/metadata/ixi_cases.csv').set_index('case_id');sources.add(ROOT/'dataset/IXI/metadata/ixi_cases.csv')
 rows=[];ins=[]
 for ds,split in [('fastmri','dataset/fastMRI_brain_T2/processed/splits/nifti_seed3407/test_cases.txt'),('ixi','dataset/IXI/splits/seed3407/test_cases.txt')]:
  sp=ROOT/split;sources.add(sp);cases=sp.read_text().split()
  for i,c in enumerate(cases):
   src=ROOT/'dataset/fastMRI_brain_T2/processed/nifti'/(c+'.nii.gz') if ds=='fastmri' else Path(str(meta.loc[c,'T2_path']))
   sources.add(src);im=nib.load(src);v=im.get_fdata(dtype=np.float32);depth=v.shape[2]
   a0=list(range(0,depth,4));a2=list(range(2,depth,4));zs=[3,5,7,9,11] if ds=='fastmri' else balanced([z for z in range(3,min(a0[-1],a2[-1])+1,2)],c)
   # IXI evaluation targets use the legacy integer-header staging contract.
   if ds=='ixi':
    img=nib.Nifti1Image(v[:,:,:a0[-1]+1],im.affine,im.header.copy());gt=nib.Nifti1Image.from_bytes(img.to_bytes()).get_fdata(dtype=np.float32)
   else:gt=v
   dst=P/'targets'/f'{ds}_{c}_cross.npz';np.savez_compressed(dst,z=np.array(zs),gt=np.stack([gt[:,:,z] for z in zs]),mask=np.stack([fg(gt[:,:,z]) for z in zs]));ins.append(dst)
   zinf=sorted(set(int(round(x)) for x in np.linspace(3,depth-4,5)[1:-1]));central=int(round((3+depth-4)/2))
   for z in zinf:
    ids=[z+k for k in [-3,-2,-1,1,2,3]];pool=v[:,:,ids];vals=pool[np.isfinite(pool)&(abs(pool)>0)];lo,hi=np.percentile(vals,[1,99]);scale=float(hi-lo)
    assert np.isfinite(scale) and scale>0 and min(ids)>=0 and max(ids)<depth
    mask=fg(v[:,:,z-1])|fg(v[:,:,z+1]);assert mask.any()
    inp=P/'inputs'/f'{ds}_{c}_z{z}.npz';np.savez_compressed(inp,anchors=pool,anchor_ids=np.array(ids),mask=mask,lo=float(lo),scale=scale);ins.append(inp)
    tgt=P/'targets'/f'{ds}_{c}_z{z}.npy';np.save(tgt,v[:,:,z]);ins.append(tgt)
   rows.append({'dataset':ds,'case':c,'source':src.relative_to(ROOT).as_posix(),'depth':depth,'shape':list(v.shape),'phase0':a0,'phase2':a2,'targets':zs,'influence_targets':zinf,'central_target':central,'cross_targets':dst.relative_to(P).as_posix()})
   for s in [s for s in specs if s['dataset']==ds]:
    f=ROOT/s['stored_predictions']/('diff_'+src.name)
    if not f.exists():raise FileNotFoundError(f)
    sources.add(f)
   if (i+1)%20==0:print('freeze inputs',ds,i+1,flush=True)
 write(P/'case_registry.json',rows)
 models=['hat','swinir','i3net','saint','cycleinr'];write(P/'pair_registry.json',[{'a':a,'b':b,'pair':a+'__'+b} for a in models for b in models if a!=b])
 prop=sorted([r['case'] for r in rows if r['dataset']=='ixi'],key=lambda c:hashlib.sha256(('MIRA-final-proposition:'+c).encode()).hexdigest())[:12];write(P/'proposition_case_registry.json',prop)
 paths=sorted(sources);records=[]
 for i,f in enumerate(paths):
  if not f.exists():raise FileNotFoundError(f)
  records.append({'path':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
  if (i+1)%400==0:print('hash sources',i+1,'/',len(paths),flush=True)
 write(P/'source_manifest.json',records)
 write(P/'prepared_input_manifest.json',[{'path':f.relative_to(P).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)} for f in ins])
 bound=['FINAL_ITERATION_PROTOCOL.md','original_manifest.json','model_registry.json','case_registry.json','historical_case_registry.csv','pair_registry.json','proposition_case_registry.json','source_manifest.json','prepared_input_manifest.json','scripts/prepare_freeze.py']
 write(P/'freeze.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'description':'Frozen final-iteration protocol; retrospective, no new inference/summary yet','artifacts':{n:sha(P/n) for n in bound},'sources':len(records),'original_files':len(original),'prepared_inputs':len(ins),'cross_arch_pairs_per_cohort':20})
 print('FROZEN',len(records),'source assets',len(ins),'prepared arrays',flush=True)

if __name__=='__main__':main()
