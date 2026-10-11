"""Pure CPU developer input loader. Sparse reconstruction has no label/native argument."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import hashlib,json,zipfile
from dataclasses import dataclass
from pathlib import Path
import nibabel as nib
import numpy as np
import pydicom
from scipy.interpolate import PchipInterpolator
ROOT=Path(__file__).resolve().parents[1]
DEVELOPERS={'VS-MC-RC-'+x for x in ('001','002','004','005','006','007','009','010','011','012','013')}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def array_sha(a):
    a=np.ascontiguousarray(a);h=hashlib.sha256(json.dumps(dict(shape=list(a.shape),dtype=a.dtype.str),sort_keys=True).encode());h.update(memoryview(a).cast('B'));return h.hexdigest()
@dataclass(frozen=True)
class ObservedMRI:
    pixels:np.ndarray
    indices:tuple
    native_planes:int
    affine_rcz_ras:tuple
    sop_uids:tuple
    decoded_members:tuple
def require_developer(case):
    if case['patient'] not in DEVELOPERS:raise ValueError('Only predeclared developers authorized in this CPU loader')
def read_observed(case):
    require_developer(case)
    if sha(ROOT/case['header_file'])!=case['header_sha256'] or sha(ROOT/case['mr_zip_file'])!=case['mr_zip_sha256']:raise ValueError('Authenticated MR source differs')
    head=read(ROOT/case['header_file']);by={x['zip_member']:x for x in head['records']};indices=tuple(range(0,case['native_shape'][2],4));planes=[];members=[];sops=[]
    with zipfile.ZipFile(ROOT/case['mr_zip_file']) as archive:
        for z in indices:
            name=case['ordered_zip_members'][z]
            with archive.open(name) as f:d=pydicom.dcmread(f)
            if (str(d.PatientID),str(d.StudyInstanceUID),str(d.SeriesInstanceUID),str(d.SOPInstanceUID))!=(case['patient'],case['study_uid'],case['uid'],by[name]['sop_uid']):raise ValueError('Observed exact identity differs')
            if str(d.PhotometricInterpretation)!='MONOCHROME2' or [int(d.Rows),int(d.Columns)]!=case['native_shape'][:2]:raise ValueError('Observed shape or photometric differs')
            slope,offset=float(d.get('RescaleSlope',1)),float(d.get('RescaleIntercept',0));assert np.isfinite([slope,offset]).all()
            plane=d.pixel_array.astype(np.float32)*slope+offset
            if not np.isfinite(plane).all():raise ValueError('Nonfinite observed pixel')
            planes.append(plane);members.append(name);sops.append(str(d.SOPInstanceUID))
    values=np.stack(planes,axis=2);assert values.nbytes<=256000000
    values.flags.writeable=False
    return ObservedMRI(values,indices,case['native_shape'][2],tuple(tuple(x) for x in case['affine_rcz_ras']),tuple(sops),tuple(members))
def from_dense_observations_only(dense,affine):
    # Used for counterfactual tests only; hidden values are neither validated nor retained.
    indices=tuple(range(0,dense.shape[2],4));values=np.array(dense[:,:,indices],dtype=np.float32,copy=True);assert np.isfinite(values).all();values.flags.writeable=False
    return ObservedMRI(values,indices,dense.shape[2],tuple(tuple(x) for x in affine),(),())
def reconstruct(observed,method):
    if method not in ('raw_linear','raw_pchip'):raise ValueError('Unsupported sparse method')
    a=observed.pixels;n=observed.native_planes;assert tuple(range(0,n,4))==observed.indices
    generated=np.zeros((*a.shape[:2],n),dtype=np.float32);assert generated.nbytes<=256000000
    generated[:,:,observed.indices]=a;last=observed.indices[-1]
    for z in range(1,last):
        if z%4==0:continue
        i,t=z//4,z%4/4
        if method=='raw_pchip' and i>=1 and i+2<a.shape[2]:
            ix=np.arange(i-1,i+3);plane=PchipInterpolator(ix*4,a[:,:,ix],axis=2)(z)
        else:plane=(1-t)*a[:,:,i]+t*a[:,:,i+1]
        generated[:,:,z]=plane
    generated[:,:,last+1:]=a[:,:,-1,None]
    assert np.isfinite(generated).all() and np.array_equal(generated[:,:,observed.indices],a)
    return generated
def stats(values):
    mean=float(np.mean(values,dtype=np.float64));std=float(np.std(values,dtype=np.float64,ddof=0));assert np.isfinite([mean,std]).all()
    return dict(mean=mean,population_std=std,divisor=std if std>0 else 1.,elements=int(values.size),zero_std=std==0)
def normalize(reconstruction,observed,policy):
    if policy not in ('observed_shared','full_own'):raise ValueError('Unknown statistics input contract')
    st=stats(observed.pixels if policy=='observed_shared' else reconstruction)
    x=((reconstruction.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
    return x,st
def to_ras(values,observed):
    orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(np.asarray(observed.affine_rcz_ras)),nib.orientations.axcodes2ornt('RAS'))
    affine=np.asarray(observed.affine_rcz_ras)@nib.orientations.inv_ornt_aff(orientation,values.shape)
    return np.ascontiguousarray(nib.orientations.apply_orientation(values,orientation)),affine,orientation
def support_domains(observed):
    n=observed.native_planes;last=observed.indices[-1];anchors=np.zeros(n,dtype=bool);anchors[list(observed.indices)]=True
    missing=np.arange(n)<last;missing&=~anchors;tail=np.arange(n)>last
    assert np.all(anchors.astype(int)+missing.astype(int)+tail.astype(int)==1)
    return dict(anchors=anchors,missing=missing,tail=tail)
def read_supervised_label(case):
    require_developer(case)
    if sha(ROOT/case['label_file'])!=case['label_sha256']:raise ValueError('Authenticated developer label differs')
    image=nib.load(ROOT/case['label_file']);transform=np.asarray(case['dicom_rcz_from_label_xyz']);assert np.array_equal(transform,np.rint(transform));transform=transform.astype(int)
    result=np.zeros(case['native_shape'],dtype=bool)
    for start in range(0,image.shape[2],4):
        slab=np.asanyarray(image.dataobj[:,:,start:start+4]);assert slab.nbytes<=32000000 and np.isfinite(slab).all() and np.isin(slab,[0,1]).all()
        xyz=np.asarray(np.nonzero(slab));xyz[2]+=start;rcz=transform[:3,:3]@xyz+transform[:3,3,None]
        assert (rcz>=0).all() and (rcz<np.asarray(case['native_shape'])[:,None]).all();result[tuple(rcz)]=True
    assert int(result.sum())==case['expected_label_foreground_voxels'];return result
