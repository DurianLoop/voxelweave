"""All development-series cost preparation using synthetic masks, without MR/GT values."""
import json, math, sys, time, traceback
from datetime import datetime, timezone
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,sha,resource_guard,fixed_cases,lattice,physical_mr,tile_plan,PATCH,torch,np
from mc_rc_true_native_reference_v2_2026_10_07 import DEVELOPERS
OUT=ROOT/'experiments/mc_rc_3d_local_edit_cache_2026_10_07/development_metadata_cost_attempt01.json'

def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not OUT.exists();started=time.perf_counter()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        real_MRI_arrays_loaded=0,GT_arrays_loaded=0,actual_model_forwards=0,actual_training_updates=0,actual_GPU_updates=0,
        validation_pixel_arrays_loaded=0,confirmation_patients_opened=False,scientific_confirmation_patients=0,
        publication_claim_confirmed=False,action_benefit_measured=False,synthetic_source_mask_support_only=True,series=[])
    def save():OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-started<=600
        r=resource_guard();assert not torch.cuda.is_initialized();return r
    save()
    try:
        torch.set_num_threads(4);guard()
        cases=[x for x in fixed_cases() if x[0]=='development'];assert len(cases)==19
        assert {c['patient'] for role,c,row in cases}==DEVELOPERS
        for role,case,row in cases:
            guard();shape=case['native_shape'];grid=lattice(case)
            missing=[z for z in range(shape[2]) if z%4 and z<(shape[2]-1)//4*4]
            z=min(missing,key=lambda v:(abs(v-(shape[2]-1)/2),v));actions=[]
            for width in (7,32,64):
                assert min(shape[:2])>=width
                starts=[n//2-width//2 for n in shape[:2]]
                mask=np.zeros(shape,np.float32)
                mask[starts[0]:starts[0]+width,starts[1]:starts[1]+width,z]=1
                physical=physical_mr(mask,grid)>0
                locations,axes=tile_plan(physical.shape)
                affected=[i for i,start in enumerate(locations) if physical[tuple(slice(s,s+p) for s,p in zip(start,PATCH))].any()]
                batches=sorted({i//2 for i in affected});N=(len(locations)+1)//2;k=len(batches)
                actions.append(dict(ROI_width_rc=width,z=z,synthetic_native_mask_voxels=width**2,
                    physical_nonzero_support_voxels=int(physical.sum()),directly_affected_tiles=len(affected),
                    recomputed_batch_pairs=k,recomputed_tiles=sum(min(2,len(locations)-2*b) for b in batches),
                    saved_forward_calls_per_action=N-k,saved_forward_fraction=(N-k)/N,
                    baseline_plus5_same_support_actions_forward_calls=N+5*k,
                    full5_same_support_actions_forward_calls=5*N,
                    count_ratio_for5_with_initialization=(N+5*k)/(5*N),
                    minimum_action_count_for_strict_forward_count_saving=math.floor(N/(N-k))+1 if k<N else None))
            result['series'].append(dict(patient=case['patient'],uid=case['uid'],native_shape_rcz=shape,
                physical_shape_zrc=list(physical.shape),tiles=len(locations),full_forward_calls=N,
                all_tile_probability_cache_bytes=len(locations)*int(np.prod(PATCH))*4,proxy_actions=actions))
            save()
        summaries=[]
        for width in (7,32,64):
            pairs=[(s,next(a for a in s['proxy_actions'] if a['ROI_width_rc']==width)) for s in result['series']]
            patients={p:[] for p in sorted(DEVELOPERS)}
            for s,a in pairs:patients[s['patient']].append(a['saved_forward_fraction'])
            totalfull=sum(s['full_forward_calls'] for s,a in pairs);totalcached=sum(a['recomputed_batch_pairs'] for s,a in pairs)
            summaries.append(dict(ROI_width_rc=width,series_with_any_forward_saving=sum(a['saved_forward_calls_per_action']>0 for s,a in pairs),
                series_with_no_forward_saving=[s['uid'] for s,a in pairs if a['saved_forward_calls_per_action']==0],
                total_full_forward_calls_per_proxy_action=totalfull,total_cached_forward_calls_per_proxy_action=totalcached,
                total_saved_forward_calls=totalfull-totalcached,
                patient_first_mean_saved_forward_fraction=sum(sum(v)/len(v) for v in patients.values())/len(patients),
                patient_means_saved_forward_fraction={p:sum(v)/len(v) for p,v in patients.items()},
                count_ratio_for5_with_initialization=(totalfull+5*totalcached)/(5*totalfull)))
        result.update(summaries=summaries,development_patients=len(DEVELOPERS),development_series=len(cases),
            total_tiles=sum(s['tiles'] for s in result['series']),
            probability_cache_bytes_if_all19_series_simultaneously=sum(s['all_tile_probability_cache_bytes'] for s in result['series']),
            probability_cache_bytes_if_one_series_at_a_time=max(s['all_tile_probability_cache_bytes'] for s in result['series']),
            recommended_execution='one series at a time; invalidate by model/device/precision/stats/lattice/batch/input identity',
            limitations='Central synthetic 2D single-missing-plane supports; not real lesion/action support, actual speed, action benefit, or equivalence on 19 MRI inputs.',
            resources_after=guard(),cuda_initialized=torch.cuda.is_initialized(),complete=True)
    except Exception as e:result['errors'].append(type(e).__name__+': '+str(e));result['traceback']=traceback.format_exc()
    result.update(elapsed_seconds=time.perf_counter()-started,finished_utc=datetime.now(timezone.utc).isoformat());save()
    print(json.dumps({k:result.get(k) for k in ('complete','errors','development_series','total_tiles','probability_cache_bytes_if_all19_series_simultaneously',
        'probability_cache_bytes_if_one_series_at_a_time','summaries','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
