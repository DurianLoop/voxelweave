"""Record exact legacy primitives and map equal patch supports through integer D4."""
import hashlib,json
from mc_rc_global_local_task_cpu_support import (
    np,torch,F,TILE,context_plane,global_view,starts,array_sha)
ARMS=('legacy_aug','legacy_none','coverage_aug','coverage_none')

def d4_matrix(shape,flip_rows,flip_cols,k):
    h,w=map(int,shape);a=np.eye(3,dtype=np.int64)
    if flip_rows:a=np.array([[-1,0,h-1],[0,1,0],[0,0,1]],np.int64)@a
    if flip_cols:a=np.array([[1,0,0],[0,-1,w-1],[0,0,1]],np.int64)@a
    rotations=(np.eye(3,dtype=np.int64),np.array([[0,-1,w-1],[1,0,0],[0,0,1]],np.int64),
        np.array([[-1,0,h-1],[0,-1,w-1],[0,0,1]],np.int64),np.array([[0,1,0],[-1,0,h-1],[0,0,1]],np.int64))
    return rotations[k]@a

def map_rectangle(location,matrix):
    r,c=map(int,location);v=np.array([[r,c,1],[r+TILE-1,c,1],[r,c+TILE-1,1],[r+TILE-1,c+TILE-1,1]],np.int64)
    output=v@np.asarray(matrix).T;rounded=np.rint(output).astype(np.int64)
    assert np.max(abs(output-rounded))<1e-10
    lo,hi=rounded[:,:2].min(axis=0),rounded[:,:2].max(axis=0);assert np.array_equal(hi-lo,[TILE-1,TILE-1])
    return tuple(map(int,lo))

def transform_spatial(value,record,channel=False):
    raxis,caxis=(1,2) if channel else (0,1)
    if record['flip_rows']:value=np.flip(value,raxis)
    if record['flip_cols']:value=np.flip(value,caxis)
    return np.rot90(value,record['rot90'],axes=(raxis,caxis))

def legacy_primitive(item,rng,step,cursors):
    rng.integers(1);rng.integers(1)
    image,label=item['image_zrc'],item['label_zrc'];fg=item['native_foreground']
    select_foreground=bool(rng.random()<.5)
    index=int(rng.integers(len(fg))) if select_foreground else None
    z=int(fg[index,2]) if select_foreground else int(rng.integers(image.shape[0]))
    record=dict(step=step,z=z,foreground_z_selected=select_foreground,foreground_voxel_index=index,
        flip_rows=bool(rng.random()<.5),flip_cols=bool(rng.random()<.5),rot90=int(rng.integers(4)),
        scale=float(rng.uniform(.9,1.1)),shift=float(rng.uniform(-.1,.1)))
    target=transform_spatial(label[z],record);coords=np.argwhere(target>0);locations=[]
    for j in range(2):
        if j==0 and len(coords):rr,cc=coords[int(rng.integers(len(coords)))]+rng.integers(-32,33,size=2)
        else:rr,cc=[int(rng.integers(n)) for n in target.shape]
        locations.append((int(np.clip(rr-TILE//2,0,target.shape[0]-TILE)),int(np.clip(cc-TILE//2,0,target.shape[1]-TILE))))
    a=d4_matrix(label[z].shape,record['flip_rows'],record['flip_cols'],record['rot90'])
    inverse=np.linalg.inv(a);original=[map_rectangle(loc,inverse) for loc in locations]
    tiles=[(r,c) for r in starts(label[z].shape[0]) for c in starts(label[z].shape[1])]
    cursor=cursors.get(z,0);ids=[(cursor+j)%len(tiles) for j in range(2)];cursors[z]=cursor+2
    coverage=[tiles[i] for i in ids]
    record.update(augmentation_matrix_rc=a.tolist(),legacy_augmented_locations=[list(v) for v in locations],
        legacy_native_locations=[list(v) for v in original],coverage_native_locations=[list(v) for v in coverage],
        coverage_augmented_locations=[list(map_rectangle(loc,a)) for loc in coverage],coverage_tile_ids=ids,
        foreground_plane=bool(len(coords)))
    return record

def example_from_record(item,record,arm):
    assert arm in ARMS
    plane=context_plane(item['image_zrc'],record['z'],item['zspacing']);target=item['label_zrc'][record['z']].copy()
    augmented=arm.endswith('_aug');coverage=arm.startswith('coverage')
    if augmented:
        plane=transform_spatial(plane,record,channel=True);target=transform_spatial(target,record)
        plane=plane*record['scale']+record['shift']
    plane=np.ascontiguousarray(plane,dtype=np.float32);target=np.ascontiguousarray(target,dtype=np.float32)
    prefix='coverage' if coverage else 'legacy';suffix='augmented' if augmented else 'native'
    locations=[tuple(v) for v in record[prefix+'_'+suffix+'_locations']]
    xs,ys=[],[]
    for r,c in locations:
        assert 0<=r<=target.shape[0]-TILE and 0<=c<=target.shape[1]-TILE
        xs.append(plane[:,r:r+TILE,c:c+TILE]);ys.append(target[r:r+TILE,c:c+TILE][None])
    gt=F.interpolate(torch.from_numpy(target)[None,None],size=(256,256),mode='area')
    return global_view(plane),torch.from_numpy(np.stack(xs)),torch.from_numpy(np.stack(ys)),gt,locations,target.shape,dict(z=record['z'],foreground_plane=record['foreground_plane'])

def example_sha(example):
    gv,x,y,gt,locations,shape,record=example;h=hashlib.sha256()
    for tensor in (gv,x,y,gt):h.update(array_sha(tensor.numpy()).encode())
    h.update(json.dumps(dict(locations=locations,shape=shape,record=record),sort_keys=True).encode());return h.hexdigest()

def record_sha(record):return hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()
