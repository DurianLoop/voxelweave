"""Verify head-only final states with the module network and original full-FOV inference."""
import json,math,sys,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,physical_mr,lattice,
    physical_label,read_reference_label,sample_batch,TaskUNet3D,infer_full_fov,loss,torch,np,SEED)
from mc_rc_3d_independent_replay_2026_10_07 import logical_counts
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07'
def main():
    sys.stdout.reconfigure(encoding='utf-8');path=OUT/'module_full_fov_verification_attempt01.json';assert not path.exists()
    prodpath=OUT/'attempt01.json';prod=read(prodpath)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],arms=[],script_sha256=sha(__file__),
           result_sha256=sha(prodpath),actual_training_updates=0,actual_gpu_updates=0,scientific_confirmation_patients=0,
           validation_effects_opened=False,confirmation_patients_opened=False,second_independently_trained_task_network=False)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        assert prod['complete'] and not prod['errors'] and prod['actual_patient_cpu_head_parameter_updates']==4096
        r['source_bindings']=prod['source_bindings']
        for s in prod['source_bindings']:assert sha(ROOT/s['path'])==s['sha256']
        resource_guard();role,case,row=fixed_cases()[0];assert role=='development' and case['patient']=='VS-MC-RC-001'
        grid=lattice(case);native_label=read_reference_label(case);target=physical_label(native_label,grid)
        for arm in prod['arms']:
            resource_guard();assert arm['complete'] and arm['evaluation_complete'] and arm['updates_completed']==1024
            history=arm['history'];assert len(history)==1024 and [h['update'] for h in history]==list(range(1,1025))
            assert all(h['lr']==.01 and all(math.isfinite(h[k]) for k in ('main_head_bce','main_head_soft_dice','deep_supervision_loss')) for h in history)
            assert arm['trainable_parameters']==(1 if arm['branch']=='bias_only' else 17)
            source=ROOT/arm['source_checkpoint_file'];checkpoint=ROOT/arm['checkpoint_file']
            assert sha(source)==arm['source_checkpoint_sha256'] and sha(checkpoint)==arm['checkpoint_sha256']
            original=torch.load(source,map_location='cpu',weights_only=True)['state_dict']
            cp=torch.load(checkpoint,map_location='cpu',weights_only=True);state=cp['state_dict']
            assert cp['protocol_sha256']==prod['protocol_sha256'] and cp['updates']==1024
            assert state_hash(state)==cp['final_weights_sha256']==arm['final_weights_sha256']
            fixed=0
            for k in original:
                if not k.startswith('heads.2.') or (k.endswith('weight') and arm['branch']=='bias_only'):
                    assert torch.equal(original[k],state[k]);fixed+=1
            assert fixed==arm['fixed_backbone_state_entries']+(arm['branch']=='bias_only')
            model=TaskUNet3D();model.load_state_dict(state,strict=True);model.eval();model.requires_grad_(False)
            normalized,stats=source_image(case,row,arm['kind']);image=physical_mr(normalized,grid)
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED))
            assert array_sha(x.numpy())==arm['input_batch_sha256'] and array_sha(y.numpy())==arm['label_batch_sha256']
            with torch.inference_mode():outputs=model(x);p=outputs[0].sigmoid();objective=float(loss(outputs,y))
            assert abs(objective-(4/7*arm['final_main_head_numpy_loss']['loss']+arm['constant_auxiliary_contribution']))<=3e-6
            for pred,gt,metrics in zip(p.numpy()[:,0]>=.5,y.numpy()[:,0]>=.5,arm['patch_metrics']):assert logical_counts(pred,gt)==metrics
            probability,coverage=infer_full_fov(model,image,grid,case['native_shape'])
            dest=ROOT/arm['prediction_file'];assert sha(dest)==arm['prediction_sha256']
            with np.load(dest,allow_pickle=False) as saved:
                error=float(np.max(np.abs(probability-saved['probability_rcz'])))
                differences=int(np.count_nonzero((probability>=.5)!=saved['prediction_rcz']))
                assert error<=3e-6 and differences==0
            assert coverage['total_tiles']==arm['inference']['total_tiles'] and coverage['axis_starts']==arm['inference']['axis_starts']
            zs=np.arange(native_label.shape[2]);last=zs[zs%4==0][-1]
            domains=dict(full=np.ones(len(zs),bool),anchors=zs%4==0,missing=(zs<last)&(zs%4!=0),tail=zs>last)
            for k,mask in domains.items():assert logical_counts(probability[:,:,mask]>=.5,native_label[:,:,mask])==arm['metrics'][k]
            m=arm['metrics']['full'];gate=dict(foreground_patch_dice=arm['patch_metrics'][0]['dice'] is not None and arm['patch_metrics'][0]['dice']>=.9,
                training_full_dice=m['dice'] is not None and m['dice']>=.9,training_full_recall=m['recall'] is not None and m['recall']>=.9,
                training_full_absRVE=m['absRVE'] is not None and m['absRVE']<=.25,training_tp_positive=m['tp']>0)
            assert gate==arm['training_fit_gate'] and all(gate.values())==arm['training_fit_gate_passed']
            item=dict(kind=arm['kind'],branch=arm['branch'],complete=True,history_rows_verified=1024,
                      frozen_state_entries_verified=fixed,full_native_voxels_replayed=int(probability.size),
                      probability_max_absolute_error=error,prediction_disagreements=differences,
                      all_four_domains_and_gate_verified=True,total_tiles=coverage['total_tiles'])
            r['arms'].append(item);save();print(json.dumps(item),flush=True)
            del model,state,cp,original,normalized,image,x,y,outputs,p,probability
        assert not torch.cuda.is_initialized();r['cuda_initialized']=False;r['resources_after']=resource_guard()
        r['complete']=len(r['arms'])==4
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','actual_training_updates','cuda_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
