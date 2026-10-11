"""Fresh analytic/normalizer input SHA replay and all36 paired pilot scalars."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import json,math,sys,traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import nibabel as nib
from skimage.transform import resize
from vs_seg_task_cpu_support import ROOT,resource_gate
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_full_volume_runtime import decode_source,reconstruct,array_sha,sha
from vs_seg_selection_sensitivity import completion_gate,load_verified_records
from remind_native_t2_ixi_pair import prepared
OUT=ROOT/'experiments/anchor_bandwidth_task_cpu_pilot'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def check(ok,text):
 if not ok:raise ValueError(text)
def close(a,b,text):check(a==b if a is None or b is None else math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12),text)
def rt(a,lo,span):
 coarse=resize(((a-lo)/(span+1e-8)).astype(np.float32),(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32);return (resize(np.clip(coarse,0,1),a.shape,preserve_range=True,anti_aliasing=True)*span+lo).astype(np.float32)
def norm(a,mu,sigma):return np.divide(np.subtract(a,mu),sigma)[None].astype(np.float32)
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();r=read(OUT/'attempt_01.json');c=read(OUT/'run_contract.json');path=OUT/'independent_inputs_and_all36_estimates.json';check(not path.exists(),'First proof already exists');proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),contract_sha256=sha(OUT/'run_contract.json'),complete=False,errors=[],patients=[],normalized_inputs_replayed=0,fixed_missing_identities_verified=0,saved_prediction_proofs_verified=0,new_neural_forwards=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,independence='Fresh analytic input reconstruction and NumPy normalization expression instead of MONAI class; actual full array hashes and fixed missing identities, all saved prediction proof bindings, paired scalar estimates. Shared decoder/PCHIP/resize and NumPy; no independent cohort/model/stack.')
 try:
  check(r['complete'] and not r['errors'] and r['new_neural_forwards']==12 and len(r['patients'])==12 and len(r['analysis'])==36,'Whole12/all36 completion required')
  for f in c['files']:check(sha(ROOT.parent/f['path'])==f['sha256'],'Frozen input changed '+f['path'])
  records={}
  for e in r['patients']:
   check(sha(ROOT/e['file'])==e['sha256'] and sha(ROOT/e['verification_file'])==e['verification_sha256'],'Actual record/proof SHA differs');v=read(ROOT/e['verification_file']);x=read(ROOT/e['file']);check(v['complete'] and not v['errors'] and v['record_sha256']==sha(ROOT/e['file']) and v['prediction_sha256']==sha(ROOT/x['prediction_file']),'Saved prediction proof differs');check(x['complete'] and not x['cuda_initialized'] and not x['deployable_sr_method'],'CPU diagnostic role differs');records.setdefault(e['patient'],{})[e['condition']]=x;proof['saved_prediction_proofs_verified']+=1
  cases={x['patient']:x for x in cases_from_sources()};gate,original=completion_gate();check(gate['allowed'],'Original task cohort incomplete');coverage=read(ROOT/'experiments/vs_seg_full_volume_coverage/attempt_01.json');old,_=load_verified_records(original['main_roster'],{x['patient']:x for x in coverage['patients']});post=ROOT/'experiments/vs_seg_post_resize_task_cpu';oldpost={p:read(post/(p+'.json')) for p in c['roster']}
  for patient in c['roster']:
   resource_gate();native,affine,refs=decode_source(cases[patient]);del refs;prep=prepared(native[:,:,::4]);lo=prep[1];span=prep[2]-prep[1];obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];raw=reconstruct('raw_pchip',native,prep,{});mixed=raw.copy()
   for z in targets:mixed[:,:,z]=rt(raw[:,:,z],lo,span)
   orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'));mask=np.zeros(native.shape,dtype=bool);mask[:,:,targets]=True;mask=nib.orientations.apply_orientation(mask,orientation)
   for basename,base in [('raw',raw),('post',mixed)]:
    changed=base.copy()
    for z in obs:changed[:,:,z]=rt(native[:,:,z],lo,span)
    check(np.array_equal(changed[:,:,targets],base[:,:,targets]) and np.array_equal(changed[:,:,obs[-1]+1:],base[:,:,obs[-1]+1:]),'Actual intervention changes missing/tail');br=np.ascontiguousarray(nib.orientations.apply_orientation(base,orientation));ar=np.ascontiguousarray(nib.orientations.apply_orientation(changed,orientation));mu=np.mean(br.ravel());sd=np.std(br.ravel());sd=np.float32(1) if sd==0 else sd;base_norm=norm(br,mu,sd)
    for nname in ('own','fixed'):
     x=records[patient][basename+'_anchor_'+nname];close(float(mu),x['normalization_baseline_mean'],'Baseline mean differs');close(float(sd),x['normalization_baseline_std'],'Baseline std differs');check(array_sha(changed)==x['reconstructed_array_sha256'] and array_sha(native)==x['native_array_sha256'],'New native/diagnostic volume differs');sub=mu if nname=='fixed' else np.mean(ar.ravel());div=sd if nname=='fixed' else np.std(ar.ravel());div=np.float32(1) if div==0 else div;normalized=norm(ar,sub,div);check(array_sha(normalized)==x['normalized_input_array_sha256'],'Fresh manual normalization input SHA differs');same=np.array_equal(normalized[0][mask],base_norm[0][mask]);check(same==x['missing_network_input_bitwise_equal_to_baseline'],'Missing network identity flag differs');proof['normalized_inputs_replayed']+=1
     if nname=='fixed':check(same,'Fixed stats changes actual missing input');proof['fixed_missing_identities_verified']+=1
   proof['patients'].append(dict(patient=patient,all_four_input_hashes_verified=True));write(path,proof);print(json.dumps(dict(patient=patient,verified_patients=len(proof['patients']))),flush=True)
  for e in r['analysis']:
   ref,domain=e['reference'],e['domain'];left,right=e['comparison'].split('-');values=[];undefined=[]
   for patient in c['roster']:
    a=records[patient][left]['task_metrics'][ref][domain]['dice'];b=(old[patient]['raw_pchip']['task_metrics'][ref][domain]['dice'] if right=='raw' else oldpost[patient]['task_metrics'][ref][domain]['dice'] if right=='post' else records[patient][right]['task_metrics'][ref][domain]['dice'])
    if a is None or b is None:undefined.append(patient)
    else:values.append(dict(patient=patient,difference=a-b))
   check(undefined==e['undefined_patients'] and len(values)==e['defined_n'] and [x['patient'] for x in values]==[x['patient'] for x in e['patient_differences']],'Paired undefined roster differs')
   for a,b in zip(values,e['patient_differences']):close(a['difference'],b['difference'],'Actual paired difference differs')
   close(math.fsum(v['difference'] for v in values)/len(values) if values else None,e['mean'],'Actual pilot mean differs')
  proof.update(complete=True,task_analysis_endpoints_verified=36,scientific_confirmation_patients=0)
 except Exception as exc:proof['errors'].append(type(exc).__name__+': '+str(exc));proof['traceback']=traceback.format_exc()
 proof['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,proof);print(json.dumps({k:proof.get(k) for k in ('complete','errors','normalized_inputs_replayed','fixed_missing_identities_verified','task_analysis_endpoints_verified')}),flush=True)
 if not proof['complete']:raise SystemExit(1)
if __name__=='__main__':main()
