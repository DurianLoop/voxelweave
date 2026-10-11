import ast
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'verify_compact_norm_model_gpu_v1.py').read_text(encoding='utf-8')
s=s.replace('compact_norm_model_gpu_attempt01','compact_norm_offload_small_attempt01').replace('COMPACT_NORM_GRAPH_PROTOCOL_V1.md','COMPACT_NORM_OFFLOAD_SMALL_PROTOCOL_V1.md')
s=s.replace('from compact_norm_task_model_v1 import','from audited_saved_cpu_v1 import CpuSavedTensorAudit\nfrom compact_norm_task_model_v1 import')
s=s.replace("STAGE/'compact_norm_task_model_v1.py',", "STAGE/'audited_saved_cpu_v1.py',STAGE/'compact_norm_task_model_v1.py',",1)
anchor="  for step in range(2):";assert s.count(anchor)==1
s=s.replace(anchor,"  prior_gpu=read(STAGE/'compact_norm_model_gpu_attempt01/receipt.json');assert prior_gpu['complete'] and not prior_gpu['errors'];r['source_bindings'].append(entry(STAGE/'compact_norm_model_gpu_attempt01/receipt.json'));audit=CpuSavedTensorAudit(array_sha,check)\n"+anchor)
old="    check();tick=time.perf_counter();opt.zero_grad(set_to_none=True);outputs=[model(v) for v in (gpuviews if index==0 else views)]\n    assert all(z.dtype==torch.float64 for head in outputs for z in head)\n    value=stable_production_total_loss(outputs,gputarget) if index==0 else independent_total_loss(outputs,target)\n    assert value.dtype==torch.float64 and torch.isfinite(value);value.backward()"
new="    check();tick=time.perf_counter();opt.zero_grad(set_to_none=True)\n    context=audit.context() if index==0 else __import__('contextlib').nullcontext()\n    with context:\n     outputs=[model(v) for v in (gpuviews if index==0 else views)]\n     assert all(z.dtype==torch.float64 for head in outputs for z in head)\n     value=stable_production_total_loss(outputs,gputarget) if index==0 else independent_total_loss(outputs,target)\n     assert value.dtype==torch.float64 and torch.isfinite(value);value.backward()"
assert old in s;s=s.replace(old,new)
old="  for s in r['source_bindings']:bind(s)"
new="  r.update(audit.write(out/'saved_tensor_journal.jsonl.gz'));r['saved_tensor_journal']=entry(out/'saved_tensor_journal.jsonl.gz')\n"+old
assert old in s;s=s.replace(old,new);ast.parse(s)
p=HERE/'verify_compact_norm_offload_small_v1.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
