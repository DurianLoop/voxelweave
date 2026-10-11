"""Describe frozen GT counts in physical units; never open MR, GT or model arrays."""
import sys,json,hashlib,math
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def det(a):
    return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=client.resource_guard()
    ep=ROOT/'lossless_final_evaluation_entry_2026_10_08/medical_attempt03/evaluation_attempt01.json'
    q=read(ep);assert q['complete'] and not q['errors'] and q['prediction_files_saved']==56
    sources=[Path(__file__),ep];cases=[]
    for role,name,n in [('development','mc_rc_current_development_input_preparation',19),('validation','mc_rc_validation_task_case_preparation',9)]:
        path=ROOT/'experiments'/name/'attempt_01.json';p=read(path);assert p['complete'] and not p['errors'] and len(p['cases'])==n
        sources.append(path);cases.extend((role,c) for c in p['cases'])
    assert len(cases)==28 and len({c['uid'] for _,c in cases})==28
    models={a['kind']:{s['uid']:s for s in a['series']} for a in q['arms']};assert set(models)=={'native_reference','raw_pchip'}
    rows=[]
    for role,c in cases:
        a=c['affine_rcz_ras'];v=abs(det(a));spacing=[math.sqrt(sum(a[i][j]**2 for i in range(3))) for j in range(3)]
        assert v>0 and all(x>0 for x in spacing)
        native=models['native_reference'][c['uid']];raw=models['raw_pchip'][c['uid']]
        assert native['role']==raw['role']==role and native['patient']==raw['patient']==c['patient']
        gt=native['metrics']['full']['gt_foreground'];assert gt==raw['metrics']['full']['gt_foreground']
        row=dict(role=role,patient=c['patient'],uid=c['uid'],native_shape=c['native_shape'],spacing_rcz_mm=spacing,
            affine_voxel_volume_mm3=v,label_foreground_voxels=gt,label_volume_ml=gt*v/1000,
            model_metrics={kind:dict(full_dice=s['metrics']['full']['dice'],full_recall=s['metrics']['full']['recall'],
                predicted_volume_ml=s['metrics']['full']['pred_foreground']*v/1000,
                signed_relative_volume_error=s['metrics']['full']['signed_relative_volume_error'])
                for kind,s in [('native_reference',native),('raw_pchip',raw)]})
        rows.append(row)
    summary=[]
    for patient in sorted({r['patient'] for r in rows}):
        p=[r for r in rows if r['patient']==patient];vol=[r['label_volume_ml'] for r in p]
        summary.append(dict(patient=patient,role=p[0]['role'],series=len(p),label_volume_ml_min=min(vol),label_volume_ml_max=max(vol),
            max_to_min_volume_ratio=max(vol)/min(vol),raw_voxel_count_ratio=max(r['label_foreground_voxels'] for r in p)/min(r['label_foreground_voxels'] for r in p)))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],series_count=28,
        sources=[client.base.entry(p) for p in sources],resource_snapshot=resources,series=rows,patients=summary,
        clinical_alignment_not_verified_by_this_metadata_audit=True,volume_variation_is_not_proof_of_registration_or_label_error=True,
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,GPU_forwards=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,new_training_updates=0,publication_claim_confirmed=False,goal_status='active')
    dest=HERE/'PHYSICAL_VOLUME_METADATA_AUDIT.json';client.base.new(dest,result)
    print(json.dumps(dict(complete=True,receipt=client.base.entry(dest),patients=summary,validation_series=[r for r in rows if r['role']=='validation']),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
