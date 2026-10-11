"""V2 serial forest fit; reuse frozen complete preparation from failed V1."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import hashlib,json,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/'tools/anchor_forest_runtime_v4_2026_10_07'
sys.path.insert(0,str(RUNTIME/'site_packages'))
import joblib
from sklearn.ensemble import ExtraTreesClassifier
from scipy import ndimage
from mc_rc_anchor_qda_cpu import feature_plane,normalization,observed_truth,fit_model,decision,FEATURES
from mc_rc_3d_baseline_v2_2026_10_07 import read,sha,array_sha,observed_package,resource_guard,lattice,physical_mr,tile_plan,PATCH,np,torch
from mc_rc_true_native_reference_v2_2026_10_07 import read_reference_label,DEVELOPERS
from mc_rc_native_competence_cpu import roi_summary
from mc_rc_frozen_predicted_region_cpu import task_counts
PREPARED=ROOT/'experiments/mc_rc_anchor_prior_forest_diagnostic_2026_10_07/attempt01.json'
OUT=ROOT/'experiments/mc_rc_anchor_prior_forest_diagnostic_v2_2026_10_07'
PREP=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json'
OBS=ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json'
PROTOCOL=ROOT/'MC_RC_ANCHOR_PRIOR_FOREST_DIAGNOSTIC_PROTOCOL_2026-10-07.md'
METHODS=('joint_QDA_empirical_prior_19','joint_QDA_balanced_prior_19','joint_ExtraTrees_balanced_19')
FOREST=dict(n_estimators=64,max_depth=16,max_leaf_nodes=256,min_samples_leaf=5,max_features='sqrt',bootstrap=False,random_state=20261007,n_jobs=1)
def stamp():return datetime.now(timezone.utc).isoformat()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def save(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(anchors,labels,c,norm):
    flat=labels.ravel();sampled=[];seeds=[];counts=[]
    for k in (0,1):
        eligible=np.flatnonzero(flat==bool(k));assert len(eligible)>0
        seed=int(hashlib.sha256(f'20261007|{c["uid"]}|{k}'.encode()).hexdigest()[:16],16)
        picked=np.sort(np.random.Generator(np.random.PCG64(seed)).choice(eligible,min(8192,len(eligible)),replace=False))
        sampled.append(picked);seeds.append(seed);counts.append(len(picked))
    chosen=np.concatenate(sampled);target=np.repeat([0,1],counts).astype(np.uint8);samples=np.empty((len(chosen),9),np.float32)
    total=labels.size;mass=np.zeros(2);first=np.zeros((2,9));second=np.zeros((2,9,9));planes=labels.shape[2]
    for j,z in enumerate(range(0,c['native_shape'][2],4)):
        features=feature_plane(anchors[:,:,j],z,c,norm);values=features.astype(np.float64);yy=labels[:,:,j].ravel()
        for k in (0,1):
            selected=values[yy==bool(k)];mass[k]+=len(selected)/total;first[k]+=selected.sum(0)/total;second[k]+=selected.T@selected/total
        ids=np.flatnonzero(chosen%planes==j);samples[ids]=features[chosen[ids]//planes]
    assert np.isfinite(samples).all() and np.array_equal(flat[chosen],target.astype(bool))
    return dict(mass=mass.tolist(),first=first.tolist(),second=second.tolist(),observed_pixels=total,observed_foreground=int(labels.sum())),samples,target,chosen,counts,seeds
def geometry_cost(native,c):
    grid=lattice(c);physical=physical_mr(native.astype(np.float32),grid)>0;locations,_=tile_plan(physical.shape)
    ids=[i for i,start in enumerate(locations) if physical[tuple(slice(s,s+p) for s,p in zip(start,PATCH))].any()]
    pairs=sorted({i//2 for i in ids});n=(len(locations)+1)//2;k=len(pairs)
    return dict(native_ROI_voxels=int(native.sum()),native_ROI_sha256=array_sha(native),physical_support_voxels=int(physical.sum()),physical_support_sha256=array_sha(physical),
        full_forward_calls=n,recomputed_batch_pairs=k,affected_tile_ids=ids,recomputed_batch_pair_ids=pairs,
        saved_forward_fraction=(n-k)/n,five_same_support_actions_with_initialization_count_ratio=(n+5*k)/(5*n),
        empty_ROI_no_proposed_edit=not native.any(),physical_grid=json.loads(json.dumps(grid)),tile_locations_zrc=[list(x) for x in locations])
def summaries(rows):
    patients=sorted({s['patient'] for s in rows});result=[]
    for method in METHODS:
        pairs=[(s,s['methods'][method]) for s in rows];means={}
        for p in patients:
            a=[m for s,m in pairs if s['patient']==p]
            means[p]=dict(observed_dice=sum(m['observed_task']['dice'] for m in a)/len(a),
                foreground_recall=sum(m['roi']['metrics']['foreground_recall'] for m in a)/len(a),
                boundary_recall=sum(m['roi']['metrics']['boundary_recall'] for m in a)/len(a),
                roi_fraction=sum(m['roi']['metrics']['roi_fraction'] for m in a)/len(a),
                saved_forward_fraction=sum(m['geometry_cost']['saved_forward_fraction'] for m in a)/len(a))
        result.append(dict(method=method,series=len(rows),patients=len(patients),ROI_gates_passed=sum(m['roi']['gate_passed'] for s,m in pairs),
            coverage_boundary_ge099_and_any_forward_saving=sum(m['roi']['metrics']['foreground_recall']>=.99 and m['roi']['metrics']['boundary_recall']>=.99 and m['geometry_cost']['saved_forward_fraction']>0 for s,m in pairs),
            empty_ROI_series=sum(m['geometry_cost']['empty_ROI_no_proposed_edit'] for s,m in pairs),
            all_batch_affected_series=sum(m['geometry_cost']['saved_forward_fraction']==0 for s,m in pairs),
            full_forward_calls_total=sum(m['geometry_cost']['full_forward_calls'] for s,m in pairs),recomputed_batch_pairs_total=sum(m['geometry_cost']['recomputed_batch_pairs'] for s,m in pairs),
            patient_means=means,patient_first_means={key:sum(v[key] for v in means.values())/len(means) for key in next(iter(means.values()))}))
    return result
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);started=time.perf_counter();dest=OUT/'attempt01.json'
    r=dict(created_utc=stamp(),complete=False,errors=[],active_stage='preparation',source_bindings=[],source_snapshots=[],series_statistics=[],folds=[],series=[],prediction_receipts=[],
        observed_MRI_packages_loaded=0,observed_label_arrays_loaded=0,full_development_GT_arrays_loaded=0,anchor_classifier_calls=0,QDA_moment_model_fits=0,
        balanced_prior_decision_variants=0,forest_models_fitted=0,neural_forwards=0,GPU_forwards=0,neural_training_updates=0,native_reference_MRI_arrays_loaded=0,
        confirmation_patients_opened=False,validation_data_read=False,publication_claim_confirmed=False,clinical_benefit_measured=False,workspace_read_paths=[],prohibited_access_attempts=[],other_processes_modified=False)
    allowed=set()
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if not p.is_relative_to(ROOT.parent.resolve()) or p.is_relative_to(OUT.resolve()) or p.is_relative_to(RUNTIME.resolve()):return
        if p not in allowed:r['prohibited_access_attempts'].append(str(p));raise PermissionError('Unlisted workspace access: '+str(p))
        rel=p.relative_to(ROOT).as_posix()
        if rel not in r['workspace_read_paths']:r['workspace_read_paths'].append(rel)
    def persist():save(dest,r)
    def guard():
        assert time.perf_counter()-started<1800;v=resource_guard()
        assert not torch.cuda.is_initialized() and torch.get_num_threads()==1 and torch.get_num_interop_threads()==1
        paths=[OUT,PREPARED.parent,ROOT/'tools/anchor_forest_runtime_2026_10_07',ROOT/'tools/anchor_forest_runtime_v2_2026_10_07',ROOT/'tools/anchor_forest_runtime_v3_2026_10_07',RUNTIME,ROOT/'tools/anchor_forest_joblib_tls12_2026_10_07']
        assert sum(p.stat().st_size for folder in paths for p in folder.rglob('*') if p.is_file())<250_000_000
        v.update(BLAS_threads=1,forest_fit_threads=1,forest_predict_threads=1);return v
    persist()
    try:
        r['resources_before']=guard()
        initial=[Path(__file__),PROTOCOL,PREP,OBS,RUNTIME/'install_attempt04.json',ROOT/'MC_RC_ANCHOR_PRIOR_FOREST_RUNTIME_ADDENDUM_2026-10-07.md',
            ROOT/'experiments/mc_rc_anchor_qda_cpu.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
            ROOT/'experiments/mc_rc_native_competence_cpu.py',ROOT/'experiments/mc_rc_frozen_predicted_region_cpu.py',ROOT/'experiments/mc_rc_observed_region_propagation.py',
            ROOT/'experiments/mc_rc_true_native_reference_v2_2026_10_07.py',ROOT/'experiments/mc_rc_true_native_reference_2026_10_07.py']
        initial.extend([PREPARED,ROOT/'MC_RC_ANCHOR_PRIOR_FOREST_SERIAL_EXECUTION_ADDENDUM_2026-10-07.md']);allowed.update(p.resolve() for p in initial);sys.addaudithook(audit)
        prepared=read(PREPARED);assert not prepared['complete'] and prepared['forest_models_fitted']==0 and prepared['full_development_GT_arrays_loaded']==0 and not prepared['prediction_receipts'] and len(prepared['series_statistics'])==19
        assert prepared['errors']==['PermissionError: [WinError 5] ?????'] and 'multiprocessing' in prepared['traceback']
        for binding in prepared['source_bindings']:allowed.add((ROOT/binding['path']).resolve());assert sha(ROOT/binding['path'])==binding['sha256']
        for row in prepared['series_statistics']:
            p=ROOT/row['training_sample_file']['path'];allowed.add(p.resolve());initial.append(p);assert sha(p)==row['training_sample_file']['sha256']
        install=read(initial[4]);assert install['complete'] and not install['errors']
        for v in install['installed_files']:assert sha(ROOT/v['path'])==v['sha256']
        prep=read(PREP);obs=read(OBS);assert prep['complete'] and obs['complete'] and not prep['errors'] and not obs['errors']
        cases=prep['cases'];by_obs={o['uid']:o for o in obs['series']};patients=sorted({c['patient'] for c in cases})
        assert len(cases)==19 and len(patients)==11 and set(patients)==DEVELOPERS
        for c in cases:
            for p in (ROOT/by_obs[c['uid']]['observed_package'],ROOT/c['label_file']):allowed.add(p.resolve());initial.append(p)
        r['source_bindings']=[entry(p) for p in initial];r['features']=FEATURES;r['forest_hyperparameters']=FOREST;r['primary']=METHODS[1]
        for i,p in enumerate(initial[:14]):
            snapshot=OUT/(f'{i:02d}_'+p.name+'.source_snapshot');snapshot.write_bytes(p.read_bytes());r['source_snapshots'].append(dict(source_path=p.relative_to(ROOT).as_posix(),snapshot=entry(snapshot)))
        r['series_statistics']=prepared['series_statistics']
        r['inherited_preparation']=dict(file=entry(PREPARED),observed_MRI_packages_loaded=prepared['observed_MRI_packages_loaded'],observed_label_arrays_loaded=prepared['observed_label_arrays_loaded'],all19_completed=True,new_preparation_arrays_loaded=0)
        persist()
        stats={s['uid']:s for s in r['series_statistics']};r['active_stage']='LOPO_fit_and_predict';persist()
        for patient in patients:
            guard();training=[s for s in r['series_statistics'] if s['patient']!=patient];assert len({s['patient'] for s in training})==10
            qda=fit_model(training,'joint_QDA');balanced=dict(qda,priors=[.5,.5]);r['QDA_moment_model_fits']+=1;r['balanced_prior_decision_variants']+=1
            xx=[];yy=[];ww=[];membership=[]
            for s in training:
                with np.load(ROOT/s['training_sample_file']['path'],allow_pickle=False) as pack:x=pack['features'];y=pack['labels']
                assert array_sha(x)==s['sample_features_sha256'] and array_sha(y)==s['sample_labels_sha256']
                count=sum(v['patient']==s['patient'] for v in training);w=np.empty(len(y),np.float64)
                for k in (0,1):w[y==k]=1/(10*count*2*int(np.count_nonzero(y==k)))
                xx.append(x);yy.append(y);ww.append(w);membership.append(dict(patient=s['patient'],uid=s['uid'],class_sample_counts=s['class_sample_counts'],series_weight=1/(10*count)))
            forest=ExtraTreesClassifier(**FOREST);forest.fit(np.concatenate(xx),np.concatenate(yy),sample_weight=np.concatenate(ww));forest.n_jobs=1;r['forest_models_fitted']+=1
            assert np.array_equal(forest.classes_,[0,1])
            modelfile=OUT/(patient+'_models.joblib');joblib.dump(dict(QDA_empirical=qda,QDA_balanced=balanced,forest=forest,membership=membership),modelfile,compress=3)
            fold=dict(patient=patient,training_patients=sorted({s['patient'] for s in training}),training_membership=membership,model=entry(modelfile),forest_nodes=sum(t.tree_.node_count for t in forest.estimators_))
            assert patient not in fold['training_patients'];r['folds'].append(fold);persist();del xx,yy,ww
            for i,c in [(i,c) for i,c in enumerate(cases) if c['patient']==patient]:
                guard();o=by_obs[c['uid']];obsdata=observed_package(c,o);r['observed_MRI_packages_loaded']+=1;s=stats[c['uid']]
                assert array_sha(obsdata.pixels)==s['observed_array_sha256'];pred={name:np.empty(obsdata.pixels.shape,bool) for name in METHODS};margins={name:float('inf') for name in METHODS}
                for j,z in enumerate(obsdata.indices):
                    guard();features=feature_plane(obsdata.pixels[:,:,j],z,c,s['normalization'])
                    scores=[decision(features,qda),decision(features,balanced),forest.predict_proba(features)[:,1]-.5]
                    for name,score in zip(METHODS,scores):
                        assert np.isfinite(score).all();pred[name][:,:,j]=(score>=0).reshape(obsdata.pixels.shape[:2]);margins[name]=min(margins[name],float(np.min(np.abs(score))));r['anchor_classifier_calls']+=1
                path=OUT/f'{i:02d}_anchor_predictions.npz';np.savez_compressed(path,**pred)
                receipt=dict(patient=patient,uid=c['uid'],model_sha256=fold['model']['sha256'],prediction_file=entry(path),prediction_array_sha256={k:array_sha(v) for k,v in pred.items()},
                    minimum_absolute_decision_margins=margins,full_GT_not_read_for_scoring_yet=True)
                save(OUT/f'{i:02d}_prediction_before_full_GT.json',receipt);r['prediction_receipts'].append(receipt);persist()
                print(json.dumps(dict(stage='prediction_frozen',patient=patient,series=len(r['prediction_receipts']))),flush=True)
        assert len(r['prediction_receipts'])==19 and r['full_development_GT_arrays_loaded']==0
        r['all19_predictions_saved_before_full_GT_scoring']=True;r['active_stage']='full_GT_scoring';persist();receipts={v['uid']:v for v in r['prediction_receipts']}
        for c in cases:
            guard();receipt=receipts[c['uid']];ref=read_reference_label(c);r['full_development_GT_arrays_loaded']+=1
            edge=ref&~ndimage.binary_erosion(ref,structure=ndimage.generate_binary_structure(3,1),border_value=0)
            n=c['native_shape'][2];targets=[z for z in range(1,(n-1)//4*4) if z%4];row=dict(patient=c['patient'],uid=c['uid'],complete=False,methods={})
            with np.load(ROOT/receipt['prediction_file']['path'],allow_pickle=False) as pack:
                for method in METHODS:
                    pred=pack[method];assert array_sha(pred)==receipt['prediction_array_sha256'][method]
                    full=np.zeros(c['native_shape'],bool);full[:,:,::4]=pred;roi=roi_summary(full,ref,edge,c,targets)
                    native=np.zeros(c['native_shape'],bool);cache={}
                    for z in targets:
                        j=z//4
                        if j not in cache:
                            union=pred[:,:,j]|pred[:,:,j+1];cache[j]=ndimage.distance_transform_edt(~union,sampling=c['native_spacing_rcz_mm'][:2])<=2.+1e-12 if union.any() else np.zeros(union.shape,bool)
                        native[:,:,z]=cache[j]
                    assert int(native.sum())==roi['metrics']['roi_voxels']
                    row['methods'][method]=dict(observed_task=task_counts(full,ref,np.arange(0,n,4)),roi=roi,geometry_cost=geometry_cost(native,c))
            row['complete']=True;r['series'].append(row);persist();print(json.dumps(dict(stage='scored',series=len(r['series']))),flush=True)
        r.update(summaries=summaries(r['series']),complete=len(r['series'])==19,active_stage='complete',resources_after=guard(),CUDA_initialized=torch.cuda.is_initialized())
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc();r['active_stage']='failed'
    r.update(elapsed_seconds=time.perf_counter()-started,finished_utc=stamp());persist()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','forest_models_fitted','observed_MRI_packages_loaded','observed_label_arrays_loaded','full_development_GT_arrays_loaded','summaries','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
