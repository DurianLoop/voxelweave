"""Two pending factor arms; preserve legacy source support and primitive stream."""
from mc_rc_global_local_task_cpu_support import (
    np,torch,F,TILE,context_plane,global_view)
from mc_rc_coverage_augmentation_draw_cpu_support import transform_spatial

PARTIAL_ARMS=('geometry_only','intensity_only')


def partial_example(item,record,arm):
    assert arm in PARTIAL_ARMS
    geometric=arm=='geometry_only'
    plane=context_plane(item['image_zrc'],record['z'],item['zspacing'])
    target=item['label_zrc'][record['z']].copy()
    if geometric:
        plane=transform_spatial(plane,record,channel=True)
        target=transform_spatial(target,record)
    else:
        plane=plane*record['scale']+record['shift']
    plane=np.ascontiguousarray(plane,dtype=np.float32)
    target=np.ascontiguousarray(target,dtype=np.float32)
    key='legacy_augmented_locations' if geometric else 'legacy_native_locations'
    locations=[tuple(v) for v in record[key]]
    xs=[];ys=[]
    for r,c in locations:
        assert 0<=r<=target.shape[0]-TILE and 0<=c<=target.shape[1]-TILE
        xs.append(plane[:,r:r+TILE,c:c+TILE])
        ys.append(target[r:r+TILE,c:c+TILE][None])
    gt=F.interpolate(torch.from_numpy(target)[None,None],size=(256,256),mode='area')
    return (global_view(plane),torch.from_numpy(np.stack(xs)),torch.from_numpy(np.stack(ys)),
            gt,locations,target.shape,dict(z=record['z'],foreground_plane=record['foreground_plane']))
