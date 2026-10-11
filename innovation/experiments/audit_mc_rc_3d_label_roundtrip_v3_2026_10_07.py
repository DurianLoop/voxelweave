"""No-MR, no-training developer-label grid round trip with two interpolation implementations."""
import json,sys,time,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,read,sha,array_sha,resource_guard,fixed_cases,lattice,physical_label,read_reference_label,torch,np,F
from mc_rc_3d_independent_replay_2026_10_07 import independent_native_resample,logical_counts
OUT=ROOT/'experiments/mc_rc_3d_label_roundtrip_v3_2026_10_07'
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt01.json';started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],script_sha256=sha(__file__),
           source_bindings=[],actual_training_updates=0,actual_gpu_updates=0,scientific_confirmation_patients=0,
           validation_effects_opened=False,confirmation_patients_opened=False,mr_pixels_opened=False,
           mathematical_upper_bound_asserted=False,publication_claim_confirmed=False)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        sources=['MC_RC_3D_LABEL_ROUNDTRIP_PROTOCOL_2026-10-07.md','experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
                 'experiments/mc_rc_3d_baseline_2026_10_07.py','experiments/mc_rc_3d_independent_replay_2026_10_07.py',
                 'experiments/mc_rc_true_native_reference_v2_2026_10_07.py','experiments/mc_rc_true_native_reference_2026_10_07.py',
                 'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json']
        sources += ['MC_RC_3D_LABEL_ROUNDTRIP_COORDINATE_ADDENDUM_V2_2026-10-07.md','experiments/mc_rc_3d_label_roundtrip_2026_10_07/attempt01.json','experiments/prepare_mc_rc_3d_label_roundtrip_v2_2026_10_07.py']
        sources += ['experiments/mc_rc_3d_label_roundtrip_v2_2026_10_07/attempt01.json','experiments/prepare_mc_rc_3d_label_roundtrip_v3_2026_10_07.py']
        r['source_bindings']=[dict(path=p,sha256=sha(ROOT/p)) for p in sources]
        certified=read(ROOT/'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json');assert certified['complete'] and not certified['errors']
        cert={s['uid']:s for s in certified['series']};r['resources_before']=resource_guard()
        for role,case,row in fixed_cases():
            if role!='development':continue
            assert time.perf_counter()-started<=180;resource_guard()
            gt=read_reference_label(case);grid=lattice(case);target=physical_label(gt,grid)
            assert array_sha(target)==cert[case['uid']]['physical_label_sha256']
            crop=tuple(slice(p[0],p[0]+n) for n,p in zip(grid['unpadded_shape_zrc'],grid['padding']))
            physical=np.ascontiguousarray(target[crop],dtype=np.float32)
            numpy_prob=independent_native_resample(physical,case['native_shape'])
            with torch.inference_mode():torch_prob=F.interpolate(torch.from_numpy(physical)[None,None],size=(gt.shape[2],gt.shape[0],gt.shape[1]),mode='trilinear',align_corners=False)[0,0].numpy().transpose(1,2,0)
            error=float(np.abs(numpy_prob-torch_prob).max());differences=int(np.count_nonzero((numpy_prob>=.5)!=(torch_prob>=.5)))
            with torch.inference_mode():double_prob=F.interpolate(torch.from_numpy(physical.astype(np.float64))[None,None],size=(gt.shape[2],gt.shape[0],gt.shape[1]),mode='trilinear',align_corners=False)[0,0].numpy().transpose(1,2,0).astype(np.float32)
            double_error=float(np.abs(numpy_prob-double_prob).max());double_diff=int(np.count_nonzero((numpy_prob>=.5)!=(double_prob>=.5)))
            zs=np.arange(gt.shape[2]);last=zs[zs%4==0][-1]
            domains=dict(full=np.ones(len(zs),bool),anchors=zs%4==0,missing=(zs<last)&(zs%4!=0),tail=zs>last)
            metrics={k:logical_counts(numpy_prob[:,:,mask]>=.5,gt[:,:,mask]) for k,mask in domains.items()}
            torch_metrics={k:logical_counts(torch_prob[:,:,mask]>=.5,gt[:,:,mask]) for k,mask in domains.items()}
            m=metrics['full'];gate=dict(full_dice=m['dice'] is not None and m['dice']>=.9,full_recall=m['recall'] is not None and m['recall']>=.9,
                                      full_absRVE=m['absRVE'] is not None and m['absRVE']<=.25,tp_positive=m['tp']>0)
            record=dict(patient=case['patient'],uid=case['uid'],label_file=case['label_file'],label_sha256=case['label_sha256'],
                        native_shape=case['native_shape'],grid=grid,native_label_sha256=array_sha(gt),physical_label_sha256=array_sha(target),
                        native_gt_foreground=int(gt.sum()),physical_gt_foreground=int(target.sum()),
                        numpy_probability_sha256=array_sha(numpy_prob),torch_probability_sha256=array_sha(torch_prob),
                        probability_max_absolute_error=error,prediction_disagreements=differences,
                        numpy_metrics=metrics,torch_metrics=torch_metrics,full_diagnostic_gate=gate,full_diagnostic_gate_passed=all(gate.values()))
            record['production_float32_strict_comparison_passed']=error<=3e-6 and differences==0
            record['float64_coordinate_verification']=dict(max_probability_error=double_error,prediction_disagreements=double_diff)
            r['series'].append(record);save()
            assert double_error<=3e-6 and double_diff==0,'Independent float64 coordinate implementations differ; observations retained'
            if differences==0:assert metrics==torch_metrics
            print(json.dumps(dict(patient=case['patient'],dice=m['dice'],recall=m['recall'],absRVE=m['absRVE'],gate=all(gate.values()))),flush=True)
            del gt,target,physical,numpy_prob,torch_prob,double_prob
        assert len(r['series'])==19 and len({s['patient'] for s in r['series']})==11
        patients=[]
        for pid in sorted({s['patient'] for s in r['series']}):
            records=[s for s in r['series'] if s['patient']==pid]
            mean={k:float(np.mean([s['numpy_metrics']['full'][k] for s in records])) for k in ('dice','recall','precision','absRVE')}
            patients.append(dict(patient=pid,n_series=len(records),within_patient_mean=mean))
        float32_patients=[]
        for pid in sorted({s['patient'] for s in r['series']}):
            rows=[s for s in r['series'] if s['patient']==pid]
            float32_patients.append(dict(patient=pid,n_series=len(rows),within_patient_mean={k:float(np.mean([s['torch_metrics']['full'][k] for s in rows])) for k in ('dice','recall','precision','absRVE')}))
        r['production_float32_patients']=float32_patients
        r['production_float32_patient_macro_mean']={k:float(np.mean([p['within_patient_mean'][k] for p in float32_patients])) for k in ('dice','recall','precision','absRVE')}
        r['production_float32_strict_comparisons_passed']=sum(s['production_float32_strict_comparison_passed'] for s in r['series'])
        r['production_float32_series_full_diagnostic_gates_passed']=sum(all([s['torch_metrics']['full']['dice']>=.9,s['torch_metrics']['full']['recall']>=.9,s['torch_metrics']['full']['absRVE']<=.25,s['torch_metrics']['full']['tp']>0]) for s in r['series'])
        r['patients']=patients;r['patient_macro_mean']={k:float(np.mean([p['within_patient_mean'][k] for p in patients])) for k in ('dice','recall','precision','absRVE')}
        r['series_full_diagnostic_gates_passed']=sum(s['full_diagnostic_gate_passed'] for s in r['series'])
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized'];r['resources_after']=resource_guard();r['complete']=True
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-started;save();assert path.stat().st_size<=3_000_000
    print(json.dumps({k:r.get(k) for k in ('complete','errors','patient_macro_mean','series_full_diagnostic_gates_passed','cuda_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
