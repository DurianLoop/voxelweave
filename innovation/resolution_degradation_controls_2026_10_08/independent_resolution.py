"""Independent integer grid sizes, physical voxel coordinates and SciPy interpolation."""
import math
import numpy as np
from scipy.ndimage import affine_transform,map_coordinates
MODES={'throughplane':{0},'inplane':{1,2},'allaxes':{0,1,2}}

def independent_shapes(grid,primitive,mode):
    fine=tuple(map(int,grid['unpadded_shape_zrc']))
    f=1.1+.4*((float(primitive['scale'])-.85)/.30)
    coarse=tuple((min(k,max(2,math.floor((k-1)/f+.5)+1)) if k>1 else 1)
                 if primitive['enabled'] and a in MODES[mode] else k for a,k in enumerate(fine))
    return fine,coarse

def coordinate_axes(fine,coarse):
    first=[];second=[];max_error=0.
    for n,m in zip(fine,coarse):
        if n==1:
            assert m==1;first.append(np.array([0.]));second.append(np.array([0.]));continue
        k=np.arange(m,dtype=np.int64);integer=k*(n-1);lo,rem=np.divmod(integer,m-1)
        exact=lo+rem.astype(np.float64)/(m-1)
        ordinary=np.linspace(0.,n-1,m);max_error=max(max_error,float(np.max(np.abs(exact-ordinary))))
        assert lo.min()>=0 and np.max(lo+(rem!=0))<=n-1
        j=np.arange(n,dtype=np.int64);numerator=j*(m-1);low,remainder=np.divmod(numerator,n-1)
        exact_second=low+remainder.astype(np.float64)/(n-1)
        normalized=2*j.astype(np.float64)/(n-1)-1
        torch_position=(normalized+1)*(m-1)/2
        max_error=max(max_error,float(np.max(np.abs(exact_second-torch_position))))
        assert low.min()>=0 and np.max(low+(remainder!=0))<=m-1
        assert np.all(rem>=0) and np.all(rem<m-1) and np.all(remainder>=0) and np.all(remainder<n-1)
        first.append(exact);second.append(exact_second)
    return first,second,max_error

def independent_apply(cache,grid,geometry,primitive,mode,patch_shape=(64,128,128)):
    fine,coarse=independent_shapes(grid,primitive,mode)
    first,second,error=coordinate_axes(fine,coarse);assert error<=3e-12
    pad=[int(p[0]) for p in grid['padding']]
    base=cache[tuple(slice(int(s),int(s)+int(k)) for s,k in zip(geometry['start'],patch_shape))].copy()
    for a,flip in enumerate(geometry['flips']):
        if flip:base=np.flip(base,a)
    base=(np.ascontiguousarray(base)*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)
    output=base.copy();support=np.zeros(patch_shape,np.float64)
    index=[];positions=[]
    for a,(n,k) in enumerate(zip(fine,patch_shape)):
        start=int(geometry['start'][a])-pad[a]
        array=np.arange(start,start+k,dtype=np.int64)
        if geometry['flips'][a]:array=array[::-1]
        accepted=[i for i,v in enumerate(array) if 0<=v<n]
        index.append(accepted);positions.append(array[accepted])
    count=int(np.prod([len(x) for x in index]))
    if count:
        target=np.ix_(*index)
        if not primitive['enabled']:support[target]=1.
        else:
            source=cache[tuple(slice(p,p+n) for p,n in zip(pad,fine))].astype(np.float64)
            ratios=np.array([(n-1)/(m-1) if m>1 else 0. for n,m in zip(fine,coarse)])
            matrix=np.diag(ratios)
            down=affine_transform(source,matrix,offset=0.,output_shape=coarse,order=1,mode='grid-constant',cval=0.,prefilter=False)
            down_support=affine_transform(np.ones(fine,np.float64),matrix,offset=0.,output_shape=coarse,order=1,mode='grid-constant',cval=0.,prefilter=False)
            coords=np.stack(np.meshgrid(*[axis[p] for axis,p in zip(second,positions)],indexing='ij'))
            values=map_coordinates(down,coords,order=1,mode='grid-constant',cval=0.,prefilter=False)
            valid=map_coordinates(down_support,coords,order=1,mode='grid-constant',cval=0.,prefilter=False)
            output[target]=(values.astype(np.float32)*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)
            support[target]=valid
    return output,support,dict(coordinate_max_error=error,validity_voxels=count,coarse_shape_zrc=list(coarse))
