"""Independent native-label plane counts and complete-plane replay of minimal fit."""
import sys,json,traceback
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import ROOT,SEED,GlobalLocalUNet,weight_hash,read,sha,array_sha,load_authenticated_observed,sparse_image,physical_shape,resize_image,np,torch
from mc_rc_task_metrics_cpu import independent_label,independent_counts
from verify_mc_rc_global_local_task_validation_cpu import replay_plane
OUT=ROOT/'experiments/mc_rc_global_local_fixed_plane_fit_cpu'
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();source=OUT/'attempt_01.json';r=read(source)
    assert r['complete'] and not r['errors'];path=OUT/'independent_metrics_and_plane_attempt_01.json';assert not path.exists()
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),result_sha256=sha(source),
        native_hidden_MR_pixels_decoded=False,confirmation_patients_opened=False,scientific_confirmation_patients=0,
        publication_claim_confirmed=False,same_architecture_replay=True,full_patient_evaluated=False)
    try:
        assert r['updates_completed']==1000 and r['training_patient_ids']==['VS-MC-RC-012'] and r['seed']==SEED
        for item in r['source_bindings']:assert sha(ROOT/item['path'])==item['sha256']
        assert sha(ROOT/r['protocol_file'])==r['protocol_sha256'] and sha(ROOT/'experiments/mc_rc_global_local_task_cpu_support.py')==r['support_sha256']
        assert sha(ROOT/'experiments/run_mc_rc_global_local_fixed_plane_fit_cpu.py')==r['script_sha256']
        case=r['case_binding'];label=independent_label(case);assert array_sha(label)==r['native_label_sha256']
        zs=np.where(label.any(axis=(0,1)))[0];assert zs.tolist()==r['foreground_plane_z_values'] and r['z']==int(zs[len(zs)//2])
        e=r['evaluation'];p=ROOT/e['prediction_file'];assert sha(p)==e['prediction_file_sha256']
        with np.load(p,allow_pickle=False) as data:pred=data['prediction_rcz'].copy()
        assert pred.shape==label[:,:,r['z']:r['z']+1].shape and pred.dtype==bool and array_sha(pred)==e['prediction_array_sha256']
        c=independent_counts(pred,label[:,:,r['z']:r['z']+1]);assert all(v==e['metrics'][k] for k,v in c.items())
        checks=dict(native_plane_dice=c['dice']>=.95,native_plane_recall=c['recall']>=.95,absolute_relative_area_error=c['absolute_relative_volume_error']<=.05)
        assert checks==e['fit_gate_checks'] and all(checks.values())==e['fit_gate_passed']
        assert len(r['tile_exposure'])==len(r['locations']) and sum(r['tile_exposure'].values())==2000 and min(r['tile_exposure'].values())>0
        torch.manual_seed(SEED);model=GlobalLocalUNet();assert weight_hash(model)==r['initial_weights_sha256']
        cp=ROOT/r['checkpoint_file'];assert sha(cp)==r['checkpoint_sha256'];checkpoint=torch.load(cp,map_location='cpu',weights_only=True)
        assert checkpoint['z']==r['z'] and checkpoint['updates_completed']==1000 and checkpoint['training_patient_ids']==r['training_patient_ids']
        model.load_state_dict(checkpoint['state_dict'],strict=True);model.eval();assert weight_hash(model)==r['final_weights_sha256']
        row=next(e for e in read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json')['series'] if e['uid']==case['uid'])
        obs=load_authenticated_observed(case,row);native,_=sparse_image(obs,'raw_pchip',row);shape,spacing=physical_shape(case);image=resize_image(native,shape)
        assert array_sha(native)==r['native_input_sha256'] and array_sha(image)==r['physical_input_sha256']
        direct,cov,axes=replay_plane(model,image,r['z'],spacing,case['native_shape'])
        assert np.array_equal(direct,pred[:,:,0]) and array_sha(cov)==e['coverage']['coverage_sha256']
        assert axes==[e['coverage']['row_starts'],e['coverage']['col_starts']]
        q.update(independent_plane_counts=c,fit_gate_passed_verified=all(checks.values()),checkpoint_replayed_planes=1,
            global_forward_calls=model.global_calls,local_forward_calls=model.local_calls,gpu_initialized=torch.cuda.is_initialized())
        assert not q['gpu_initialized'];q['complete']=True
    except Exception as error:q['errors'].append(type(error).__name__+': '+str(error));q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(q,ensure_ascii=False));return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
