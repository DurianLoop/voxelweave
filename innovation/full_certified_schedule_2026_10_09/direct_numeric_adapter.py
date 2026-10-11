"""Independent direct reference plus independently checked coordinate diagnostic; no candidate calls."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'direct_oracle_efficiency_2026_10_09'))
sys.path.insert(0,str(ROOT/'resolution_degradation_controls_2026_10_08'))
from direct_separable_reference import apply_reference,dimensions
from independent_resolution import coordinate_axes

def independent_apply(cache,grid,geometry,primitive,mode,patch_shape=(64,128,128)):
    image,support,meta=apply_reference(cache,grid,geometry,primitive,mode,patch_shape)
    fine=tuple(map(int,grid['unpadded_shape_zrc']));coarse=dimensions(fine,primitive['scale'],primitive['enabled'],mode)
    meta['coordinate_max_error']=coordinate_axes(fine,coarse)[2]
    return image,support,meta
