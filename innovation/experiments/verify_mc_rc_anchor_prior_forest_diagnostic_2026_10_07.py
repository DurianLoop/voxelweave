"""Independent label/moments, Cholesky QDA, refitted trees and leaf accumulation.

Shared old observed feature extractor/SciPy filters and sklearn tree traversal.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[name]='1'
import hashlib,itertools,json,math,sys,time,traceback
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/'tools/anchor_forest_runtime_v4_2026_10_07'
sys.path.insert(0,str(RUNTIME/'site_packages'))
import joblib,nibabel as nib,numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from scipy.ndimage import binary_dilation
from mc_rc_anchor_qda_cpu import feature_plane,normalization
from mc_rc_reference_resources_2026_10_07 import resource_guard
OUT=ROOT/'experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07'
METHODS=('joint_QDA_empirical_prior_19','joint_QDA_balanced_prior_19','joint_ExtraTrees_balanced_19')
PATCH=(64,128,128)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()
def array_hash(a):
    a=np.ascontiguousarray(a);h=hashlib.sha256(json.dumps(dict(shape=list(a.shape),dtype=a.dtype.str),sort_keys=True).encode());h.update(memoryview(a).cast('B'));return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def observed_labels(c):
    img=nib.load(ROOT/c['label_file']);inverse=np.rint(np.linalg.inv(np.asarray(c['dicom_rcz_from_label_xyz']))).astype(int)
    rr,cc=np.indices(c['native_shape'][:2]);coords=np.stack([rr.ravel(),cc.ravel(),np.zeros(rr.size,dtype=int)]);planes=[];indices=[]
    for z in range(0,c['native_shape'][2],4):
        coords[2]=z;xyz=inverse[:3,:3]@coords+inverse[:3,3,None];axes=[i for i in range(3) if np.ptp(xyz[i])==0];assert len(axes)==1
        axis=axes[0];index=int(xyz[axis,0]);selection=[slice(None)]*3;selection[axis]=index
        slab=np.asanyarray(img.dataobj[tuple(selection)]);assert slab.nbytes<=32_000_000 and np.isin(slab,[0,1]).all()
        planes.append(slab[tuple(xyz[i] for i in range(3) if i!=axis)].reshape(c['native_shape'][:2]).astype(bool))
        indices.append(dict(native_z=z,label_axis=axis,label_index=index))
    return np.stack(planes,axis=2),indices
def full_truth(c):
    image=nib.load(ROOT/c['label_file']);raw=np.empty(image.shape,bool)
    for z in range(0,image.shape[2],4):
        slab=np.asanyarray(image.dataobj[:,:,z:z+4]);assert slab.nbytes<=32_000_000 and np.isin(slab,[0,1]).all();raw[:,:,z:z+4]=slab
    matrix=np.rint(c['dicom_rcz_from_label_xyz']).astype(int);axes=np.argmax(np.abs(matrix[:3,:3]),axis=1);value=raw.transpose(axes)
    for axis,column in enumerate(axes):
        assert matrix[axis,3]==(value.shape[axis]-1 if matrix[axis,column]<0 else 0)
        if matrix[axis,column]<0:value=np.flip(value,axis)
    return np.ascontiguousarray(value)
def boundary(value):
    core=value.copy()
    for axis in range(3):
        for step in (-1,1):
            at=[slice(None)]*3;neighbor=at.copy();at[axis]=slice(1,None) if step<0 else slice(None,-1);neighbor[axis]=slice(None,-1) if step<0 else slice(1,None)
            core[tuple(at)]&=value[tuple(neighbor)]
        for edge in (0,-1):at=[slice(None)]*3;at[axis]=edge;core[tuple(at)]=False
    return value&~core
def compare(a,b):
    if isinstance(b,float):assert math.isclose(a,b,rel_tol=0,abs_tol=1e-12),(a,b)
    elif isinstance(b,dict):
        assert set(a)==set(b)
        for key in b:compare(a[key],b[key])
    else:assert a==b,(a,b)
def center_neighbors(n,m):
    low=[];high=[]
    for j in range(m):
        q=max(Fraction(0),min(Fraction((2*j+1)*n-m,2*m),Fraction(n-1)))
        low.append(q.numerator//q.denominator);high.append(-((-q.numerator)//q.denominator))
    return np.array(low),np.array(high)
def physical_support(native,grid):
    out=native.transpose(2,0,1).copy()
    for axis,(n,m) in enumerate(zip(out.shape,grid['unpadded_shape_zrc'])):
        low,high=center_neighbors(n,m);out=np.take(out,low,axis=axis)|np.take(out,high,axis=axis)
    return np.pad(out,grid['padding'],mode='constant',constant_values=False)
def qda_score(features,model):
    x=features.astype(np.float64);values=[]
    for k in (0,1):
        chol=np.linalg.cholesky(model['covariances'][k]);white=np.linalg.solve(chol,(x-np.array(model['means'][k])).T)
        values.append(np.log(model['priors'][k])-np.log(np.diag(chol)).sum()-.5*(white*white).sum(axis=0))
    return values[1]-values[0]
def forest_score(features,forest):
    result=np.zeros(len(features),np.float64)
    for tree in forest.estimators_:
        leaf=tree.apply(features);value=tree.tree_.value[leaf,0,:];result+=value[:,1]/value.sum(axis=1)
    return result/len(forest.estimators_)-.5
def roi_metrics(mask,truth,edge,targets):
    rows,cols=truth.shape[:2];counts=dict(roi_voxels=0,true_positive_voxels=0,boundary_covered_voxels=0,selected_tiles=0,tile_area_voxels=0,tile_true_positive_voxels=0);records=[]
    for z in targets:
        p=mask[:,:,z];t=truth[:,:,z];b=edge[:,:,z];expanded=np.zeros(p.shape,bool);selected=0
        for r in range(0,rows,32):
            for c in range(0,cols,32):
                sl=(slice(r,min(rows,r+32)),slice(c,min(cols,c+32)))
                if p[sl].any():expanded[sl]=True;selected+=1
        per=dict(roi_voxels=int(p.sum()),true_positive_voxels=int((p&t).sum()),boundary_covered_voxels=int((p&b).sum()),selected_tiles=selected,tile_area_voxels=int(expanded.sum()),tile_true_positive_voxels=int((expanded&t).sum()))
        for k,v in per.items():counts[k]+=v
        records.append(dict(z=z,counts=per))
    foreground=sum(int(truth[:,:,z].sum()) for z in targets);nb=sum(int(edge[:,:,z].sum()) for z in targets);area=len(targets)*rows*cols;roi=counts['roi_voxels'];tp=counts['true_positive_voxels']
    m=dict(counts,foreground_recall=tp/foreground if foreground else None,boundary_recall=counts['boundary_covered_voxels']/nb if nb else None,
        roi_precision=tp/roi if roi else None,geometric_mask_dice=2*tp/(roi+foreground) if roi+foreground else None,
        roi_fraction=roi/area,roi_foreground_inflation=roi/foreground if foreground else None,
        tile_foreground_recall=counts['tile_true_positive_voxels']/foreground if foreground else None,tile_fraction=counts['tile_area_voxels']/area)
    return dict(metrics=m,gate_passed=bool(m['foreground_recall']>=.99 and m['boundary_recall']>=.99 and m['tile_foreground_recall']>=.995 and m['roi_fraction']<=.05 and m['tile_fraction']<=.10),target_records=records)
def main():
    sys.stdout.reconfigure(encoding='utf-8');dest=OUT/'independent_label_models_roi_attempt01.json';assert not dest.exists();started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],checked_series=0,checked_candidate_supports=0,checked_missing_plane_records=0,
        forest_models_refitted=0,forest_trees_compared=0,QDA_models_rederived=0,observed_MRI_packages_loaded=0,observed_label_arrays_loaded=0,full_development_GT_arrays_loaded=0,
        fresh_anchor_classifier_calls=0,native_reference_MRI_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,neural_training_updates=0,confirmation_patients_opened=False,validation_data_read=False,
        publication_claim_confirmed=False,workspace_read_paths=[],prohibited_access_attempts=[],shared_components=['old feature_plane/normalization and SciPy filters','sklearn ExtraTrees training/tree.apply; independent leaf aggregation'],source_bindings=[])
    allowed=set()
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if not p.is_relative_to(ROOT.parent.resolve()) or p.is_relative_to(OUT.resolve()) or p.is_relative_to(RUNTIME.resolve()):return
        if p not in allowed:r['prohibited_access_attempts'].append(str(p));raise PermissionError('Unlisted workspace access: '+str(p))
        name=p.relative_to(ROOT).as_posix()
        if name not in r['workspace_read_paths']:r['workspace_read_paths'].append(name)
    def save():dest.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():assert time.perf_counter()-started<1800;return resource_guard()
    save()
    try:
        r['resources_before']=guard();sys.addaudithook(audit);prod=read(OUT/'attempt01.json');assert prod['complete'] and not prod['errors'] and not prod['prohibited_access_attempts']
        allowed.update((ROOT/x['path']).resolve() for x in prod['source_bindings']);allowed.add(Path(__file__).resolve())
        for x in prod['source_bindings']:assert sha(ROOT/x['path'])==x['sha256']
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (Path(__file__),OUT/'attempt01.json')]
        (OUT/(Path(__file__).name+'.source_snapshot')).write_bytes(Path(__file__).read_bytes())
        cases=read(ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json')['cases'];obs={v['uid']:v for v in read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json')['series']}
        source={v['uid']:v for v in prod['series_statistics']};rows={v['uid']:v for v in prod['series']};receipt={v['uid']:v for v in prod['prediction_receipts']};assert len(source)==len(rows)==len(receipt)==len(cases)==19
        recomputed={};sample_data={}
        for c in cases:
            guard();s=source[c['uid']];o=obs[c['uid']]
            with np.load(ROOT/o['observed_package'],allow_pickle=False) as pack:anchors=pack['observed_rcz'].copy()
            r['observed_MRI_packages_loaded']+=1;assert array_hash(anchors)==s['observed_array_sha256']==o['observed_array_sha256']
            labels,indices=observed_labels(c);r['observed_label_arrays_loaded']+=1
            assert array_hash(labels)==s['observed_label_array_sha256'] and indices==s['label_decoded_planes']
            norm=normalization(anchors);assert norm==s['normalization']
            with np.load(ROOT/s['training_sample_file']['path'],allow_pickle=False) as pack:x=pack['features'].copy();y=pack['labels'].copy();chosen=pack['flat_rcz_indices'].copy()
            assert array_hash(x)==s['sample_features_sha256'] and array_hash(y)==s['sample_labels_sha256'] and array_hash(chosen)==s['sampled_indices_sha256']
            expected=[]
            for k in (0,1):
                ids=np.flatnonzero(labels.ravel()==bool(k));seed=int(hashlib.sha256(f'20261007|{c["uid"]}|{k}'.encode()).hexdigest()[:16],16)
                expected.append(np.sort(np.random.Generator(np.random.PCG64(seed)).choice(ids,min(len(ids),8192),replace=False)))
            assert np.array_equal(chosen,np.concatenate(expected)) and np.array_equal(labels.ravel()[chosen],y.astype(bool))
            n=labels.size;mass=np.zeros(2);first=np.zeros((2,9));second=np.zeros((2,9,9));fresh_samples=np.empty(x.shape,np.float32)
            for j,z in enumerate(range(0,c['native_shape'][2],4)):
                features=feature_plane(anchors[:,:,j],z,c,norm);f=features.astype(np.float64);truth=labels[:,:,j].ravel()
                for k in (0,1):
                    v=f[truth==bool(k)];m=len(v)
                    if not m:continue
                    avg=v.mean(axis=0);center=v-avg;mass[k]+=m/n;first[k]+=m*avg/n;second[k]+=(center.T@center+m*np.outer(avg,avg))/n
                ids=np.flatnonzero(chosen%labels.shape[2]==j);fresh_samples[ids]=features[chosen[ids]//labels.shape[2]]
            assert np.array_equal(fresh_samples,x)
            for key,value in [('mass',mass),('first',first),('second',second)]:assert np.allclose(value,s['moments'][key],rtol=1e-10,atol=1e-11),(c['uid'],key)
            recomputed[c['uid']]=dict(patient=c['patient'],mass=mass,first=first,second=second);sample_data[c['uid']]=(x,y)
        for fold in prod['folds']:
            guard();patient=fold['patient'];members=[c for c in cases if c['patient']!=patient];people={c['patient'] for c in members};assert len(people)==10 and patient not in people
            assert fold['training_patients']==sorted(people) and sha(ROOT/fold['model']['path'])==fold['model']['sha256']
            models=joblib.load(ROOT/fold['model']['path']);mass=np.zeros(2);first=np.zeros((2,9));second=np.zeros((2,9,9));xx=[];yy=[];ww=[];membership=[]
            for c in members:
                count=sum(m['patient']==c['patient'] for m in members);weight=1/(10*count);s=recomputed[c['uid']];mass+=weight*s['mass'];first+=weight*s['first'];second+=weight*s['second']
                x,y=sample_data[c['uid']];w=np.empty(len(y),np.float64)
                # Canonical weight expression is an input contract; association
                # changes would make an exact tree-array comparison invalid.
                for k in (0,1):w[y==k]=1/(10*count*2*int(np.count_nonzero(y==k)))
                xx.append(x);yy.append(y);ww.append(w);membership.append(dict(patient=c['patient'],uid=c['uid'],class_sample_counts=[int(np.count_nonzero(y==k)) for k in (0,1)],series_weight=weight))
            assert membership==fold['training_membership']==models['membership']
            means=first/mass[:,None];covariances=[]
            for k in (0,1):
                cov=second[k]/mass[k]-np.outer(means[k],means[k]);cov=(cov+cov.T)/2;covariances.append(.9*cov+.1*np.diag(np.diag(cov))+1e-4*np.eye(9))
            for name,priors in [('QDA_empirical',mass),('QDA_balanced',[.5,.5])]:
                q=models[name];assert np.allclose(q['means'],means,rtol=1e-10,atol=1e-11) and np.allclose(q['covariances'],covariances,rtol=1e-10,atol=1e-11)
                assert np.allclose(q['priors'],priors,rtol=1e-10,atol=1e-11);r['QDA_models_rederived']+=1
            refitted=ExtraTreesClassifier(**prod['forest_hyperparameters']);refitted.fit(np.concatenate(xx),np.concatenate(yy),sample_weight=np.concatenate(ww));refitted.n_jobs=1
            assert len(refitted.estimators_)==64
            for new,old in zip(refitted.estimators_,models['forest'].estimators_):
                for key in ('children_left','children_right','feature','threshold','value','n_node_samples','weighted_n_node_samples'):
                    assert np.array_equal(getattr(new.tree_,key),getattr(old.tree_,key)),(patient,key)
                r['forest_trees_compared']+=1
            r['forest_models_refitted']+=1;del xx,yy,ww,refitted
            for c in [c for c in cases if c['patient']==patient]:
                guard();s=source[c['uid']];o=obs[c['uid']];stored=rows[c['uid']];rec=receipt[c['uid']]
                with np.load(ROOT/o['observed_package'],allow_pickle=False) as pack:anchors=pack['observed_rcz'].copy()
                r['observed_MRI_packages_loaded']+=1;assert array_hash(anchors)==s['observed_array_sha256']
                assert sha(ROOT/rec['prediction_file']['path'])==rec['prediction_file']['sha256']
                preds={m:np.empty(anchors.shape,bool) for m in METHODS}
                for j,z in enumerate(range(0,c['native_shape'][2],4)):
                    guard();features=feature_plane(anchors[:,:,j],z,c,s['normalization'])
                    scores=[qda_score(features,models['QDA_empirical']),qda_score(features,models['QDA_balanced']),forest_score(features,models['forest'])]
                    for method,score in zip(METHODS,scores):preds[method][:,:,j]=(score>=0).reshape(anchors.shape[:2]);r['fresh_anchor_classifier_calls']+=1
                with np.load(ROOT/rec['prediction_file']['path'],allow_pickle=False) as pack:
                    for m in METHODS:assert np.array_equal(preds[m],pack[m]) and array_hash(preds[m])==rec['prediction_array_sha256'][m],(c['uid'],m)
                truth=full_truth(c);r['full_development_GT_arrays_loaded']+=1;assert int(truth.sum())==c['expected_label_foreground_voxels'];edge=boundary(truth)
                targets=[z for z in range(1,(truth.shape[2]-1)//4*4) if z%4]
                sr,sc=c['native_spacing_rcz_mm'][:2];rr,cc=math.ceil(2/sr),math.ceil(2/sc);disk=np.hypot(np.arange(-rr,rr+1)[:,None]*sr,np.arange(-cc,cc+1)[None,:]*sc)<=2.+1e-12
                for method in METHODS:
                    pred=preds[method];pp=int(pred.sum());tt=int(truth[:,:,::4].sum());tp=int((pred&truth[:,:,::4]).sum());expected=dict(predicted_voxels=pp,truth_voxels=tt,true_positive_voxels=tp,dice=2*tp/(pp+tt) if pp+tt else None,recall=tp/tt if tt else None,precision=tp/pp if pp else None)
                    compare(stored['methods'][method]['observed_task'],expected)
                    native=np.zeros(truth.shape,bool);cache={}
                    for z in targets:
                        j=z//4
                        if j not in cache:cache[j]=binary_dilation(pred[:,:,j]|pred[:,:,j+1],structure=disk,border_value=0)
                        native[:,:,z]=cache[j]
                    compare(stored['methods'][method]['roi'],roi_metrics(native,truth,edge,targets))
                    g=stored['methods'][method]['geometry_cost'];assert int(native.sum())==g['native_ROI_voxels'] and array_hash(native)==g['native_ROI_sha256']
                    physical=physical_support(native,g['physical_grid']);assert int(physical.sum())==g['physical_support_voxels'] and array_hash(physical)==g['physical_support_sha256']
                    starts=[sorted(set(range(0,n-p+1,p//2))|{n-p}) for n,p in zip(physical.shape,PATCH)];locations=list(itertools.product(*starts));assert [list(x) for x in locations]==g['tile_locations_zrc']
                    ids=[i for i,start in enumerate(locations) if physical[tuple(slice(s,s+p) for s,p in zip(start,PATCH))].any()];pairs=sorted({i//2 for i in ids});n=(len(locations)+1)//2;k=len(pairs)
                    assert ids==g['affected_tile_ids'] and pairs==g['recomputed_batch_pair_ids'] and n==g['full_forward_calls'] and k==g['recomputed_batch_pairs']
                    compare(g['saved_forward_fraction'],float(Fraction(n-k,n)));compare(g['five_same_support_actions_with_initialization_count_ratio'],float(Fraction(n+5*k,5*n)))
                    r['checked_candidate_supports']+=1;r['checked_missing_plane_records']+=len(targets)
                r['checked_series']+=1;save();print(json.dumps(dict(stage='independent_replay',series=r['checked_series'],forests=r['forest_models_refitted'])),flush=True)
        assert r['checked_series']==19 and r['checked_candidate_supports']==57 and r['forest_trees_compared']==704
        # Summaries recomputed from independently checked scalar endpoints.
        exact=[]
        for summary in prod['summaries']:
            method=summary['method'];patients=sorted({c['patient'] for c in cases});means={}
            for patient in patients:
                members=[s['methods'][method] for s in prod['series'] if s['patient']==patient]
                means[patient]=dict(observed_dice=sum(v['observed_task']['dice'] for v in members)/len(members),foreground_recall=sum(v['roi']['metrics']['foreground_recall'] for v in members)/len(members),boundary_recall=sum(v['roi']['metrics']['boundary_recall'] for v in members)/len(members),roi_fraction=sum(v['roi']['metrics']['roi_fraction'] for v in members)/len(members),saved_forward_fraction=float(sum(Fraction(v['geometry_cost']['full_forward_calls']-v['geometry_cost']['recomputed_batch_pairs'],v['geometry_cost']['full_forward_calls']) for v in members)/len(members)))
            compare(summary['patient_means'],means);compare(summary['patient_first_means'],{key:sum(v[key] for v in means.values())/11 for key in next(iter(means.values()))})
            a=[s['methods'][method] for s in prod['series']]
            assert summary['series']==19 and summary['patients']==11
            assert sum(v['geometry_cost']['empty_ROI_no_proposed_edit'] for v in a)==summary['empty_ROI_series']
            assert sum(v['geometry_cost']['saved_forward_fraction']==0 for v in a)==summary['all_batch_affected_series']
            assert sum(v['geometry_cost']['full_forward_calls'] for v in a)==summary['full_forward_calls_total']
            assert sum(v['geometry_cost']['recomputed_batch_pairs'] for v in a)==summary['recomputed_batch_pairs_total']
            assert sum(v['roi']['gate_passed'] for v in a)==summary['ROI_gates_passed']
            assert sum(v['roi']['metrics']['foreground_recall']>=.99 and v['roi']['metrics']['boundary_recall']>=.99 and v['geometry_cost']['saved_forward_fraction']>0 for v in a)==summary['coverage_boundary_ge099_and_any_forward_saving']
            exact.append(dict(method=method,patient_first_saving_fraction=str(sum(sum(Fraction(s['methods'][method]['geometry_cost']['full_forward_calls']-s['methods'][method]['geometry_cost']['recomputed_batch_pairs'],s['methods'][method]['geometry_cost']['full_forward_calls']) for s in prod['series'] if s['patient']==p)/sum(s['patient']==p for s in prod['series']) for p in patients)/11)))
        r.update(complete=True,exact_fraction_summaries=exact,resources_after=guard())
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-started,finished_utc=datetime.now(timezone.utc).isoformat());save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','checked_series','checked_candidate_supports','forest_models_refitted','forest_trees_compared','fresh_anchor_classifier_calls','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
