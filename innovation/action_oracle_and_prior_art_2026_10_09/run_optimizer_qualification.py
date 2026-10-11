"""Bounded development-only six first AdamW updates with independent float64 formula and memory capture."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import torch
original_cuda_initializer=torch.cuda._lazy_init
import sys,json,time,gzip,gc,traceback,subprocess,io
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import (
    development_cases,lattice,source_image,physical_mr,physical_label,read_reference_label,
    sample_batch,batch_rng,TaskUNet3D,loss,state_hash,array_sha,QPATH)
sys.path.insert(0,str(ROOT/'resolution_degradation_controls_2026_10_08'))
from qualify_synthetic_and_schedule_v2 import independent_domain
sys.path.insert(0,str(ROOT/'intensity_precision_failure_diagnosis_2026_10_09'))
import intensity_float64_stats as intensity
sys.path.insert(0,str(ROOT/'certified_resolution_rounding_2026_10_09'))
import certified_resolution as candidate
sys.path.insert(0,str(ROOT/'direct_oracle_efficiency_2026_10_09'))
import direct_separable_reference as reference
sys.path.insert(0,str(ROOT/'gpu_graph_cost_smoke_2026_10_09'))
from checkpointed_model import CheckpointedTaskUNet3D
PATCH=(64,128,128);KINDS=['native_reference','raw_pchip'];MODES=['throughplane','inplane','allaxes']
WALL=1800;LIMIT=2_000_000;OTHER_ALLOWANCES=16_800_000

def now():return datetime.now(timezone.utc).isoformat()
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1)
    started=time.perf_counter();out=HERE/'optimizer_smoke_attempt01';out.mkdir(exist_ok=False)
    dest=out/'receipt.json';r=dict(complete=False,status='preparing',errors=[],branches=[],
        activation_checkpointing=True,backward_includes_recomputation=True,training_updates=0,GPU_forwards=0,GPU_backwards=0,MRI_input_arrays_loaded=0,model_arrays_loaded=0,optimizer_created=False,weights_saved=False,full_fov_inference=False,in_memory_captures=0,
        independent_probability_qualification=False,medical_effect_scored=False,
        validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        other_PIDs_enumerated=False,other_PIDs_modified=False,original_training_modified=False,
        strict_LOPO_warm_start_allowed=False,training_ready=False,publication_claim_confirmed=False,goal_status='active')
    def save():
        tmp=dest.with_name(dest.name+'.tmp');tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(dest)
    def guard(cuda=False):
        v=resource_guard();assert torch.get_num_threads()==torch.get_num_interop_threads()==1
        assert time.perf_counter()-started<WALL
        size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());assert size<LIMIT
        assert v['workspace_free_bytes']-OTHER_ALLOWANCES-(LIMIT-size)>=8_000_000_000
        if cuda:
            free,total=torch.cuda.mem_get_info(0);peak=torch.cuda.max_memory_reserved(0)
            assert free>=4_000_000_000 and peak<=2_500_000_000
            v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
        return v
    save()
    try:
        r['resources_before']=guard();assert not torch.cuda.is_initialized()
        numerical=ROOT/'direct_oracle_efficiency_2026_10_09'
        term=read(numerical/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json')
        audit=read(numerical/'all_patient_terminal_audit_attempt01/receipt.json')
        assert term['exit_code']==0 and 'session_id' not in term and audit['complete']
        schedule_stage=ROOT/'real_context_and_author_code_followup_2026_10_08'
        rp=schedule_stage/'full_schedule_attempt01/receipt.json';old=read(rp);jp=ROOT/old['journal_path']
        assert old['complete'] and sha(jp)==old['journal_sha256']
        with gzip.open(jp,'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
        indexed={(x['step'],x['patch']):x for x in rows};assert len(indexed)==5984
        step=next(s for s in range(1,2993) if all(indexed[(s,p)]['primitive']['enabled'] for p in range(2)))
        fields=[indexed[(step,p)] for p in range(2)]
        cases=development_cases();c,row=next((c,row) for c,row in cases if c['uid']==fields[0]['uid'])
        assert all(x['uid']==c['uid'] and x['patient']==c['patient'] for x in fields)
        tp=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json';train=read(tp)
        assert train['training_observed_tool_exit']==0 and train['formal_training_updates']==39996
        cpentries={a['kind']:a for a in train['arms']};assert set(cpentries)==set(KINDS)
        configpath=ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01/frozen_config.json'
        config=read(configpath)
        sources={Path(__file__),HERE/'OPTIMIZER_QUALIFICATION_PROTOCOL.md',HERE/'build_optimizer_qualification.py',ROOT/'gpu_graph_cost_smoke_2026_10_09/ACTUAL_GPU_SMOKE_V3_TERMINAL_TOOL.json',ROOT/'gpu_graph_cost_smoke_2026_10_09/terminal_audit_attempt01/receipt.json',ROOT/'gpu_graph_cost_smoke_2026_10_09/checkpointed_cpu_qualification_attempt01/receipt.json',rp,jp,tp,QPATH,configpath,
            numerical/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json',numerical/'all_patient_terminal_audit_attempt01/receipt.json',
            Path(candidate.__file__),Path(reference.__file__),Path(intensity.__file__),Path(intensity.legacy.__file__)}
        for rel in [c['label_file'],c['header_file'],c['mr_zip_file'],row['observed_package']]:
            sources.add(bind(next(b for b in config['source_bindings'] if b['path']==rel)))
        for a in cpentries.values():
            cpfile=ROOT/a['checkpoint_path'];assert sha(cpfile)==a['checkpoint_sha256'];sources.add(cpfile)
        # Bind every imported local module, including the original sampler/network and independent oracle.
        for mod in list(sys.modules.values()):
            value=getattr(mod,'__file__',None)
            if value:
                p=Path(value).resolve()
                if p.is_relative_to(ROOT) and p.suffix=='.py':sources.add(p)
        frozen=dict(step=step,case=dict(patient=c['patient'],uid=c['uid']),fields=fields,kinds=KINDS,modes=MODES,
            total_patch_fields=12,wall_seconds=WALL,stage_limit_bytes=LIMIT,other_allowances_bytes=OTHER_ALLOWANCES,
            GPU_minimum_free_MiB=8192,GPU_allocator_fraction=.1,GPU_max_reserved_bytes=2_500_000_000,
            GPU_runtime_minimum_free_bytes=4_000_000_000,FP32=True,TF32=False,
            source_bindings=[entry(p) for p in sorted(sources)])
        dump(out/'frozen_config.json',frozen);r['frozen_config_sha256']=sha(out/'frozen_config.json')
        r.update(selected_patient=c['patient'],selected_uid=c['uid'],selected_step=step,source_bindings=frozen['source_bindings']);save()
        query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
        gpu=[dict(zip(['index','total_MiB','free_MiB','utilization_percent'],map(int,line.split(',')))) for line in query.stdout.strip().splitlines()]
        r['aggregate_GPU_observation']=gpu;assert len(gpu)==1 and gpu[0]['index']==0 and gpu[0]['free_MiB']>=8192
        r['CUDA_VISIBLE_DEVICES_after_CPU_imports']=os.environ.get('CUDA_VISIBLE_DEVICES')
        os.environ['CUDA_VISIBLE_DEVICES']='0'
        r['CUDA_VISIBLE_DEVICES_at_GPU_admission']=os.environ['CUDA_VISIBLE_DEVICES']
        r['torch_version']=str(torch.__version__);r['torch_CUDA_version']=torch.version.cuda
        torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()
        torch.cuda.set_per_process_memory_fraction(.1,0)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
        torch.cuda.synchronize();r['device']='cuda:0';r['GPU_name']=torch.cuda.get_device_name(0);guard(True)
        q=read(QPATH);refs={a['kind']:{s['uid']:s for s in a['cache_records']} for a in q['arms']}
        tick=time.perf_counter();grid=lattice(c);target=physical_label(read_reference_label(c),grid)
        r['GT_load_resample_seconds']=time.perf_counter()-tick;th=array_sha(target);r['GT_arrays_loaded']=1
        assert th==refs[KINDS[0]][c['uid']]['label_sha256']==refs[KINDS[1]][c['uid']]['label_sha256']
        mother_hash=None;geometry_reference=None;r['status']='running';save()
        for kind in KINDS:
            guard(True);tick=time.perf_counter();normalized,stats=source_image(c,row,kind);cache=physical_mr(normalized,grid);del normalized
            cache_seconds=time.perf_counter()-tick;r['MRI_input_arrays_loaded']+=1;ih=array_sha(cache);assert ih==refs[kind][c['uid']]['input_sha256']
            tick=time.perf_counter();x,y,geometry=sample_batch(cache,target,batch_rng(19998+step));sampling_seconds=time.perf_counter()-tick
            labels=y.numpy();labelhash=array_sha(labels)
            assert all(fields[p]['geometry']==geometry[p] and fields[p]['mother_label_sha256']==labelhash and fields[p]['target_label_sha256']==array_sha(labels[p,0]) for p in range(2))
            if mother_hash is None:mother_hash=labelhash;geometry_reference=geometry
            else:assert labelhash==mother_hash and geometry==geometry_reference
            tick=time.perf_counter();a=cpentries[kind];cp=torch.load(ROOT/a['checkpoint_path'],map_location='cpu',weights_only=True)
            r['model_arrays_loaded']+=1;assert cp['updates_completed']==19998 and state_hash(cp['state_dict'])==cp['final_weights_sha256']
            model=CheckpointedTaskUNet3D();model.load_state_dict(cp['state_dict']);before=state_hash(model.state_dict())
            assert before==cp['final_weights_sha256'];model.to('cuda:0');model.train();torch.cuda.synchronize()
            checkpoint_seconds=time.perf_counter()-tick;initial_state=cp['state_dict'];del cp
            for mode in MODES:
                guard(True);branch_start=time.perf_counter();prepared=[];numerics=[];cost={}
                model.load_state_dict(initial_state);assert state_hash(model.state_dict())==before
                opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4,foreach=False,fused=False)
                r['optimizer_created']=True
                tick=time.perf_counter()
                for p in range(2):
                    prim=fields[p]['primitive'];image,support,meta=candidate.apply(cache,grid,geometry[p],prim,mode,PATCH)
                    independent,isupport,imeta=reference.apply_reference(cache,grid,geometry[p],prim,mode,PATCH)
                    domain=independent_domain(grid,geometry[p],PATCH)
                    assert np.array_equal(image.view(np.uint32),independent.view(np.uint32))
                    assert np.array_equal(support>=1-1e-9,domain) and np.array_equal(isupport>=1-1e-9,domain)
                    padding=int(np.count_nonzero(image[~domain].view(np.uint32)!=x.numpy()[p,0][~domain].view(np.uint32)));assert padding==0
                    prepared.append(image);numerics.append(dict(patch=p,valid_voxels=int(domain.sum()),bitwise_disagreements=0,padding_disagreements=padding,
                        candidate_exact_fallback_voxels=meta['exact_fallback_voxels'],reference_exact_fallback_voxels=imeta['direct_exact_fallback_voxels']))
                cost['resolution_candidate_and_independent_seconds']=time.perf_counter()-tick
                tick=time.perf_counter();xx=intensity.apply(np.stack(prepared)[:,None],intensity.primitives(step))
                assert array_sha(labels)==mother_hash and np.isfinite(xx).all();cost['intensity_and_label_check_seconds']=time.perf_counter()-tick
                inputhash=array_sha(xx);model.zero_grad(set_to_none=True);torch.cuda.reset_peak_memory_stats(0)
                tick=time.perf_counter();gx=torch.from_numpy(xx).to('cuda:0');gy=y.to('cuda:0');torch.cuda.synchronize()
                cost['transfer_sync_seconds']=time.perf_counter()-tick
                tick=time.perf_counter();outputs=model(gx);torch.cuda.synchronize();cost['forward_sync_seconds']=time.perf_counter()-tick;r['GPU_forwards']+=1
                tick=time.perf_counter();value=loss(outputs,gy);torch.cuda.synchronize();cost['loss_sync_seconds']=time.perf_counter()-tick
                tick=time.perf_counter();value.backward();torch.cuda.synchronize();cost['backward_sync_seconds']=time.perf_counter()-tick;r['GPU_backwards']+=1
                tick=time.perf_counter();assert torch.isfinite(value) and all(torch.isfinite(t).all() for t in outputs)
                assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
                gradients={n:max(float(p.grad.abs().max()) for p in module.parameters()) for n,module in [('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads)]}
                assert all(v>0 for v in gradients.values())
                original_parameters={n:p.detach().cpu().numpy().copy() for n,p in model.named_parameters()}
                original_gradients={n:p.grad.detach().cpu().numpy().copy() for n,p in model.named_parameters()}
                cost['finite_gradient_and_state_verification_seconds']=time.perf_counter()-tick
                tick=time.perf_counter();opt.step();torch.cuda.synchronize()
                cost['optimizer_update_sync_seconds']=time.perf_counter()-tick;r['training_updates']+=1
                tick=time.perf_counter();max_weight=max_m=max_v=0.;parameter_records=[]
                for n,p in model.named_parameters():
                    old=original_parameters[n].astype(np.float64);g=original_gradients[n].astype(np.float64)
                    expected=old*(1.-1e-4*1e-4)-1e-4*g/(np.abs(g)+1e-8)
                    actual=p.detach().cpu().numpy();state=opt.state[p]
                    assert int(state['step'].item())==1 and np.isfinite(actual).all()
                    m=state['exp_avg'].detach().cpu().numpy();v=state['exp_avg_sq'].detach().cpu().numpy()
                    assert np.isfinite(m).all() and np.isfinite(v).all()
                    ew=float(np.max(np.abs(actual.astype(np.float64)-expected)))
                    em=float(np.max(np.abs(m.astype(np.float64)-.1*g)))
                    ev=float(np.max(np.abs(v.astype(np.float64)-.001*g*g)))
                    assert max(ew,em,ev)<=3e-6
                    max_weight=max(max_weight,ew);max_m=max(max_m,em);max_v=max(max_v,ev)
                    parameter_records.append(dict(name=n,elements=p.numel(),step=1,weight_error=ew,first_moment_error=em,second_moment_error=ev))
                after=state_hash(model.state_dict());assert before!=after
                cost['independent_first_update_verification_seconds']=time.perf_counter()-tick
                tick=time.perf_counter();capture={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
                stream=io.BytesIO();torch.save(dict(state_dict=capture),stream);capture_bytes=stream.tell();stream.seek(0)
                captured=torch.load(stream,map_location='cpu',weights_only=True)
                assert state_hash(captured['state_dict'])==after
                r['in_memory_captures']+=1
                capture_seconds=time.perf_counter()-tick
                cost['in_memory_capture_and_reload_seconds']=capture_seconds
                optimizer_check=dict(parameters=parameter_records,parameter_tensors=len(parameter_records),
                    maximum_weight_error=max_weight,maximum_first_moment_error=max_m,maximum_second_moment_error=max_v,
                    capture_bytes=capture_bytes,capture_state_hash=after,all_first_step_counters_one=True,
                    independent_formula='float64 p*(1-lr*wd)-lr*g/(abs(g)+eps)',absolute_gate=3e-6)
                del capture,captured,stream,old,g,actual,m,v,state,expected
                torch.cuda.synchronize()
                res=guard(True);b=dict(kind=kind,mode=mode,complete=True,input_sha256=inputhash,mother_label_sha256=mother_hash,
                    cache_sha256=ih,cache_load_seconds=cache_seconds,sampling_seconds=sampling_seconds,checkpoint_load_and_transfer_seconds=checkpoint_seconds,
                    outputs_shapes=[list(t.shape) for t in outputs],loss=float(value.detach()),module_gradient_max=gradients,
                    starting_weights_sha256=before,ending_weights_sha256=after,model_state_unchanged=False,optimizer_reset=True,optimizer_check=optimizer_check,numerics=numerics,cost_seconds=cost,
                    branch_elapsed_seconds=time.perf_counter()-branch_start,peak_reserved_bytes=res['GPU_peak_reserved_bytes'],peak_allocated_bytes=torch.cuda.max_memory_allocated(0))
                r['branches'].append(b);save();print(json.dumps(dict(kind=kind,mode=mode,loss=b['loss'],finite_nonzero_gradients=True,actual_AdamW_updates=1,maximum_weight_error=max_weight,
                    branch_elapsed_seconds=b['branch_elapsed_seconds'],peak_reserved_bytes=b['peak_reserved_bytes'])),flush=True)
                del gx,gy,outputs,value,prepared,xx,image,independent,support,isupport
                model.zero_grad(set_to_none=True);del opt,original_parameters,original_gradients;gc.collect();torch.cuda.empty_cache();guard(True)
            del model,cache,x,y,labels,initial_state;gc.collect();torch.cuda.empty_cache();guard(True)
        assert len(r['branches'])==6
        for b in frozen['source_bindings']:bind(b)
        r.update(complete=True,status='completed',all_six_GPU_branches_finite_nonzero_gradients=True,all_parent_source_files_unchanged=True,all_six_first_AdamW_updates_verified=True,all_six_memory_captures_verified=True,
            all12_numeric_patch_fields_bitwise_matched=True,all_mother_GT_geometry_paired=True,MRI_input_arrays_loaded=2,model_arrays_loaded=2,
            GPU_forwards=6,GPU_backwards=6,training_updates=6,in_memory_captures=6,resources_after=guard(True))
    except Exception as e:
        r.update(status='failed',traceback=traceback.format_exc());r['errors'].append(type(e).__name__+': '+str(e))
    r.update(CUDA_initialized=torch.cuda.is_initialized(),finished_utc=now(),elapsed_seconds=time.perf_counter()-started)
    save();print(json.dumps({k:r.get(k) for k in ['complete','status','errors','GPU_forwards','GPU_backwards','training_updates','in_memory_captures','elapsed_seconds']}),flush=True)
    return int(not r['complete'] or bool(r['errors']))
if __name__=='__main__':raise SystemExit(main())
