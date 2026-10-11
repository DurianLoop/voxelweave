"""Full exact tiny corpus and all three modes of fixed million-voxel geometry."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,itertools,traceback
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import direct_separable_reference as new
BASE=new.BASE;ROOT=BASE.parent;HERE=Path(__file__).resolve().parent
import certified_resolution as candidate
import direct_interval_reference as old
import exact_tensor_reference as exact
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,bind,entry,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,array_sha,QPATH
import torch
sys.path.insert(0,str(ROOT/'intensity_precision_failure_diagnosis_2026_10_09'))
import intensity_float64_stats as intensity
sys.path.insert(0,str(ROOT/'resolution_degradation_controls_2026_10_08'))
from independent_intensity import apply_reference as intensity_reference

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);started=time.perf_counter()
    def guard():
        v=resource_guard();assert time.perf_counter()-started<900 and v['workspace_free_bytes']-15_800_000>=8_000_000_000
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000 and not torch.cuda.is_initialized();return v
    before=guard();out=HERE/'qualification_attempt01';out.mkdir(exist_ok=False)
    prerequisites=[BASE/'synthetic_attempt01/receipt.json',BASE/'direct_oracle_synthetic_attempt01/receipt.json',BASE/'failed_full_field_regression_attempt01/receipt.json']
    for p in prerequisites:
        q=read(p);assert q['complete'] and not q['errors']
        for b in q['source_bindings']:bind(b)
    sources={Path(__file__),HERE/'PROTOCOL.md',HERE/'direct_separable_reference.py',BASE/'certified_resolution.py',BASE/'direct_interval_reference.py',BASE/'exact_tensor_reference.py',*prerequisites,QPATH}
    dump(out/'frozen_config.json',dict(expected_tiny_fields=144,expected_full_real_fields=3,extra_extreme_points=9,image_bitwise_gate=0,intensity_gate=3e-6,source_bindings=[entry(p) for p in sorted(sources)]))
    r=dict(complete=False,errors=[],tiny_fields=0,exact_points=0,real_fields=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,training_updates=0,CUDA_initialized=False,all_patient_qualification_passed=False,full35904_qualification_passed=False,training_ready=False,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
    try:
        definitions=[((1,1,1),(3,5,7)),((1,5,7),(3,5,7)),((3,5,7),(3,5,7)),((7,9,11),(3,5,7))]
        for fine,patch in definitions:
            padding=[(max(0,k-n)//2,(max(0,k-n)+1)//2) for n,k in zip(fine,patch)];grid=dict(unpadded_shape_zrc=list(fine),padding=padding)
            z,u,v=np.meshgrid(*[np.arange(n) for n in fine],indexing='ij');textures=[np.full(fine,2.5,np.float32),(z*.25+u*.125-v*.375).astype(np.float32),(np.sin(z*1.3)+np.cos(u*.7)-np.sin(v*.31)).astype(np.float32)]
            for texture in textures:
                cache=np.pad(texture,padding);extent=np.asarray(cache.shape)-patch
                for gi,(start,flips) in enumerate([(np.zeros(3,int),[False]*3),(extent//2,[True,False,True])]):
                    geometry=dict(start=start.tolist(),flips=flips,intensity_scale=1.03,intensity_shift=-.073)
                    for enabled,mode in itertools.product([False,True],['throughplane','inplane','allaxes']):
                        guard();primitive=dict(enabled=enabled,scale=.85 if gi==0 else 1.15)
                        a,s,am,ai=new.apply_reference(cache,grid,geometry,primitive,mode,patch,True)
                        b,t,bm=old.apply_reference(cache,grid,geometry,primitive,mode,patch);c,w,cm=candidate.apply(cache,grid,geometry,primitive,mode,patch)
                        d,domain,values=exact.patch_reference(cache,grid,geometry,primitive,mode,patch)
                        for other in [b,c,d]:assert np.array_equal(a.view(np.uint32),other.view(np.uint32))
                        assert np.array_equal(s,t) and np.array_equal(s,w) and np.array_equal(s.astype(bool),domain)
                        for target,value in values.items():
                            local=tuple(list(ai['local'][axis]).index(target[axis]) for axis in range(3));lo,hi=ai['bounds']
                            assert F(float(lo[local]))<=value<=F(float(hi[local]));r['exact_points']+=1
                        r['tiny_fields']+=1
        tiny=np.array([0.,1e-40,-1e-40,1e-20,-1e-20,1e20,-1e20,1e30,-1e30],np.float32).reshape(1,3,3)
        raw,meta,(lo,hi)=new.interpolate_direct(tiny,(1,2,2),[np.arange(n) for n in tiny.shape],True)
        for index in np.ndindex(*tiny.shape):
            val=exact.point(tiny,(1,2,2),index);assert F(float(lo[index]))<=val<=F(float(hi[index]));assert raw[index].view(np.uint32)==exact.nearest_float32(val).view(np.uint32)
        f=read(ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01/receipt.json')['failed_field'];c,row=development_cases()[f['case']];grid=lattice(c)
        normal,stats=source_image(c,row,f['kind']);cache=physical_mr(normal,grid);del normal;r['MRI_arrays_loaded']=1
        cache_sha=array_sha(cache);ref=next(v for arm in read(QPATH)['arms'] if arm['kind']==f['kind'] for v in arm['cache_records'] if v['uid']==c['uid']);assert cache_sha==ref['input_sha256']
        sources.update([ROOT/c['header_file'],ROOT/c['mr_zip_file']])
        for mode in ['throughplane','inplane','allaxes']:
            guard();times={};tick=time.perf_counter();a,s,am,ai=new.apply_reference(cache,grid,f['geometry'],f['primitive'],mode,include_intervals=True);times['separable']=time.perf_counter()-tick
            tick=time.perf_counter();b,t,bm=old.apply_reference(cache,grid,f['geometry'],f['primitive'],mode);times['tensor_product']=time.perf_counter()-tick
            tick=time.perf_counter();c,w,cm=candidate.apply(cache,grid,f['geometry'],f['primitive'],mode);times['candidate']=time.perf_counter()-tick
            assert np.array_equal(a.view(np.uint32),b.view(np.uint32)) and np.array_equal(a.view(np.uint32),c.view(np.uint32)) and np.array_equal(s,t) and np.array_equal(s,w)
            aa=intensity.apply(a[None,None],[f['intensity_primitives']])[0,0];bb=intensity_reference(b,f['intensity_primitives']);post=float(np.max(np.abs(aa-bb)));assert post<=3e-6
            fine,coarse=candidate.shapes(grid,f['primitive'],mode);source=cache[tuple(slice(int(p[0]),int(p[0])+n) for p,n in zip(grid['padding'],fine))];probes=0
            for local in set(itertools.product(*[np.linspace(0,len(q)-1,4,dtype=int).tolist() for q in ai['queries']])):
                query=tuple(int(ai['queries'][axis][local[axis]]) for axis in range(3));value=exact.point(source,coarse,query);lo,hi=ai['bounds'];assert F(float(lo[local]))<=value<=F(float(hi[local]));probes+=1
            r['real_fields'].append(dict(mode=mode,full_target_voxels=int(a.size),bitwise_disagreements=0,support_disagreements=0,intensity_max_error=post,exact_probes=probes,times_seconds=times,new=am,old=bm))
            print(json.dumps(r['real_fields'][-1]),flush=True)
        assert r['tiny_fields']==144 and r['exact_points']==4428 and len(r['real_fields'])==3 and array_sha(cache)==cache_sha
        r.update(complete=True,extra_extreme_points=9,all144_tiny_and3_full_real_fields_verified=True)
    except Exception as exc:r['errors'].append(dict(type=type(exc).__name__,message=str(exc)));r['traceback']=traceback.format_exc();traceback.print_exc()
    r.update(source_bindings=[entry(p) for p in sorted(sources)]+[entry(out/'frozen_config.json')],resources_before=before,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(out/'receipt.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ['source_bindings','real_fields','traceback']},ensure_ascii=False),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
