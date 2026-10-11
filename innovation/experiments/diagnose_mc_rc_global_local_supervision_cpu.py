"""Developer label sampling only, with zero MR placeholders and no network/checkpoint."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[name]='1'
import json,sys,traceback
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT,read,sha,array_sha,np,torch,DEVELOPERS,physical_shape,resize_training_label,training_example)
from mc_rc_observed_only_training_input import read_supervised_label
def write(path,r):path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');out=ROOT/'experiments/mc_rc_global_local_supervision_cpu'
    out.mkdir(exist_ok=False);path=out/'attempt_01.json'
    prepfile=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json'
    prep=read(prepfile);assert prep['complete'] and not prep['errors']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        resources=resource_gate(),script_sha256=sha(__file__),preparation_sha256=sha(prepfile),
        support_sha256=sha(ROOT/'experiments/mc_rc_global_local_task_cpu_support.py'),
        protocol_sha256=sha(ROOT/'MC_RC_GLOBAL_LOCAL_SUPERVISION_DIAGNOSTIC_PLAN_2026-10-03.md'),
        seed=20261006,samples_per_series=32,series=[],samples_completed=0,
        MRI_pixels_loaded=False,checkpoint_loaded=False,neural_forward_calls=0,training_updates=0,
        validation_or_confirmation_labels_loaded=False,scientific_confirmation_patients=0,
        publication_claim_confirmed=False)
    write(path,r)
    try:
        assert len(prep['cases'])==19 and {c['patient'] for c in prep['cases']}==DEVELOPERS
        for index,case in enumerate(prep['cases']):
            resource_gate();label=read_supervised_label(case);shape,spacing=physical_shape(case)
            physical=resize_training_label(label,shape)
            item=dict(image_zrc=np.zeros_like(physical),label_zrc=physical,
                      native_foreground=np.argwhere(label),zspacing=spacing)
            rng=np.random.default_rng(20261006+index);samples=[]
            for sample_index in range(32):
                _,_,local,global_target,locations,target_shape,details=training_example(item,rng)
                lt,gt=local.numpy(),global_target.numpy()
                samples.append(dict(index=sample_index,z=details['z'],positive_plane=details['foreground_plane'],
                    local_positive_mass=[float(a.sum(dtype=np.float64)) for a in lt],
                    local_positive_pixel_ratio=[float(np.mean(a>0)) for a in lt],
                    global_positive_mass=float(gt.sum(dtype=np.float64)),
                    global_positive_pixel_ratio=float(np.mean(gt>0)),
                    local_targets_sha256=array_sha(lt),global_target_sha256=array_sha(gt),
                    locations=locations,target_shape=list(target_shape)))
                r['samples_completed']+=1
            row=dict(patient=case['patient'],uid=case['uid'],native_label_sha256=array_sha(label),
                native_foreground=int(label.sum()),native_foreground_ratio=float(label.mean()),
                physical_label_sha256=array_sha(physical),physical_shape=list(physical.shape),
                physical_soft_mass=float(physical.sum(dtype=np.float64)),samples=samples,
                positive_plane_samples=sum(s['positive_plane'] for s in samples),
                global_positive_mass_mean=float(np.mean([s['global_positive_mass'] for s in samples])),
                local_positive_mass_mean=float(np.mean([s['local_positive_mass'] for s in samples])))
            r['series'].append(row);write(path,r)
            print(json.dumps({k:row[k] for k in ('patient','uid','native_foreground_ratio',
                                               'positive_plane_samples','global_positive_mass_mean')}),flush=True)
            del item,physical,label
        r['patient_summary']={p:{k:float(np.mean([s[k] for s in r['series'] if s['patient']==p]))
            for k in ('native_foreground_ratio','global_positive_mass_mean','local_positive_mass_mean')}
            for p in sorted(DEVELOPERS)}
        r['patient_first_means']={k:float(np.mean([s[k] for s in r['patient_summary'].values()]))
            for k in ('native_foreground_ratio','global_positive_mass_mean','local_positive_mass_mean')}
        r['gpu_initialized']=torch.cuda.is_initialized();assert not r['gpu_initialized']
        r['complete']=len(r['series'])==19 and r['samples_completed']==608
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','samples_completed','neural_forward_calls')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
