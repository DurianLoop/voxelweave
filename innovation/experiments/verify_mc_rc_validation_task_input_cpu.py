"""Independent original observed DICOM reread, Hermite interpolation and axis label mapping."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import hashlib,json,itertools,sys,traceback,zipfile
from datetime import datetime,timezone
from pathlib import Path
import nibabel as nib
import numpy as np
import pydicom
from vs_seg_task_cpu_support import resource_gate
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_validation_task_input_cpu'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def array_sha(a):
    a=np.ascontiguousarray(a);h=hashlib.sha256(json.dumps(dict(shape=list(a.shape),dtype=a.dtype.str),sort_keys=True).encode());h.update(memoryview(a).cast('B'));return h.hexdigest()
def reorder(values,orientation):
    x=values
    for axis,(_,sign) in enumerate(orientation):
        if sign==-1:x=np.flip(x,axis)
    return np.ascontiguousarray(np.transpose(x,np.argsort(np.asarray(orientation)[:,0].astype(int))))
def manual_stats(a):
    count=a.size;mean=sum(float(np.asarray(a[:,:,j],dtype=np.float64).sum()) for j in range(a.shape[2]))/count
    var=sum(float(np.square(np.asarray(a[:,:,j],dtype=np.float64)-mean).sum()) for j in range(a.shape[2]))/count
    return mean,var**.5
def independent_interp(anchors,n,method):
    ix=list(range(0,n,4));out=np.zeros((*anchors.shape[:2],n),dtype=np.float32);out[:,:,ix]=anchors;out[:,:,ix[-1]+1:]=anchors[:,:,-1,None];maximum=0.
    for z in range(1,ix[-1]):
        if z%4==0:continue
        i=z//4;t=(z-ix[i])/4;left,right=anchors[:,:,i],anchors[:,:,i+1]
        if method=='raw_linear' or i==0 or i+2>=anchors.shape[2]:plane=(1-t)*left+t*right
        else:
            v=anchors[:,:,i-1:i+3].astype(np.float64);d=np.diff(v,axis=2)/4;m=[]
            for a,b in [(d[:,:,0],d[:,:,1]),(d[:,:,1],d[:,:,2])]:
                same=(a*b>0);slope=np.zeros_like(a);np.divide(2*a*b,a+b,out=slope,where=same);m.append(slope)
            plane=(1+2*t)*(1-t)**2*v[:,:,1]+t*(1-t)**2*4*m[0]+t*t*(3-2*t)*v[:,:,2]+t*t*(t-1)*4*m[1]
        out[:,:,z]=plane
    return out
def label_by_axis(case):
    image=nib.load(ROOT/case['label_file']);arr=np.zeros(image.shape,dtype=bool)
    for z in range(image.shape[2]):
        plane=np.asanyarray(image.dataobj[:,:,z]);assert plane.nbytes<=32000000 and np.isfinite(plane).all() and np.isin(plane,[0,1]).all();arr[:,:,z]=plane!=0
    transform=np.asarray(case['dicom_rcz_from_label_xyz'],dtype=int);perm=np.argmax(abs(transform[:3,:3]),axis=1);native=arr.transpose(tuple(perm))
    for axis,j in enumerate(perm):
        sign=transform[axis,j];assert sign in (-1,1) and transform[axis,3]==(case['native_shape'][axis]-1 if sign==-1 else 0)
        if sign==-1:native=np.flip(native,axis)
    assert list(native.shape)==case['native_shape'];return np.ascontiguousarray(native)
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();r=read(OUT/'attempt_01.json');prep=read(ROOT/'experiments/mc_rc_validation_task_case_preparation/attempt_01.json');path=OUT/'independent_all9_observed_inputs_and_label_axes_attempt_01.json';assert not path.exists()
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),complete=False,errors=[],series=[],observed_dicom_planes_verified=0,sparse_inputs_verified=0,labels_verified=0,non_observed_MR_pixels_decoded=False,torch_imported=False,new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    try:
        assert r['complete'] and not r['errors'] and len(r['series'])==9 and r['preparation_sha256']==sha(ROOT/'experiments/mc_rc_validation_task_case_preparation/attempt_01.json')
        assert r['loader_sha256']==sha(ROOT/'experiments/mc_rc_task_roles_input_cpu.py')
        assert {c['patient'] for c in prep['cases']}=={'VS-MC-RC-020','VS-MC-RC-022','VS-MC-RC-024','VS-MC-RC-025'} and len(prep['cases'])==9
        byuid={x['uid']:x for x in r['series']}
        for case in prep['cases']:
            resource_gate();uid=case['uid'];row=byuid[uid];heads=read(ROOT/case['header_file'])['records'];normal=np.cross(heads[0]['iop'][:3],heads[0]['iop'][3:]);ordered=sorted(heads,key=lambda x:np.asarray(x['ipp'])@normal);selected=ordered[::4]
            assert [x['zip_member'] for x in selected]==row['decoded_zip_members'];planes=[]
            with zipfile.ZipFile(ROOT/case['mr_zip_file']) as archive:
                for x in selected:
                    with archive.open(x['zip_member']) as f:d=pydicom.dcmread(f)
                    assert str(d.PatientID)==case['patient'] and str(d.SeriesInstanceUID)==uid and str(d.SOPInstanceUID)==x['sop_uid'] and str(d.StudyInstanceUID)==case['study_uid']
                    assert np.array_equal(np.asarray(d.ImagePositionPatient,dtype=float),x['ipp']);planes.append(d.pixel_array.astype(np.float32)*float(d.get('RescaleSlope',1))+float(d.get('RescaleIntercept',0)));q['observed_dicom_planes_verified']+=1
            anchors=np.stack(planes,axis=2);assert array_sha(anchors)==row['observed_array_sha256']
            assert sha(ROOT/row['observed_package'])==row['observed_package_sha256']
            with np.load(ROOT/row['observed_package'],allow_pickle=False) as pack:
                assert set(pack.files)=={'observed_rcz','observed_indices','native_shape','affine_rcz_ras'} and np.array_equal(pack['observed_rcz'],anchors) and list(pack['observed_indices'])==row['observed_indices']
            mean,std=manual_stats(anchors);assert np.isclose(mean,row['observed_stats']['mean'],rtol=1e-12,atol=1e-9) and np.isclose(std,row['observed_stats']['population_std'],rtol=1e-12,atol=1e-9)
            n=case['native_shape'][2];ix=list(range(0,n,4));missing=[z for z in range(ix[-1]) if z%4];tail=list(range(ix[-1]+1,n));assert row['domain_planes']==dict(anchors=len(ix),missing=len(missing),tail=len(tail))
            maxima={}
            for method in ('raw_linear','raw_pchip'):
                generated=independent_interp(anchors,n,method)
                # Independent formula may differ by float32 rounding at interpolation ties.
                from mc_rc_observed_only_training_input import ObservedMRI,reconstruct
                obs=ObservedMRI(anchors,tuple(ix),n,tuple(tuple(v) for v in case['affine_rcz_ras']),(),())
                producer=reconstruct(obs,method);maximum=float(np.max(np.abs(generated.astype(np.float64)-producer.astype(np.float64))));maxima[method]=maximum
                assert maximum<=max(1e-5,float(abs(producer).max())*2e-7) and np.array_equal(generated[:,:,ix],anchors)
                assert array_sha(producer)==row['inputs'][method+'_observed_shared']['raw_reconstruction_sha256']
                for policy in ('observed_shared','full_own'):
                    cell=row['inputs'][method+'_'+policy];src=anchors if policy=='observed_shared' else producer;m,s=manual_stats(src)
                    assert np.isclose(m,cell['statistics']['mean'],rtol=1e-12,atol=1e-9) and np.isclose(s,cell['statistics']['population_std'],rtol=1e-12,atol=1e-9)
                    # Use authenticated producer statistics to isolate permutation and dtype handling.
                    st=cell['statistics'];norm=((producer.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
                    assert array_sha(norm)==cell['normalized_rcz_sha256'] and array_sha(reorder(norm,cell['orientation']))==cell['normalized_ras_sha256'];q['sparse_inputs_verified']+=1
                del producer,generated
            label=label_by_axis(case);assert array_sha(label)==row['label_array_sha256'] and int(label.sum())==row['label_foreground']
            ori=row['inputs']['raw_pchip_observed_shared']['orientation'];raslabel=reorder(label,ori);assert array_sha(raslabel)==row['label_ras_sha256'];q['labels_verified']+=1
            q['series'].append(dict(patient=case['patient'],uid=uid,observed_planes=len(selected),input_cells_verified=4,label_axes_verified=True,independent_interpolation_max_abs_difference=maxima));print(json.dumps(q['series'][-1]),flush=True);del label,raslabel,anchors,planes
        q['independent_algorithms_reused_from_sha256']='14549b978af41657e7c437af500903eae39ac6e1177e5ad24f647db476bf941d'
        assert q['sparse_inputs_verified']==36 and q['labels_verified']==9 and 'torch' not in sys.modules;q['complete']=True
    except Exception as exc:q['errors'].append(type(exc).__name__+': '+str(exc));q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in q.items() if k!='series'},ensure_ascii=False));return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
