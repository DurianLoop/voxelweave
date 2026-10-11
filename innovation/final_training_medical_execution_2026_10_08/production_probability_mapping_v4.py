"""V4: retain the frozen network/fusion; use float64 for native coordinate interpolation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'lossless_final_evaluation_entry_2026_10_08'))
from final_eval_lossless_v3 import torch,np,PATCH,tile_plan,array_sha
from mc_rc_3d_baseline_2026_10_07 import blending_weight
from torch.nn import functional as F

def infer_full_fov_v4(model,image_zrc,grid,native_shape_rcz,device='cpu',patch=PATCH):
    model.eval();locations,starts=tile_plan(image_zrc.shape,patch);weight=blending_weight(patch)
    sums=np.zeros(image_zrc.shape,dtype=np.float64);coverage=np.zeros_like(sums)
    with torch.inference_mode():
        for at in range(0,len(locations),2):
            chunk=locations[at:at+2];slabs=[tuple(slice(s,s+p) for s,p in zip(start,patch)) for start in chunk]
            x=torch.from_numpy(np.stack([image_zrc[sl] for sl in slabs])[:,None]).to(device)
            probabilities=model(x)[0].sigmoid().cpu().numpy()[:,0]
            assert probabilities.shape[1:]==patch and np.isfinite(probabilities).all()
            for sl,prob in zip(slabs,probabilities):sums[sl]+=prob*weight;coverage[sl]+=weight
    assert coverage.min()>0
    probs=sums/coverage
    crop=tuple(slice(lo,lo+n) for n,(lo,hi) in zip(grid['unpadded_shape_zrc'],grid['padding']))
    probs=np.ascontiguousarray(probs[crop],dtype=np.float32)
    with torch.no_grad():
        mapped=F.interpolate(torch.from_numpy(probs.astype(np.float64))[None,None],
            size=(native_shape_rcz[2],native_shape_rcz[0],native_shape_rcz[1]),
            mode='trilinear',align_corners=False)[0,0].numpy()
    result=np.ascontiguousarray(mapped.transpose(1,2,0),dtype=np.float32)
    return result,dict(shape_zrc=list(image_zrc.shape),axis_starts=starts,total_tiles=len(locations),
        coverage_min=float(coverage.min()),coverage_max=float(coverage.max()),coverage_sha256=array_sha(coverage),
        full_fov=True,label_used_for_inference=False,threshold=.5,blend_weight_sha256=array_sha(weight))
