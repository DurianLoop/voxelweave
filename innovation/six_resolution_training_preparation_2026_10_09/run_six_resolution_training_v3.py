"""New v2: latest104,156,359-byte family and all19 optimizer admission; v1 remains immutable."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import torch
original_cuda_initializer=torch.cuda._lazy_init
import argparse,gc,gzip,itertools,json,sys,time,traceback,zlib,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import (
    development_cases,lattice,source_image,physical_mr,physical_label,read_reference_label,
    sample_batch,batch_rng,loss,state_hash,array_sha,QPATH,np)
sys.path.insert(0,str(ROOT/'gpu_graph_cost_smoke_2026_10_09'))
from checkpointed_model import CheckpointedTaskUNet3D
sys.path.insert(0,str(ROOT/'certified_resolution_rounding_2026_10_09'))
from certified_resolution import apply as resolution_apply
sys.path.insert(0,str(ROOT/'intensity_precision_failure_diagnosis_2026_10_09'))
import intensity_float64_stats as intensity

STEPS=2992;KINDS=['native_reference','raw_pchip'];MODES=['throughplane','inplane','allaxes']
FAMILY_BYTES=61_356_359;TRAIN_BYTES=54_356_359;OTHER_BYTES=42_800_000;DISK_RESERVE=8_000_000_000
TRAIN=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'

def terminal(path,session=None):
    if not path.exists():return False
    v=read(path)
    return v.get('exit_code')==0 and 'session_id' not in v and (session is None or v.get('observed_unified_exec_session')==session)

def checks():
    resources=resource_guard();full=ROOT/'full_certified_schedule_2026_10_09'
    opt=ROOT/'action_oracle_and_prior_art_2026_10_09'
    flags={};bindings=[entry(Path(__file__)),entry(HERE/'V3_PROTOCOL.md'),entry(HERE/'V2_PROTOCOL.md'),entry(HERE/'prepare_v3_entries.py'),entry(HERE/'PROTOCOL.md'),entry(HERE/'prepare_runner_v2.py'),entry(HERE/'run_six_resolution_training.py')]
    def completed(path,required):
        if not path.exists():return False
        v=read(path)
        if not v.get('complete') or v.get('errors') or not all(v.get(k) is True for k in required):return False
        for b in v.get('source_bindings',v.get('sources',[])):bind(b)
        bindings.append(entry(path));return True
    flags['full35904_actual_terminal']=terminal(full/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json',44317)
    flags['full35904_independent_terminal_audit']=flags['full35904_actual_terminal'] and completed(
        full/'full_real_terminal_audit_attempt01/receipt.json',['all35904_unique_journal_fields_verified','all_strict_numeric_gates_verified_from_actual_journal'])
    flags['six_first_AdamW_actual_terminal']=terminal(opt/'ACTUAL_OPTIMIZER_TERMINAL_TOOL.json',61338)
    flags['six_first_AdamW_terminal_audit']=flags['six_first_AdamW_actual_terminal'] and completed(
        opt/'optimizer_audit_attempt01/receipt.json',['all_six_first_update_identities_verified','all_first_step_parameter_and_moment_checks_verified','all_six_memory_captures_verified'])
    coverage=ROOT/'development_optimizer_coverage_2026_10_09'
    flags['all19_optimizer_actual_terminal']=terminal(coverage/'ACTUAL_COVERAGE_TERMINAL_TOOL.json',78758)
    flags['all19_optimizer_independent_terminal_audit']=flags['all19_optimizer_actual_terminal'] and completed(
        coverage/'terminal_audit_attempt01/receipt.json',['all228_unique_updates_and456_patch_fields_verified',
        'all19_series11_patients_and114_branch_denominators_verified',
        'all_optimizer_step1_step2_parameter_moment_and_memory_capture_records_verified'])
    deployment=HERE/'FULL_GPU_DEPLOYMENT_QUALIFICATION_V3.json'
    flags['full_fov_probability_binary_coordinate_and_atomic_capture']=completed(deployment,[
        'all38_parent_full_fov_probabilities_independently_verified','all_probability_errors_le_3e_6',
        'all_coordinate_errors_le_3e_12','all_binary_disagreements_zero','disk_atomic_capture_and_reload_verified',
        'complete_pipeline_cost_components_measured','all19_development_series_represented_in_training_cost_measurements','memory_contract_passed'])
    if flags['full_fov_probability_binary_coordinate_and_atomic_capture']:
        d=read(deployment);assert d['complete_family_wall_forecast_seconds']>0
        assert d['admitted_training_wall_seconds']>0 and d['complete_family_wall_forecast_seconds']>=d['admitted_training_wall_seconds']
        assert terminal(bind(d['actual_terminal_binding']))
        audit=read(bind(d['independent_audit_binding']));assert audit['complete'] and not audit['errors']
    cfg=read(TRAIN/'frozen_config.json');schedule=TRAIN/cfg['schedule_file']
    for b in cfg['source_bindings']:bind(b)
    assert sha(schedule)==cfg['schedule_file_sha256']
    draws=np.load(schedule,allow_pickle=False)[:STEPS]
    assert draws.shape==(STEPS,2) and all(np.count_nonzero(draws[:,0]==i)==272 for i in range(11))
    cases=development_cases();assert len(cases)==19
    assert cfg['series']==[dict(patient=c['patient'],uid=c['uid']) for c,row in cases]
    bindings.extend([entry(TRAIN/'frozen_config.json'),entry(schedule),entry(QPATH)])
    tp=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json';train=read(tp)
    assert train['training_observed_tool_exit']==0 and train['formal_training_updates']==39996
    assert set(a['kind'] for a in train['arms'])==set(KINDS)
    for a in train['arms']:
        p=ROOT/a['checkpoint_path'];assert sha(p)==a['checkpoint_sha256'];bindings.append(entry(p))
    bindings.append(entry(tp))
    for mod in list(sys.modules.values()):
        value=getattr(mod,'__file__',None)
        if value:
            path=Path(value).resolve()
            if path.is_relative_to(ROOT) and path.suffix=='.py':bindings.append(entry(path))
    flags['matched2992_schedule_and_parent_SHA']=True
    flags['complete_family_disk_admitted']=resources['workspace_free_bytes']-DISK_RESERVE>=FAMILY_BYTES+OTHER_BYTES
    q=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
    gpu=[list(map(int,line.split(','))) for line in q.stdout.strip().splitlines()]
    flags['GPU_aggregate_admitted']=len(gpu)==1 and gpu[0][0]==0 and gpu[0][1]>=8192
    return dict(complete=True,errors=[],ready=all(flags.values()),checks=flags,pending=[k for k,v in flags.items() if not v],
        resources=resources,GPU_aggregate=gpu,required_above_reserve_bytes=FAMILY_BYTES+OTHER_BYTES,
        disk_shortfall_bytes=max(0,FAMILY_BYTES+OTHER_BYTES-(resources['workspace_free_bytes']-DISK_RESERVE)),
        planned_updates=STEPS*6,patient_exposure_per_branch=272,source_bindings=bindings,
        MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,CUDA_initialized=torch.cuda.is_initialized(),
        new_training_launched=False,strict_LOPO_warm_start_allowed=False,confirmation_patients_opened=False,
        lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')

def atomic(path,value,torch_file=False):
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('wb' if torch_file else 'w',**({} if torch_file else dict(encoding='utf-8'))) as f:
        if torch_file:torch.save(value,f)
        else:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
        f.flush();os.fsync(f.fileno())
    tmp.replace(path)

def train(report):
    assert report['ready'],'Missing readiness gates: '+', '.join(report['pending'])
    assert not torch.cuda.is_initialized();started=time.perf_counter()
    full=ROOT/'full_certified_schedule_2026_10_09';qualification=read(full/'full_real_pipeline_attempt01/receipt.json')
    assert qualification['complete'] and qualification['all35904_full_target_MRI_and_intensity_fields_verified']
    for b in qualification['source_bindings']:bind(b)
    oldpath=ROOT/'real_context_and_author_code_followup_2026_10_08/full_schedule_attempt01/receipt.json'
    old=read(oldpath);journal=ROOT/old['journal_path'];assert sha(journal)==old['journal_sha256']
    with gzip.open(journal,'rt',encoding='utf-8') as f:rows=[json.loads(x) for x in f]
    indexed={(v['step'],v['patch']):v for v in rows}
    assert len(indexed)==len(rows)==5984 and set(indexed)==set(itertools.product(range(1,2993),range(2)))
    cfg=read(TRAIN/'frozen_config.json');draws=np.load(TRAIN/cfg['schedule_file'],allow_pickle=False)[:STEPS]
    cases=development_cases();parent=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json')
    refs={a['kind']:{c['uid']:c for c in a['cache_records']} for a in read(QPATH)['arms']}
    cost=read(HERE/'FULL_GPU_DEPLOYMENT_QUALIFICATION_V3.json');wall=cost['admitted_training_wall_seconds']
    out=HERE/'training_v3_attempt01';out.mkdir(exist_ok=False)
    bindings=report['source_bindings']+[entry(full/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json'),entry(full/'full_real_pipeline_attempt01/receipt.json'),entry(journal),entry(oldpath)]
    frozen=dict(steps_per_arm=STEPS,kinds=KINDS,modes=MODES,optimizer=dict(name='AdamW',lr=1e-4,weight_decay=1e-4,foreach=False,fused=False,reset=True),
        schedule_prefix_sha256=array_sha(draws),source_bindings=bindings,training_wall_seconds=wall,stage_limit_bytes=FAMILY_BYTES,
        strict_LOPO_warm_start_allowed=False,confirmation_patients_opened=False,lockedIXI_opened=False)
    dump(out/'frozen_config.json',frozen)
    r=dict(complete=False,status='running',errors=[],arms=[],training_updates=0,source_bindings=bindings,
        validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        publication_claim_confirmed=False,goal_status='active',optimizer_resume_supported=False)
    def save():atomic(out/'receipt.json',r)
    def guard(cuda=True):
        res=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        assert size<TRAIN_BYTES and res['workspace_free_bytes']-OTHER_BYTES-(FAMILY_BYTES-size)>=DISK_RESERVE
        assert time.perf_counter()-started<wall and torch.get_num_threads()==torch.get_num_interop_threads()==1
        if cuda:
            free,total=torch.cuda.mem_get_info(0);assert free>=4_000_000_000 and torch.cuda.max_memory_reserved(0)<=2_500_000_000
        return res
    save()
    try:
        guard(False);os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer
        assert torch.cuda.is_available();torch.cuda.set_per_process_memory_fraction(.1,0)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
        free,total=torch.cuda.mem_get_info(0);assert free>=8192*1024**2
        for kind in KINDS:
            a=next(v for v in parent['arms'] if v['kind']==kind)
            cp=torch.load(ROOT/a['checkpoint_path'],map_location='cpu',weights_only=True)
            assert cp['updates_completed']==19998 and state_hash(cp['state_dict'])==cp['final_weights_sha256']
            cache={}
            for c,row in cases:
                guard();grid=lattice(c);image,stats=source_image(c,row,kind);image=physical_mr(image,grid)
                target=physical_label(read_reference_label(c),grid)
                assert array_sha(image)==refs[kind][c['uid']]['input_sha256'] and array_sha(target)==refs[kind][c['uid']]['label_sha256']
                cache[c['uid']]=(image,target,grid)
            for mode in MODES:
                guard();model=CheckpointedTaskUNet3D();model.load_state_dict(cp['state_dict'])
                assert state_hash(model.state_dict())==cp['final_weights_sha256'];model.to('cuda:0');model.train()
                opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4,foreach=False,fused=False)
                arm=dict(kind=kind,mode=mode,complete=False,updates_completed=0,starting_weights_sha256=cp['final_weights_sha256'],optimizer_reset=True)
                r['arms'].append(arm);logpath=out/(kind+'_'+mode+'_history.jsonl.gz');save()
                with logpath.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',compresslevel=6,mtime=0) as stream:
                    for step,(pi,ci) in enumerate(draws,1):
                        guard();tick=time.perf_counter();c,row=cases[int(ci)];assert c['patient']==cfg['patient_ids'][int(pi)]
                        image,target,grid=cache[c['uid']];x,y,geometry=sample_batch(image,target,batch_rng(19998+step))
                        mother=array_sha(y.numpy());prepared=[];metas=[]
                        for p in range(2):
                            source=indexed[(step,p)]
                            assert source['uid']==c['uid'] and source['patient']==c['patient']
                            assert source['geometry']==geometry[p] and source['mother_label_sha256']==mother
                            assert source['target_label_sha256']==array_sha(y.numpy()[p,0])
                            xx,support,meta=resolution_apply(image,grid,geometry[p],source['primitive'],mode)
                            prepared.append(xx);metas.append(meta)
                        xx=intensity.apply(np.stack(prepared)[:,None],intensity.primitives(step))
                        assert array_sha(y.numpy())==mother;ih=array_sha(xx);base=array_sha(x.numpy())
                        gx=torch.from_numpy(xx).to('cuda:0');gy=y.to('cuda:0');opt.zero_grad(set_to_none=True)
                        outputs=model(gx);value=loss(outputs,gy);assert torch.isfinite(value)
                        value.backward();assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
                        opt.step();assert all(torch.isfinite(p).all() for p in model.parameters());torch.cuda.synchronize()
                        record=dict(step=step,patient=c['patient'],uid=c['uid'],geometry=geometry,mother_label_sha256=mother,
                            base_input_sha256=base,input_sha256=ih,resolution_primitives=[indexed[(step,p)]['primitive'] for p in range(2)],
                            intensity_primitives=intensity.primitives(step),resolution_metadata=metas,loss=float(value.detach()),seconds=time.perf_counter()-tick)
                        stream.write((json.dumps(record,separators=(',',':'))+'\n').encode('utf-8'));stream.flush(zlib.Z_SYNC_FLUSH)
                        arm['updates_completed']=step;r['training_updates']+=1
                        del gx,gy,outputs,value,prepared,xx,x,y,support
                        if step%110==0 or step==STEPS:
                            raw.flush();os.fsync(raw.fileno());save();print(json.dumps(dict(kind=kind,mode=mode,updates=step)),flush=True)
                    raw.flush();os.fsync(raw.fileno())
                state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};final=state_hash(state)
                assert final!=cp['final_weights_sha256'];guard()
                checkpoint=out/(kind+'_'+mode+'_last2992.pt');assert not checkpoint.exists()
                atomic(checkpoint,dict(state_dict=state,kind=kind,mode=mode,updates=STEPS,starting_original_updates=19998,
                    starting_weights_sha256=cp['final_weights_sha256'],final_weights_sha256=final,history_sha256=sha(logpath),
                    frozen_config_sha256=sha(out/'frozen_config.json')),True)
                restored=torch.load(checkpoint,map_location='cpu',weights_only=True);assert state_hash(restored['state_dict'])==final
                with gzip.open(logpath,'rt',encoding='utf-8') as f:history=[json.loads(line) for line in f]
                assert [v['step'] for v in history]==list(range(1,STEPS+1))
                assert all(sum(v['patient']==pid for v in history)==272 for pid in cfg['patient_ids'])
                arm.update(complete=True,checkpoint=entry(checkpoint),journal=entry(logpath),final_weights_sha256=final)
                del model,opt,state,history,restored;gc.collect();torch.cuda.empty_cache();guard();save()
            del cache,cp;gc.collect();torch.cuda.empty_cache()
        for b in bindings:bind(b)
        assert r['training_updates']==17952 and len(r['arms'])==6 and all(v['complete'] for v in r['arms'])
        r.update(complete=True,status='completed',resources_after=guard())
    except Exception as e:r.update(status='failed',traceback=traceback.format_exc());r['errors'].append(type(e).__name__+': '+str(e))
    r['elapsed_seconds']=time.perf_counter()-started;save();print(json.dumps({k:r[k] for k in ['complete','status','errors','training_updates']}))
    return int(not r['complete'])

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    p=argparse.ArgumentParser();m=p.add_mutually_exclusive_group();m.add_argument('--preflight',action='store_true');m.add_argument('--train',action='store_true');args=p.parse_args()
    report=checks()
    if args.train:return train(report)
    out=HERE/'preflight_v3_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='source_bindings'}));return 0
if __name__=='__main__':raise SystemExit(main())
