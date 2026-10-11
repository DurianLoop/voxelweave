"""Matched FN/FP synthetic errors and input-domain guards for the prepared loss."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import torch
from vs_seg_task_cpu_support import resource_gate
from unified_focal_binary_cpu_port import asymmetric_unified
ROOT=Path(__file__).resolve().parents[1]
torch.set_num_threads(1);torch.set_num_interop_threads(1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    resource_gate();path=ROOT/'experiments/unified_focal_binary_cpu_port/output_bias_and_input_guards_attempt_01.json';assert not path.exists()
    target=np.zeros((1,1,3,3));target[0,0,1,1]=1
    clean=np.where(target>0,.9,.1);fn=clean.copy();fp=clean.copy();fn[0,0,1,1]=.2;fp[0,0,0,0]=.8
    def value(p):return float(asymmetric_unified(torch.tensor(np.log(p/(1-p))),torch.tensor(target)))
    scores={name:value(p) for name,p in (('clean',clean),('same_magnitude_FN',fn),('same_magnitude_FP',fp))}
    assert scores['same_magnitude_FN']>scores['same_magnitude_FP']>scores['clean']
    guards=[]
    for name,y in (('negative',torch.tensor(target)-.01),('above_one',torch.tensor(target)+.01),
                   ('nonfinite',torch.full_like(torch.tensor(target),float('nan')))):
        try:asymmetric_unified(torch.zeros_like(y),y)
        except AssertionError:guards.append(name)
        else:raise AssertionError('Invalid target accepted: '+name)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        script_sha256=sha(__file__),port_sha256=sha(ROOT/'experiments/unified_focal_binary_cpu_port.py'),
        matched_error_probability_change=.7,losses=scores,invalid_target_guards=guards,
        MRI_pixels_loaded=False,network_forward_calls=0,training_updates=0,
        statement='One synthetic matched-error scenario only; does not establish clinical precision/recall tradeoff',
        gpu_initialized=torch.cuda.is_initialized(),scientific_confirmation_patients=0,publication_claim_confirmed=False)
    assert not result['gpu_initialized'];path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(scores))
if __name__=='__main__':main()
