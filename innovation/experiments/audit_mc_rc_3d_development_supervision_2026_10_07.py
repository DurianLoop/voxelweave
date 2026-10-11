"""19 development label-only 32-draw deep-supervision audit with independent strided replay."""
import hashlib
import json
import sys
import traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,lattice,physical_label,read_reference_label,
    sample_batch,torch,np,SEED,PATCH)
OUT=ROOT/'experiments/mc_rc_3d_development_supervision_2026_10_07'

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],
           script_sha256=sha(__file__),source_bindings=[],development_patients=11,development_series=19,
           planned_draws_per_series=32,MR_source_pixels_decoded=False,neural_forwards=0,actual_training_updates=0,
           confirmation_patients_opened=False,validation_model_effects_opened=False,scientific_confirmation_patients=0,
           publication_claim_confirmed=False)
    sources=['MC_RC_3D_DEVELOPMENT_SUPERVISION_AUDIT_PROTOCOL_2026-10-07.md','experiments/mc_rc_3d_baseline_2026_10_07.py',
             'experiments/mc_rc_3d_baseline_v2_2026_10_07.py','experiments/mc_rc_reference_resources_2026_10_07.py',
             'experiments/mc_rc_true_native_reference_v2_2026_10_07.py','experiments/mc_rc_true_native_reference_2026_10_07.py',
             'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json']
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        cert=read(ROOT/sources[-1]);assert cert['complete'] and not cert['errors']
        r['source_bindings']=[dict(path=p,sha256=sha(ROOT/p)) for p in sources]
        expected={x['uid']:x for x in cert['series']}; cases=[v for v in fixed_cases() if v[0]=='development'];assert len(cases)==19
        r['resources_before']=resource_guard();stream=hashlib.sha256();total_gt_voxels=0
        for role,case,row in cases:
            resource_guard();grid=lattice(case);native_label=read_reference_label(case);target=physical_label(native_label,grid)
            assert array_sha(target)==expected[case['uid']]['physical_label_sha256']
            rng=np.random.default_rng(SEED);image=np.zeros(target.shape,dtype=np.float32)
            entry=dict(patient=case['patient'],uid=case['uid'],target_shape=list(target.shape),target_sha256=array_sha(target),
                       native_foreground=int(native_label.sum()),physical_foreground=int(target.sum()),draws=[],
                       forced_patch_zero_gt_by_scale=[0,0,0],whole_batch_zero_gt_by_scale=[0,0,0],complete=False)
            for draw in range(32):
                # A synthetic zero image only supplies the production sampler's shape. No actual MR is read.
                x,y,primitive=sample_batch(image,target,rng)
                levels=[y,torch.nn.functional.interpolate(y,size=tuple(p//2 for p in PATCH),mode='nearest-exact'),
                        torch.nn.functional.interpolate(y,size=tuple(p//4 for p in PATCH),mode='nearest-exact')]
                a=y.numpy();independent=[a,a[:,:,1::2,1::2,1::2],a[:,:,2::4,2::4,2::4]]
                counts=[]
                for level,replay in zip(levels,independent):
                    actual=level.numpy();assert np.array_equal(actual,replay)
                    total_gt_voxels+=actual.size;counts.append([int(p.sum()) for p in actual])
                assert counts[0][0]>0
                item=dict(draw=draw,primitive=primitive,patch_foreground_by_scale=counts,
                          label_batch_sha256=array_sha(a),coarse_label_sha256=[array_sha(level.numpy()) for level in levels[1:]],
                          foreground_fraction_by_scale=[[v/int(np.prod(level.shape[2:])) for v in perpatch] for level,perpatch in zip(levels,counts)])
                stream.update(json.dumps(item,sort_keys=True,separators=(',',':')).encode())
                entry['draws'].append(item)
                for i,perpatch in enumerate(counts):
                    entry['forced_patch_zero_gt_by_scale'][i]+=perpatch[0]==0
                    entry['whole_batch_zero_gt_by_scale'][i]+=sum(perpatch)==0
                del x,y,levels,independent,a
            entry['complete']=True;r['series'].append(entry);save()
            print(json.dumps(dict(patient=case['patient'],physical_foreground=entry['physical_foreground'],
                                  forced_zero=entry['forced_patch_zero_gt_by_scale'],batch_zero=entry['whole_batch_zero_gt_by_scale'])),flush=True)
            del image,target,native_label
        r['draws_checked']=sum(len(s['draws']) for s in r['series']);assert r['draws_checked']==608
        r['all_scaled_gt_voxels_replayed']=total_gt_voxels;r['draw_stream_sha256']=stream.hexdigest()
        r['forced_patch_zero_gt_by_scale']=[sum(s['forced_patch_zero_gt_by_scale'][i] for s in r['series']) for i in range(3)]
        r['whole_batch_zero_gt_by_scale']=[sum(s['whole_batch_zero_gt_by_scale'][i] for s in r['series']) for i in range(3)]
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        r['resources_after']=resource_guard();r['complete']=len(r['series'])==19
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();save();assert path.stat().st_size<=20_000_000
    print(json.dumps({k:r.get(k) for k in ('complete','errors','draws_checked','forced_patch_zero_gt_by_scale','whole_batch_zero_gt_by_scale','all_scaled_gt_voxels_replayed')}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
