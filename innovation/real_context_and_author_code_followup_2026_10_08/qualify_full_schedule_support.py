"""5984 original candidate crop geometries; labels and geometry only, no MRI or task model."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,json,time,gc,gzip,hashlib,itertools,traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,sha,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,physical_label,read_reference_label,batch_rng,array_sha,QPATH
sys.path.insert(0,str(ROOT/'full_support_oracle_and_vinn_followup_2026_10_08'))
from diagnose_development_label_support import domain_support,overlap
from verify_full_geometry_support_v2 import independently_physical_matrices,stats
from roundtrip_support import plan_support
from spatial_transform import primitives,pivots
PATCH=np.array([64,128,128]);STEPS=2992

def sample_geometry(target,fg,step):
    rng=batch_rng(step);geometries=[];labels=[]
    for force in [True,False]:
        center=fg[int(rng.integers(len(fg)))] if force else np.array([rng.integers(n) for n in target.shape])
        start=np.clip(center-PATCH//2,0,np.array(target.shape)-PATCH).astype(int)
        p=target[tuple(slice(int(a),int(a)+int(n)) for a,n in zip(start,PATCH))].copy();flips=[]
        for axis in range(3):
            flip=bool(rng.random()<.5);flips.append(flip)
            if flip:p=np.flip(p,axis)
        scale=float(rng.uniform(.9,1.1));shift=float(rng.uniform(-.1,.1))
        labels.append(np.ascontiguousarray(p));geometries.append(dict(forced_foreground=force,center=center.tolist(),start=start.tolist(),flips=flips,
            intensity_scale=scale,intensity_shift=shift,target_foreground=int(p.sum())))
    return geometries,labels

def identity_support(geometry,grid):
    axes=[];axis_independent=[];pad=np.array(grid['padding'])[:,0];high=pad+np.array(grid['unpadded_shape_zrc'])-1
    for axis,n in enumerate(PATCH):
        local=np.arange(n);positions=geometry['start'][axis]+(n-1-local if geometry['flips'][axis] else local)
        axes.append((positions>=pad[axis])&(positions<=high[axis]))
        a=pad[axis]-geometry['start'][axis];b=high[axis]-geometry['start'][axis]
        if geometry['flips'][axis]:a,b=n-1-b,n-1-a
        axis_independent.append((local>=a)&(local<=b))
    result=(axes[0][:,None,None]&axes[1][None,:,None]&axes[2][None,None,:]).astype(np.float64)
    other=np.minimum(np.minimum(axis_independent[0][:,None,None],axis_independent[1][None,:,None]),axis_independent[2][None,None,:]).astype(np.float64)
    assert np.array_equal(result,other);return result

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);resource_guard();started=time.perf_counter()
    out=HERE/'full_schedule_attempt01';out.mkdir(exist_ok=False)
    oldpath=ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json'
    fullsupport=read(ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/full_support_attempt02/receipt.json')
    bind(next(b for b in fullsupport['source_bindings'] if b['path']==oldpath.relative_to(ROOT).as_posix()))
    previous=read(oldpath);assert previous['complete'] and not previous['errors'];oldseries={s['uid']:s for s in previous['series']}
    qualified=read(QPATH);assert qualified['complete'] and not qualified['errors']
    bind(next(b for b in previous['source_bindings'] if b['path']==QPATH.relative_to(ROOT).as_posix()))
    refs={s['uid']:s for a in qualified['arms'] if a['kind']=='native_reference' for s in a['cache_records']}
    parent=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
    current=ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01/frozen_config.json';immutable=read(current)
    parentconfig=parent/'frozen_config.json';config=read(parentconfig);schedulefile=parent/config['schedule_file']
    assert sha(schedulefile)==config['schedule_file_sha256']
    schedule=np.load(schedulefile,allow_pickle=False)[:STEPS];assert schedule.shape==(STEPS,2) and array_sha(schedule)==immutable['schedule_prefix_sha256']
    assert all(int(np.count_nonzero(schedule[:,0]==i))==272 for i in range(11))
    cases=development_cases();assert len(cases)==19
    assert [c['uid'] for c,_ in cases]==[c['uid'] for c in config['series']]
    sources={Path(__file__),HERE/'FULL_SCHEDULE_SUPPORT_PROTOCOL.md',HERE/'real_context_attempt02/receipt.json',oldpath,QPATH,current,parentconfig,schedulefile,
        ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/full_support_attempt02/receipt.json',
        ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/diagnose_development_label_support.py',
        ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/verify_full_geometry_support_v2.py',
        ROOT/'resolution_and_lesion_followup_2026_10_08/roundtrip_support.py',ROOT/'spatial_adaptation_matched_2026_10_08/spatial_transform.py',
        ROOT/'experiments/mc_rc_3d_19series_common_init_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py'}
    frozen=dict(created_utc=datetime.now(timezone.utc).isoformat(),steps=STEPS,geometry_patches=2*STEPS,schedule_prefix_sha256=array_sha(schedule),
        enabled_probability=.3,domain='unpadded_resampled_image',support_threshold=1-1e-9,coordinate_gate=3e-12,support_numeric_gate=3e-6,
        max_seconds=5400,stage_saved_bound_bytes=5_000_000,CPU_threads=1,source_bindings=[entry(p) for p in sorted(sources)])
    dump(out/'frozen_config.json',frozen)
    receipt=dict(complete=False,status='running',errors=[],series=[],geometry_patches_completed=0,GT_arrays_loaded=0,MRI_arrays_loaded=0,
        model_arrays_loaded=0,patient_neural_forwards=0,training_updates=0,validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        training_crop_and_pivot_GT_derived=True,support_generation_uses_additional_GT_beyond_frozen_training_geometry=False,
        fullschedule_actual_medical_effects=0,publication_claim_confirmed=False,goal_status='active',source_bindings=frozen['source_bindings'])
    def save():
        receipt['elapsed_seconds']=time.perf_counter()-started
        tmp=out/'receipt.json.tmp';tmp.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(out/'receipt.json')
    def guard():
        r=resource_guard();assert time.perf_counter()-started<5400 and not torch.cuda.is_initialized()
        assert torch.get_num_threads()==torch.get_num_interop_threads()==1
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
        return r
    save();journal=out/'geometry.journal.jsonl.gz';keys=set();active=0;foreground_missing=0;foreground_exposures=0;fully=0;max_error=0.;max_coordinate=0.
    try:
        with journal.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as log:
            for ci,(c,_) in enumerate(cases):
                guard();old=oldseries[c['uid']];grid=lattice(c);path=ROOT/c['label_file'];sources.add(path)
                bind(next(b for b in previous['source_bindings'] if b['path']==c['label_file']))
                target=physical_label(read_reference_label(c),grid);receipt['GT_arrays_loaded']+=1
                assert array_sha(target)==old['physical_label_sha256']==refs[c['uid']]['label_sha256']
                fg=np.argwhere(target>0);assert len(fg)
                geom,y=sample_geometry(target,fg,19998+ci+1);oldarm=next(a for a in old['arms'] if a['kind']=='native_reference')
                assert geom==oldarm['geometry'] and array_sha(np.stack(y)[:,None])==oldarm['mother_label_sha256'];del y
                selected=np.flatnonzero(schedule[:,1]==ci);sr=dict(patient=c['patient'],uid=c['uid'],steps_expected=len(selected),steps_completed=0,patches=0,active=0,FG_incomplete_voxels=0,FG_exposure_voxels=0)
                for ix in selected:
                    step=int(ix)+1;guard();geometries,labels=sample_geometry(target,fg,19998+step);pivot=pivots(geometries,PATCH);prs=primitives(step)
                    mother=array_sha(np.stack(labels)[:,None])
                    for pi,(geometry,label,p,primitive) in enumerate(zip(geometries,labels,pivot,prs)):
                        plan=plan_support(primitive,p,grid['realized_spacing_zrc_mm'],PATCH);row=dict(plan=plan,geometry=geometry)
                        at=time.perf_counter();coordinate=0.;error=0.;binary=0
                        if plan['active']:
                            matrices=independently_physical_matrices(primitive,p,grid['realized_spacing_zrc_mm']);coordinates=[]
                            for (a,b),production in zip(matrices,[plan['first_voxel_matrix'],plan['second_voxel_matrix']]):
                                m=np.array(production)
                                for corner in itertools.product([0,127],[0,127],[0,63]):coordinates.append(float(np.max(np.abs(a@corner+b-(m[:3,:3]@corner+m[:3,3])))))
                            coordinate=max(coordinates);assert coordinate<=3e-12
                            mask,error,binary=domain_support(row,grid,matrices);active+=1;sr['active']+=1
                        else:
                            assert all(np.max(np.abs(np.array(m)-np.eye(4)))<=3e-12 for m in [plan['first_voxel_matrix'],plan['second_voxel_matrix']])
                            mask=identity_support(geometry,grid)
                        stat=stats(mask);ov=overlap(mask,label.astype(bool));key=(step,pi);assert key not in keys;keys.add(key)
                        foreground_missing+=ov['foreground']['incomplete_support_voxels'];foreground_exposures+=ov['foreground']['voxels'];fully+=int(stat['fully_supported_fraction']==1.)
                        max_error=max(max_error,error);max_coordinate=max(max_coordinate,coordinate)
                        sr['FG_incomplete_voxels']+=ov['foreground']['incomplete_support_voxels'];sr['FG_exposure_voxels']+=ov['foreground']['voxels'];sr['patches']+=1
                        r=dict(step=step,patch=pi,patient=c['patient'],uid=c['uid'],geometry=geometry,pivot_zrc=p,primitive=primitive,mother_label_sha256=mother,
                            target_label_sha256=array_sha(label),support_stats=stat,overlap=ov,coordinate_max_error=coordinate,support_max_error=error,binary_disagreements=binary,
                            all_target_voxels_verified=True,active=plan['active'],elapsed_seconds=time.perf_counter()-at)
                        log.write((json.dumps(r,separators=(',',':'))+'\n').encode('utf-8'));del mask;gc.collect()
                        receipt['geometry_patches_completed']+=1
                    sr['steps_completed']+=1
                    if receipt['geometry_patches_completed']%100==0:
                        log.flush();raw.flush();receipt.update(active_patches_completed=active,FG_incomplete_exposure_voxels_so_far=foreground_missing,
                            FG_exposure_voxels_so_far=foreground_exposures,series_in_progress=sr);save()
                        print(json.dumps(dict(geometry_patches_completed=receipt['geometry_patches_completed'],active=active,FG_incomplete=foreground_missing,elapsed_seconds=time.perf_counter()-started)),flush=True)
                    del labels
                assert sr['steps_completed']==sr['steps_expected'];receipt['series'].append(sr);receipt.pop('series_in_progress',None);save();del target,fg;gc.collect()
        assert keys==set(itertools.product(range(1,STEPS+1),range(2))) and receipt['geometry_patches_completed']==5984
        assert len(receipt['series'])==19 and len({s['patient'] for s in receipt['series']})==11
        assert all(sum(s['steps_completed'] for s in receipt['series'] if s['patient']==p)==272 for p in config['patient_ids'])
        receipt.update(complete=True,status='completed',active_patches_completed=active,inactive_identity_patches=5984-active,patches_entirely_supported=fully,
            FG_incomplete_exposure_voxels=foreground_missing,FG_exposure_voxels=foreground_exposures,max_support_error=max_error,max_coordinate_error=max_coordinate,
            all5984_geometry_targets_verified=True,geometry_target_exposure_voxels=5984*1048576,old38_geometry_and_label_batches_replayed=True,
            journal_path=journal.relative_to(ROOT).as_posix(),journal_sha256=sha(journal),journal_bytes=journal.stat().st_size,
            frozen_config_sha256=sha(out/'frozen_config.json'),source_bindings=[entry(p) for p in sorted(sources)],
            strict_support_qualification_not_task_output_safety=True,independent_journal_audit_completed=False)
    except Exception as e:receipt.update(status='failed');receipt['errors'].append(type(e).__name__+': '+str(e));receipt['traceback']=traceback.format_exc();traceback.print_exc()
    receipt['resources']=guard();save();print(json.dumps({k:receipt.get(k) for k in ['complete','status','errors','geometry_patches_completed','active_patches_completed','FG_incomplete_exposure_voxels','elapsed_seconds']}),flush=True)
    return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
