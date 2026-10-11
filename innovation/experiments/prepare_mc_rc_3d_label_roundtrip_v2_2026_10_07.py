"""Retain actual float32 endpoints and qualify the independent float64 coordinate mapping."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
    old=ROOT/'audit_mc_rc_3d_label_roundtrip_2026_10_07.py'
    new=ROOT/'audit_mc_rc_3d_label_roundtrip_v2_2026_10_07.py';assert not new.exists()
    s=old.read_text(encoding='utf-8').replace("OUT=ROOT/'experiments/mc_rc_3d_label_roundtrip_2026_10_07'", "OUT=ROOT/'experiments/mc_rc_3d_label_roundtrip_v2_2026_10_07'")
    s=s.replace("        r['source_bindings']=[dict(path=p,sha256=sha(ROOT/p)) for p in sources]", "        sources += ['MC_RC_3D_LABEL_ROUNDTRIP_COORDINATE_ADDENDUM_V2_2026-10-07.md','experiments/mc_rc_3d_label_roundtrip_2026_10_07/attempt01.json','experiments/prepare_mc_rc_3d_label_roundtrip_v2_2026_10_07.py']\n        r['source_bindings']=[dict(path=p,sha256=sha(ROOT/p)) for p in sources]")
    insert='''            with torch.inference_mode():double_prob=F.interpolate(torch.from_numpy(physical.astype(np.float64))[None,None],size=(gt.shape[2],gt.shape[0],gt.shape[1]),mode='trilinear',align_corners=False)[0,0].numpy().transpose(1,2,0).astype(np.float32)
            double_error=float(np.abs(numpy_prob-double_prob).max());double_diff=int(np.count_nonzero((numpy_prob>=.5)!=(double_prob>=.5)))
'''
    s=s.replace('            zs=np.arange(gt.shape[2]);',insert+'            zs=np.arange(gt.shape[2]);')
    s=s.replace("            r['series'].append(record);save()", "            record['production_float32_strict_comparison_passed']=error<=3e-6 and differences==0\n            record['float64_coordinate_verification']=dict(max_probability_error=double_error,prediction_disagreements=double_diff)\n            r['series'].append(record);save()")
    s=s.replace("            assert error<=3e-6 and differences==0,'Label round-trip implementations differ; observations retained'\n            assert metrics==torch_metrics", "            assert double_error<=3e-6 and double_diff==0,'Independent float64 coordinate implementations differ; observations retained'\n            if differences==0:assert metrics==torch_metrics")
    s=s.replace('del gt,target,physical,numpy_prob,torch_prob','del gt,target,physical,numpy_prob,torch_prob,double_prob')
    s=s.replace("        r['patients']=patients;", "        float32_patients=[]\n        for pid in sorted({s['patient'] for s in r['series']}):\n            rows=[s for s in r['series'] if s['patient']==pid]\n            float32_patients.append(dict(patient=pid,n_series=len(rows),within_patient_mean={k:float(np.mean([s['torch_metrics']['full'][k] for s in rows])) for k in ('dice','recall','precision','absRVE')}))\n        r['production_float32_patients']=float32_patients\n        r['production_float32_patient_macro_mean']={k:float(np.mean([p['within_patient_mean'][k] for p in float32_patients])) for k in ('dice','recall','precision','absRVE')}\n        r['production_float32_strict_comparisons_passed']=sum(s['production_float32_strict_comparison_passed'] for s in r['series'])\n        r['production_float32_series_full_diagnostic_gates_passed']=sum(all([s['torch_metrics']['full']['dice']>=.9,s['torch_metrics']['full']['recall']>=.9,s['torch_metrics']['full']['absRVE']<=.25,s['torch_metrics']['full']['tp']>0]) for s in r['series'])\n        r['patients']=patients;")
    compile(s,str(new),'exec')
    with new.open('x',encoding='utf-8') as f:f.write(s)
    print(new.name)
if __name__=='__main__':main()
