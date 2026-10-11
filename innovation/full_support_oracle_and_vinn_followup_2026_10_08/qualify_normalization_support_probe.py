"""Nonmedical falsification: input support does not bound output dependence."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json
from pathlib import Path
import numpy as np
import torch
from scipy.ndimage import correlate
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);torch.set_num_interop_threads(1);resource_guard();started=time.perf_counter()
    out=HERE/'normalization_support_attempt01';out.mkdir(exist_ok=False)
    valid=np.zeros((8,8,8),bool);valid[2:6,2:6,2:6]=True
    eroded=np.zeros_like(valid);eroded[3:5,3:5,3:5]=True
    a=np.linspace(.1,2.,512,dtype=np.float64).reshape(8,8,8);b=a.copy();b[~valid]=0
    assert np.array_equal(a[valid],b[valid]);kernel=np.full((3,3,3),1/27,np.float64)
    module=torch.nn.InstanceNorm3d(1,eps=1e-5,affine=False,track_running_stats=False).double().eval()
    outputs=[];records=[]
    with torch.inference_mode():
        for x in [a,b]:
            conv=torch.nn.functional.conv3d(torch.from_numpy(x)[None,None],torch.from_numpy(kernel)[None,None],padding=1)
            norm=module(conv)[0,0].numpy().copy();conv=conv[0,0].numpy().copy()
            independent_conv=correlate(x,kernel,mode='constant',cval=0.)
            independent_norm=(independent_conv-independent_conv.mean())/np.sqrt(independent_conv.var(ddof=0)+1e-5)
            ce=float(np.max(np.abs(conv-independent_conv)));ne=float(np.max(np.abs(norm-independent_norm)))
            assert ce<=3e-6 and ne<=3e-6
            outputs.append((conv,norm));records.append(dict(conv_oracle_max_error=ce,normalization_oracle_max_error=ne))
    ca,na=outputs[0];cb,nb=outputs[1]
    convolution_eroded_error=float(np.max(np.abs(ca[eroded]-cb[eroded])))
    norm_eroded_error=float(np.max(np.abs(na[eroded]-nb[eroded])))
    assert convolution_eroded_error<=3e-12 and norm_eroded_error>.01
    task=ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py';src=task.read_text(encoding='utf-8')
    assert 'nn.InstanceNorm3d(o,affine=True)' in src and 'track_running_stats' not in src
    r=dict(complete=True,errors=[],nonmedical_cases=2,valid_input_voxels=64,eroded_valid_voxels=8,
        identical_valid_inputs=True,conv_eroded_max_difference=convolution_eroded_error,
        instance_norm_eroded_max_difference=norm_eroded_error,independent_oracle_records=records,
        actual_task_source_uses_current_sample_spatial_normalization=True,
        input_support_mask_alone_not_a_task_output_independence_certificate=True,
        checkpoint_arrays_loaded=0,medical_arrays_loaded=0,GT_arrays_loaded=0,patient_neural_forwards=0,training_updates=0,
        validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        CUDA_initialized=torch.cuda.is_initialized(),elapsed_seconds=time.perf_counter()-started,
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'NORMALIZATION_SUPPORT_PROBE_PROTOCOL.md',task]],
        resources=resource_guard(),publication_claim_confirmed=False,goal_status='active')
    assert not r['CUDA_initialized'] and r['elapsed_seconds']<30;dump(out/'receipt.json',r)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(r),flush=True)
if __name__=='__main__':main()
