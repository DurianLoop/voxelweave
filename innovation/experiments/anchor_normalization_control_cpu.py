"""Three fixed source-volume normalization controls, no torch or network import."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import ast,json,math,sys,zipfile,traceback
from pathlib import Path
from datetime import datetime,timezone
from typing import Optional,Sequence
import numpy as np
import nibabel as nib
from vs_seg_task_cpu_support import ROOT,STAGE,resource_gate
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_full_volume_runtime import decode_source,reconstruct,array_sha,sha
from remind_native_t2_ixi_pair import prepared
from vs_seg_resampling_order_cpu import post_resize
OUT=ROOT/'experiments/anchor_normalization_control_cpu'
ROSTER=['VS-SEG-202','VS-SEG-203','VS-SEG-204']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def compare(a,b,mask):
 x=a[mask];y=b[mask];d=x.astype(float)-y.astype(float)
 return dict(pixels=len(d),changed_pixels=int((x!=y).sum()),max_abs=float(np.abs(d).max()) if len(d) else None,rms=math.sqrt(float(np.dot(d,d))/len(d)) if len(d) else None,bitwise_equal=bool(np.array_equal(x,y)))
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();OUT.mkdir(exist_ok=False);source=STAGE/'vendor/monai/transforms/intensity/array.py';manifestdir=ROOT/'literature/source_cache/vs_seg_cpu_compat_sources_2026-10-02';manifest=read(manifestdir/'index.json');wheel=manifestdir/manifest['monai_wheel']['file'];assert sha(wheel)==manifest['monai_wheel']['sha256']
 with zipfile.ZipFile(wheel) as z:assert z.read('monai/transforms/intensity/array.py')==source.read_bytes()
 tree=ast.parse(source.read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='NormalizeIntensity');env=dict(np=np,Transform=object,Optional=Optional,Sequence=Sequence);exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),env);Normalize=env['NormalizeIntensity'];cases={x['patient']:x for x in cases_from_sources()};paths=[Path(__file__),ROOT/'ANCHOR_NORMALIZATION_CONTROL_CPU_PLAN_2026-10-03.md',source,manifestdir/'index.json',wheel,ROOT/'experiments/vs_seg_full_volume_runtime.py',ROOT/'experiments/vs_seg_resampling_order_cpu.py'];contract=dict(created_utc=datetime.now(timezone.utc).isoformat(),roster=ROSTER,files=[dict(path=p.relative_to(ROOT.parent).as_posix(),sha256=sha(p)) for p in paths],isolated_class_execution=True,full_monai_environment_imported=False,new_neural_forwards=0)
 write(OUT/'run_contract.json',contract);r=dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),complete=False,patients=[],errors=[],gpu_used=False,torch_imported=False,new_neural_forwards=0,post_task_results_read=False,new_method_confirmation_patients=0,publication_claim_confirmed=False)
 try:
  for patient in ROSTER:
   resource_gate();native,affine,refs=decode_source(cases[patient]);del refs;prep=prepared(native[:,:,::4]);obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];raw=reconstruct('raw_pchip',native,prep,{});mixed,_=post_resize(raw,prep,targets);old=read(ROOT/'experiments/vs_seg_resampling_order_cpu'/f'{patient}.json');orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'));miss=np.zeros(native.shape,dtype=bool);miss[:,:,targets]=True;tail=np.zeros(native.shape,dtype=bool);tail[:,:,obs[-1]+1:]=True;miss=nib.orientations.apply_orientation(miss,orientation);tail=nib.orientations.apply_orientation(tail,orientation);patient_rows=[]
   for name,base,key in [('raw',raw,'raw_pchip'),('mixed_post',mixed,'post_resize_pchip')]:
    assert array_sha(base)==old['conditions'][key]['array_sha256'];altered,_=post_resize(base,prep,obs);assert np.array_equal(altered[:,:,targets],base[:,:,targets]) and np.array_equal(altered[:,:,obs[-1]+1:],base[:,:,obs[-1]+1:]);br=np.ascontiguousarray(nib.orientations.apply_orientation(base,orientation));ar=np.ascontiguousarray(nib.orientations.apply_orientation(altered,orientation));selected=br[None].copy();mask=np.ones(selected.shape,dtype=np.bool_);mu=np.mean(selected[mask]);sigma=np.std(selected[mask]);sigma=np.float32(1) if sigma==0 else sigma;mb=np.mean(ar[None].copy()[mask]);sb=np.std(ar[None].copy()[mask]);normalized_base=Normalize()(br[None].copy())[0];normalized_own=Normalize()(ar[None].copy())[0];normalized_fixed=Normalize(subtrahend=mu,divisor=sigma)(ar[None].copy())[0];fixed_missing=compare(normalized_fixed,normalized_base,miss);fixed_tail=compare(normalized_fixed,normalized_base,tail);assert fixed_missing['bitwise_equal'] and fixed_tail['bitwise_equal'];patient_rows.append(dict(baseline=name,baseline_array_sha256=array_sha(base),intervention_array_sha256=array_sha(altered),baseline_mean=float(mu),baseline_std=float(sigma),intervention_mean=float(mb),intervention_std=float(sb),missing_own_stats_minus_baseline=compare(normalized_own,normalized_base,miss),missing_fixed_stats_minus_baseline=fixed_missing,tail_own_stats_minus_baseline=compare(normalized_own,normalized_base,tail),tail_fixed_stats_minus_baseline=fixed_tail,original_missing_pixels_bitwise_unchanged=True,isolated_authenticated_normalizer_used=True))
   r['patients'].append(dict(patient=patient,conditions=patient_rows));write(OUT/'attempt_01.json',r);print(json.dumps(dict(patient=patient,completed_patients=len(r['patients']))),flush=True);del native,raw,mixed,altered,br,ar,selected,normalized_base,normalized_own,normalized_fixed
  assert len(r['patients'])==3 and 'torch' not in sys.modules;r.update(complete=True,all_six_fixed_stats_missing_and_tail_bitwise_equal=True,all_six_own_stats_missing_changed=all(x['missing_own_stats_minus_baseline']['changed_pixels']>0 for p in r['patients'] for x in p['conditions']),neural_activation_or_dice_measured=False)
 except Exception as exc:r['errors'].append(type(exc).__name__+': '+str(exc));r['traceback']=traceback.format_exc()
 r['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',r);print(json.dumps({k:r.get(k) for k in ('complete','errors','all_six_fixed_stats_missing_and_tail_bitwise_equal','all_six_own_stats_missing_changed','torch_imported')}),flush=True)
 if not r['complete']:raise SystemExit(1)
if __name__=='__main__':main()
