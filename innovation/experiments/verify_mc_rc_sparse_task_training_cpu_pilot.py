"""Independent saved-prediction counts/surface geometry and checkpoint plane replay."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import json,sys,traceback,hashlib
from pathlib import Path
from datetime import datetime,timezone
import nibabel as nib
from scipy.spatial import cKDTree
from vs_seg_task_cpu_support import resource_gate
from mc_rc_sparse_task_cpu_pilot_support import ROOT,SEED,PilotUNet,weight_hash,read,sha,array_sha,load_package,image_input,training_batch,np,torch
OUT=ROOT/'experiments/mc_rc_sparse_task_training_cpu_pilot'
def write(p,r):Path(p).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def independent_label(case):
    p=ROOT/case['label_file'];assert sha(p)==case['label_sha256'];raw=np.asanyarray(nib.load(p).dataobj);assert np.isin(raw,[0,1]).all()
    t=np.asarray(case['dicom_rcz_from_label_xyz'],int);axes=np.argmax(np.abs(t[:3,:3]),axis=1);assert len(set(axes))==3;result=np.transpose(raw,axes)
    for axis,src in enumerate(axes):
        sign=t[axis,src];assert sign in (-1,1)
        assert t[axis,3]==(result.shape[axis]-1 if sign==-1 else 0)
        if sign<0:result=np.flip(result,axis)
    return np.ascontiguousarray(result,dtype=bool)
def independent_counts(p,g):
    # Different count construction: encode the two binary labels and bincount each slice.
    sums=np.zeros(4,np.int64)
    for z in range(p.shape[2]):sums+=np.bincount((p[:,:,z].astype(np.uint8)+2*g[:,:,z].astype(np.uint8)).ravel(),minlength=4)
    tn,fp,fn,tp=map(int,sums);a=tp+fp;b=tp+fn
    return dict(tp=tp,fp=fp,fn=fn,gt_foreground=b,pred_foreground=a,dice=2*tp/(a+b) if a+b else None,precision=tp/a if a else None,recall=tp/b if b else None,signed_relative_volume_error=(a-b)/b if b else None,absolute_relative_volume_error=abs(a-b)/b if b else None,empty_ground_truth=b==0,empty_prediction=a==0)
def surface_points(x,affine):
    padded=np.pad(x,1);inside=x.copy()
    for axis in range(3):
        for direction in (-1,1):
            slices=[slice(1,1+n) for n in x.shape];slices[axis]=slice(1+direction,1+direction+x.shape[axis]);inside&=padded[tuple(slices)]
    xyz=np.argwhere(x&~inside);return xyz@np.asarray(affine)[:3,:3].T+np.asarray(affine)[:3,3]
def independent_surface(p,g,affine):
    if not p.any() or not g.any():return dict(assd_mm=None,hd95_mm=None)
    a,b=surface_points(p,affine),surface_points(g,affine);da=cKDTree(b).query(a,workers=1)[0];db=cKDTree(a).query(b,workers=1)[0];dist=np.sort(np.concatenate([da,db]));q=(len(dist)-1)*.95;lo=int(q);hi=min(lo+1,len(dist)-1)
    return dict(assd_mm=float(dist.sum()/len(dist)),hd95_mm=float(dist[lo]*(1-(q-lo))+dist[hi]*(q-lo)),pred_surface_voxels=len(a),gt_surface_voxels=len(b))
def locations(n):
    values=[0]
    while values[-1]+96<n:values.append(min(values[-1]+64,n-96))
    return values
def independent_plane(model,image,z):
    rows,cols=locations(image.shape[0]),locations(image.shape[1]);loc=[(r,c) for r in rows for c in cols];scores=np.zeros(image.shape[:2],np.float64);coverage=np.zeros(image.shape[:2],np.int64)
    with torch.inference_mode():
        for start in range(0,len(loc),4):
            chunk=loc[start:start+4];batch=[]
            for r,c in chunk:batch.append(np.stack([image[r:r+96,c:c+96,min(max(z+delta,0),image.shape[2]-1)] for delta in (-2,-1,0,1,2)]))
            output=model(torch.from_numpy(np.stack(batch))).sigmoid().numpy()[:,0]
            for (r,c),v in zip(chunk,output):scores[r:r+96,c:c+96]+=v;coverage[r:r+96,c:c+96]+=1
    assert coverage.min()>0;return scores/coverage>=.5,coverage,rows,cols
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();source=OUT/'attempt_01.json';r=read(source);path=OUT/'independent_metrics_and_checkpoint_attempt_01.json';assert not path.exists();assert r['complete'] and not r['errors']
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),result_sha256=sha(source),evaluations=[],checkpoint_replayed_planes=0,development_only=True,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,q)
    try:
        assert r['updates_completed']==4000 and sum(r['training_sampling_counts'].values())==4000 and 'VS-MC-RC-013' not in r['training_patient_ids']
        prep=read(ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json');cases={x['uid']:x for x in prep['cases']};assert len(r['training_series_uids'])==18 and all(cases[u]['patient']!='VS-MC-RC-013' for u in r['training_series_uids'])
        assert set(r['training_patient_ids'])=={cases[u]['patient'] for u in r['training_series_uids']}
        production=read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json');by={x['uid']:x for x in production['series']}
        torch.manual_seed(SEED);model=PilotUNet();assert weight_hash(model)==r['initial_weights_sha256'];ck=ROOT/r['checkpoint_file'];assert sha(ck)==r['checkpoint_sha256'];checkpoint=torch.load(ck,map_location='cpu',weights_only=True)
        assert checkpoint['training_patient_ids']==r['training_patient_ids'] and checkpoint['training_series_uids']==r['training_series_uids'];model.load_state_dict(checkpoint['state_dict']);assert weight_hash(model)==r['final_weights_sha256'];model.eval()
        for e in r['evaluations']:
            resource_gate();case=cases[e['uid']];g=independent_label(case);assert array_sha(g)==e['label_array_sha256'];predfile=ROOT/e['prediction_file'];assert sha(predfile)==e['prediction_file_sha256']
            with np.load(predfile,allow_pickle=False) as data:p=np.array(data['prediction_rcz'],copy=True)
            assert p.dtype==bool and p.shape==g.shape and array_sha(p)==e['prediction_array_sha256'];n=p.shape[2];last=((n-1)//4)*4
            domains={'full':np.arange(n),'anchors':np.arange(0,n,4),'missing':np.asarray([z for z in range(last) if z%4]),'tail':np.arange(last+1,n)}
            recomputed={}
            for name,zs in domains.items():
                counts=independent_counts(p[:,:,zs],g[:,:,zs]);assert all(counts[k]==e['metrics'][name][k] for k in counts);recomputed[name]=counts
            surf=independent_surface(p,g,case['affine_rcz_ras']);original=e['metrics']['full_surface']
            for key,value in surf.items():
                if value is None:assert original[key] is None
                else:assert abs(value-original[key])<.0001
            o=load_package(case,by[e['uid']]);image,st=image_input(o,e['method'],by[e['uid']]);assert array_sha(image)==e['input_sha256']
            replay=[]
            for z in (0,n//2,n-1):
                direct,cov,rs,cs=independent_plane(model,image,z);assert np.array_equal(direct,p[:,:,z]);assert rs==e['coverage']['row_starts'] and cs==e['coverage']['col_starts'];assert array_sha(cov.astype(np.uint16))==e['coverage']['coverage_sha256'];replay.append(z);q['checkpoint_replayed_planes']+=1
            row=dict(patient=e['patient'],method=e['method'],counts=recomputed,independent_kdtree_surface=surf,checkpoint_replayed_planes=replay,coverage_verified=True);q['evaluations'].append(row);write(path,q);print(json.dumps(dict(patient=e['patient'],method=e['method'],all_counts_verified=True,physical_surface_verified=True,checkpoint_planes=len(replay))),flush=True)
            del image,p,g
        # Frozen model on supervised training patches: diagnosis only, no optimizer or choices.
        case=next(c for c in cases.values() if c['patient']=='VS-MC-RC-012');o=load_package(case,by[case['uid']]);image,_=image_input(o,'raw_pchip',by[case['uid']]);label=independent_label(case);rng=np.random.default_rng(SEED+1);item=dict(image=image,label=label,foreground=np.argwhere(label));diagnosis=[]
        with torch.inference_mode():
            for j in range(25):
                x,y=training_batch(item,rng);pred=model(x).sigmoid().numpy()[:,0]>=.5;gt=y.numpy()[:,0].astype(bool)
                for k in range(4):
                    cc=independent_counts(pred[k,:,:,None],gt[k,:,:,None]);diagnosis.append(dict(batch=j,index=k,sampler='foreground_centered' if k<2 else 'uniform_full_FOV',**cc))
        q['frozen_model_training_patch_diagnosis']=diagnosis;q['neural_forward_calls']=model.forward_calls;q['gpu_initialized']=torch.cuda.is_initialized();assert not q['gpu_initialized'];q['complete']=len(q['evaluations'])==4 and q['checkpoint_replayed_planes']==12
    except Exception as e:q['errors'].append(type(e).__name__+': '+str(e));q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,q);print(json.dumps({k:q.get(k) for k in ('complete','errors','checkpoint_replayed_planes','neural_forward_calls','gpu_initialized','scientific_confirmation_patients')}),flush=True);return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
