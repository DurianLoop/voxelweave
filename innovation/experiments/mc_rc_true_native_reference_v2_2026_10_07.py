"""Memory-bounded label override. First-attempt native decoder is preserved."""
from mc_rc_true_native_reference_2026_10_07 import (
    ROOT, resource_guard, read, sha, array_sha, read_reference, require_reference_role,
    fixed_cases, DEVELOPERS, VALIDATORS, NativeReference, np, nib)

def read_reference_label(case):
    require_reference_role(case)
    assert sha(ROOT / case['label_file']) == case['label_sha256']
    image = nib.load(ROOT / case['label_file'])
    assert np.prod(image.shape) <= 256_000_000
    raw = np.empty(image.shape, dtype=bool)
    for z in range(0, image.shape[2], 4):
        slab = np.asanyarray(image.dataobj[:,:,z:z+4])
        assert slab.nbytes <= 32_000_000 and np.isfinite(slab).all() and np.isin(slab,[0,1]).all()
        raw[:,:,z:z+4] = slab
    t = np.asarray(case['dicom_rcz_from_label_xyz'])
    assert np.array_equal(t, np.rint(t)); t = t.astype(int)
    axes = np.argmax(np.abs(t[:3,:3]), axis=1)
    assert len(set(axes)) == 3 and np.array_equal(np.sort(np.abs(t[:3,:3]).sum(axis=0)),[1,1,1])
    result = np.transpose(raw, axes)
    for axis, src in enumerate(axes):
        sign = t[axis,src]; assert sign in (-1,1)
        assert t[axis,3] == (result.shape[axis]-1 if sign == -1 else 0)
        if sign == -1: result = np.flip(result,axis)
    result = np.ascontiguousarray(result,dtype=bool)
    assert list(result.shape) == case['native_shape'] and int(result.sum()) == case['expected_label_foreground_voxels']
    return result
