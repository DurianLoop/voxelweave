"""Resume fixed-budget common-init CPU task training; intentionally no MRI task scoring."""
import argparse,collections,gc,json,shutil,sys,time,traceback
from mc_rc_3d_19series_common_init_2026_10_07 import *

def history_rows(kind):
    p=OUT/(kind+'_history.jsonl')
    if not p.exists():return []
    with p.open(encoding='utf-8') as f:return [json.loads(line) for line in f if line.strip()]
def journal_hash(kind):
    p=OUT/(kind+'_history.jsonl');return sha(p) if p.exists() else None
def commit(kind,model,opt,step,config,rng):
    state={k:v.detach().clone() for k,v in model.state_dict().items()}
    cp=OUT/(kind+'_resume.pt');atomic_torch(cp,dict(state_dict=state,optimizer_state_dict=opt.state_dict(),
        torch_rng_state=rng,kind=kind,updates_completed=step,initial_weights_sha256=config['initial_weights_sha256'],
        final_weights_sha256=state_hash(state),frozen_config_sha256=sha(OUT/'frozen_config.json'),
        history_sha256=journal_hash(kind)))
    return dict(kind=kind,updates_completed=step,resume_file=cp.name,resume_file_sha256=sha(cp),
        current_weights_sha256=state_hash(state),history_sha256=journal_hash(kind))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--attempt',required=True);ap.add_argument('--stop-after',required=True,type=int)
    ap.add_argument('--wall-limit',required=True,type=int);args=ap.parse_args()
    assert args.attempt.isdigit() and len(args.attempt)==2 and 0<args.stop_after<=BUDGET and args.stop_after%11==0
    assert 0<args.wall_limit<=MAX_SECONDS
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();torch.set_num_threads(4)
    dest=OUT/('invocation'+args.attempt+'.json');assert not dest.exists()
    config=read(OUT/'frozen_config.json');pre=read(OUT/'preflight_attempt01.json')
    assert pre['complete'] and not pre['errors'] and sha(OUT/'frozen_config.json')==pre['frozen_config_sha256']
    assert sha(PROTOCOL)==config['protocol_sha256'] and config['planned_updates_per_arm']==BUDGET
    for b in config['source_bindings']:assert sha(ROOT/b['path'])==b['sha256'],'Source changed: '+b['path']
    assert sha(OUT/config['initial_file'])==config['initial_file_sha256'] and sha(OUT/config['schedule_file'])==config['schedule_file_sha256']
    cases=development_cases();assert config['series']==[dict(patient=c['patient'],uid=c['uid']) for c,row in cases]
    draws=np.load(OUT/config['schedule_file'],allow_pickle=False);assert array_sha(draws)==config['schedule_array_sha256']
    initial=torch.load(OUT/config['initial_file'],map_location='cpu',weights_only=True)['state_dict']
    assert state_hash(initial)==config['initial_weights_sha256']
    previous=[read(p) for p in sorted(OUT.glob('invocation[0-9][0-9].json'))]
    assert all(p['status']=='completed_segment' and p['complete'] and not p['errors'] for p in previous),'Previous invocation requires explicit audit before resume'
    assert len(previous)==int(args.attempt)-1
    prior_seconds=sum(p['elapsed_seconds'] for p in previous);assert prior_seconds<MAX_SECONDS
    r=dict(created_utc=now(),complete=False,status='preparing',errors=[],script_sha256=sha(__file__),
        frozen_config_sha256=sha(OUT/'frozen_config.json'),preflight_sha256=sha(OUT/'preflight_attempt01.json'),
        stop_after=args.stop_after,planned_final_updates_per_arm=BUDGET,invocation_wall_seconds_limit=args.wall_limit,
        prior_invocation_wall_seconds=prior_seconds,cumulative_train_wall_seconds_limit=MAX_SECONDS,
        arms=[],new_cpu_backbone_updates=0,actual_gpu_updates=0,task_effects_scored=False,
        validation_MR_or_GT_loaded=False,validation_metadata_only=True,confirmation_patients_opened=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    dump_new(dest,r)
    def save():atomic_json(dest,r)
    def runtime_guard():
        elapsed=time.perf_counter()-started
        assert elapsed<=args.wall_limit,'Invocation frozen wall-clock limit exceeded'
        assert elapsed+prior_seconds<=MAX_SECONDS,'Formal cumulative wall-clock limit exceeded'
        return guard()
    model=opt=None;active_kind=None;safe_step=None;model_step=None;log=None
    try:
        r['resources_before']=runtime_guard()
        for kind in ARM_KINDS:
            active_kind=kind;safe_step=None;runtime_guard();records=history_rows(kind);oldcp=OUT/(kind+'_resume.pt')
            model=TaskUNet3D();model.load_state_dict(initial);model.train();opt=optimizer_for(model);completed=0
            if oldcp.exists():
                cp=torch.load(oldcp,map_location='cpu',weights_only=True)
                assert cp['kind']==kind and cp['initial_weights_sha256']==config['initial_weights_sha256']
                assert cp['frozen_config_sha256']==sha(OUT/'frozen_config.json') and cp['history_sha256']==journal_hash(kind)
                completed=int(cp['updates_completed']);model.load_state_dict(cp['state_dict']);opt.load_state_dict(cp['optimizer_state_dict'])
                torch.set_rng_state(cp['torch_rng_state']);assert state_hash(model.state_dict())==cp['final_weights_sha256'];del cp
            else:assert not records
            assert len(records)==completed and completed<=args.stop_after
            for step,h in enumerate(records,1):
                pi,ci=map(int,draws[step-1]);assert h['update']==step and h['uid']==cases[ci][0]['uid'] and h['patient']==config['patient_ids'][pi]
            safe_step=completed;model_step=completed
            arm=dict(kind=kind,initial_weights_sha256=config['initial_weights_sha256'],starting_updates=completed,
                updates_completed=completed,complete=False,cache_records=[],new_update_seconds=[])
            r['arms'].append(arm);save()
            if completed==args.stop_after:
                arm['complete']=True;save();del model,opt;model=opt=None;continue
            r['status']='loading_development_cache';save();cache,cache_records,cache_seconds=load_cache(kind,cases)
            arm.update(cache_records=cache_records,cache_seconds=cache_seconds,cache_array_bytes=1909712000)
            runtime_guard();r['status']='training';save()
            log=(OUT/(kind+'_history.jsonl')).open('a',encoding='utf-8')
            for step in range(completed+1,args.stop_after+1):
                runtime_guard();tick=time.perf_counter();pi,ci=map(int,draws[step-1]);c,row=cases[ci]
                assert c['patient']==config['patient_ids'][pi];image,target=cache[c['uid']]
                x,y,primitive=sample_batch(image,target,batch_rng(step));xh,yh=array_sha(x.numpy()),array_sha(y.numpy())
                opt.zero_grad(set_to_none=True);outputs=model(x);value=loss(outputs,y);assert torch.isfinite(value)
                value.backward();assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
                if step==1:
                    arm['first_update_branch_gradient_max']={name:max(float(p.grad.abs().max()) for p in module.parameters())
                        for name,module in (('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads))}
                    assert all(v>0 for v in arm['first_update_branch_gradient_max'].values())
                opt.step();model_step=step;assert all(torch.isfinite(p).all() for p in model.parameters())
                elapsed=time.perf_counter()-tick
                h=dict(update=step,patient=c['patient'],uid=c['uid'],input_sha256=xh,label_sha256=yh,
                    augmentation_primitive=primitive,label_foreground=[int(g.sum()) for g in y],loss=float(value.detach()),
                    lr=.0001,total_update_seconds=elapsed)
                log.write(json.dumps(h,ensure_ascii=False,separators=(',',':'))+'\n');log.flush()
                safe_step=step;arm['updates_completed']=step;arm['new_update_seconds'].append(elapsed);r['new_cpu_backbone_updates']+=1
                if step%99==0 or step==args.stop_after:
                    os.fsync(log.fileno());arm['latest_committed_checkpoint']=commit(kind,model,opt,step,config,torch.get_rng_state())
                    runtime_guard();save();print(json.dumps(dict(kind=kind,updates=step,loss=h['loss'],new_updates=r['new_cpu_backbone_updates'],
                        cumulative_wall_seconds=prior_seconds+time.perf_counter()-started)),flush=True)
            log.close();log=None
            timed=arm['new_update_seconds'];arm.update(complete=True,new_update_median_seconds=float(np.median(timed)),new_update_max_seconds=max(timed))
            if args.stop_after==99:
                # Immutable short-segment evidence survives later rolling resume/history updates.
                snap=OUT/(kind+'_segment99.pt');hist=OUT/(kind+'_segment99_history.jsonl')
                assert not snap.exists() and not hist.exists()
                shutil.copyfile(OUT/(kind+'_resume.pt'),snap);shutil.copyfile(OUT/(kind+'_history.jsonl'),hist)
                arm.update(segment_checkpoint_file=snap.relative_to(ROOT).as_posix(),segment_checkpoint_sha256=sha(snap),
                    segment_history_file=hist.relative_to(ROOT).as_posix(),segment_history_sha256=sha(hist),
                    rolling_resume_and_history_paths_are_mutable=True)
            if args.stop_after==BUDGET:
                final=OUT/(kind+'_last19998.pt');assert not final.exists()
                torch.save(dict(state_dict={k:v.detach().clone() for k,v in model.state_dict().items()},kind=kind,updates_completed=BUDGET,
                    initial_weights_sha256=config['initial_weights_sha256'],final_weights_sha256=state_hash(model.state_dict()),
                    frozen_config_sha256=sha(OUT/'frozen_config.json'),history_sha256=journal_hash(kind)),final)
                arm.update(final_checkpoint_file=final.relative_to(ROOT).as_posix(),final_checkpoint_sha256=sha(final),
                    final_weights_sha256=state_hash(model.state_dict()))
            save();del model,opt,cache,x,y,outputs,value,image,target;model=opt=None;active_kind=None;safe_step=None;gc.collect()
        first,second=[history_rows(k) for k in ARM_KINDS];assert len(first)==len(second)==args.stop_after
        keys=('update','patient','uid','label_sha256','label_foreground','augmentation_primitive')
        assert all({k:a[k] for k in keys}=={k:b[k] for k in keys} for a,b in zip(first,second))
        r.update(complete=True,status='completed_segment',paired_GT_and_augmentation_identical=True,
            total_formal_updates_so_far=2*args.stop_after,formal_final_budget_completed=args.stop_after==BUDGET,
            all_last_weights_frozen=args.stop_after==BUDGET,cuda_initialized=torch.cuda.is_initialized(),resources_after=runtime_guard())
        if args.stop_after==BUDGET:r['both_last_checkpoints_frozen_utc']=now()
    except Exception as e:
        r['status']='failed';r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
        if log is not None:log.flush();os.fsync(log.fileno());log.close();log=None
        # Preserve a last finite boundary for explicit later audit; failed runs never silently auto-resume.
        if model is not None and safe_step is not None and safe_step==model_step and all(torch.isfinite(p).all() for p in model.parameters()):
            try:r['failure_recovery_checkpoint']=commit(active_kind,model,opt,safe_step,config,torch.get_rng_state())
            except Exception as ce:r['recovery_checkpoint_error']=type(ce).__name__+': '+str(ce)
    r['finished_utc']=now();r['elapsed_seconds']=time.perf_counter()-started
    r['cumulative_train_wall_seconds']=prior_seconds+r['elapsed_seconds'];r['stage_saved_bytes']=saved_bytes();save()
    print(json.dumps({k:r.get(k) for k in ('status','complete','errors','new_cpu_backbone_updates','total_formal_updates_so_far',
        'formal_final_budget_completed','elapsed_seconds','stage_saved_bytes')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
