"""All28 allowed metadata directions, without loading MR, GT, model or CUDA."""
import json,hashlib,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    resource_guard();rows=[];sources=[]
    for role,folder,n in [('development','mc_rc_current_development_input_preparation',19),('validation','mc_rc_validation_task_case_preparation',9)]:
        p=ROOT/'experiments'/folder/'attempt_01.json';q=json.loads(p.read_text());assert q['complete'] and not q['errors'] and len(q['cases'])==n;sources.append(p)
        for c in q['cases']:
            a=np.asarray(c['affine_rcz_ras'],float)[:3,:3];spacing=np.linalg.norm(a,axis=0);direction=a/spacing
            rows.append(dict(role=role,patient=c['patient'],uid=c['uid'],direction_rcz_in_RAS=direction.tolist(),
                spacing_rcz_mm=spacing.tolist(),orthogonality_max_error=float(np.max(np.abs(direction.T@direction-np.eye(3)))),
                through_plane_angle_from_RAS_axial_degrees=float(np.rad2deg(np.arccos(np.clip(abs(direction[2,2]),0,1)))),
                angle_to_nearest_world_axis_by_rcz_degrees=np.rad2deg(np.arccos(np.clip(np.max(np.abs(direction),axis=0),0,1))).tolist()))
    summary=[]
    for role in ['development','validation']:
        rr=[s for s in rows if s['role']==role];v=[s['through_plane_angle_from_RAS_axial_degrees'] for s in rr]
        summary.append(dict(role=role,series=len(rr),distinct_patients=len({s['patient'] for s in rr}),
            min_angle=min(v),max_angle=max(v),series_above15deg=sum(x>15 for x in v),series_above45deg=sum(x>45 for x in v)))
    r=dict(complete=True,errors=[],series=rows,summary=summary,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        input_spatial_canonicalization_applied_by_this_audit=False,
        source_inspection='Existing physical_mr resizes RCZ lattice with F.interpolate; affine directions are recorded but no RAS reorientation is applied',
        orientation_difference_is_not_causal_failure_evidence=True,confirmation_patients_opened=False,lockedIXI_opened=False,
        publication_claim_confirmed=False,source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources+[Path(__file__)]])
    with (HERE/'ALLOWED_ORIENTATION_AUDIT.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,summary=summary)),flush=True)
if __name__=='__main__':main()
