"""Actual two-input 28-series physical-grid audit; independent interpolation and CPU gradient checks."""
import json
import sys
import time
import traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_2026_10_07 import (
    ROOT, read, sha, array_sha, resource_guard, fixed_cases, source_image, read_reference_label,
    lattice, physical_mr, physical_label, TaskUNet3D, loss, infer_full_fov, PATCH, torch, nn, np)
OUT = ROOT/'experiments/mc_rc_3d_baseline_inputs_2026_10_07'

def independently_sample_linear(raw_zrc, newshape, points):
    n=np.asarray(raw_zrc.shape); m=np.asarray(newshape)
    at=np.clip((points+.5)*n/m-.5,0,n-1); lo=np.floor(at).astype(int); hi=np.minimum(lo+1,n-1)
    fraction=at-lo; result=np.zeros(len(points),float)
    for dz in (0,1):
        for dr in (0,1):
            for dc in (0,1):
                bits=np.array([dz,dr,dc]); indices=np.where(bits,hi,lo)
                weight=np.prod(np.where(bits,fraction,1-fraction),axis=1)
                result+=raw_zrc[tuple(indices.T)]*weight
    return result

def independent_label_grid(label,grid):
    raw=label.transpose(2,0,1)
    indices=[np.minimum(np.floor((np.arange(m)+.5)*n/m).astype(int),n-1) for n,m in zip(raw.shape,grid['unpadded_shape_zrc'])]
    out=raw[np.ix_(*indices)].astype(np.float32)
    return np.pad(out,grid['padding'],mode='constant')

def geometry_toy_and_gradient():
    torch.manual_seed(20261007)
    toycase=dict(native_shape=[19,23,11],affine_rcz_ras=[[0.,-.6,.05,13.],[.7,0.,0.,-9.],[0.,0.,.9,2.],[0.,0.,0.,1.]])
    grid=lattice(toycase); coords=np.indices(toycase['native_shape']); raw=(coords[0]*.3-coords[1]*.2+coords[2]*.6).astype(np.float32)
    actual=physical_mr(raw,grid); rng=np.random.default_rng(20261007)
    points=np.stack([rng.integers(n,size=201) for n in grid['unpadded_shape_zrc']],axis=1)
    pad=np.asarray(grid['padding'])[:,0]; sample=actual[tuple((points+pad).T)]
    error=float(np.max(np.abs(sample-independently_sample_linear(raw.transpose(2,0,1),grid['unpadded_shape_zrc'],points))))
    assert error<=2e-4
    # Inference blending must cover the entire irregular, padded FOV and preserve a constant probability.
    class ConstantNet(nn.Module):
        def forward(self,x): return (torch.full_like(x,float(np.log(.73/.27))),)
    smallpatch=(8,16,16)
    image=np.zeros((13,29,35),np.float32)
    smallgrid=dict(unpadded_shape_zrc=[11,25,31],padding=[(1,1),(2,2),(2,2)])
    probabilities,coverage=infer_full_fov(ConstantNet(),image,smallgrid,[25,31,11],patch=smallpatch)
    assert probabilities.shape==(25,31,11) and np.max(np.abs(probabilities-.73))<=1e-6
    # Independent voxel membership count from each axis, including every final boundary.
    axis_counts=[]
    for n,p,starts in zip(image.shape,smallpatch,coverage['axis_starts']):
        membership=np.asarray([[s<=v<s+p for s in starts] for v in range(n)])
        axis_counts.append(membership.sum(axis=1)); assert membership.any(axis=1).all()
    model=TaskUNet3D(); x=torch.randn(2,1,16,32,40); y=torch.zeros_like(x); y[0,0,4:10,10:20,12:22]=1
    started=time.perf_counter(); outputs=model(x); value=loss(outputs,y); value.backward()
    branches={}
    for name,collection in (('encoders',model.encoders),('decoders',model.decoders),('ups',model.ups),('heads',model.heads)):
        for index,layer in enumerate(collection):
            gradients=[p.grad for p in layer.parameters()]
            assert all(g is not None and torch.isfinite(g).all() for g in gradients)
            maximum=max(float(g.abs().max()) for g in gradients); assert maximum>0
            branches[name+'_'+str(index)]=dict(parameters_with_gradient=len(gradients),maximum_absolute_gradient=maximum)
    assert not torch.cuda.is_initialized()
    return dict(trilinear_phantom_max_absolute_error=error,constant_probability_full_fov_max_absolute_error=float(np.abs(probabilities-.73).max()),
                independent_all_voxel_coverage=True,coverage=coverage,parameters=sum(p.numel() for p in model.parameters()),
                cpu_test_shape=list(x.shape),cpu_forward_backward_seconds=time.perf_counter()-started,loss=float(value.detach()),
                branch_gradients=branches,actual_gpu_updates=0,cuda_initialized=False,
                real_patch_shape_zrc=list(PATCH),actual_real_patch_gpu_memory_not_measured=True)

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],
           native_copies_saved=0,physical_copies_saved=0,actual_gpu_updates=0,
           confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,
           script_sha256=sha(__file__),source_bindings=[])
    sourcepaths=['MC_RC_3D_BASELINE_PREPARATION_PROTOCOL_2026-10-07.md','experiments/mc_rc_3d_baseline_2026_10_07.py',
                 'experiments/mc_rc_reference_resources_2026_10_07.py','experiments/mc_rc_true_native_reference_2026_10_07.py',
                 'experiments/mc_rc_true_native_reference_v2_2026_10_07.py','experiments/mc_rc_observed_only_training_input.py',
                 'experiments/mc_rc_true_native_reference_attempt02_2026_10_07/attempt_01.json',
                 'experiments/mc_rc_true_native_reference_attempt02_2026_10_07/independent_all28_pixels_and_labels_2026_10_07.json',
                 'experiments/mc_rc_current_development_input_preparation/attempt_01.json','experiments/mc_rc_validation_task_case_preparation/attempt_01.json',
                 'experiments/mc_rc_development_training_input_cpu/attempt_01.json','experiments/mc_rc_validation_task_input_cpu/attempt_01.json']
    def save(): path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        proof=read(ROOT/sourcepaths[7]); assert proof['complete'] and not proof['errors']
        r['source_bindings']=[dict(path=p,sha256=sha(ROOT/p)) for p in sourcepaths]
        r['resources_before']=resource_guard();r['synthetic_and_cpu_gradient']=geometry_toy_and_gradient();save()
        rng=np.random.default_rng(20261007)
        for role,case,row in fixed_cases():
            resource_guard();grid=lattice(case); inputs={}
            points=np.stack([rng.integers(n,size=201) for n in grid['unpadded_shape_zrc']],axis=1)
            for kind in ('raw_pchip','native_reference'):
                normalized,st=source_image(case,row,kind);image=physical_mr(normalized,grid)
                pad=np.asarray(grid['padding'])[:,0]
                actual=image[tuple((points+pad).T)]
                expected=independently_sample_linear(normalized.transpose(2,0,1),grid['unpadded_shape_zrc'],points)
                error=float(np.max(np.abs(actual-expected)));assert error<=2e-4
                old=grid['native_shape_zrc'];new=grid['unpadded_shape_zrc']
                native_coords=(points+.5)*np.asarray(old)/new-.5
                rcz=native_coords[:,[1,2,0]]
                source_world=rcz@np.asarray(case['affine_rcz_ras'])[:3,:3].T+np.asarray(case['affine_rcz_ras'])[:3,3]
                actual_world=points@np.asarray(grid['physical_affine_zrc_ras'])[:3,:3].T+np.asarray(grid['physical_affine_zrc_ras'])[:3,3]
                worlderror=float(np.max(np.linalg.norm(source_world-actual_world,axis=1)));assert worlderror<=1e-8
                inputs[kind]=dict(normalized_rcz_sha256=array_sha(normalized),physical_image_sha256=array_sha(image),
                                  physical_image_shape_zrc=list(image.shape),observed_statistics=st,
                                  independent_trilinear_points_checked=201,max_trilinear_error=error,max_world_coordinate_error_mm=worlderror)
                del normalized,image
            assert inputs['raw_pchip']['observed_statistics']==inputs['native_reference']['observed_statistics']
            # Labels opened only after both image contracts are fixed.
            label=read_reference_label(case);target=physical_label(label,grid);replay=independent_label_grid(label,grid)
            assert np.array_equal(target,replay) and target.sum()>0 and np.isin(target,[0,1]).all()
            record=dict(role=role,patient=case['patient'],uid=case['uid'],grid=grid,inputs=inputs,
                        native_label_sha256=array_sha(label),physical_label_sha256=array_sha(target),
                        native_foreground=int(label.sum()),physical_foreground=int(target.sum()),
                        all_label_grid_voxels_replayed=int(target.size),label_read_after_both_image_inputs=True,complete=True)
            r['series'].append(record);save()
            print(json.dumps(dict(role=role,patient=case['patient'],physical_shape=target.shape,foreground=int(target.sum()),complete=True)),flush=True)
            del label,target,replay
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        r['complete']=len(r['series'])==28
        r['resources_after']=resource_guard()
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','actual_gpu_updates','cuda_initialized')}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
