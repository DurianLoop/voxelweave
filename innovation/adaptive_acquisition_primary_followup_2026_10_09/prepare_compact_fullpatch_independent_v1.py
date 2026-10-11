import ast
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'verify_compact_norm_offload_small_v1.py').read_text(encoding='utf-8')
s=s.replace('compact_norm_offload_small_attempt01','compact_norm_fullpatch_independent_attempt01').replace('COMPACT_NORM_OFFLOAD_SMALL_PROTOCOL_V1.md','COMPACT_NORM_FULLPATCH_INDEPENDENT_PROTOCOL_V1.md').replace('guard(started,360)','guard(started,10800)')
old="shape=(2,1,16,16,16);x=torch.randn(shape,generator=torch.Generator().manual_seed(49));views=[gin(x,draw_parameters(shape,480000+i))[0] for i in range(3)]\n  target=(torch.randn(shape,generator=torch.Generator().manual_seed(501))>.8).float()"
new="shape=(2,1,64,128,128);x=torch.randn(shape,generator=torch.Generator().manual_seed(991));views=[gin(x,draw_parameters(shape,801+i))[0] for i in range(3)];del x\n  z,row,col=torch.meshgrid(torch.arange(64),torch.arange(128),torch.arange(128),indexing='ij');target=(((z-31.5)/16).square()+((row-63.5)/24).square()+((col-63.5)/24).square()<1).float()[None,None].repeat(2,1,1,1,1);del z,row,col"
assert old in s;s=s.replace(old,new)
old="assert r['input_sha256']==prior['input_sha256'] and r['synthetic_target_sha256']==prior['synthetic_target_sha256']"
new="cost=read(STAGE/'compact_norm_fullpatch_cost_attempt01/receipt.json');assert cost['complete'] and not cost['errors'];assert r['input_sha256']==cost['view_sha256'] and r['synthetic_target_sha256']==cost['target_sha256'];r['source_bindings'].append(entry(STAGE/'compact_norm_fullpatch_cost_attempt01/receipt.json'))"
assert old in s;s=s.replace(old,new)
anchor="    check();tick=time.perf_counter();opt.zero_grad(set_to_none=True)"
newanchor="    r['current_step']=step;r['current_branch']='GPU' if index==0 else 'CPU_independent';save();print(json.dumps(dict(step=step,branch=r['current_branch'],status='started',elapsed_seconds=time.perf_counter()-started)),flush=True)\n"+anchor
assert anchor in s;s=s.replace(anchor,newanchor)
old="     outputs=[model(v) for v in (gpuviews if index==0 else views)]"
new="     outputs=[]\n     for viewindex,v in enumerate(gpuviews if index==0 else views):\n      outputs.append(model(v));check();r['current_view_forward_completed']=viewindex+1;save();print(json.dumps(dict(step=step,branch=r['current_branch'],view_forward_completed=viewindex+1,elapsed_seconds=time.perf_counter()-started)),flush=True)"
assert old in s;s=s.replace(old,new)
s=s.replace("    del outputs,value,grads,probs;gc.collect();check();save()","    del outputs,value,grads,probs;gc.collect();check();save();print(json.dumps(dict(step=step,branch=r['current_branch'],status='optimizer_update_completed',elapsed_seconds=time.perf_counter()-started)),flush=True)")
s=s.replace("r.update(complete=True,all_two_synthetic_GPU_CPU_steps_passed=True,resources_after=check())", "r.update(complete=True,all_two_synthetic_GPU_CPU_steps_passed=True,original_fullpatch_two_synthetic_steps_passed=True,resources_after=check())")
ast.parse(s);p=HERE/'verify_compact_norm_fullpatch_independent_v1.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
