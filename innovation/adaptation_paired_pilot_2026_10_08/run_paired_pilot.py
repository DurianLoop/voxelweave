"""Four matched 99-update continuation branches; no medical scoring during fitting."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import torch
original_cuda_initializer=torch.cuda._lazy_init
import gc,json,sys,time,traceback,subprocess
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import (
    development_cases,source_image,lattice,physical_mr,physical_label,read_reference_label,
    sample_batch,batch_rng,TaskUNet3D,loss,state_hash,read,sha,array_sha,np,resource_guard,QPATH)
from augmentation import apply,primitives
TRAIN=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
V4=ROOT/'final_training_medical_execution_2026_10_08'
OUT=HERE/'attempt01';STEPS=99;MAX_BYTES=40_000_000

def now():return datetime.now(timezone.utc).isoformat()
def saved():return sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
def atomic_json(path,value):
    temp=path.with_name(path.name+'.tmp')
    with temp.open('w',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temp,path)
def atomic_torch(path,value):
    assert not path.exists();temp=path.with_name(path.name+'.tmp')
    with temp.open('xb') as f:torch.save(value,f);f.flush();os.fsync(f.fileno())
    os.replace(temp,path)

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();torch.set_num_threads(4)
    OUT.mkdir(exist_ok=False);dest=OUT/'receipt.json';r=dict(created_utc=now(),complete=False,status='preparing',errors=[],arms=[],
        source_bindings=[],new_cpu_updates=0,new_GPU_updates=0,planned_updates_per_branch=STEPS,planned_total_updates=396,
        validation_arrays_loaded=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        task_effects_scored=False,publication_claim_confirmed=False,goal_status='active',original_training_modified=False,
        other_PIDs_enumerated=False,other_PIDs_modified=False)
    device='cpu'
    def save():atomic_json(dest,r)
    def guard():
        assert time.perf_counter()-started<=3600,'pilot wall3600s exceeded'
        res=resource_guard();assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1
        assert saved()<MAX_BYTES,'pilot40MB storage exceeded';res.update(cpu_threads=4,pilot_saved_bytes=saved())
        if device=='cuda:0':
            free,total=torch.cuda.mem_get_info(0);peak=torch.cuda.max_memory_reserved(0)
            assert free>=4_000_000_000 and peak<=2_500_000_000,'GPU runtime reserve/peak gate failed'
            res.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
        else:assert not torch.cuda.is_initialized()
        return res
    save()
    try:
        qualification=read(HERE/'QUALIFICATION.json')
        assert qualification['complete'] and not qualification['errors'] and qualification['all_formula_gates_passed']
        for b in qualification['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        exitpath=V4/'ACTUAL_PRECISION_V4_EXIT.json';ex=read(exitpath);vr=read(V4/'precision_v4_attempt01/receipt.json')
        assert ex['observed_tool_exit']==0 and ex['result_sha256']==sha(V4/'precision_v4_attempt01/receipt.json')
        assert vr['complete'] and not vr['errors'] and vr['all_strict_numeric_gates_passed']
        # Medical failure authorizes a separate adaptation diagnostic, not a downstream action claim.
        r['parent_medical_capability_passed']=vr['all_arms_validation_gates_passed']
        r['resources_before']=guard()
        assert r['resources_before']['workspace_free_bytes']-8_000_000_000>=MAX_BYTES-saved()
        query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.total,memory.free','--format=csv,noheader,nounits'],
            capture_output=True,text=True,timeout=20,check=True)
        rows=[dict(zip(['index','total_MiB','free_MiB'],map(int,l.split(',')))) for l in query.stdout.strip().splitlines()]
        assert len(rows)==1 and rows[0]['index']==0;r['GPU_totals_observation']=rows
        r['GPU_start_gate_passed']=rows[0]['free_MiB']>=8192
        if r['GPU_start_gate_passed']:
            os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer
            assert torch.cuda.is_available();torch.cuda.set_per_process_memory_fraction(.1,0)
            torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
            torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
            free,total=torch.cuda.mem_get_info(0);assert free>=8_000_000_000
            device='cuda:0'
        r['device']=device;guard();save()
        config=read(TRAIN/'frozen_config.json');trainexit=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json')
        assert trainexit['training_observed_tool_exit']==0 and trainexit['formal_training_updates']==39996
        assert sha(TRAIN/'invocation02.json')==trainexit['training_result_sha256']
        for b in config['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        draws=np.load(TRAIN/config['schedule_file'],allow_pickle=False)[:STEPS]
        assert sha(TRAIN/config['schedule_file'])==config['schedule_file_sha256'] and draws.shape==(STEPS,2)
        assert all(int(np.count_nonzero(draws[:,0]==i))==9 for i in range(11))
        cases=development_cases();assert config['series']==[dict(patient=c['patient'],uid=c['uid']) for c,row in cases]
        sources={Path(__file__),HERE/'augmentation.py',HERE/'PROTOCOL.md',HERE/'QUALIFICATION.json',exitpath,
            V4/'precision_v4_attempt01/receipt.json',TRAIN/'frozen_config.json',TRAIN/config['schedule_file'],
            ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json'}
        sources.update(ROOT/b['path'] for b in config['source_bindings'])
        sources.update(ROOT/a['checkpoint_path'] for a in trainexit['arms'])
        frozen_sources=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(sources)]
        frozen=dict(created_utc=now(),steps=STEPS,device=device,source_bindings=frozen_sources,
            schedule_prefix_sha256=array_sha(draws),protocol_sha256=sha(HERE/'PROTOCOL.md'))
        with (OUT/'frozen_config.json').open('x',encoding='utf-8') as f:json.dump(frozen,f,indent=2);f.write('\n')
        r['frozen_config_sha256']=sha(OUT/'frozen_config.json');save()
        cross_input_pairing={}
        for kind in ('native_reference','raw_pchip'):
            binding=next(a for a in trainexit['arms'] if a['kind']==kind)
            cpfile=ROOT/binding['checkpoint_path'];assert sha(cpfile)==binding['checkpoint_sha256'];sources.add(cpfile)
            cp=torch.load(cpfile,map_location='cpu',weights_only=True);initial=cp['state_dict']
            assert cp['updates_completed']==19998 and state_hash(initial)==cp['final_weights_sha256']
            cache={};cache_records=[];old={s['uid']:s for s in next(a for a in read(QPATH)['arms'] if a['kind']==kind)['cache_records']}
            r['status']='loading_development_cache';save()
            for c,row in cases:
                guard();image,st=source_image(c,row,kind);grid=lattice(c);image=physical_mr(image,grid)
                target=physical_label(read_reference_label(c),grid);ih,yh=array_sha(image),array_sha(target)
                assert ih==old[c['uid']]['input_sha256'] and yh==old[c['uid']]['label_sha256']
                cache[c['uid']]=(image,target);cache_records.append(dict(patient=c['patient'],uid=c['uid'],input_sha256=ih,label_sha256=yh))
            paired={}
            for augment in ('basic','strong'):
                name=kind+'_'+augment;model=TaskUNet3D();model.load_state_dict(initial);model.to(device);model.train()
                assert state_hash(model.state_dict())==cp['final_weights_sha256']
                opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4)
                arm=dict(name=name,kind=kind,augmentation=augment,complete=False,updates_completed=0,
                    starting_weights_sha256=cp['final_weights_sha256'],starting_original_updates=19998,
                    optimizer_reset=True,cache_records=cache_records,step_seconds=[])
                r['arms'].append(arm);r['status']='training';save();logpath=OUT/(name+'_history.jsonl')
                with logpath.open('x',encoding='utf-8') as log:
                    for step,(pi,ci) in enumerate(draws,1):
                        guard();tick=time.perf_counter();c,row=cases[int(ci)]
                        assert c['patient']==config['patient_ids'][int(pi)]
                        x,y,geometry=sample_batch(*cache[c['uid']],batch_rng(19998+step));basic_sha=array_sha(x.numpy());label_sha=array_sha(y.numpy())
                        strong_primitives=primitives(step)
                        identity=dict(patient=c['patient'],uid=c['uid'],label_sha256=label_sha,geometry=geometry,strong_primitives=strong_primitives)
                        if augment=='basic':paired[step]=dict(identity=identity,basic_input_sha256=basic_sha)
                        else:assert paired[step]==dict(identity=identity,basic_input_sha256=basic_sha)
                        if kind=='native_reference' and augment=='basic':cross_input_pairing[step]=identity
                        else:assert cross_input_pairing[step]==identity
                        if augment=='strong':x=torch.from_numpy(apply(x.numpy(),strong_primitives))
                        assert array_sha(y.numpy())==label_sha;input_sha=array_sha(x.numpy());x=x.to(device);y=y.to(device)
                        opt.zero_grad(set_to_none=True);outputs=model(x);value=loss(outputs,y);assert torch.isfinite(value)
                        value.backward();assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
                        if step==1:
                            arm['first_update_branch_gradient_max']={n:max(float(p.grad.abs().max()) for p in module.parameters())
                                for n,module in [('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads)]}
                            assert all(v>0 for v in arm['first_update_branch_gradient_max'].values())
                        opt.step();assert all(torch.isfinite(p).all() for p in model.parameters())
                        elapsed=time.perf_counter()-tick
                        record=dict(step=step,input_sha256=input_sha,basic_input_sha256=basic_sha,**identity,loss=float(value.detach()),lr=1e-4,total_step_seconds=elapsed)
                        log.write(json.dumps(record,separators=(',',':'))+'\n');log.flush()
                        arm['updates_completed']=step;arm['step_seconds'].append(elapsed)
                        r['new_GPU_updates' if device=='cuda:0' else 'new_cpu_updates']+=1
                        if step%11==0:
                            save();print(json.dumps(dict(branch=name,updates=step,loss=record['loss'],elapsed_seconds=time.perf_counter()-started)),flush=True)
                        del x,y,outputs,value
                    os.fsync(log.fileno())
                state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};final_hash=state_hash(state)
                assert final_hash!=cp['final_weights_sha256'];checkpoint=OUT/(name+'_last99.pt')
                guard();assert resource_guard()['workspace_free_bytes']-8_000_000_000>=sum(v.numel()*v.element_size() for v in state.values())+200_000
                atomic_torch(checkpoint,dict(state_dict=state,kind=kind,augmentation=augment,updates=STEPS,
                    starting_original_updates=19998,starting_weights_sha256=cp['final_weights_sha256'],final_weights_sha256=final_hash,
                    protocol_sha256=sha(HERE/'PROTOCOL.md'),history_sha256=sha(logpath)))
                arm.update(complete=True,checkpoint_path=checkpoint.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(checkpoint),
                    final_weights_sha256=final_hash,history_path=logpath.relative_to(ROOT).as_posix(),history_sha256=sha(logpath),
                    median_step_seconds=float(np.median(arm['step_seconds'])))
                del model,opt,state;gc.collect()
                if device=='cuda:0':torch.cuda.empty_cache()
                guard();save()
            del cache,cp,initial;gc.collect()
        for b in frozen_sources:assert sha(ROOT/b['path'])==b['sha256']
        r.update(complete=len(r['arms'])==4 and all(a['complete'] for a in r['arms']),status='completed',
            paired_labels_geometry_and_strong_primitives_verified=True,resources_after=guard(),
            source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(sources)])
    except Exception as e:r['status']='failed';r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(finished_utc=now(),elapsed_seconds=time.perf_counter()-started,CUDA_initialized=torch.cuda.is_initialized());save()
    print(json.dumps({k:r.get(k) for k in ('complete','status','errors','device','new_cpu_updates','new_GPU_updates','elapsed_seconds')}),flush=True)
    return int(not r['complete'] or bool(r['errors']))
if __name__=='__main__':raise SystemExit(main())
