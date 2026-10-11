"""Prospective full38 development FOVs, GPU production vs independent CPU functional, atomic weights."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import torch
original_cuda_initializer=torch.cuda._lazy_init
import gc,json,sys,time,traceback,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,state_hash,array_sha,QPATH,np
sys.path.insert(0,str(ROOT/'gpu_graph_cost_smoke_2026_10_09'))
from checkpointed_model import CheckpointedTaskUNet3D
sys.path.insert(0,str(ROOT/'lossless_final_evaluation_entry_2026_10_08'))
from final_eval_lossless_v3 import GuardedModel
from verify_final_lossless_v3 import functional_fov
from production_probability_mapping_v4 import infer_full_fov_v4
LIMIT=20_000_000;OTHER=22_800_000;WALL=10800;KINDS=['native_reference','raw_pchip']

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    started=time.perf_counter();stage=ROOT/'development_optimizer_coverage_2026_10_09'
    terminal=read(stage/'ACTUAL_COVERAGE_TERMINAL_TOOL.json');assert terminal['exit_code']==0 and 'session_id' not in terminal
    coverage=read(stage/'terminal_audit_attempt01/receipt.json');assert coverage['complete'] and not coverage['errors'] and coverage['all19_series11_patients_and114_branch_denominators_verified']
    for b in coverage['source_bindings']:bind(b)
    out=HERE/'full_fov_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,status='preparing',errors=[],series=[],atomic_captures=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_model_arrays_loaded=0,
        training_updates=0,medical_effect_scored=False,validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        other_PIDs_enumerated=False,other_PIDs_modified=False,original_training_modified=False,publication_claim_confirmed=False,training_ready=False,goal_status='active')
    def save():
        tmp=out/'receipt.json.tmp';tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(out/'receipt.json')
    def guard(cuda=True):
        v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        assert size<LIMIT and v['workspace_free_bytes']-OTHER-(LIMIT-size)>=8_000_000_000
        assert time.perf_counter()-started<WALL and torch.get_num_threads()==torch.get_num_interop_threads()==1
        if cuda:
            free,total=torch.cuda.mem_get_info(0);peak=torch.cuda.max_memory_reserved(0);assert free>=4_000_000_000 and peak<=2_500_000_000
            v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
        return v
    save()
    try:
        r['resources_before']=guard(False);assert not torch.cuda.is_initialized()
        cases=development_cases();assert len(cases)==19 and len({c['patient'] for c,row in cases})==11
        tp=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json';train=read(tp);assert train['training_observed_tool_exit']==0
        parent={a['kind']:a for a in train['arms']};assert set(parent)==set(KINDS)
        refs={a['kind']:{s['uid']:s for s in a['cache_records']} for a in read(QPATH)['arms']}
        metadata=read(stage/'coverage_attempt01/frozen_config.json')
        sources={Path(__file__),HERE/'PROTOCOL.md',stage/'ACTUAL_COVERAGE_TERMINAL_TOOL.json',stage/'terminal_audit_attempt01/receipt.json',tp,QPATH}
        for b in metadata['source_bindings']:sources.add(bind(b))
        for mod in list(sys.modules.values()):
            value=getattr(mod,'__file__',None)
            if value:
                p=Path(value).resolve()
                if p.is_relative_to(ROOT) and p.suffix=='.py':sources.add(p)
        frozen=dict(expected_FOVs=38,kinds=KINDS,cases=[dict(patient=c['patient'],uid=c['uid']) for c,row in cases],
            max_probability_gate=3e-6,coordinate_gate=3e-12,binary_gate=0,threshold=.5,stage_limit_bytes=LIMIT,other_allowances_bytes=OTHER,
            wall_seconds=WALL,source_bindings=[entry(p) for p in sorted(sources)])
        dump(out/'frozen_config.json',frozen);r['source_bindings']=frozen['source_bindings'];save()
        q=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
        gpu=[list(map(int,line.split(','))) for line in q.stdout.strip().splitlines()];assert len(gpu)==1 and gpu[0][0]==0 and gpu[0][1]>=8192;r['GPU_aggregate']=gpu
        os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()
        torch.cuda.set_per_process_memory_fraction(.1,0);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.cuda.synchronize();guard()
        for kind in KINDS:
            a=parent[kind];p=ROOT/a['checkpoint_path'];assert sha(p)==a['checkpoint_sha256'];tick=time.perf_counter()
            cp=torch.load(p,map_location='cpu',weights_only=True);r['parent_model_arrays_loaded']+=1
            assert cp['updates_completed']==19998 and state_hash(cp['state_dict'])==cp['final_weights_sha256']
            model=CheckpointedTaskUNet3D();model.load_state_dict(cp['state_dict']);model.to('cuda:0');model.eval();torch.cuda.synchronize();model_seconds=time.perf_counter()-tick
            wrapped=GuardedModel(model,guard)
            tick=time.perf_counter();captured={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};assert state_hash(captured)==cp['final_weights_sha256']
            path=out/(kind+'_parent_atomic.pt');tmp=path.with_name(path.name+'.tmp');assert not path.exists() and not tmp.exists();guard()
            with tmp.open('xb') as f:torch.save(dict(state_dict=captured,kind=kind,parent_updates=19998),f);f.flush();os.fsync(f.fileno())
            tmp.replace(path);restored=torch.load(path,map_location='cpu',weights_only=True);assert state_hash(restored['state_dict'])==cp['final_weights_sha256'];guard()
            r['atomic_captures'].append(dict(kind=kind,file=entry(path),state_sha256=cp['final_weights_sha256'],reload_bitwise_equal=True,
                atomic_operation_seconds=time.perf_counter()-tick,power_failure_recovery_guaranteed=False,optimizer_resume_supported=False));save();del captured,restored
            for ci,(c,row) in enumerate(cases):
                guard();tick=time.perf_counter();image,stats=source_image(c,row,kind);grid=lattice(c);cache=physical_mr(image,grid);del image
                load_seconds=time.perf_counter()-tick;ih=array_sha(cache);assert ih==refs[kind][c['uid']]['input_sha256'];r['MRI_arrays_loaded']+=1
                tick=time.perf_counter();prob,meta=infer_full_fov_v4(wrapped,cache,grid,c['native_shape'],device='cuda:0');torch.cuda.synchronize();gpu_seconds=time.perf_counter()-tick
                tick=time.perf_counter();replay,imeta=functional_fov(cp['state_dict'],cache,grid,c['native_shape'],guard);cpu_seconds=time.perf_counter()-tick
                tick=time.perf_counter();error=float(np.max(np.abs(prob-replay)));binary=int(np.count_nonzero((prob>=.5)!=(replay>=.5)))
                assert meta['total_tiles']==imeta['total_tiles'] and meta['axis_starts']==imeta['axis_starts']
                numeric=error<=3e-6 and binary==0 and imeta['float64_coordinate_gate_passed']
                record=dict(case=ci,patient=c['patient'],uid=c['uid'],kind=kind,complete=True,native_shape=list(prob.shape),native_voxels=prob.size,
                    input_sha256=ih,GPU_probability_sha256=array_sha(prob),CPU_probability_sha256=array_sha(replay),
                    GPU_binary_sha256=array_sha(prob>=.5),CPU_binary_sha256=array_sha(replay>=.5),max_probability_error=error,
                    binary_disagreements=binary,coordinate_max_error=imeta['float64_coordinate_max_probability_error'],
                    coordinate_binary_disagreements=imeta['float64_coordinate_threshold_disagreements'],numeric_gate_passed=numeric,
                    production_inference=meta,independent_inference=imeta,cost_seconds=dict(MRI_load_resample=load_seconds,GPU_full_pipeline=gpu_seconds,
                        CPU_independent_full_pipeline=cpu_seconds,comparison_and_hash=time.perf_counter()-tick),parent_load_transfer_seconds=model_seconds,
                    GPU_peak_reserved_bytes=torch.cuda.max_memory_reserved(0))
                r['series'].append(record);save();print(json.dumps(dict(FOVs_completed=len(r['series']),expected_FOVs=38,kind=kind,max_probability_error=error,
                    binary_disagreements=binary,numeric_gate_passed=numeric,elapsed_seconds=time.perf_counter()-started)),flush=True)
                assert numeric,'Strict full FOV numerical gate failed; prefix retained'
                assert array_sha(cache)==ih;del cache,prob,replay;gc.collect();guard()
            assert state_hash(model.state_dict())==cp['final_weights_sha256'];del wrapped,model,cp;gc.collect();torch.cuda.empty_cache();guard()
        for b in frozen['source_bindings']:bind(b)
        assert len(r['series'])==38 and len(r['atomic_captures'])==2 and r['MRI_arrays_loaded']==38 and r['GT_arrays_loaded']==0
        r.update(complete=True,status='completed',all38_fullFOV_strict_numeric_gates_passed=True,all_two_atomic_weight_captures_passed=True,
            frozen_config_sha256=sha(out/'frozen_config.json'),resources_after=guard())
    except Exception as e:r.update(status='failed',traceback=traceback.format_exc());r['errors'].append(type(e).__name__+': '+str(e))
    r.update(elapsed_seconds=time.perf_counter()-started,CUDA_initialized=torch.cuda.is_initialized());save()
    print(json.dumps({k:r.get(k) for k in ['complete','status','errors','MRI_arrays_loaded','GT_arrays_loaded','elapsed_seconds']}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
