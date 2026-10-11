"""Recompute feature/label SHA, all tile outputs and complete FOV via the module network."""
import hashlib,json,math,sys,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,physical_mr,lattice,
    physical_label,read_reference_label,sample_batch,TaskUNet3D,tile_plan,infer_full_fov,PATCH,torch,np,SEED)
from mc_rc_3d_independent_replay_2026_10_07 import logical_counts
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_all_tile_head_fit_2026_10_07'
def array_stream_hasher(shape):
    h=hashlib.sha256(json.dumps(dict(shape=list(shape),dtype=np.dtype(np.float32).str),sort_keys=True).encode());return h
def main():
    sys.stdout.reconfigure(encoding='utf-8');path=OUT/'module_features_and_full_fov_verification_attempt01.json';assert not path.exists()
    prodpath=OUT/'attempt01.json';prod=read(prodpath)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],arms=[],script_sha256=sha(__file__),
           result_sha256=sha(prodpath),source_bindings=prod['source_bindings'],actual_training_updates=0,actual_gpu_updates=0,
           validation_effects_opened=False,confirmation_patients_opened=False,scientific_confirmation_patients=0,
           second_independently_trained_task_network=False)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        assert prod['complete'] and not prod['errors'] and prod['actual_patient_cpu_head_parameter_updates']==2048
        for binding in prod['source_bindings']:assert sha(ROOT/binding['path'])==binding['sha256']
        resource_guard();role,case,row=fixed_cases()[0];assert role=='development' and case['patient']=='VS-MC-RC-001'
        grid=lattice(case);label=read_reference_label(case);target=physical_label(label,grid);vox=int(np.prod(PATCH))
        for arm in prod['arms']:
            resource_guard();assert arm['complete'] and arm['evaluation_complete'] and arm['updates_completed']==1024
            history=arm['history'];assert len(history)==1024 and [h['update'] for h in history]==list(range(1,1025))
            assert all(h['lr']==.01 and all(math.isfinite(h[k]) for k in ('bce','soft_dice','weighted_loss')) for h in history)
            src=ROOT/arm['source_checkpoint_file'];cp=ROOT/arm['checkpoint_file']
            assert sha(src)==arm['source_checkpoint_sha256'] and sha(cp)==arm['checkpoint_sha256']
            original=torch.load(src,map_location='cpu',weights_only=True)['state_dict']
            stored=torch.load(cp,map_location='cpu',weights_only=True);state=stored['state_dict']
            assert state_hash(state)==stored['final_weights_sha256']==arm['final_weights_sha256']
            assert stored['updates']==1024 and stored['protocol_sha256']==sha(ROOT/'MC_RC_3D_ALL_TILE_HEAD_FIT_PROTOCOL_2026-10-07.md')
            fixed=0
            for k in original:
                if not k.startswith('heads.2.'):assert torch.equal(original[k],state[k]);fixed+=1
            assert fixed==arm['fixed_backbone_state_entries']==52
            model=TaskUNet3D();model.load_state_dict(state,strict=True);model.eval();model.requires_grad_(False)
            normalized,stats=source_image(case,row,arm['kind']);image=physical_mr(normalized,grid)
            assert array_sha(image)==arm['physical_input_sha256'] and array_sha(target)==arm['physical_label_sha256']
            locations,starts=tile_plan(image.shape);assert [list(p) for p in locations]==arm['tile_locations'] and starts==arm['axis_starts']
            feature_hash=array_stream_hasher((len(locations)*vox,16));label_hash=array_stream_hasher((len(locations)*vox,))
            cache=[];hook=model.heads[-1].register_forward_pre_hook(lambda module,args:cache.append(args[0].detach()))
            label_counts=[];tile_metrics=[];ce_sum=0.;p_sum=0.;g_sum=0.;pg_sum=0.
            for at in range(0,len(locations),2):
                resource_guard();slabs=[tuple(slice(s,s+p) for s,p in zip(start,PATCH)) for start in locations[at:at+2]]
                x=torch.from_numpy(np.stack([image[sl] for sl in slabs])[:,None]);y=np.stack([target[sl] for sl in slabs])[:,None]
                with torch.inference_mode():outputs=model(x)
                assert len(cache)==1;features=cache.pop().permute(0,2,3,4,1).reshape(-1,16).contiguous().numpy()
                feature_hash.update(memoryview(features).cast('B'));label_hash.update(memoryview(np.ascontiguousarray(y.reshape(-1))).cast('B'))
                z=outputs[0].numpy().astype(np.float64);truth=y.astype(np.float64);prob=1/(1+np.exp(-z))
                ce_sum+=float(np.sum(np.logaddexp(0,z)-z*truth));p_sum+=float(prob.sum());g_sum+=float(truth.sum());pg_sum+=float((prob*truth).sum())
                label_counts.extend(int(t.sum()) for t in y)
                tile_metrics.extend(logical_counts(p>=0,g>=.5) for p,g in zip(outputs[0].numpy()[:,0],y[:,0]))
                del x,y,outputs,features,z,truth,prob
            hook.remove();assert feature_hash.hexdigest()==arm['feature_matrix_sha256'] and label_hash.hexdigest()==arm['label_vector_sha256']
            assert label_counts==arm['label_foreground_by_tile'] and tile_metrics==arm['last_all_tile_metrics']
            sd=(2*pg_sum+1)/(p_sum+g_sum+1);ce=ce_sum/(len(locations)*vox)
            assert abs(sd-arm['final_training_objective']['soft_dice'])<=3e-6 and abs(ce-arm['final_training_objective']['bce'])<=3e-6
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED))
            with torch.inference_mode():o=model(x)[0]
            for p,g,m in zip(o.numpy()[:,0],y.numpy()[:,0],arm['original_fixed_batch_patch_metrics']):assert logical_counts(p>=0,g>=.5)==m
            probability,coverage=infer_full_fov(model,image,grid,case['native_shape']);prediction=probability>=.5
            saved=ROOT/arm['prediction_file'];assert sha(saved)==arm['prediction_sha256']
            with np.load(saved,allow_pickle=False) as f:
                error=float(np.abs(probability-f['probability_rcz']).max());diff=int(np.count_nonzero(prediction!=f['prediction_rcz']))
                assert error<=3e-6 and diff==0
            zs=np.arange(label.shape[2]);last=zs[zs%4==0][-1]
            domains=dict(full=np.ones(len(zs),bool),anchors=zs%4==0,missing=(zs<last)&(zs%4!=0),tail=zs>last)
            for key,mask in domains.items():assert logical_counts(prediction[:,:,mask],label[:,:,mask])==arm['metrics'][key]
            m=arm['metrics']['full'];gate=dict(foreground_patch_dice=arm['original_fixed_batch_patch_metrics'][0]['dice'] is not None and arm['original_fixed_batch_patch_metrics'][0]['dice']>=.9,
                training_full_dice=m['dice'] is not None and m['dice']>=.9,training_full_recall=m['recall'] is not None and m['recall']>=.9,
                training_full_absRVE=m['absRVE'] is not None and m['absRVE']<=.25,training_tp_positive=m['tp']>0)
            assert gate==arm['training_fit_gate'] and all(gate.values())==arm['training_fit_gate_passed']
            record=dict(kind=arm['kind'],complete=True,history_rows_verified=1024,feature_bytes_replayed=arm['feature_matrix_bytes'],
                        feature_matrix_sha_verified=True,label_vector_sha_verified=True,all_tile_labels_outputs_and_loss_verified=True,
                        numpy_bce=ce,numpy_soft_dice=sd,full_native_voxels_replayed=int(prediction.size),
                        probability_max_absolute_error=error,prediction_disagreements=diff,all_four_domains_and_gate_verified=True)
            r['arms'].append(record);save();print(json.dumps(record),flush=True)
            del model,state,stored,original,normalized,image,x,y,o,probability,prediction
        assert not torch.cuda.is_initialized();r['cuda_initialized']=False;r['resources_after']=resource_guard();r['complete']=len(r['arms'])==2
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();save();print(json.dumps({k:r.get(k) for k in ('complete','errors','cuda_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
