"""New fixed20k capability training, same old exogenous draws, no augmentation bundle."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import copy, hashlib, json, math, sys, time, traceback
from datetime import datetime, timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT, SEED, DEVELOPERS, GlobalLocalUNet, weight_hash, read, sha, array_sha,
    load_authenticated_observed, sparse_image, physical_shape, resize_image,
    resize_training_label, training_example, context_tiles, segmentation_loss, np, torch)
from mc_rc_observed_only_training_input import read_supervised_label
from mc_rc_global_local_no_augmentation_cpu_support import no_augmentation_training_example
from mc_rc_coverage_augmentation_draw_cpu_support import example_from_record, example_sha, record_sha
OUT=ROOT/'experiments/mc_rc_no_augmentation_all_development_cpu'


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate()
    files=[ROOT/'experiments/mc_rc_coverage_augmentation_factorial_cpu/attempt_01.json',
           ROOT/'experiments/mc_rc_coverage_augmentation_factorial_cpu/independent_all_arms_metrics_draws_checkpoint_attempt_01.json',
           ROOT/'experiments/mc_rc_no_augmentation_development_cpu_preflight/attempt_01.json',
           ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json',
           ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json',
           ROOT/'experiments/mc_rc_global_local_task_training_cpu/attempt_01.json']
    factorial,verified,preflight,prep,prod,old=[read(p) for p in files]
    assert all(r['complete'] and not r['errors'] for r in (factorial,verified,preflight,prep,prod,old))
    assert verified['result_sha256']==sha(files[0]) and verified['checkpoint_replayed_planes']==12
    assert next(a for a in factorial['arms'] if a['name']=='legacy_none')['evaluation']['fit_gate_passed']
    assert preflight['same_rng_final_state_matches']==preflight['old_aug_input_sha_matches']==preflight['new_none_reference_sha_matches']==608
    assert preflight['full_patch_source_mapping_checks']==1216 and preflight['network_forward_calls']==preflight['training_updates']==0
    assert sha(ROOT/'experiments/prepare_mc_rc_no_augmentation_development_cpu.py')==preflight['script_sha256']
    for binding in preflight['source_bindings']+preflight['code_bindings']:
        assert sha(ROOT/binding['path'])==binding['sha256']
    assert sha(ROOT/preflight['protocol_file'])==preflight['protocol_sha256']
    cases=prep['cases'];assert len(cases)==19 and {c['patient'] for c in cases}==DEVELOPERS
    assert set(old['training_patient_ids'])==DEVELOPERS and old['updates_completed']==20000
    OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    protocol=ROOT/'MC_RC_NO_AUGMENTATION_ALL_DEVELOPMENT_CPU_PROTOCOL_2026-10-03.md'
    code=('mc_rc_global_local_task_cpu_support.py','mc_rc_global_local_no_augmentation_cpu_support.py',
          'mc_rc_coverage_augmentation_draw_cpu_support.py','mc_rc_observed_only_training_input.py')
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],resources=resources,
        protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),script_sha256=sha(__file__),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in files],
        code_bindings=[dict(path='experiments/'+s,sha256=sha(ROOT/'experiments'/s)) for s in code],
        seed=SEED,device='cpu',torch_version=str(torch.__version__),pretrained_weights_loaded=False,
        training_patient_ids=sorted(DEVELOPERS),training_series_uids=[c['uid'] for c in cases],
        updates_planned=20000,updates_completed=0,training_sampling_counts={},training_series_counts={},
        inputs=[],training_history=[],training_draws=[],same_rng_final_state_checks=0,
        old_aug_input_sha_matches=0,validation_neural_forwards_before_final_checkpoint=0,
        confirmation_patients_opened=False,native_hidden_MR_pixels_decoded=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,r)
    try:
        by={s['uid']:s for s in prod['series']};pf={s['uid']:s for s in preflight['series']}
        oldinputs={s['uid']:s for s in old['inputs']};cache={}
        for case in cases:
            resource_gate();uid=case['uid'];obs=load_authenticated_observed(case,by[uid]);native,stats=sparse_image(obs,'raw_pchip',by[uid])
            label=read_supervised_label(case);shape,spacing=physical_shape(case)
            image=resize_image(native,shape);target=resize_training_label(label,shape)
            bindings=dict(native_input_sha256=array_sha(native),native_label_sha256=array_sha(label),
                physical_image_sha256=array_sha(image),physical_label_sha256=array_sha(target))
            assert all(bindings[k]==pf[uid][k] for k in bindings)
            assert bindings['native_input_sha256']==oldinputs[uid]['original_input_sha256']
            assert all(bindings[k]==oldinputs[uid][k] for k in ('native_label_sha256','physical_image_sha256','physical_label_sha256'))
            cache[uid]=dict(image_zrc=image,label_zrc=target,native_foreground=np.argwhere(label),zspacing=spacing)
            r['inputs'].append(dict(patient=case['patient'],uid=uid,**bindings,physical_shape=list(image.shape),
                                    original_shape=case['native_shape'],zspacing_mm=spacing,observed_statistics=stats))
            write(path,r);print(json.dumps(dict(patient=case['patient'],uid=uid,input_authenticated=True)),flush=True)
        resource_gate();torch.manual_seed(SEED);model=GlobalLocalUNet();model.train()
        r['model_parameters']=sum(p.numel() for p in model.parameters());r['initial_weights_sha256']=weight_hash(model)
        assert r['model_parameters']==981602 and r['initial_weights_sha256']==old['initial_weights_sha256']
        opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001);rng=np.random.default_rng(SEED)
        patients=r['training_patient_ids'];patient_cases={p:[c for c in cases if c['patient']==p] for p in patients}
        r['cache_bytes']=sum(v['image_zrc'].nbytes+v['label_zrc'].nbytes+v['native_foreground'].nbytes for v in cache.values())
        r['training_started_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
        began=time.perf_counter();losses=[];stream=hashlib.sha256()
        for step in range(20000):
            if step%100==0:resource_gate()
            patient=patients[int(rng.integers(len(patients)))];choices=patient_cases[patient]
            case=choices[int(rng.integers(len(choices)))];item=cache[case['uid']]
            oldrng=np.random.default_rng();oldrng.bit_generator.state=copy.deepcopy(rng.bit_generator.state)
            oldexample=training_example(item,oldrng);example,record=no_augmentation_training_example(item,rng,step)
            assert oldrng.bit_generator.state==rng.bit_generator.state;r['same_rng_final_state_checks']+=1
            olddigest=example_sha(oldexample);assert olddigest==example_sha(example_from_record(item,record,'legacy_aug'))
            r['old_aug_input_sha_matches']+=1;digest=example_sha(example);stream.update(digest.encode())
            r['training_draws'].append(dict(step=step,patient=patient,uid=case['uid'],z=record['z'],
                native_patch_locations=record['legacy_native_locations'],primitive_sha256=record_sha(record),
                example_sha256=digest,original_aug_example_sha256=olddigest))
            gv,x,y,gt,locations,fullshape,sample=example;lr=.0001+.0009*(1+math.cos(math.pi*step/19999))/2
            for group in opt.param_groups:group['lr']=lr
            opt.zero_grad(set_to_none=True);features,coarse=model.global_forward(gv)
            prediction=model.local_forward(x,context_tiles(features,locations,fullshape))
            ll=segmentation_loss(prediction,y);gl=segmentation_loss(coarse,gt);loss=ll+.5*gl
            assert torch.isfinite(loss);loss.backward()
            assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters());opt.step()
            losses.append((float(loss.detach()),float(ll.detach()),float(gl.detach())))
            r['updates_completed']=step+1;r['training_sampling_counts'][patient]=r['training_sampling_counts'].get(patient,0)+1
            r['training_series_counts'][case['uid']]=r['training_series_counts'].get(case['uid'],0)+1
            if step==9:
                r['first10_updates_seconds_per_update']=(time.perf_counter()-began)/10
                write(path,r);assert r['first10_updates_seconds_per_update']<=2
            if (step+1)%100==0:
                h=dict(update=step+1,last100_loss_mean=np.mean(losses[-100:],axis=0).tolist(),lr=lr,
                    training_elapsed_seconds=time.perf_counter()-began,last_patient=patient,last_sample=sample,resources=resource_gate())
                r['training_history'].append(h);write(path,r);print(json.dumps(h),flush=True)
        r['training_finished_utc']=datetime.now(timezone.utc).isoformat();r['draw_stream_sha256']=stream.hexdigest()
        r['final_weights_sha256']=weight_hash(model);checkpoint=OUT/'final_update_20000.pt'
        torch.save(dict(state_dict=model.state_dict(),updates_completed=20000,seed=SEED,
            initial_weights_sha256=r['initial_weights_sha256'],final_weights_sha256=r['final_weights_sha256'],
            training_patient_ids=patients,training_series_uids=r['training_series_uids'],
            protocol_sha256=r['protocol_sha256'],draw_stream_sha256=r['draw_stream_sha256']),checkpoint)
        r.update(checkpoint_file=checkpoint.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(checkpoint),
                 global_forward_calls=model.global_calls,local_forward_calls=model.local_calls,gpu_initialized=torch.cuda.is_initialized())
        assert not r['gpu_initialized'] and model.global_calls==model.local_calls==20000
        assert r['same_rng_final_state_checks']==r['old_aug_input_sha_matches']==20000
        assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<100000000
        r['complete']=r['updates_completed']==20000
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','updates_completed','global_forward_calls','local_forward_calls','gpu_initialized')}),flush=True)
    return int(not r['complete'])


if __name__=='__main__':
    raise SystemExit(main())
