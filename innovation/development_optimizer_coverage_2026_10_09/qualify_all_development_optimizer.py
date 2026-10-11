"""All19 series x two inputs x three modes x two actual consecutive AdamW updates."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import torch
original_cuda_initializer=torch.cuda._lazy_init
import gc,gzip,hashlib,io,itertools,json,sys,time,traceback,subprocess,zlib
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
sys.path.insert(0,str(ROOT/'resolution_degradation_controls_2026_10_08'))
from qualify_synthetic_and_schedule_v2 import independent_domain
sys.path.insert(0,str(ROOT/'certified_resolution_rounding_2026_10_09'))
from certified_resolution import apply as candidate
sys.path.insert(0,str(ROOT/'direct_oracle_efficiency_2026_10_09'))
from direct_separable_reference import apply_reference as reference
sys.path.insert(0,str(ROOT/'intensity_precision_failure_diagnosis_2026_10_09'))
import intensity_float64_stats as intensity

KINDS=['native_reference','raw_pchip'];MODES=['throughplane','inplane','allaxes']
PATCH=(64,128,128);WALL=7200;LIMIT=2_000_000;OTHER=18_800_000;JOURNAL_LIMIT=1_400_000

def equal_tree(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.detach().cpu(),b.detach().cpu())
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(equal_tree(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a)==type(b) and len(a)==len(b) and all(equal_tree(x,y) for x,y in zip(a,b))
    return type(a)==type(b) and a==b

def optimizer_hash(opt,model):
    h=hashlib.sha256()
    for n,p in model.named_parameters():
        h.update(n.encode())
        for key in ['step','exp_avg','exp_avg_sq']:
            t=opt.state[p][key].detach().cpu().contiguous();h.update(key.encode());h.update(str(t.dtype).encode());h.update(str(tuple(t.shape)).encode());h.update(t.numpy().tobytes())
    return h.hexdigest()

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    started=time.perf_counter();out=HERE/'coverage_attempt01';out.mkdir(exist_ok=False);journal=out/'steps.jsonl.gz'
    r=dict(complete=False,status='preparing',errors=[],branches=[],cache_records=[],training_updates=0,GPU_forwards=0,GPU_backwards=0,
        in_memory_captures=0,MRI_input_arrays_loaded=0,GT_arrays_loaded=0,parent_model_arrays_loaded=0,
        formal_six_arm_training_launched=False,weights_saved=False,full_fov_inference=False,medical_effect_scored=False,
        validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,other_PIDs_enumerated=False,
        other_PIDs_modified=False,original_training_modified=False,strict_LOPO_warm_start_allowed=False,
        training_ready=False,publication_claim_confirmed=False,goal_status='active')
    def save():
        tmp=out/'receipt.json.tmp';tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(out/'receipt.json')
    def guard(cuda=False):
        v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        assert size<LIMIT and v['workspace_free_bytes']-OTHER-(LIMIT-size)>=8_000_000_000
        assert time.perf_counter()-started<WALL and torch.get_num_threads()==torch.get_num_interop_threads()==1
        if journal.exists():assert journal.stat().st_size<JOURNAL_LIMIT
        if cuda:
            free,total=torch.cuda.mem_get_info(0);peak=torch.cuda.max_memory_reserved(0)
            assert free>=4_000_000_000 and peak<=2_500_000_000
            v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
        return v
    save()
    try:
        r['resources_before']=guard();assert not torch.cuda.is_initialized()
        prev=ROOT/'action_oracle_and_prior_art_2026_10_09'
        term=read(prev/'ACTUAL_OPTIMIZER_TERMINAL_TOOL.json');audit=read(prev/'optimizer_audit_attempt01/receipt.json')
        assert term['exit_code']==0 and 'session_id' not in term and audit['complete']
        for b in audit['sources']:bind(b)
        schedule_stage=ROOT/'real_context_and_author_code_followup_2026_10_08'
        oldpath=schedule_stage/'full_schedule_attempt01/receipt.json';old=read(oldpath);jp=ROOT/old['journal_path']
        assert old['complete'] and sha(jp)==old['journal_sha256']
        with gzip.open(jp,'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
        indexed={(v['step'],v['patch']):v for v in rows};assert len(indexed)==len(rows)==5984
        cases=development_cases();assert len(cases)==19 and len({c['patient'] for c,row in cases})==11
        configpath=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/frozen_config.json';cfg=read(configpath)
        sp=configpath.parent/cfg['schedule_file'];assert sha(sp)==cfg['schedule_file_sha256'];draws=np.load(sp,allow_pickle=False)[:2992]
        assert cfg['series']==[dict(patient=c['patient'],uid=c['uid']) for c,row in cases]
        selection=[]
        for ci,(c,row) in enumerate(cases):
            exposures=[int(s)+1 for s in np.flatnonzero(draws[:,1]==ci)]
            first=next(s for s in exposures if all(indexed[(s,p)]['primitive']['enabled'] for p in range(2)))
            second=next(s for s in exposures if s>first)
            for s in [first,second]:
                assert all(indexed[(s,p)]['uid']==c['uid'] and indexed[(s,p)]['patient']==c['patient'] for p in range(2))
            selection.append(dict(case=ci,patient=c['patient'],uid=c['uid'],scheduled_steps=[first,second],
                original_fields=[[indexed[(s,p)] for p in range(2)] for s in [first,second]]))
        tp=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json';train=read(tp)
        assert train['training_observed_tool_exit']==0 and train['formal_training_updates']==39996
        cpentries={a['kind']:a for a in train['arms']};assert set(cpentries)==set(KINDS)
        medicalcfg=ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01/frozen_config.json';medical=read(medicalcfg)
        sources={Path(__file__),HERE/'PROTOCOL.md',prev/'ACTUAL_OPTIMIZER_TERMINAL_TOOL.json',prev/'optimizer_audit_attempt01/receipt.json',
            prev/'optimizer_smoke_attempt01/receipt.json',oldpath,jp,tp,QPATH,configpath,sp,medicalcfg}
        for c,row in cases:
            for rel in [c['label_file'],c['header_file'],c['mr_zip_file'],row['observed_package']]:sources.add(bind(next(b for b in medical['source_bindings'] if b['path']==rel)))
        for a in cpentries.values():
            p=ROOT/a['checkpoint_path'];assert sha(p)==a['checkpoint_sha256'];sources.add(p)
        for mod in list(sys.modules.values()):
            value=getattr(mod,'__file__',None)
            if value:
                p=Path(value).resolve()
                if p.is_relative_to(ROOT) and p.suffix=='.py':sources.add(p)
        frozen=dict(kinds=KINDS,modes=MODES,cases=selection,expected_branches=114,expected_updates=228,total_patch_fields=456,
            selection_uses_only_original_schedule_and_primitive=True,GT_or_prediction_based_selection=False,
            wall_seconds=WALL,stage_limit_bytes=LIMIT,journal_limit_bytes=JOURNAL_LIMIT,other_allowances_bytes=OTHER,
            CPU_threads=1,GPU_minimum_free_MiB=8192,GPU_allocator_fraction=.1,GPU_max_reserved_bytes=2_500_000_000,
            GPU_runtime_minimum_free_bytes=4_000_000_000,absolute_optimizer_gate=3e-6,FP32=True,TF32=False,
            source_bindings=[entry(p) for p in sorted(sources)])
        dump(out/'frozen_config.json',frozen);r.update(source_bindings=frozen['source_bindings'],frozen_config_sha256=sha(out/'frozen_config.json'));save()
        query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
        gpu=[dict(zip(['index','total_MiB','free_MiB','utilization_percent'],map(int,line.split(',')))) for line in query.stdout.strip().splitlines()]
        assert len(gpu)==1 and gpu[0]['index']==0 and gpu[0]['free_MiB']>=8192;r['GPU_aggregate']=gpu
        os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()
        torch.cuda.set_per_process_memory_fraction(.1,0);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.cuda.synchronize();guard(True)
        parents={}
        for kind,a in cpentries.items():
            cp=torch.load(ROOT/a['checkpoint_path'],map_location='cpu',weights_only=True)
            assert cp['updates_completed']==19998 and state_hash(cp['state_dict'])==cp['final_weights_sha256']
            parents[kind]=cp;r['parent_model_arrays_loaded']+=1
        refs={a['kind']:{s['uid']:s for s in a['cache_records']} for a in read(QPATH)['arms']}
        r['status']='running';save()
        with journal.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',compresslevel=6,mtime=0) as stream:
            for selected,(c,row) in zip(selection,cases):
                guard(True);tick=time.perf_counter();grid=lattice(c);target=physical_label(read_reference_label(c),grid)
                GT_seconds=time.perf_counter()-tick;th=array_sha(target);r['GT_arrays_loaded']+=1
                assert th==refs[KINDS[0]][c['uid']]['label_sha256']==refs[KINDS[1]][c['uid']]['label_sha256']
                for kind in KINDS:
                    tick=time.perf_counter();image,stats=source_image(c,row,kind);cache=physical_mr(image,grid);del image
                    cache_seconds=time.perf_counter()-tick;ih=array_sha(cache);r['MRI_input_arrays_loaded']+=1
                    assert ih==refs[kind][c['uid']]['input_sha256']
                    r['cache_records'].append(dict(case=selected['case'],kind=kind,input_sha256=ih,label_sha256=th,GT_load_resample_seconds=GT_seconds,MRI_load_resample_seconds=cache_seconds,cache_bytes=cache.nbytes))
                    for mode in MODES:
                        guard(True);branch_start=time.perf_counter();tick=time.perf_counter();cp=parents[kind]
                        model=CheckpointedTaskUNet3D();model.load_state_dict(cp['state_dict']);before=state_hash(model.state_dict());assert before==cp['final_weights_sha256']
                        model.to('cuda:0');model.train();opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4,foreach=False,fused=False)
                        independent={n:[p.detach().cpu().numpy().astype(np.float64).copy(),np.zeros(p.shape,np.float64),np.zeros(p.shape,np.float64)] for n,p in model.named_parameters()}
                        torch.cuda.synchronize();model_seconds=time.perf_counter()-tick;step_records=[]
                        for optimizer_step,step in enumerate(selected['scheduled_steps'],1):
                            guard(True);tick=time.perf_counter();x,y,geometry=sample_batch(cache,target,batch_rng(19998+step));costs=dict(sampling=time.perf_counter()-tick)
                            labels=y.numpy();mother=array_sha(labels);fields=selected['original_fields'][optimizer_step-1]
                            assert all(fields[p]['geometry']==geometry[p] and fields[p]['mother_label_sha256']==mother and fields[p]['target_label_sha256']==array_sha(labels[p,0]) for p in range(2))
                            prepared=[];numerics=[];costs['resolution_candidate']=costs['resolution_independent']=0.
                            for p in range(2):
                                tick=time.perf_counter();xx,support,meta=candidate(cache,grid,geometry[p],fields[p]['primitive'],mode,PATCH);costs['resolution_candidate']+=time.perf_counter()-tick
                                tick=time.perf_counter();other,other_support,ometa=reference(cache,grid,geometry[p],fields[p]['primitive'],mode,PATCH);costs['resolution_independent']+=time.perf_counter()-tick
                                domain=independent_domain(grid,geometry[p],PATCH)
                                assert np.array_equal(xx.view(np.uint32),other.view(np.uint32)) and np.array_equal(support>=1-1e-9,domain) and np.array_equal(other_support>=1-1e-9,domain)
                                assert np.array_equal(xx[~domain].view(np.uint32),x.numpy()[p,0][~domain].view(np.uint32))
                                numerics.append(dict(patch=p,valid_voxels=int(domain.sum()),changed_voxels=int(np.count_nonzero(xx!=x.numpy()[p,0])),
                                    bitwise_disagreements=0,padding_disagreements=0,candidate_fallback_voxels=meta['exact_fallback_voxels'],reference_fallback_voxels=ometa['direct_exact_fallback_voxels']))
                                prepared.append(xx);del other,other_support,support
                            tick=time.perf_counter();xx=intensity.apply(np.stack(prepared)[:,None],intensity.primitives(step));assert array_sha(labels)==mother
                            xh=array_sha(xx);costs['intensity_and_hash']=time.perf_counter()-tick
                            opt.zero_grad(set_to_none=True);tick=time.perf_counter();gx=torch.from_numpy(xx).to('cuda:0');gy=y.to('cuda:0');torch.cuda.synchronize();costs['transfer_sync']=time.perf_counter()-tick
                            tick=time.perf_counter();outputs=model(gx);torch.cuda.synchronize();costs['forward_sync']=time.perf_counter()-tick;r['GPU_forwards']+=1
                            tick=time.perf_counter();value=loss(outputs,gy);torch.cuda.synchronize();costs['loss_sync']=time.perf_counter()-tick
                            tick=time.perf_counter();value.backward();torch.cuda.synchronize();costs['backward_sync']=time.perf_counter()-tick;r['GPU_backwards']+=1
                            assert torch.isfinite(value) and all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
                            tick=time.perf_counter();grads={n:p.grad.detach().cpu().numpy().astype(np.float64) for n,p in model.named_parameters()}
                            module_grads={n:max(float(p.grad.abs().max()) for p in module.parameters()) for n,module in [('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads)]}
                            assert all(v>0 for v in module_grads.values());costs['gradient_capture']=time.perf_counter()-tick
                            tick=time.perf_counter();opt.step();torch.cuda.synchronize();costs['AdamW_sync']=time.perf_counter()-tick;r['training_updates']+=1
                            tick=time.perf_counter();checks=[]
                            for n,p in model.named_parameters():
                                expected,m,v=independent[n];g=grads[n];m*=.9;m+=.1*g;v*=.999;v+=.001*g*g
                                expected*=1.-1e-4*1e-4;expected-=1e-4*(m/(1.-.9**optimizer_step))/(np.sqrt(v/(1.-.999**optimizer_step))+1e-8)
                                actual=p.detach().cpu().numpy();state=opt.state[p];assert int(state['step'].item())==optimizer_step
                                am=state['exp_avg'].detach().cpu().numpy();av=state['exp_avg_sq'].detach().cpu().numpy()
                                assert np.isfinite(actual).all() and np.isfinite(am).all() and np.isfinite(av).all()
                                ew=float(np.max(np.abs(actual-expected)));em=float(np.max(np.abs(am-m)));ev=float(np.max(np.abs(av-v)))
                                assert max(ew,em,ev)<=3e-6
                                checks.append(dict(name=n,elements=p.numel(),step=optimizer_step,weight_error=ew,m_error=em,v_error=ev))
                            costs['independent_optimizer_check']=time.perf_counter()-tick;after=state_hash(model.state_dict());assert after!=before
                            tick=time.perf_counter();capture=dict(model=model.state_dict(),optimizer=opt.state_dict());buf=io.BytesIO();torch.save(capture,buf);capture_bytes=buf.tell();buf.seek(0)
                            restored=torch.load(buf,map_location='cpu',weights_only=True);assert equal_tree(capture,restored)
                            assert state_hash(restored['model'])==after;r['in_memory_captures']+=1;oh=optimizer_hash(opt,model);costs['memory_capture_reload_and_optimizer_hash']=time.perf_counter()-tick
                            res=guard(True)
                            record=dict(case=selected['case'],patient=c['patient'],uid=c['uid'],kind=kind,mode=mode,optimizer_step=optimizer_step,scheduled_step=step,
                                input_sha256=xh,mother_label_sha256=mother,cache_sha256=ih,starting_parent_weights_sha256=before,
                                ending_weights_sha256=after,optimizer_state_sha256=oh,model_and_optimizer_memory_reload_bitwise_equal=True,
                                loss=float(value.detach()),module_gradient_max=module_grads,parameter_checks=checks,numerics=numerics,cost_seconds=costs,
                                capture_bytes=capture_bytes,peak_reserved_bytes=res['GPU_peak_reserved_bytes'])
                            tick=time.perf_counter();stream.write((json.dumps(record,separators=(',',':'))+'\n').encode('utf-8'));stream.flush(zlib.Z_SYNC_FLUSH);write_seconds=time.perf_counter()-tick
                            step_records.append(dict(optimizer_step=optimizer_step,scheduled_step=step,ending_weights_sha256=after,optimizer_state_sha256=oh,
                                maximum_weight_error=max(v['weight_error'] for v in checks),maximum_m_error=max(v['m_error'] for v in checks),maximum_v_error=max(v['v_error'] for v in checks),
                                mother_label_sha256=mother,input_sha256=xh,cost_seconds=costs,journal_write_seconds=write_seconds,peak_reserved_bytes=res['GPU_peak_reserved_bytes']))
                            del gx,gy,outputs,value,prepared,xx,x,y,labels,grads,buf,capture,restored,actual,am,av,state,expected,m,v,g,checks
                        b=dict(case=selected['case'],patient=c['patient'],uid=c['uid'],kind=kind,mode=mode,complete=True,optimizer_reset=True,
                            starting_weights_sha256=before,steps=step_records,model_load_transfer_seconds=model_seconds,elapsed_seconds=time.perf_counter()-branch_start)
                        r['branches'].append(b);raw.flush();save();print(json.dumps(dict(branches_completed=len(r['branches']),expected_branches=114,updates_completed=r['training_updates'],
                            patient=c['patient'],kind=kind,mode=mode,peak_reserved_bytes=b['steps'][-1]['peak_reserved_bytes'],elapsed_seconds=time.perf_counter()-started)),flush=True)
                        del model,opt,independent,step_records;gc.collect();torch.cuda.empty_cache();guard(True)
                    assert array_sha(cache)==ih;del cache;gc.collect()
                assert array_sha(target)==th;del target;gc.collect();save()
            raw.flush();os.fsync(raw.fileno())
        assert len(r['branches'])==114 and r['training_updates']==r['GPU_forwards']==r['GPU_backwards']==r['in_memory_captures']==228
        assert r['MRI_input_arrays_loaded']==38 and r['GT_arrays_loaded']==19 and r['parent_model_arrays_loaded']==2
        for b in frozen['source_bindings']:bind(b)
        r.update(complete=True,status='completed',all19_series_and11_patients_optimizer_coverage_verified=True,
            all114_reset_branches_two_steps_verified=True,all456_numeric_patch_fields_bitwise_matched=True,
            journal=entry(journal),resources_after=guard(True))
    except Exception as e:r.update(status='failed',traceback=traceback.format_exc());r['errors'].append(type(e).__name__+': '+str(e))
    r.update(elapsed_seconds=time.perf_counter()-started,CUDA_initialized=torch.cuda.is_initialized());save()
    print(json.dumps({k:r.get(k) for k in ['complete','status','errors','training_updates','GPU_forwards','GPU_backwards','in_memory_captures','elapsed_seconds']}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
