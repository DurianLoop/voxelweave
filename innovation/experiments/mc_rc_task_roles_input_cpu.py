"""Observed-only loading for fixed developers and validators. Confirmation explicitly denied."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import zipfile
import numpy as np
import nibabel as nib
import pydicom
from mc_rc_observed_only_training_input import ROOT,read,sha,ObservedMRI,array_sha,reconstruct,normalize,stats,to_ras,support_domains
DEVELOPERS={'VS-MC-RC-'+p for p in ('001','002','004','005','006','007','009','010','011','012','013')}
VALIDATORS={'VS-MC-RC-'+p for p in ('020','022','025','024')}
def require_role(case):
    if case['patient'] not in DEVELOPERS|VALIDATORS:raise ValueError('Final confirmation and unallocated subjects prohibited')
def read_task_observed(case):
    require_role(case);assert sha(ROOT/case['header_file'])==case['header_sha256'] and sha(ROOT/case['mr_zip_file'])==case['mr_zip_sha256'];head=read(ROOT/case['header_file']);by={x['zip_member']:x for x in head['records']};indices=tuple(range(0,case['native_shape'][2],4));planes=[];members=[];sops=[]
    with zipfile.ZipFile(ROOT/case['mr_zip_file']) as archive:
        for z in indices:
            name=case['ordered_zip_members'][z]
            with archive.open(name) as f:d=pydicom.dcmread(f)
            assert (str(d.PatientID),str(d.StudyInstanceUID),str(d.SeriesInstanceUID),str(d.SOPInstanceUID))==(case['patient'],case['study_uid'],case['uid'],by[name]['sop_uid']);assert str(d.PhotometricInterpretation)=='MONOCHROME2'
            assert [int(d.Rows),int(d.Columns)]==case['native_shape'][:2];slope,offset=float(d.get('RescaleSlope',1)),float(d.get('RescaleIntercept',0));assert np.isfinite([slope,offset]).all();plane=d.pixel_array.astype(np.float32)*slope+offset;assert np.isfinite(plane).all();planes.append(plane);members.append(name);sops.append(str(d.SOPInstanceUID))
    values=np.stack(planes,axis=2);assert values.nbytes<=256000000;values.flags.writeable=False;return ObservedMRI(values,indices,case['native_shape'][2],tuple(tuple(x) for x in case['affine_rcz_ras']),tuple(sops),tuple(members))
def read_task_supervised_label(case):
    require_role(case);assert sha(ROOT/case['label_file'])==case['label_sha256'];image=nib.load(ROOT/case['label_file']);t=np.asarray(case['dicom_rcz_from_label_xyz']);assert np.array_equal(t,np.rint(t));t=t.astype(int);result=np.zeros(case['native_shape'],bool)
    for start in range(0,image.shape[2],4):
        slab=np.asanyarray(image.dataobj[:,:,start:start+4]);assert slab.nbytes<=32000000 and np.isfinite(slab).all() and np.isin(slab,[0,1]).all();xyz=np.asarray(np.nonzero(slab));xyz[2]+=start;rcz=t[:3,:3]@xyz+t[:3,3,None];assert (rcz>=0).all() and (rcz<np.asarray(case['native_shape'])[:,None]).all();result[tuple(rcz)]=True
    assert int(result.sum())==case['expected_label_foreground_voxels'];return result
