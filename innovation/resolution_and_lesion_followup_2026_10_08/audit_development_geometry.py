"""Geometry only: 76 previously qualified patches; no patient image/GT array access."""
import sys,time,json,itertools
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard,bind
from roundtrip_support import plan_support
SHAPE=np.array([64,128,128])
def neighbors(pos):
    lo=np.floor(pos).astype(int);f=pos-lo
    for bits in itertools.product([0,1],repeat=3):
        b=np.asarray(bits);yield lo+b,float(np.prod(np.where(b,f,1-f)))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    out=HERE/'development_geometry_attempt01';out.mkdir(exist_ok=False)
    prior=ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json'
    qual=ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json'
    rp=read(ROOT/'vs_task_baseline_followup_2026_10_08/READING_PROVENANCE.json')
    b=next(b for b in rp['source_bindings'] if b['path']==prior.relative_to(ROOT).as_posix());bind(b)
    q=read(prior);assert q['complete'] and q['all38_real_batches_verified'] and not q['errors']
    b=next(b for b in q['source_bindings'] if b['path']==qual.relative_to(ROOT).as_posix());bind(b)
    qq=read(qual);assert qq['complete'] and not qq['errors']
    refs={a['kind']:{s['uid']:s for s in a['cache_records']} for a in qq['arms']}
    records=[]
    for series in q['series']:
        paired={}
        for arm in series['arms']:
            full=np.array(refs[arm['kind']][series['uid']]['shape_zrc'])
            for i,(geometry,pivot,primitive) in enumerate(zip(arm['geometry'],arm['pivots_zrc'],arm['stress_primitives'])):
                plan=plan_support(primitive,pivot,series['realized_spacing_zrc_mm'],SHAPE)
                if i in paired:assert paired[i]==plan
                else:paired[i]=plan
                low=np.array(plan['source_low_xyz'])[::-1];high=np.array(plan['source_high_xyz'])[::-1]
                start=np.array(geometry['start']);flip=np.array(geometry['flips'])
                global_low=start+np.where(flip,SHAPE-1-high,low);global_high=start+np.where(flip,SHAPE-1-low,high)
                bbox_fits=bool(np.all(global_low>=0) and np.all(global_high<full));witness=None
                m1=np.array(plan['first_voxel_matrix']);m2=np.array(plan['second_voxel_matrix'])
                for p in itertools.product([0,127],[0,127],[0,63]):
                    inter=m2[:3,:3]@p+m2[:3,3]
                    for j,w2 in neighbors(inter):
                        if w2<=1e-10:continue
                        src=m1[:3,:3]@j+m1[:3,3]
                        for k,w1 in neighbors(src):
                            if w1*w2<=1e-10:continue
                            zrc=k[::-1];global_point=start+np.where(flip,SHAPE-1-zrc,zrc)
                            if np.any(global_point<0) or np.any(global_point>=full):
                                witness=dict(target_xyz=list(p),intermediate_xyz=j.tolist(),source_patch_xyz=k.tolist(),
                                    full_FOV_source_zrc=global_point.tolist(),positive_interpolation_weight=w1*w2);break
                        if witness:break
                    if witness:break
                if bbox_fits:assert witness is None
                records.append(dict(patient=series['patient'],uid=series['uid'],input=arm['kind'],patch=i,full_shape_zrc=full.tolist(),
                    geometry=geometry,pivot_zrc=pivot,primitive=primitive,plan=plan,
                    source_bbox_full_FOV_low_zrc=global_low.tolist(),source_bbox_full_FOV_high_zrc=global_high.tolist(),
                    conservative_source_bbox_fits_full_FOV=bbox_fits,corner_positive_weight_source_outside_full_FOV_witness=witness,
                    source_voxel_ratio=float(np.prod(plan['source_shape_zrc'])/np.prod(SHAPE)),
                    intermediate_voxel_ratio=float(np.prod(plan['intermediate_shape_zrc'])/np.prod(SHAPE))))
    assert len(records)==76 and len(q['series'])==19 and len({s['patient'] for s in q['series']})==11
    r=dict(complete=True,errors=[],records=records,development_patients=11,development_series=19,qualified_previous_batches=38,patch_support_plans=76,
        same_geometry_input_pairs=38,all_input_pair_support_plans_identical=True,
        conservative_source_bbox_fits_count=sum(x['conservative_source_bbox_fits_full_FOV'] for x in records),
        direct_corner_outside_real_FOV_witness_count=sum(x['corner_positive_weight_source_outside_full_FOV_witness'] is not None for x in records),
        no_witness_does_not_prove_full_support=True,source_voxel_ratio_range=[min(x['source_voxel_ratio'] for x in records),max(x['source_voxel_ratio'] for x in records)],
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,new_patient_medical_effects=0,
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'DEVELOPMENT_GEOMETRY_ONLY_PROTOCOL.md',HERE/'roundtrip_support.py',prior,qual]],
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(out/'receipt.json',r);assert time.perf_counter()-started<120 and sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps({k:r[k] for k in ['complete','patch_support_plans','same_geometry_input_pairs','conservative_source_bbox_fits_count','direct_corner_outside_real_FOV_witness_count','source_voxel_ratio_range','elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
