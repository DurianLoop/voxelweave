"""Create a new bounded first-update diagnostic; never mutate the frozen graph source."""
import ast, difflib, hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
original = ROOT / 'gpu_graph_cost_smoke_2026_10_09/run_gpu_graph_smoke_v3.py'
src = original.read_text(encoding='utf-8')
def replace(old, new):
    global src
    assert src.count(old) == 1, old[:100]
    src = src.replace(old, new)

replace('Bounded development-only six-branch GPU gradient/cost diagnostic, zero optimizer updates.',
        'Bounded development-only six first AdamW updates with independent float64 formula and memory capture.')
replace('import sys,json,time,gzip,gc,traceback,subprocess', 'import sys,json,time,gzip,gc,traceback,subprocess,io')
replace('from checkpointed_model import CheckpointedTaskUNet3D',
        "sys.path.insert(0,str(ROOT/'gpu_graph_cost_smoke_2026_10_09'))\nfrom checkpointed_model import CheckpointedTaskUNet3D")
replace('WALL=1800;LIMIT=1_000_000;OTHER_ALLOWANCES=15_800_000',
        'WALL=1800;LIMIT=2_000_000;OTHER_ALLOWANCES=16_800_000')
replace("out=HERE/'attempt03'", "out=HERE/'optimizer_smoke_attempt01'")
replace('optimizer_created=False,weights_saved=False,full_fov_inference=False,',
        'optimizer_created=False,weights_saved=False,full_fov_inference=False,in_memory_captures=0,')
replace("HERE/'PROTOCOL.md',HERE/'V2_RUNTIME_REPAIR.md',HERE/'V2_PREPARATION.json',HERE/'CHECKPOINTED_GRAPH_PROTOCOL.md',HERE/'V3_PREPARATION.json',HERE/'checkpointed_cpu_qualification_attempt01/receipt.json'",
        "HERE/'OPTIMIZER_QUALIFICATION_PROTOCOL.md',HERE/'build_optimizer_qualification.py',ROOT/'gpu_graph_cost_smoke_2026_10_09/ACTUAL_GPU_SMOKE_V3_TERMINAL_TOOL.json',ROOT/'gpu_graph_cost_smoke_2026_10_09/terminal_audit_attempt01/receipt.json',ROOT/'gpu_graph_cost_smoke_2026_10_09/checkpointed_cpu_qualification_attempt01/receipt.json'")
replace("checkpoint_seconds=time.perf_counter()-tick;del cp", "checkpoint_seconds=time.perf_counter()-tick;initial_state=cp['state_dict'];del cp")
replace('guard(True);branch_start=time.perf_counter();prepared=[];numerics=[];cost={}',
        "guard(True);branch_start=time.perf_counter();prepared=[];numerics=[];cost={}\n                model.load_state_dict(initial_state);assert state_hash(model.state_dict())==before\n                opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4,foreach=False,fused=False)\n                r['optimizer_created']=True")
replace("assert all(v>0 for v in gradients.values());after=state_hash(model.state_dict());assert before==after",
"""assert all(v>0 for v in gradients.values())
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
                del capture,captured,stream,old,g,actual,m,v,state,expected""")
replace("torch.cuda.synchronize();cost['finite_gradient_and_state_verification_seconds']=time.perf_counter()-tick",
        'torch.cuda.synchronize()')
replace('model_state_unchanged=True,numerics=numerics,cost_seconds=cost,',
        'model_state_unchanged=False,optimizer_reset=True,optimizer_check=optimizer_check,numerics=numerics,cost_seconds=cost,')
replace('finite_nonzero_gradients=True,weights_unchanged=True,',
        'finite_nonzero_gradients=True,actual_AdamW_updates=1,maximum_weight_error=max_weight,')
replace('model.zero_grad(set_to_none=True);gc.collect();torch.cuda.empty_cache();guard(True)',
        'model.zero_grad(set_to_none=True);del opt,original_parameters,original_gradients;gc.collect();torch.cuda.empty_cache();guard(True)')
replace('del model,cache,x,y,labels;', 'del model,cache,x,y,labels,initial_state;')
replace('all_parent_weights_unchanged=True,', 'all_parent_source_files_unchanged=True,all_six_first_AdamW_updates_verified=True,all_six_memory_captures_verified=True,')
replace("GPU_forwards=6,GPU_backwards=6,resources_after=guard(True)",
        'GPU_forwards=6,GPU_backwards=6,training_updates=6,in_memory_captures=6,resources_after=guard(True)')
replace("'GPU_forwards','GPU_backwards','training_updates','elapsed_seconds'", "'GPU_forwards','GPU_backwards','training_updates','in_memory_captures','elapsed_seconds'")
ast.parse(src)
target=HERE/'run_optimizer_qualification.py'
assert not target.exists()
target.write_text(src,encoding='utf-8')
diff=''.join(difflib.unified_diff(original.read_text(encoding='utf-8').splitlines(True),src.splitlines(True),fromfile=original.name,tofile=target.name))
(HERE/'OPTIMIZER_EXACT_DIFF.patch').write_text(diff,encoding='utf-8')
record=dict(complete=True,original_source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
            generated_source_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),AST_passed=True,
            optimizer_diagnostic_executed=False,original_source_modified=False,formal_training_ready=False)
with (HERE/'OPTIMIZER_PREPARATION.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record))
