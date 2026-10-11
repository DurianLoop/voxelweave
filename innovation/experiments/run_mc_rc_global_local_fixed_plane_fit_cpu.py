"""One fixed developer plane, cyclic complete tile exposure, fixed1000 updates."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,sys,time,math,traceback
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT,SEED,GlobalLocalUNet,weight_hash,read,sha,array_sha,load_authenticated_observed,sparse_image,
    physical_shape,resize_image,resize_training_label,context_plane,global_view,context_tiles,
    segmentation_loss,infer_native,starts,np,torch,F)
from mc_rc_task_metrics_cpu import counts
from mc_rc_observed_only_training_input import read_supervised_label
OUT=ROOT/'experiments/mc_rc_global_local_fixed_plane_fit_cpu'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    protocol=ROOT/'MC_RC_GLOBAL_LOCAL_FIXED_PLANE_FIT_CPU_PROTOCOL_2026-10-03.md'
    sp=ROOT/'experiments/mc_rc_global_local_single_case_loss_cpu/attempt_01.json'
    qp=sp.parent/'independent_metrics_draws_and_checkpoint_attempt_01.json';s,q=read(sp),read(qp)
    assert s['complete'] and q['complete'] and not s['errors'] and not q['errors'] and q['result_sha256']==sha(sp)
    assert not any(a['evaluation']['fit_gate_passed'] for a in s['arms'])
    prep=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json'
    prod=ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json'
    case=next(c for c in read(prep)['cases'] if c['uid']==s['uid']);assert case['patient']=='VS-MC-RC-012'
    row=next(e for e in read(prod)['series'] if e['uid']==case['uid'])
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],resources=resources,
        protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),script_sha256=sha(__file__),
        support_sha256=sha(ROOT/'experiments/mc_rc_global_local_task_cpu_support.py'),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (sp,qp,prep,prod)],
        training_patient_ids=['VS-MC-RC-012'],training_series_uids=[case['uid']],case_binding=case,seed=SEED,
        updates_planned=1000,updates_completed=0,training_history=[],tile_exposure={},
        pretrained_weights_loaded=False,native_hidden_MR_pixels_decoded=False,validation_patients_opened=False,
        confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,r)
    try:
        obs=load_authenticated_observed(case,row);native,_=sparse_image(obs,'raw_pchip',row);label=read_supervised_label(case)
        assert array_sha(label)==row['label_array_sha256'];zs=np.where(label.any(axis=(0,1)))[0];z=int(zs[len(zs)//2])
        shape,spacing=physical_shape(case);image=resize_image(native,shape);target=resize_training_label(label,shape)
        plane=context_plane(image,z,spacing);gv=global_view(plane)
        gt=F.interpolate(torch.from_numpy(target[z])[None,None],size=(256,256),mode='area')
        locations=[(rr,cc) for rr in starts(shape[0]) for cc in starts(shape[1])]
        r.update(z=z,foreground_plane_z_values=zs.tolist(),locations=locations,native_input_sha256=array_sha(native),
            physical_input_sha256=array_sha(image),native_label_sha256=array_sha(label),native_plane_label_sha256=array_sha(label[:,:,z]))
        torch.manual_seed(SEED);model=GlobalLocalUNet();model.train();opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
        r['initial_weights_sha256']=weight_hash(model);r['model_parameters']=sum(p.numel() for p in model.parameters());write(path,r)
        print(json.dumps(dict(fixed_z=z,complete_FOV_tiles=len(locations),initial_weights_sha256=r['initial_weights_sha256'])),flush=True)
        began=time.perf_counter();losses=[]
        for step in range(1000):
            if step%100==0:resource_gate()
            indices=[(2*step+j)%len(locations) for j in range(2)];loc=[locations[i] for i in indices]
            x=torch.from_numpy(np.stack([plane[:,rr:rr+128,cc:cc+128] for rr,cc in loc]))
            y=torch.from_numpy(np.stack([target[z,rr:rr+128,cc:cc+128][None] for rr,cc in loc]))
            lr=.0001+.0009*(1+math.cos(math.pi*step/999))/2
            for group in opt.param_groups:group['lr']=lr
            opt.zero_grad(set_to_none=True);features,coarse=model.global_forward(gv);p=model.local_forward(x,context_tiles(features,loc,shape))
            loss=segmentation_loss(p,y)+.5*segmentation_loss(coarse,gt);assert torch.isfinite(loss);loss.backward()
            assert all(v.grad is None or torch.isfinite(v.grad).all() for v in model.parameters());opt.step();losses.append(float(loss.detach()))
            r['updates_completed']=step+1
            for i in indices:r['tile_exposure'][str(i)]=r['tile_exposure'].get(str(i),0)+1
            if step==9:
                elapsed=(time.perf_counter()-began)/10;r['first10_updates_seconds_per_update']=elapsed;write(path,r);assert elapsed<=2
            if (step+1)%100==0:
                h=dict(update=step+1,last100_loss=float(np.mean(losses[-100:])),lr=lr,elapsed_seconds=time.perf_counter()-began)
                r['training_history'].append(h);write(path,r);print(json.dumps(h),flush=True)
        assert len(r['tile_exposure'])==len(locations) and sum(r['tile_exposure'].values())==2000
        r['final_weights_sha256']=weight_hash(model);cp=OUT/'final_update_1000.pt'
        torch.save(dict(state_dict=model.state_dict(),updates_completed=1000,seed=SEED,z=z,
            training_patient_ids=r['training_patient_ids'],training_series_uids=r['training_series_uids'],
            initial_weights_sha256=r['initial_weights_sha256'],final_weights_sha256=r['final_weights_sha256'],protocol_sha256=r['protocol_sha256']),cp)
        r.update(checkpoint_file=cp.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(cp));write(path,r)
        pred,coverage=infer_native(model,image,spacing,case['native_shape'],only_planes=[z]);m=counts(pred,label[:,:,z:z+1])
        checks=dict(native_plane_dice=m['dice']>=.95,native_plane_recall=m['recall']>=.95,
            absolute_relative_area_error=m['absolute_relative_volume_error']<=.05)
        pp=OUT/'native_fixed_plane_prediction.npz';np.savez_compressed(pp,prediction_rcz=pred)
        r['evaluation']=dict(prediction_file=pp.relative_to(ROOT).as_posix(),prediction_file_sha256=sha(pp),
            prediction_array_sha256=array_sha(pred),metrics=m,coverage=coverage,fit_gate_checks=checks,
            fit_gate_passed=all(checks.values()),ratio_interpretation='single native plane relative area error, not full volume error')
        r.update(global_forward_calls=model.global_calls,local_forward_calls=model.local_calls,gpu_initialized=torch.cuda.is_initialized())
        assert not r['gpu_initialized'] and sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<50000000;r['complete']=True
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','updates_completed','evaluation','global_forward_calls','local_forward_calls')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
