"""Four same-budget2992step task adaptation branches; no validation scoring during fitting."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import torch
original_cuda_initializer=torch.cuda._lazy_init
import gzip,zlib,gc,json,sys,time,traceback,subprocess
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'));sys.path.insert(0,str(ROOT/'adaptation_paired_pilot_2026_10_08'))
from mc_rc_3d_19series_common_init_2026_10_07 import (
    development_cases,source_image,lattice,physical_mr,physical_label,read_reference_label,
    sample_batch,batch_rng,TaskUNet3D,loss,state_hash,read,sha,array_sha,np,resource_guard,QPATH)
import augmentation as intensity
import spatial_transform as spatial
TRAIN=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
OUT=HERE/'training_attempt01';STEPS=2992;MAX_BYTES=45_000_000;MAX_SECONDS=27000
def now():return datetime.now(timezone.utc).isoformat()
def saved():return sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
def atomic_json(path,value):
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('w',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
def final_torch(path,value):
    assert not path.exists();tmp=path.with_name(path.name+'.tmp')
    with tmp.open('xb') as f:torch.save(value,f);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(4);started=time.perf_counter();device='cpu'
    OUT.mkdir(exist_ok=False);dest=OUT/'receipt.json'
    r=dict(created_utc=now(),complete=False,status='preparing',errors=[],arms=[],source_bindings=[],
        previous_goal_turn_classification='progress',planned_updates_per_branch=STEPS,planned_total_updates=11968,
        new_cpu_updates=0,new_GPU_updates=0,validation_pixels_loaded=False,validation_GT_loaded=False,
        confirmation_patients_opened=False,lockedIXI_opened=False,scientific_confirmation_patients=0,
        task_effects_scored=False,optimizer_resume_supported=False,other_PIDs_enumerated=False,other_PIDs_modified=False,
        original_training_modified=False,publication_claim_confirmed=False,goal_status='active')
    def save():atomic_json(dest,r)
    def guard():
        assert time.perf_counter()-started<=MAX_SECONDS,'stage27000s wall bound exceeded'
        res=resource_guard();size=saved();assert size<MAX_BYTES,'stage45MB save bound exceeded'
        assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1;res.update(cpu_threads=4,stage_saved_bytes=size)
        if device=='cuda:0':
            free,total=torch.cuda.mem_get_info(0);peak=torch.cuda.max_memory_reserved(0)
            assert free>=4_000_000_000 and peak<=2_500_000_000
            res.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
        else:assert not torch.cuda.is_initialized()
        return res
    save()
    try:
        synthetic=read(HERE/'synthetic_attempt01/receipt.json');real=read(HERE/'real_batch_attempt01/receipt.json');observed=read(HERE/'QUALIFICATION_ACTUAL_TOOL_EXITS.json')
        assert synthetic['complete'] and synthetic['all10_full_patch_gates_passed'] and not synthetic['errors']
        assert real['complete'] and real['all38_real_batches_verified'] and real['all38_forced_foreground_voxels_preserved'] and not real['errors']
        assert observed['synthetic_actual_tool']['exit_code']==observed['real_batches_actual_tool']['exit_code']==0
        for q in [synthetic,real]:
            for b in q['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        r['resources_before']=guard();assert r['resources_before']['workspace_free_bytes']-8_000_000_000>=MAX_BYTES-saved()
        query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.total,memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=20,check=True)
        gpu=[dict(zip(['index','total_MiB','free_MiB'],map(int,line.split(',')))) for line in query.stdout.strip().splitlines()]
        assert len(gpu)==1 and gpu[0]['index']==0;r['GPU_totals_observation']=gpu;r['GPU_start_gate_passed']=gpu[0]['free_MiB']>=8192
        if r['GPU_start_gate_passed']:
            os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer
            assert torch.cuda.is_available();torch.cuda.set_per_process_memory_fraction(.1,0)
            torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
            torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
            free,total=torch.cuda.mem_get_info(0);assert free>=8_000_000_000;device='cuda:0'
        r['device']=device;guard();save()
        config=read(TRAIN/'frozen_config.json');trainexit=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json')
        assert trainexit['training_observed_tool_exit']==0 and trainexit['formal_training_updates']==39996
        assert sha(TRAIN/'invocation02.json')==trainexit['training_result_sha256']
        for b in config['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        draws=np.load(TRAIN/config['schedule_file'],allow_pickle=False)[:STEPS]
        assert sha(TRAIN/config['schedule_file'])==config['schedule_file_sha256'] and draws.shape==(STEPS,2)
        assert all(int(np.count_nonzero(draws[:,0]==i))==272 for i in range(11))
        cases=development_cases();assert config['series']==[dict(patient=c['patient'],uid=c['uid']) for c,row in cases]
        sources={Path(__file__),HERE/'PROTOCOL.md',HERE/'spatial_transform.py',Path(intensity.__file__),HERE/'synthetic_attempt01/receipt.json',
            HERE/'real_batch_attempt01/receipt.json',HERE/'QUALIFICATION_ACTUAL_TOOL_EXITS.json',TRAIN/'frozen_config.json',TRAIN/config['schedule_file'],
            ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json',ROOT/'adaptation_paired_pilot_2026_10_08/ACTUAL_EVALUATION_EXIT.json'}
        sources.update(ROOT/b['path'] for b in config['source_bindings']);sources.update(ROOT/b['path'] for b in real['source_bindings'])
        sources.update(ROOT/a['checkpoint_path'] for a in trainexit['arms'])
        bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(sources)]
        frozen=dict(created_utc=now(),steps_per_branch=STEPS,branches=['native_reference_intensity','native_reference_spatial','raw_pchip_intensity','raw_pchip_spatial'],
            device=device,source_bindings=bindings,schedule_prefix_sha256=array_sha(draws),mother_GT_and_crop_matched=True,
            label_changes_only_from_explicit_spatial_transform=True,optimizer=dict(name='AdamW',lr=1e-4,weight_decay=1e-4,reset=True),
            wall_bound_seconds=MAX_SECONDS,stage_save_bound_bytes=MAX_BYTES,optimizer_resume_supported=False)
        with (OUT/'frozen_config.json').open('x',encoding='utf-8') as f:json.dump(frozen,f,indent=2);f.write('\n')
        r['frozen_config_sha256']=sha(OUT/'frozen_config.json');save()
        # Actual parent checkpoint bytes are known; logs add spatial records, estimated separately with a generous cap.
        parent_bytes=sum((ROOT/a['checkpoint_path']).stat().st_size for a in trainexit['arms'])
        r['preflight_storage_forecast']=dict(four_final_weight_files_bytes=2*parent_bytes,one_atomic_weight_temp_bytes=max((ROOT/a['checkpoint_path']).stat().st_size for a in trainexit['arms']),
            four_gzip_journals_allowance_bytes=12_000_000,metadata_allowance_bytes=3_000_000)
        forecast=sum(r['preflight_storage_forecast'].values());assert forecast<MAX_BYTES
        r['preflight_storage_forecast']['total_forecast_bytes']=forecast;save()
        q=read(QPATH);old={a['kind']:{s['uid']:s for s in a['cache_records']} for a in q['arms']};cross_labels={}
        for kind in ['native_reference','raw_pchip']:
            b=next(a for a in trainexit['arms'] if a['kind']==kind);cpfile=ROOT/b['checkpoint_path'];assert sha(cpfile)==b['checkpoint_sha256']
            cp=torch.load(cpfile,map_location='cpu',weights_only=True);initial=cp['state_dict'];assert cp['updates_completed']==19998 and state_hash(initial)==cp['final_weights_sha256']
            cache={};cache_records=[];r['status']='loading_development_cache';save()
            for c,row in cases:
                guard();image,stats=source_image(c,row,kind);grid=lattice(c);image=physical_mr(image,grid)
                target=physical_label(read_reference_label(c),grid);ih,yh=array_sha(image),array_sha(target)
                assert ih==old[kind][c['uid']]['input_sha256'] and yh==old[kind][c['uid']]['label_sha256']
                cache[c['uid']]=(image,target,grid);cache_records.append(dict(patient=c['patient'],uid=c['uid'],input_sha256=ih,label_sha256=yh))
            pair={}
            for augment in ['intensity','spatial']:
                name=kind+'_'+augment;model=TaskUNet3D();model.load_state_dict(initial);assert state_hash(model.state_dict())==cp['final_weights_sha256']
                model.to(device);model.train();opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4)
                arm=dict(name=name,kind=kind,augmentation=augment,complete=False,updates_completed=0,starting_original_updates=19998,
                    starting_weights_sha256=cp['final_weights_sha256'],optimizer_reset=True,cache_records=cache_records,step_seconds=[])
                r['arms'].append(arm);r['status']='training';save();logpath=OUT/(name+'_history.jsonl.gz')
                with logpath.open('xb') as raw:
                    with gzip.GzipFile(fileobj=raw,mode='wb',compresslevel=6,mtime=0) as stream:
                        for step,(pi,ci) in enumerate(draws,1):
                            guard();tick=time.perf_counter();c,row=cases[int(ci)];assert c['patient']==config['patient_ids'][int(pi)]
                            image,target,grid=cache[c['uid']];x,y,geometry=sample_batch(image,target,batch_rng(19998+step))
                            pivot=spatial.pivots(geometry,x.shape[2:]);sp=spatial.primitives(step);ip=intensity.primitives(step)
                            mother_sha=array_sha(y.numpy());base_input_sha=array_sha(x.numpy())
                            identity=dict(patient=c['patient'],uid=c['uid'],mother_label_sha256=mother_sha,geometry=geometry,spatial_primitives=sp,intensity_primitives=ip,pivots_zrc=pivot)
                            if augment=='intensity':pair[step]=(identity,base_input_sha)
                            else:assert pair[step]==(identity,base_input_sha)
                            if kind=='native_reference' and augment=='intensity':cross_labels[step]=dict(identity=identity)
                            else:assert cross_labels[step]['identity']==identity
                            if augment=='spatial':
                                xx,yy,matrices=spatial.apply(x.numpy(),y.numpy(),sp,pivot,grid['realized_spacing_zrc_mm'])
                                assert yy[0,0][tuple(map(int,pivot[0]))]==1
                                yy_sha=array_sha(yy)
                                if kind=='native_reference':cross_labels[step]['spatial_label_sha256']=yy_sha
                                else:assert cross_labels[step]['spatial_label_sha256']==yy_sha
                            else:xx,yy,matrices=x.numpy(),y.numpy(),None
                            xx=intensity.apply(xx,ip);input_sha=array_sha(xx);label_sha=array_sha(yy)
                            x=torch.from_numpy(xx).to(device);y=torch.from_numpy(yy).to(device)
                            opt.zero_grad(set_to_none=True);outputs=model(x);value=loss(outputs,y);assert torch.isfinite(value)
                            value.backward();assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
                            if step==1:
                                arm['first_update_branch_gradient_max']={n:max(float(p.grad.abs().max()) for p in module.parameters()) for n,module in
                                    [('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads)]}
                                assert all(v>0 for v in arm['first_update_branch_gradient_max'].values())
                            opt.step();assert all(torch.isfinite(p).all() for p in model.parameters())
                            elapsed=time.perf_counter()-tick
                            record=dict(step=step,**identity,base_input_sha256=base_input_sha,input_sha256=input_sha,training_label_sha256=label_sha,
                                theta_normalized_xyz=matrices,loss=float(value.detach()),lr=1e-4,total_step_seconds=elapsed)
                            stream.write((json.dumps(record,separators=(',',':'))+'\n').encode('utf-8'));stream.flush(zlib.Z_SYNC_FLUSH)
                            arm['updates_completed']=step;arm['step_seconds'].append(elapsed);r['new_GPU_updates' if device=='cuda:0' else 'new_cpu_updates']+=1
                            if step==22 or step%110==0 or step==STEPS:
                                raw.flush();os.fsync(raw.fileno());save();print(json.dumps(dict(branch=name,updates=step,loss=record['loss'],
                                    branch_median_step_seconds=float(np.median(arm['step_seconds'])),cumulative_seconds=time.perf_counter()-started)),flush=True)
                            del x,y,xx,yy,outputs,value
                    raw.flush();os.fsync(raw.fileno())
                state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};final_hash=state_hash(state);assert final_hash!=cp['final_weights_sha256']
                checkpoint=OUT/(name+'_last2992.pt');guard()
                final_torch(checkpoint,dict(state_dict=state,kind=kind,augmentation=augment,updates=STEPS,starting_original_updates=19998,
                    starting_weights_sha256=cp['final_weights_sha256'],final_weights_sha256=final_hash,history_sha256=sha(logpath),
                    protocol_sha256=sha(HERE/'PROTOCOL.md'),frozen_config_sha256=sha(OUT/'frozen_config.json')))
                # Only terminal compressed journals are read/hashed; current rolling ones are not frozen.
                with gzip.open(logpath,'rt',encoding='utf-8') as f:history=[json.loads(line) for line in f]
                assert len(history)==STEPS and [h['step'] for h in history]==list(range(1,STEPS+1))
                arm.update(complete=True,final_weights_sha256=final_hash,checkpoint_path=checkpoint.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(checkpoint),
                    history_path=logpath.relative_to(ROOT).as_posix(),history_sha256=sha(logpath),history_bytes=logpath.stat().st_size,
                    median_step_seconds=float(np.median(arm['step_seconds'])))
                del model,opt,state,history;gc.collect()
                if device=='cuda:0':torch.cuda.empty_cache()
                guard();save()
            del cache,cp,initial,pair;gc.collect()
        for b in bindings:assert sha(ROOT/b['path'])==b['sha256']
        r.update(complete=len(r['arms'])==4 and all(a['complete'] for a in r['arms']),status='completed',
            mother_labels_geometry_and_augmentation_primitives_paired=True,cross_input_spatial_labels_paired=True,
            source_bindings=bindings,resources_after=guard())
    except Exception as e:r['status']='failed';r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(finished_utc=now(),elapsed_seconds=time.perf_counter()-started,CUDA_initialized=torch.cuda.is_initialized());save()
    print(json.dumps({k:r.get(k) for k in ['complete','status','errors','device','new_cpu_updates','new_GPU_updates','elapsed_seconds']}),flush=True)
    return int(not r['complete'] or bool(r['errors']))
if __name__=='__main__':raise SystemExit(main())
