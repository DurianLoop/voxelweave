"""Verify full fixed-fit history/checkpoints and replay both complete FOVs with a functional interpreter."""
import json
import math
import sys
import traceback
from datetime import datetime,timezone
import nibabel as nib
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,physical_mr,lattice,physical_label,read_reference_label,sample_batch,torch,np,SEED,PATCH
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
from mc_rc_3d_independent_replay_2026_10_07 import functional_forward,independent_inference,logical_counts
OUT=ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07'

def coordinate_label(case):
    source=nib.load(ROOT/case['label_file']);raw=np.asanyarray(source.dataobj);assert raw.nbytes<=256_000_000
    assert np.isin(raw,[0,1]).all()
    xyz_from_rcz=np.rint(np.linalg.solve(source.affine,np.asarray(case['affine_rcz_ras']))).astype(int)
    rr,cc=np.indices(case['native_shape'][:2]);truth=np.empty(case['native_shape'],bool)
    for z in range(case['native_shape'][2]):
        coords=np.stack((rr.ravel(),cc.ravel(),np.full(rr.size,z,dtype=int)))
        xyz=xyz_from_rcz[:3,:3]@coords+xyz_from_rcz[:3,3,None]
        assert (xyz>=0).all() and (xyz<np.asarray(raw.shape)[:,None]).all()
        truth[:,:,z]=raw[tuple(xyz)].reshape(case['native_shape'][:2])
    return truth

def main():
    sys.stdout.reconfigure(encoding='utf-8');resultpath=OUT/'attempt_01.json';prod=read(resultpath)
    assert prod['complete'] and not prod['errors'] and prod['total_updates_completed']==1024
    path=OUT/'independent_both512_and_full_fov_2026_10_07.json';assert not path.exists()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],arms=[],
           result_sha256=sha(resultpath),script_sha256=sha(__file__),source_bindings=prod['source_bindings'],
           interpreter_file='experiments/mc_rc_3d_independent_replay_2026_10_07.py',
           interpreter_sha256=sha(ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py'),
           actual_training_updates=0,actual_gpu_updates=0,scientific_confirmation_patients=0,
           second_independently_trained_task_network=False,confirmation_patients_opened=False,
           validation_model_effects_opened=False,publication_claim_confirmed=False)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        for binding in prod['source_bindings']:assert sha(ROOT/binding['path'])==binding['sha256']
        assert sha(ROOT/'experiments/run_mc_rc_3d_cpu_fixed_fit_2026_10_07.py')==prod['script_sha256']
        resource_guard();role,case,row=fixed_cases()[0];assert role=='development'
        label=coordinate_label(case);assert array_sha(label)==prod['native_label_sha256']
        grid=lattice(case);target=physical_label(read_reference_label(case),grid)
        assert array_sha(target)==prod['physical_label_sha256']
        comparison_initial=None;comparison_primitive=None;comparison_label=None
        for arm in prod['arms']:
            resource_guard();kind=arm['kind'];assert arm['updates_completed']==512 and arm['complete'] and arm['evaluation_complete']
            history=arm['every_update_history'];assert len(history)==512 and [h['update'] for h in history]==list(range(1,513))
            for h in history:
                lr=.0001+.0009*(1+math.cos(math.pi*(h['update']-1)/511))/2
                assert h['lr']==lr and math.isfinite(h['loss'])
            p=ROOT/arm['checkpoint_file'];assert sha(p)==arm['checkpoint_sha256']
            stored=torch.load(p,map_location='cpu',weights_only=True);state=stored['state_dict']
            assert state_hash(state)==stored['final_weights_sha256']==arm['final_weights_sha256']
            assert stored['updates']==512 and stored['seed']==SEED and stored['kind']==kind
            assert stored['protocol_sha256']==sha(ROOT/'MC_RC_3D_CPU_FIXED_FIT_PROTOCOL_2026-10-07.md')
            normalized,st=source_image(case,row,kind);image=physical_mr(normalized,grid)
            assert array_sha(image)==arm['physical_input_sha256']==stored['physical_input_sha256']
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED))
            assert array_sha(x.numpy())==arm['input_batch_sha256'] and array_sha(y.numpy())==arm['label_batch_sha256']==stored['label_batch_sha256']
            assert primitive==arm['primitive']==stored['primitive'] and st==arm['observed_statistics']
            if comparison_initial is None:
                comparison_initial=arm['initial_weights_sha256'];comparison_primitive=primitive;comparison_label=array_sha(y.numpy())
            else:assert comparison_initial==arm['initial_weights_sha256'] and comparison_primitive==primitive and comparison_label==array_sha(y.numpy())
            with torch.inference_mode():patch_prediction=functional_forward(x,state)[0].sigmoid().numpy()[:,0]>=.5
            for pgt,pred,metric in zip(y.numpy()[:,0]>=.5,patch_prediction,arm['patch_metrics']):assert logical_counts(pred,pgt)==metric
            probability,inference=independent_inference(state,image,grid,case['native_shape'])
            prediction=probability>=.5;dest=ROOT/arm['prediction_file'];assert sha(dest)==arm['prediction_sha256']
            with np.load(dest,allow_pickle=False) as saved:
                error=float(np.max(np.abs(probability-saved['probability_rcz'])))
                disagreements=int(np.count_nonzero(prediction!=saved['prediction_rcz']))
                assert error<=3e-6 and disagreements==0
            assert inference['total_tiles']==arm['inference']['total_tiles'] and inference['axis_starts']==arm['inference']['axis_starts']
            for key in ('coverage_min','coverage_max'):assert np.isclose(inference[key],arm['inference'][key],rtol=2e-7,atol=1e-8)
            z=np.arange(label.shape[2]);last=z[z%4==0][-1]
            domains=dict(full=np.ones(len(z),bool),anchors=z%4==0,missing=(z<last)&(z%4!=0),tail=z>last)
            for name,domain in domains.items():assert logical_counts(prediction[:,:,domain],label[:,:,domain])==arm['metrics'][name]
            full=arm['metrics']['full'];gate=dict(foreground_patch_dice=arm['patch_metrics'][0]['dice'] is not None and arm['patch_metrics'][0]['dice']>=.9,
                training_full_dice=full['dice'] is not None and full['dice']>=.9,training_full_recall=full['recall'] is not None and full['recall']>=.9,
                training_full_absRVE=full['absRVE'] is not None and full['absRVE']<=.25,training_tp_positive=full['tp']>0)
            assert gate==arm['training_fit_gate'] and all(gate.values())==arm['training_fit_gate_passed']
            r['arms'].append(dict(kind=kind,complete=True,updates_history_checked=512,checkpoint_sha256=sha(p),
                                 full_native_voxels_replayed=int(prediction.size),probability_max_absolute_error=error,
                                 prediction_disagreements=disagreements,total_tiles=inference['total_tiles'],
                                 metrics_domains_checked=list(domains),training_fit_gate_verified=gate))
            save();print(json.dumps(r['arms'][-1]),flush=True)
            del x,y,image,normalized,stored,state,probability,prediction
        assert prod['both_training_fit_gates_passed']==all(all(a['training_fit_gate_verified'].values()) for a in r['arms'])
        assert not torch.cuda.is_initialized();r['cuda_initialized']=False;r['complete']=len(r['arms'])==2
        r['resources_after']=resource_guard()
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','actual_training_updates','cuda_initialized')}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
