"""Complete immutable fixture/cohort stress of the interval-certified numeric candidate."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,itertools,gc,traceback,collections
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import torch
import certified_resolution as candidate
import direct_interval_reference as direct
import exact_tensor_reference as exact
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,array_sha,QPATH
OLD=ROOT/'resolution_degradation_controls_2026_10_08';sys.path.insert(0,str(OLD))
from resolution_control import baseline_patch
from independent_resolution import coordinate_axes
from qualify_synthetic_and_schedule_v2 import independent_domain
from independent_intensity import apply_reference as intensity_reference
sys.path.insert(0,str(ROOT/'intensity_precision_failure_diagnosis_2026_10_09'))
import intensity_float64_stats as intensity
MODES=['throughplane','inplane','allaxes'];KINDS=['native_reference','raw_pchip'];PATCH=(64,128,128)

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    started=time.perf_counter()
    def guard():
        v=resource_guard();assert time.perf_counter()-started<1800
        assert v['workspace_free_bytes']-2_000_000-3_000_000-2_800_000>=8_000_000_000
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
        assert not torch.cuda.is_initialized();return v
    before=guard();out=HERE/'all_patient_stress_attempt01';out.mkdir(exist_ok=False)
    oldconfigpath=ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01/frozen_config.json';oldconfig=read(oldconfigpath)
    metapath=ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json'
    metadata=read(metapath);assert metadata['complete'] and not metadata['errors']
    series={s['uid']:s for s in metadata['series']};cases=development_cases()
    assert len(cases)==19 and len({c['patient'] for c,row in cases})==11
    refs={a['kind']:{v['uid']:v for v in a['cache_records']} for a in read(QPATH)['arms']}
    failpaths=[OLD/'full_real_pipeline_attempt01/receipt.json',ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01/receipt.json']
    failures=[read(p)['failed_field'] for p in failpaths]
    sources={Path(__file__),HERE/'ALL_PATIENT_STRESS_PROTOCOL.md',HERE/'certified_resolution.py',HERE/'direct_interval_reference.py',HERE/'exact_tensor_reference.py',
        Path(intensity.__file__),OLD/'independent_intensity.py',OLD/'resolution_control.py',OLD/'independent_resolution.py',OLD/'qualify_synthetic_and_schedule_v2.py',
        QPATH,oldconfigpath,metapath,*failpaths,ROOT/'experiments/mc_rc_3d_19series_common_init_2026_10_07.py'}
    for p in [HERE/'synthetic_attempt01/receipt.json',HERE/'direct_oracle_synthetic_attempt01/receipt.json',HERE/'failed_full_field_regression_attempt01/receipt.json']:
        q=read(p);assert q['complete'] and not q['errors'];sources.add(p)
        for b in q['source_bindings']:bind(b)
    for c,row in cases:
        for rel in [c['header_file'],c['mr_zip_file'],row['observed_package']]:sources.add(bind(next(b for b in oldconfig['source_bindings'] if b['path']==rel)))
    bind(next(b for b in oldconfig['source_bindings'] if b['path']==metapath.relative_to(ROOT).as_posix()))
    dump(out/'frozen_config.json',dict(expected_fields=542,full_resolution_synthetic_fields=270,full_intensity_synthetic_fields=40,real_fields=228,
        old_failed_regressions=3,v2_failed_regressions=1,image_gate=3e-6,coordinate_gate=3e-12,binary_gate=0,
        image_bitwise_disagreement_gate=0,wall_seconds=1800,source_bindings=[entry(p) for p in sorted(sources)]))
    r=dict(complete=False,status='running',errors=[],fields=[],MRI_input_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,new_production_selected=False,training_ready=False,
        full35904_qualification_passed=False,publication_claim_confirmed=False,goal_status='active',exact_probe_points=0,direct_extreme_exact_points=0,
        cache_records=[],case_index=[dict(patient=c['patient'],uid=c['uid']) for c,row in cases])
    costs=collections.Counter();maxima=collections.Counter();counts=collections.Counter();current=None
    def save():
        r.update(elapsed_seconds=time.perf_counter()-started,cost_seconds=dict(costs),max_errors=dict(maxima),scope_counts=dict(counts))
        p=out/'receipt.json.tmp';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');p.replace(out/'receipt.json')
    def compare(a,b,s,t,domain,ip,identity,meta=None):
        nonlocal current
        current=dict(identity=identity);guard();tick=time.perf_counter()
        aa=intensity.apply(a[None,None],[ip])[0,0];bb=intensity_reference(b,ip)
        isolated=intensity_reference(a,ip);shared=intensity.apply(b[None,None],[ip])[0,0]
        errors=dict(pre_intensity_error=float(np.max(np.abs(a-b))),shared_post_intensity_error=float(np.max(np.abs(aa-shared))),
            isolated_intensity_error=float(np.max(np.abs(aa-isolated))),full_chain_error=float(np.max(np.abs(aa-bb))),
            support_error=float(np.max(np.abs(s-t))))
        binary=int(np.count_nonzero((s>=1-1e-9)!=(t>=1-1e-9)));bits=int(np.count_nonzero(a.view(np.uint32)!=b.view(np.uint32)))
        current.update(errors=errors,image_bitwise_disagreements=bits,binary_disagreements=binary,intensity_primitive=ip)
        assert all(v<=3e-6 for v in errors.values()),current
        assert binary==bits==0 and np.array_equal(s>=1-1e-9,domain) and np.array_equal(t>=1-1e-9,domain)
        for k,v in errors.items():maxima[k]=max(maxima[k],v)
        costs['intensity_and_comparisons']+=time.perf_counter()-tick
        record=dict(identity=identity,**errors,image_bitwise_disagreements=bits,binary_disagreements=binary,target_voxels=int(a.size),valid_voxels=int(domain.sum()))
        if meta:record.update(meta)
        r['fields'].append(record);counts[identity['scope']]+=1;save()
    def resolution_field(cache,grid,geometry,primitive,mode,patch,ip,identity):
        nonlocal current
        current=dict(identity=identity,geometry=geometry,primitive=primitive);guard();tick=time.perf_counter()
        a,s,cm,ci=candidate.apply(cache,grid,geometry,primitive,mode,patch,include_intervals=True)
        costs['candidate']+=time.perf_counter()-tick;guard();tick=time.perf_counter()
        b,t,dm,di=direct.apply_reference(cache,grid,geometry,primitive,mode,patch,include_intervals=True)
        costs['direct_oracle']+=time.perf_counter()-tick;guard();tick=time.perf_counter()
        domain=independent_domain(grid,geometry,patch);base=baseline_patch(cache,geometry,patch)
        assert np.array_equal(a[~domain].view(np.uint32),base[~domain].view(np.uint32))
        assert np.array_equal(b[~domain].view(np.uint32),base[~domain].view(np.uint32))
        if not primitive['enabled']:assert np.array_equal(a.view(np.uint32),base.view(np.uint32))
        fine,coarse=candidate.shapes(grid,primitive,mode);assert coarse==exact.dimensions(fine,primitive['scale'],primitive['enabled'],mode)
        coordinate_error=coordinate_axes(fine,coarse)[2];assert coordinate_error<=3e-12
        for n,m in zip(fine,coarse):
            for den,num,length in [(max(1,m-1),np.arange(m,dtype=np.int64)*(n-1),n),(max(1,n-1),np.arange(n,dtype=np.int64)*(m-1),m)]:
                lo,hi,rem,d=candidate.rational_axis(num,den,length)
                for k in range(len(lo)):assert F(int(lo[k]))+F(int(rem[k]),d)==F(int(num[k]),den)
        probes=0
        if primitive['enabled'] and domain.any():
            source=cache[tuple(slice(int(p[0]),int(p[0])+n) for p,n in zip(grid['padding'],fine))]
            for local in set(itertools.product(*[np.linspace(0,len(q)-1,min(4,len(q)),dtype=int).tolist() for q in ci['queries']])):
                query=tuple(int(ci['queries'][a][local[a]]) for a in range(3));value=exact.point(source,coarse,query);rounded=exact.nearest_float32(value)
                for bounds in [ci['bounds'],di['bounds']]:assert F(float(bounds[0][local]))<=value<=F(float(bounds[1][local]))
                target=tuple(int(ci['local'][a][local[a]]) for a in range(3));expected=(np.array([rounded],np.float32)*geometry['intensity_scale']+geometry['intensity_shift'])[0]
                assert int(np.asarray(a[target]).view(np.uint32))==int(np.asarray(expected).view(np.uint32));probes+=1
        costs['coordinate_padding_and_fraction_checks']+=time.perf_counter()-tick;r['exact_probe_points']+=probes
        maxima['coordinate_error']=max(maxima['coordinate_error'],coordinate_error)
        compare(a,b,s,t,domain,ip,identity,dict(coordinate_error=coordinate_error,exact_probes=probes,
            candidate_fallback=cm['exact_fallback_voxels'],direct_fallback=dm['direct_exact_fallback_voxels'],direct_source_terms=dm['direct_source_terms'],
            candidate_interval_width=cm['max_interval_width'],direct_interval_width=dm.get('max_direct_interval_width',0.)))
    save()
    try:
        tiny=np.array([0.,1e-40,-1e-40,1e-20,-1e-20,1e20,-1e20,1e30,-1e30],dtype=np.float32).reshape(1,3,3)
        raw,dm,(lo,hi)=direct.interpolate_direct(tiny,(1,2,2),[np.arange(n) for n in tiny.shape],True)
        for position in np.ndindex(*tiny.shape):
            value=exact.point(tiny,(1,2,2),position);expected=exact.nearest_float32(value)
            assert F(float(lo[position]))<=value<=F(float(hi[position]))
            assert int(np.asarray(raw[position]).view(np.uint32))==int(np.asarray(expected).view(np.uint32));r['direct_extreme_exact_points']+=1
        fixtures=[np.full((7,11,13),2.5,np.float32),np.array([[[3.]]],np.float32)];rng=np.random.default_rng(2026100828)
        fixtures.extend([rng.normal(size=(9,17,23)).astype(np.float32),rng.normal(size=PATCH).astype(np.float32)])
        padded=np.zeros(PATCH,np.float32);padded[12:52]=rng.normal(size=(40,128,128)).astype(np.float32);padded[32,50,50]=12.;padded[32,50,51]=-5.;fixtures.append(padded)
        for fi,image in enumerate(fixtures):
            before_sha=array_sha(image);support=np.ones(image.shape,np.float64);domain=np.ones(image.shape,bool)
            for gamma,bias,noise in itertools.product([False,True],repeat=3):
                ip=dict(gamma_enabled=gamma,gamma=.7 if fi%2 else 1.5,bias_enabled=bias,bias_coefficients=[-.3,.21,.3],noise_enabled=noise,noise_std=.08,noise_seed=1701+fi)
                compare(image,image,support,support,domain,ip,dict(scope='intensity_synthetic',fixture=fi,gamma=gamma,bias=bias,noise=noise));assert array_sha(image)==before_sha
        del fixtures,image,padded;gc.collect()
        specifications=[((1,1,1),(5,9,11)),((1,17,23),(5,9,11)),((9,17,23),(5,9,11)),((17,33,35),(5,9,11)),((52,181,193),PATCH)]
        ip=dict(gamma_enabled=False,bias_enabled=False,noise_enabled=False)
        for si,(fine,patch) in enumerate(specifications):
            padding=[(max(0,k-n)//2,(max(0,k-n)+1)//2) for n,k in zip(fine,patch)]
            grid=dict(unpadded_shape_zrc=list(fine),padding=padding,realized_spacing_zrc_mm=[.7,.49,.51])
            z,u,v=np.meshgrid(*[np.arange(n,dtype=np.float64) for n in fine],indexing='ij')
            textures={'constant':np.full(fine,2.5,np.float32),'linear':(z*.011+u*.004-v*.006).astype(np.float32),'texture':(np.sin(z*1.23)+np.cos(u*.73)*.8+np.sin(v*.37)*.6).astype(np.float32)}
            for name,values in textures.items():
                cache=np.pad(values,padding).astype(np.float32);extent=np.asarray(cache.shape)-patch
                for gi,(start,flips) in enumerate([(np.zeros(3,int),[False]*3),(extent//2,[True,False,True]),(extent,[True]*3)]):
                    geometry=dict(start=start.tolist(),flips=flips,intensity_scale=1.03,intensity_shift=-.073)
                    for enabled in [False,True]:
                        primitive=dict(enabled=enabled,scale=.913+gi*.091,degrees_xyz=[9.,-7.,3.])
                        for mode in MODES:resolution_field(cache,grid,geometry,primitive,mode,patch,ip,dict(scope='resolution_synthetic',fixture=si,texture=name,geometry=gi,enabled=enabled,mode=mode))
                del cache;gc.collect()
            print(json.dumps(dict(synthetic_specification=si,fields_completed=len(r['fields']),elapsed_seconds=time.perf_counter()-started)),flush=True)
        del textures,z,u,v,values;gc.collect()
        for ci,(c,row) in enumerate(cases):
            grid=lattice(c)
            for kind in KINDS:
                guard();tick=time.perf_counter();normal,stats=source_image(c,row,kind);cache=physical_mr(normal,grid);del normal
                costs['MRI_load']+=time.perf_counter()-tick;r['MRI_input_arrays_loaded']+=1;cache_sha=array_sha(cache)
                assert cache_sha==refs[kind][c['uid']]['input_sha256'];r['cache_records'].append(dict(case=ci,kind=kind,input_sha256=cache_sha,cache_bytes=int(cache.nbytes)))
                arm=next(a for a in series[c['uid']]['arms'] if a['kind']==kind)
                base=np.stack([baseline_patch(cache,g,PATCH) for g in arm['geometry']])[:,None];assert array_sha(base)==arm['base_input_sha256']
                for pi,geometry in enumerate(arm['geometry']):
                    for mode in MODES:resolution_field(cache,grid,geometry,arm['stress_primitives'][pi],mode,PATCH,arm['intensity_primitives'][pi],dict(scope='real_stress',case=ci,kind=kind,patch=pi,mode=mode))
                for fi,f in enumerate(failures):
                    if ci==f['case'] and kind==f['kind']:
                        for mode in (MODES if fi==0 else [f['mode']]):
                            resolution_field(cache,grid,f['geometry'],f['primitive'],mode,PATCH,f['intensity_primitives'],dict(scope='old_failed_regression' if fi==0 else 'v2_failed_regression',case=ci,kind=kind,step=f['step'],patch=f['patch'],mode=mode))
                assert array_sha(cache)==cache_sha;del cache,base;gc.collect()
            print(json.dumps(dict(series_completed=ci+1,expected_series=19,fields_completed=len(r['fields']),max_errors=dict(maxima),elapsed_seconds=time.perf_counter()-started)),flush=True)
        assert len(r['fields'])==542 and r['MRI_input_arrays_loaded']==38 and r['direct_extreme_exact_points']==9
        assert counts==dict(intensity_synthetic=40,resolution_synthetic=270,real_stress=228,old_failed_regression=3,v2_failed_regression=1)
        for p in sources:bind(next(b for b in read(out/'frozen_config.json')['source_bindings'] if b['path']==p.relative_to(ROOT).as_posix()))
        r.update(complete=True,status='completed',all542_full_fields_verified=True,all11_patients19_series_two_inputs_three_modes_verified=True,
            source_bindings=[entry(p) for p in sorted(sources)]+[entry(out/'frozen_config.json')])
    except Exception as exc:
        r.update(status='failed',failed_field=current,traceback=traceback.format_exc());r['errors'].append(dict(type=type(exc).__name__,message=str(exc)));traceback.print_exc()
    r.update(resources_before=before,resources_after=resource_guard());save()
    print(json.dumps({k:v for k,v in r.items() if k not in ['fields','source_bindings','case_index','cache_records','traceback']},ensure_ascii=False),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
