"""Independent full synthetic fields and all three controls across the frozen 5984 geometries."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,gzip,itertools,collections,hashlib,gc
from pathlib import Path
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,array_sha
from resolution_control import plan,apply,baseline_patch
from independent_resolution import independent_shapes,coordinate_axes,independent_apply
MODES=['throughplane','inplane','allaxes']

def independent_domain(grid,geometry,patch):
    axes=[]
    for a,n in enumerate(patch):
        low=int(grid['padding'][a][0]);high=low+int(grid['unpadded_shape_zrc'][a])
        p=int(geometry['start'][a])+np.arange(n)
        if geometry['flips'][a]:p=p[::-1]
        axes.append((p>=low)&(p<high))
    return axes[0][:,None,None]&axes[1][None,:,None]&axes[2][None,None,:]

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);torch.set_num_interop_threads(1)
    resource_guard();started=time.perf_counter();out=HERE/'geometry_and_synthetic_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],synthetic_fields=[],synthetic_fields_completed=0,metadata_geometry_controls_completed=0,
           MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,patient_neural_forwards=0,training_updates=0,
           validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
           new_distinct_primary_maintexts_completed=0,new_patient_medical_effects=0,publication_claim_confirmed=False,goal_status='active')
    def guard():
        resource_guard();assert time.perf_counter()-started<900 and not torch.cuda.is_initialized()
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    def save():
        p=out/'receipt.json.tmp';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');p.replace(out/'receipt.json')
    source=[Path(__file__),HERE/'PROTOCOL.md',HERE/'resolution_control.py',HERE/'independent_resolution.py']
    previous=ROOT/'real_context_and_author_code_followup_2026_10_08'
    index=previous/'APPEND_FULL_SCHEDULE_INDEX.json';proof=previous/'APPEND_FULL_SCHEDULE_PROOF.json'
    assert sha(index)=='a527acc5eb9dc30348a53ac40e14aa89a3469f6df9a718aa325cbeeea9463fce'
    assert sha(proof)=='c624330afcd33afa681533351914588045ebc406b6143598ae3c9917751ab1eb'
    frozen=read(index);assert frozen['complete'] and frozen['cumulative_frozen_evidence_files']==6324
    auditpath=previous/'full_schedule_audit_attempt01/receipt.json';audit=read(auditpath)
    assert audit['complete'] and audit['all5984_journal_rows_verified'] and audit['all2992_original_sample_batch_geometry_and_mother_labels_matched']
    for b in audit['source_bindings']:bind(b)
    fullpath=previous/'full_schedule_attempt01/receipt.json';full=read(fullpath);journal=ROOT/full['journal_path']
    assert full['complete'] and sha(journal)==full['journal_sha256']
    source.extend([index,proof,auditpath,fullpath,journal])
    dump(out/'frozen_config.json',dict(modes=MODES,primitive_distribution='original_enabled_and_scale_to_factor_1.1_1.5',
         image_gate=3e-6,coordinate_gate=3e-12,support_binary_gate=0,inherited_domain_support_threshold=1-1e-9,
         wall_seconds=900,source_bindings=[entry(p) for p in source]))
    try:
        # These are nonmedical arrays; both padding and singleton dimensions are explicit.
        specifications=[((1,1,1),(5,9,11)),((1,17,23),(5,9,11)),((9,17,23),(5,9,11)),
                        ((17,33,35),(5,9,11)),((52,181,193),(64,128,128))]
        max_image=0.;max_support=0.;max_coordinate=0.;field_voxels=0
        for si,(fine,patch) in enumerate(specifications):
            padding=[(max(0,k-n)//2,(max(0,k-n)+1)//2) for n,k in zip(fine,patch)]
            grid=dict(unpadded_shape_zrc=list(fine),padding=padding,realized_spacing_zrc_mm=[.7,.49,.51])
            z,a,b=np.meshgrid(*[np.arange(n,dtype=np.float64) for n in fine],indexing='ij')
            sources={'constant':np.full(fine,2.5,np.float32),
                     'linear':(z*.011+a*.004-b*.006).astype(np.float32),
                     'texture':(np.sin(z*1.23)+np.cos(a*.73)*.8+np.sin(b*.37)*.6).astype(np.float32)}
            for kind,values in sources.items():
                cache=np.pad(values,padding,mode='constant',constant_values=0).astype(np.float32)
                extent=np.asarray(cache.shape)-patch
                for gi,(start,flips) in enumerate([(np.zeros(3,int),[False]*3),(extent//2,[True,False,True]),(extent,[True]*3)]):
                    geometry=dict(start=start.tolist(),flips=flips,intensity_scale=1.03,intensity_shift=-.073)
                    for enabled in [False,True]:
                        primitive=dict(enabled=enabled,scale=.913+gi*.091,degrees_xyz=[9.,-7.,3.])
                        for mode in MODES:
                            guard();actual,support,meta=apply(cache,grid,geometry,primitive,mode,patch)
                            expected,other,imeta=independent_apply(cache,grid,geometry,primitive,mode,patch)
                            domain=independent_domain(grid,geometry,patch);baseline=baseline_patch(cache,geometry,patch)
                            ie=float(np.max(np.abs(actual-expected)));se=float(np.max(np.abs(support-other)))
                            binary=int(np.count_nonzero((support>=1-1e-9)!=(other>=1-1e-9)))
                            assert ie<=3e-6 and se<=3e-6 and binary==0 and imeta['coordinate_max_error']<=3e-12
                            assert np.array_equal(support>=1-1e-9,domain) and np.array_equal(other>=1-1e-9,domain)
                            assert np.array_equal(actual[~domain],baseline[~domain])
                            if not enabled:assert np.array_equal(actual,baseline)
                            if kind=='constant':assert np.max(np.abs(actual-baseline))<=3e-6
                            if kind=='linear':assert np.max(np.abs(actual-baseline))<=3e-6
                            record=dict(specification=si,kind=kind,geometry=gi,enabled=enabled,mode=mode,
                                        target_voxels=int(actual.size),validity_voxels=int(domain.sum()),
                                        image_max_error=ie,support_max_error=se,binary_disagreements=binary,
                                        coordinate_max_error=imeta['coordinate_max_error'],
                                        changed_voxels=int(np.count_nonzero(actual!=baseline)),
                                        inherited_padding_bitwise_unchanged=True,source=meta)
                            r['synthetic_fields'].append(record);r['synthetic_fields_completed']+=1
                            field_voxels+=actual.size;max_image=max(max_image,ie);max_support=max(max_support,se);max_coordinate=max(max_coordinate,imeta['coordinate_max_error'])
                    del cache;gc.collect()
            print(json.dumps(dict(synthetic_specification=si,fields_completed=r['synthetic_fields_completed'])),flush=True);save()
        assert r['synthetic_fields_completed']==270
        assert any(x['enabled'] and x['kind']=='texture' and x['changed_voxels']>0 for x in r['synthetic_fields'])
        cases=development_cases();assert len(cases)==19
        grids={c['uid']:lattice(c) for c,_ in cases}
        for c,_ in cases:source.append(ROOT/c['header_file'])
        with gzip.open(journal,'rt',encoding='utf-8') as f:rows=[json.loads(x) for x in f]
        assert len(rows)==5984
        totals={mode:collections.Counter() for mode in MODES};patients={mode:collections.defaultdict(collections.Counter) for mode in MODES}
        series={mode:collections.defaultdict(collections.Counter) for mode in MODES};axis_checks={};decisions=[]
        for row in sorted(rows,key=lambda x:(x['step'],x['patch'])):
            guard();g=grids[row['uid']];fine=tuple(g['unpadded_shape_zrc']);geometry=row['geometry'];primitive=row['primitive']
            baseline_valid=1
            for a,k in enumerate((64,128,128)):
                lo=geometry['start'][a]-g['padding'][a][0]
                baseline_valid*=max(0,min(lo+k,fine[a])-max(lo,0))
            for mode in MODES:
                p=plan(g,primitive,mode);n,m=independent_shapes(g,primitive,mode)
                assert list(m)==p['coarse_shape_zrc'] and list(n)==p['fine_shape_zrc']
                for a,(N,M) in enumerate(zip(n,m)):
                    key=(N,M)
                    if key not in axis_checks:
                        _,_,error=coordinate_axes([N],[M]);assert error<=3e-12;axis_checks[key]=error
                enabled=bool(primitive['enabled']);changed=bool(enabled and n!=m)
                for v in [totals[mode],patients[mode][row['patient']],series[mode][row['uid']]]:
                    v['patches']+=1;v['enabled']+=int(enabled);v['effective_degradation']+=int(changed)
                    v['valid_target_exposure_voxels']+=baseline_valid;v['inherited_padding_exposure_voxels']+=1048576-baseline_valid
                decisions.append(dict(step=row['step'],patch=row['patch'],uid=row['uid'],patient=row['patient'],mode=mode,
                    enabled=enabled,effective_degradation=changed,coarse_shape_zrc=list(m),requested_factor=p['requested_factor'],
                    mother_valid_voxels=baseline_valid,no_new_missing_source_stencils=True,
                    original_target_label_sha256=row['target_label_sha256']))
                r['metadata_geometry_controls_completed']+=1
        assert r['metadata_geometry_controls_completed']==17952
        for mode in MODES:
            assert totals[mode]['patches']==5984 and totals[mode]['enabled']==1785
            assert len(patients[mode])==11 and len(series[mode])==19
            assert all(x['patches']==544 and x['effective_degradation']>0 for x in patients[mode].values())
            assert all(x['effective_degradation']>0 for x in series[mode].values())
        metadata_journal=out/'control_decisions.jsonl.gz'
        with metadata_journal.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
            for row in decisions:f.write((json.dumps(row,separators=(',',':'))+'\n').encode('utf-8'))
        r.update(complete=True,all270_synthetic_fields_verified=True,synthetic_target_voxels=int(field_voxels),
            all17952_schedule_control_records_verified=True,all5984_original_geometry_rows_reused=True,
            source_stencil_bounds_certified_by_exact_integer_remainders=True,numeric_axis_plans_checked=len(axis_checks),
            max_image_error=max_image,max_support_error=max_support,max_coordinate_error=max(max_coordinate,max(axis_checks.values())),
            totals={k:dict(v) for k,v in totals.items()},patients={k:{p:dict(v) for p,v in x.items()} for k,x in patients.items()},
            series={k:{p:dict(v) for p,v in x.items()} for k,x in series.items()},metadata_journal=entry(metadata_journal),
            actual5984_MRI_fields_not_replayed=True,real_stress_MRI_qualification_completed=False,training_ready=False,
            source_bindings=[entry(p) for p in sorted(set(source))])
    except Exception as exc:
        import traceback
        r['errors'].append(type(exc).__name__+': '+str(exc));r['traceback']=traceback.format_exc();traceback.print_exc()
    r.update(elapsed_seconds=time.perf_counter()-started,CUDA_initialized=torch.cuda.is_initialized());save();guard()
    print(json.dumps({k:r.get(k) for k in ['complete','errors','synthetic_fields_completed','metadata_geometry_controls_completed','max_image_error','max_support_error','max_coordinate_error','elapsed_seconds']}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
