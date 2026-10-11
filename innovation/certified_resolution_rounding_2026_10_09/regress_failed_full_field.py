"""One complete fixed million-voxel failure regression, retaining old failure as evidence."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,sys,time,traceback
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import torch
import certified_resolution as candidate
import direct_interval_reference as direct
import exact_tensor_reference as exact
from qualify_certified_synthetic import ROOT,HERE,entry,dump
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,bind,sha,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,array_sha,QPATH
OLD=ROOT/'resolution_degradation_controls_2026_10_08';sys.path.insert(0,str(OLD))
from resolution_control import apply as old_production,baseline_patch
from independent_resolution import independent_apply as old_reference
from independent_intensity import apply_reference as independent_intensity
sys.path.insert(0,str(ROOT/'intensity_precision_failure_diagnosis_2026_10_09'))
import intensity_float64_stats as intensity

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);started=time.perf_counter()
    def guard():
        resources=resource_guard();assert time.perf_counter()-started<1800
        assert resources['workspace_free_bytes']-2_000_000-3_000_000-2_800_000>=8_000_000_000
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000 and not torch.cuda.is_initialized()
        return resources
    before=guard();out=HERE/'failed_full_field_regression_attempt01';out.mkdir(exist_ok=False)
    result=dict(complete=False,errors=[],MRI_input_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,training_updates=0,new_production_selected=False,training_ready=False,
        confirmation_patients_opened=False,validation_pixels_loaded=False,lockedIXI_opened=False,
        publication_claim_confirmed=False,goal_status='active')
    sources={Path(__file__),HERE/'FAILED_FIELD_REGRESSION_PROTOCOL.md',HERE/'certified_resolution.py',HERE/'direct_interval_reference.py',HERE/'exact_tensor_reference.py',
        Path(intensity.__file__),OLD/'independent_intensity.py',OLD/'resolution_control.py',OLD/'independent_resolution.py',QPATH}
    try:
        for path in [HERE/'synthetic_attempt01/receipt.json',HERE/'direct_oracle_synthetic_attempt01/receipt.json']:
            q=read(path);assert q['complete'] and not q['errors'];sources.add(path)
            for b in q['source_bindings']:bind(b)
        previous=ROOT/'resource_recovery_and_generalization_controls_2026_10_09';diagnosticpath=previous/'failed_v2_field_diagnostic_attempt01/receipt.json';diagnostic=read(diagnosticpath)
        assert diagnostic['complete'] and diagnostic['failed_v2_field_reproduced'];sources.add(diagnosticpath)
        for b in diagnostic['source_bindings']:bind(b)
        f=diagnostic['failed_field'];assert (f['case'],f['kind'],f['step'],f['patch'],f['mode'])==(8,'native_reference',2879,1,'throughplane')
        cases=development_cases();c,row=cases[8];grid=lattice(c)
        configpath=ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01/frozen_config.json';config=read(configpath);sources.add(configpath)
        for path in [c['header_file'],c['mr_zip_file']]:sources.add(bind(next(b for b in config['source_bindings'] if b['path']==path)))
        dump(out/'frozen_config.json',dict(case_identity=diagnostic['case_identity'],failed_field=f,patch_shape=[64,128,128],
            exact_probe_plan='4 equally spaced local indices per axis across valid source domain plus fixed witness',
            image_gate=3e-6,coordinate_gate=3e-12,binary_gate=0,source_bindings=[entry(p) for p in sorted(sources)]))
        tick=time.perf_counter();normalized,stats=source_image(c,row,'native_reference');cache=physical_mr(normalized,grid);del normalized
        q=read(QPATH);ref=next(v for a in q['arms'] if a['kind']=='native_reference' for v in a['cache_records'] if v['uid']==c['uid'])
        cache_sha=array_sha(cache);assert cache_sha==ref['input_sha256'];result.update(MRI_input_arrays_loaded=1,cache_bytes=int(cache.nbytes),cache_load_seconds=time.perf_counter()-tick)
        guard();tick=time.perf_counter();a,s,cm,ci=candidate.apply(cache,grid,f['geometry'],f['primitive'],f['mode'],include_intervals=True)
        result['candidate_seconds']=time.perf_counter()-tick;guard();tick=time.perf_counter()
        b,t,dm,di=direct.apply_reference(cache,grid,f['geometry'],f['primitive'],f['mode'],include_intervals=True)
        result['direct_oracle_seconds']=time.perf_counter()-tick;guard()
        assert np.array_equal(a.view(np.uint32),b.view(np.uint32)) and np.array_equal(s,t)
        base=baseline_patch(cache,f['geometry'],(64,128,128));domain=s.astype(bool)
        assert np.array_equal(a[~domain].view(np.uint32),base[~domain].view(np.uint32))
        p=f['intensity_primitives'];aa=intensity.apply(a[None,None],[p])[0,0];bb=independent_intensity(b,p)
        post=float(np.max(np.abs(aa-bb)));assert post<=3e-6
        olda,olds,om=old_production(cache,grid,f['geometry'],f['primitive'],f['mode'])
        oldb,oldt,oim=old_reference(cache,grid,f['geometry'],f['primitive'],f['mode'])
        oldaa=intensity.apply(olda[None,None],[p])[0,0];oldbb=independent_intensity(oldb,p)
        old_error=float(np.max(np.abs(oldaa-oldbb)));assert old_error==f['full_chain_error']==3.814697265625e-6
        fine,coarse=candidate.shapes(grid,f['primitive'],f['mode']);source=cache[tuple(slice(int(v[0]),int(v[0])+n) for v,n in zip(grid['padding'],fine))]
        probes=set(__import__('itertools').product(*[np.linspace(0,len(q)-1,4,dtype=int).tolist() for q in ci['queries']]))
        witness=tuple(diagnostic['failed_maximum_witness']['index_zrc']);lookups=[{int(v):i for i,v in enumerate(axis)} for axis in ci['local']]
        probes.add(tuple(lookups[a][witness[a]] for a in range(3)));probe_rows=[]
        raw_a,raw_meta,raw_intervals=candidate.interpolate(source,coarse,ci['queries'],True)
        raw_b,raw_dmeta,raw_dintervals=direct.interpolate_direct(source,coarse,di['queries'],True)
        assert np.array_equal(raw_a.view(np.uint32),raw_b.view(np.uint32))
        for local in sorted(probes):
            guard();query=tuple(int(ci['queries'][a][local[a]]) for a in range(3));value=exact.point(source,coarse,query);rounded=exact.nearest_float32(value)
            assert int(np.asarray(raw_a[local]).view(np.uint32))==int(np.asarray(rounded).view(np.uint32))
            for bounds in [raw_intervals,raw_dintervals]:assert F(float(bounds[0][local]))<=value<=F(float(bounds[1][local]))
            probe_rows.append(dict(local=list(local),query=list(query),exact=str(value),rounded=float(rounded)))
        assert len(probe_rows)==65 and array_sha(cache)==cache_sha
        result.update(complete=True,all1048576_target_voxels_compared=True,new_image_bitwise_disagreements=0,new_support_binary_disagreements=0,
            candidate=cm,direct_oracle=dm,new_post_intensity_max_error=post,old_full_chain_error_preserved=old_error,
            new_to_old_production_pre_max_error=float(np.max(np.abs(a-olda))),new_to_old_production_post_max_error=float(np.max(np.abs(aa-oldaa))),
            new_to_old_reference_pre_max_error=float(np.max(np.abs(b-oldb))),all65_prespecified_exact_probes_verified=True,
            exact_probes=probe_rows,full35904_qualification_passed=False,all_patient_real_stress_passed=False)
    except Exception as exc:result['errors'].append(dict(type=type(exc).__name__,message=str(exc)));result['traceback']=traceback.format_exc();traceback.print_exc()
    result.update(source_bindings=[entry(p) for p in sorted(sources)]+[entry(out/'frozen_config.json')] if (out/'frozen_config.json').exists() else [entry(p) for p in sorted(sources)],
        resources_before=before,resources_after=guard(),elapsed_seconds=time.perf_counter()-started)
    dump(out/'receipt.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings','exact_probes']},ensure_ascii=False),flush=True)
    return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
