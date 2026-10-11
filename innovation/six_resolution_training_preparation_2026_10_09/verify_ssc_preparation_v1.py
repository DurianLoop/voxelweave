"""Independent Torch patch SSD oracle, affine/constant/central perturbation probes and exact unary packing."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='-1'
import sys,json,time,traceback,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
import torch,numpy as np
from torch.nn import functional as F
from ssc_reference_adapter_v1 import OFFSETS,PAIRS,descriptor,quantize,pack,hamming_sad
torch.set_num_threads(1);torch.set_num_interop_threads(1)

def oracle(image):
    value=torch.from_numpy(np.ascontiguousarray(image,dtype=np.float64))[None,None]
    padded=F.pad(value,(3,3,3,3,3,3),mode='replicate');distances=[]
    # Independently enumerate orthogonal neighbour endpoints by axis and sign.
    endpoints=[tuple(sign*2 if k==axis else 0 for k in range(3)) for axis in range(3) for sign in (1,-1)]
    pairs=[(endpoints[i],endpoints[j]) for i in range(6) for j in range(i+1,6)
           if sum(u*v for u,v in zip(endpoints[i],endpoints[j]))==0]
    assert len(pairs)==12 and pairs==list(PAIRS)
    for a,b in pairs:
        av=padded[(slice(None),slice(None),*(slice(2+d,2+d+n+2) for d,n in zip(a,image.shape)))]
        bv=padded[(slice(None),slice(None),*(slice(2+d,2+d+n+2) for d,n in zip(b,image.shape)))]
        distances.append(F.avg_pool3d((av-bv).square(),3,stride=1)[0,0])
    d=torch.stack(distances,dim=-1);variance=d.mean(dim=-1,keepdim=True);safe=torch.where(variance>0,variance,torch.ones_like(variance))
    return torch.exp(-(d-d.amin(dim=-1,keepdim=True))/safe).float().numpy()

def main():
    started=time.perf_counter();out=HERE/'ssc_operator_preparation_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],descriptor_checks=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
      CUDA_initialized=False,training_updates=0,author_implementation_executed=False,medical_effect_scored=False,
      confirmation_patients_opened=False,lockedIXI_opened=False,original_training_modified=False,
      publication_claim_confirmed=False,goal_status='active')
    def guard():
        v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
        assert size<7_000_000 and fs<20_000_000 and v['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000
        assert not torch.cuda.is_initialized() and torch.get_num_threads()==torch.get_num_interop_threads()==1 and time.perf_counter()-started<180
        return v
    try:
        r['resources_before']=guard();ep=HERE/'ssc_extraction_render_attempt01/receipt.json';extract=read(ep);assert extract['complete'] and extract['verified_pages']==8
        pdf=bind(read(HERE/'ssc_primary_pdf_attempt01/receipt.json')['pdf'])
        r['source_bindings']=[entry(p) for p in [Path(__file__),HERE/'ssc_reference_adapter_v1.py',HERE/'SSC_PAPER_AND_CONTROL_PREPARATION.md',ep,pdf]]
        rng=np.random.default_rng(20261009);random=rng.normal(size=(12,13,14)).astype(np.float32)
        ramp=np.indices(random.shape).sum(axis=0).astype(np.float32)
        for name,x in [('signed_random',random),('linear_ramp',ramp),('zero',np.zeros_like(random)),('constant',np.full_like(random,.37))]:
            guard();original=x.copy();tick=time.perf_counter();y=descriptor(x);seconds=time.perf_counter()-tick;ind=oracle(x)
            error=float(np.max(np.abs(y-ind)));assert error<=3e-6
            assert np.array_equal(x,original) and np.array_equal(y,descriptor(x)) and y.shape==(*x.shape,12)
            assert np.isfinite(y).all() and y.min()>=0 and y.max()<=1 and np.all(y.max(axis=-1)==1)
            if name in ('zero','constant'):assert np.all(y==1)
            r['descriptor_checks'].append(dict(case=name,NumPy_Torch_descriptor_max_error=error,
              input_bitwise_unchanged=True,repeat_bitwise_equal=True,constant_convention_passed=True,
              full_field_voxels=x.size,CPU_descriptor_seconds=seconds))
        base=descriptor(random);affine=[]
        for a,b in [(.25,.125),(.5,0),(2,.25),(-2,.25)]:
            transformed=random.astype(np.float64)*a+b;value=descriptor(transformed)
            error=float(np.max(np.abs(value-base)));assert error<=3e-6
            affine.append(dict(scale=a,shift=b,descriptor_max_error=error,synthetic_exact_affine_not_acquisition_intervention=True))
        center=(6,6,7);noisy=random.copy();noisy[center]+=1000
        unchanged=float(np.max(np.abs(descriptor(noisy)[center]-base[center])));assert unchanged==0
        center_pairs=tuple(((0,0,0),a) for a in OFFSETS)
        central_control=float(np.max(np.abs(descriptor(noisy,center_pairs)[center]-descriptor(random,center_pairs)[center])))
        assert central_control>1e-3
        # Exhaust all36 scalar levels in each of12 slots and1000 arbitrary full vectors.
        first=[];second=[]
        for slot in range(12):
            for a,b in itertools.product(range(6),repeat=2):
                av=np.zeros(12,np.uint8);bv=np.zeros(12,np.uint8);av[slot]=a;bv[slot]=b;first.append(av);second.append(bv)
        first=np.concatenate((np.stack(first),rng.integers(0,6,size=(1000,12),dtype=np.uint8)))
        second=np.concatenate((np.stack(second),rng.integers(0,6,size=(1000,12),dtype=np.uint8)))
        result=hamming_sad(pack(first),pack(second));independent=np.abs(first.astype(np.int64)-second.astype(np.int64)).sum(axis=-1)/60
        quant_error=float(np.max(np.abs(result-independent)));assert quant_error<=3e-12 and len(first)==1432
        q=quantize(base);nearest_error=float(np.max(np.abs(base.astype(np.float64)-q.astype(np.float64)/5)))
        assert nearest_error<=.1+3e-6 and np.max(pack(q))<2**60
        # Ordinary binary popcount is unequal to the intended scalar level distance.
        assert (1^2).bit_count()==2 and abs(1-2)==1
        for b in r['source_bindings']:bind(b)
        r.update(complete=True,affine_probes=affine,central_voxel_perturbation=dict(SSC_point_difference=unchanged,
          centre_including_6NH_point_difference=central_control,control_not_complete_author_MIND_reproduction=True,
          robustness_not_medical_benefit=True),unary_quantization=dict(exhaustive_scalar_pairs_per_slot=36,
          slots=12,random_full_vectors=1000,total_vector_pair_checks=1432,
          Hamming_quantized_SAD_max_error=quant_error,nearest_level_max_error=nearest_error,packed_bits=60,
          ordinary_binary_level_encoding_counterexample_verified=True),resources_after=guard())
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r)
    print(json.dumps({k:r.get(k) for k in ['complete','errors','descriptor_checks','affine_probes','central_voxel_perturbation','unary_quantization','elapsed_seconds']},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
