"""Independent batch/optimizer/functional audit of immutable segment99; no new updates or FOV scores."""
import collections,gc,json,math,sys,time,traceback
from pathlib import Path
from mc_rc_3d_19series_common_init_2026_10_07 import *
from preflight_mc_rc_3d_19series_common_init_2026_10_07 import independent_schedule
from mc_rc_3d_independent_replay_2026_10_07 import functional_forward

def independent_augmented_batch(image,target,step):
    rng=np.random.default_rng([SEED,612,step]);foreground=np.transpose(np.nonzero(target>0));xs=[];ys=[];primitives=[]
    for forced in (True,False):
        center=foreground[int(rng.integers(foreground.shape[0]))] if forced else np.array([rng.integers(n) for n in image.shape])
        origin=np.minimum(np.maximum(center-np.array(PATCH)//2,0),np.array(image.shape)-np.array(PATCH)).astype(int)
        sl=tuple(slice(int(s),int(s)+p) for s,p in zip(origin,PATCH));a=image[sl].copy();b=target[sl].copy();flags=[]
        for axis in range(3):
            f=bool(rng.random()<.5);flags.append(f)
            if f:a=a[(slice(None),)*axis+(slice(None,None,-1),)];b=b[(slice(None),)*axis+(slice(None,None,-1),)]
        factor=float(rng.uniform(.9,1.1));offset=float(rng.uniform(-.1,.1));a=a*factor+offset
        xs.append(np.ascontiguousarray(a));ys.append(np.ascontiguousarray(b))
        primitives.append(dict(forced_foreground=forced,center=center.tolist(),start=origin.tolist(),flips=flags,
            intensity_scale=factor,intensity_shift=offset,target_foreground=int(b.sum())))
    return np.stack(xs)[:,None],np.stack(ys)[:,None],primitives
def numpy_loss(logits,label):
    terms=[]
    for out in logits:
        v=out.detach().numpy().astype(np.float64);sizes=v.shape[2:]
        ix=[((2*np.arange(m,dtype=np.int64)+1)*n)//(2*m) for n,m in zip(label.shape[2:],sizes)]
        y=label[:,:,ix[0]][:,:,:,ix[1]][:,:,:,:,ix[2]].astype(np.float64)
        assert y.shape==v.shape
        p=1/(1+np.exp(-v));bce=float(np.mean(np.maximum(v,0)+np.log1p(np.exp(-np.abs(v)))-v*y))
        dice=1-(2*float((p*y).sum())+1)/(float(p.sum())+float(y.sum())+1);terms.append(bce+dice)
    return sum(a*b for a,b in zip(terms,(4/7,2/7,1/7)))
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();torch.set_num_threads(4)
    path=OUT/'independent_segment99_attempt01.json';assert not path.exists()
    source=OUT/'invocation01.json';r=dict(created_utc=now(),complete=False,errors=[],script_sha256=sha(__file__),
        source_file=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),arms=[],actual_training_updates=0,
        actual_gpu_updates=0,task_effects_scored=False,complete_FOV_inference_performed=False,
        original99_training_updates_not_independently_retrained=True,validation_MR_or_GT_loaded=False,
        confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    def runtime_guard():
        assert time.perf_counter()-started<=1200;return guard()
    def save():atomic_json(path,r)
    dump_new(path,r)
    try:
        ex=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_SEGMENT99_2026-10-07.json')
        q=read(source);config=read(OUT/'frozen_config.json');cases=development_cases();draws=independent_schedule(cases)
        assert ex['training_observed_tool_exit']==0 and ex['training_result_sha256']==sha(source)
        assert q['complete'] and q['status']=='completed_segment' and not q['errors'] and q['stop_after']==99
        assert q['new_cpu_backbone_updates']==q['total_formal_updates_so_far']==198 and q['paired_GT_and_augmentation_identical']
        assert sha(OUT/'frozen_config.json')==q['frozen_config_sha256'] and array_sha(draws)==config['schedule_array_sha256']
        assert not q['formal_final_budget_completed'] and not q['task_effects_scored'] and not q['cuda_initialized']
        for b in config['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        initial=torch.load(OUT/config['initial_file'],map_location='cpu',weights_only=True)['state_dict']
        assert state_hash(initial)==state_hash(make_initial())==config['initial_weights_sha256']
        bindings=[source,OUT/'frozen_config.json',OUT/config['initial_file'],OUT/config['schedule_file'],OUT/'preflight_attempt01.json',
            ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_SEGMENT99_2026-10-07.json',
            ROOT/'MC_RC_3D_19SERIES_COMMON_INIT_SEGMENT99_VERIFY_PROTOCOL_2026-10-07.md',Path(__file__),
            ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py']
        for arm in q['arms']:
            runtime_guard();cpfile=ROOT/arm['segment_checkpoint_file'];histfile=ROOT/arm['segment_history_file']
            assert sha(cpfile)==arm['segment_checkpoint_sha256'] and sha(histfile)==arm['segment_history_sha256']
            cp=torch.load(cpfile,map_location='cpu',weights_only=True);bindings.extend((cpfile,histfile))
            assert cp['updates_completed']==99 and cp['initial_weights_sha256']==config['initial_weights_sha256']
            assert cp['history_sha256']==sha(histfile) and cp['frozen_config_sha256']==sha(OUT/'frozen_config.json')
            assert state_hash(cp['state_dict'])==cp['final_weights_sha256']==arm['latest_committed_checkpoint']['current_weights_sha256']
            assert cp['final_weights_sha256']!=config['initial_weights_sha256']
            model=TaskUNet3D();model.load_state_dict(cp['state_dict']);model.eval();optimizer=optimizer_for(model)
            optimizer.load_state_dict(cp['optimizer_state_dict']);states=list(optimizer.state.values())
            assert len(states)==len(list(model.parameters()))
            assert all(float(s['step'])==99 and torch.isfinite(s['exp_avg']).all() and torch.isfinite(s['exp_avg_sq']).all()
                and (s['exp_avg_sq']>=0).all() for s in states)
            assert all(torch.isfinite(p).all() for p in model.parameters())
            assert all(g['lr']==.0001 and g['weight_decay']==.0001 for g in optimizer.param_groups)
            with histfile.open(encoding='utf-8') as f:rows=[json.loads(line) for line in f if line.strip()]
            assert len(rows)==99 and all(h['update']==step and math.isfinite(h['loss']) and h['lr']==.0001 for step,h in enumerate(rows,1))
            assert len(set(h['uid'] for h in rows))==19 and set(collections.Counter(h['patient'] for h in rows).values())=={9}
            cacheby={v['uid']:v for v in arm['cache_records']};replayed=[];headproof=None
            for c,observed in cases:
                runtime_guard();g=lattice(c);normalized,stats=source_image(c,observed,arm['kind']);image=physical_mr(normalized,g)
                gt=read_reference_label(c);target=physical_label(gt,g);old=cacheby[c['uid']]
                assert array_sha(image)==old['input_sha256'] and array_sha(target)==old['label_sha256'] and stats==old['observed_statistics']
                for h in rows:
                    if h['uid']!=c['uid']:continue
                    pi,ci=map(int,draws[h['update']-1]);assert cases[ci][0]['uid']==h['uid'] and config['patient_ids'][pi]==h['patient']
                    x,y,primitive=independent_augmented_batch(image,target,h['update'])
                    assert array_sha(x)==h['input_sha256'] and array_sha(y)==h['label_sha256'] and primitive==h['augmentation_primitive']
                    assert [int(v.sum()) for v in y]==h['label_foreground'];replayed.append(h['update'])
                    if h['update']==99:
                        with torch.inference_mode():
                            mo=model(torch.from_numpy(x));fo=functional_forward(torch.from_numpy(x),cp['state_dict'])
                            errors=[float((a.sigmoid()-b.sigmoid()).abs().max()) for a,b in zip(mo,fo)]
                            binary=[int(((a>=0)!=(b>=0)).sum()) for a,b in zip(mo,fo)]
                            production_loss=float(loss(mo,torch.from_numpy(y)));reference_loss=numpy_loss(mo,y)
                        assert len(errors)==3 and max(errors)<=3e-6 and max(binary)==0
                        assert abs(production_loss-reference_loss)<=3e-6
                        headproof=dict(all_three_head_probability_max_errors=errors,all_three_head_threshold_disagreements=binary,
                            production_loss=production_loss,numpy_float64_loss=reference_loss,absolute_loss_error=abs(production_loss-reference_loss),
                            last_training_batch_used=True,neural_forward_calls=2,no_task_endpoint_computed=True)
                    del x,y
                del normalized,image,gt,target;gc.collect();runtime_guard()
            assert sorted(replayed)==list(range(1,100)) and headproof is not None
            r['arms'].append(dict(kind=arm['kind'],complete=True,all19_cached_arrays_verified=True,
                all99_batches_input_GT_primitives_verified=True,patient9_steps_each=True,optimizer_all_steps99_finite=True,
                checkpoint_weights_sha256=cp['final_weights_sha256'],functional_and_loss=headproof))
            del cp,model,optimizer;gc.collect();save()
        keys=('update','patient','uid','label_sha256','label_foreground','augmentation_primitive')
        histories=[]
        for a in q['arms']:
            with (ROOT/a['segment_history_file']).open(encoding='utf-8') as f:histories.append([json.loads(line) for line in f])
        assert all({k:a[k] for k in keys}=={k:b[k] for k in keys} for a,b in zip(*histories))
        r.update(complete=True,all198_batches_verified=True,paired_GT_and_augmentation_identical=True,
            total_neural_forward_calls=4,resources_after=runtime_guard(),cuda_initialized=torch.cuda.is_initialized(),
            source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in bindings])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=now();r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','all198_batches_verified','total_neural_forward_calls','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
