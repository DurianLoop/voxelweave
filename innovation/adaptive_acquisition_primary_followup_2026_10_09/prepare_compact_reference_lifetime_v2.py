import ast
from pathlib import Path
HERE=Path(__file__).resolve().parent
for kind,name in [('small','verify_compact_norm_offload_small_v1.py'),('fullpatch','verify_compact_norm_fullpatch_independent_v1.py')]:
 s=(HERE/name).read_text(encoding='utf-8')
 s=s.replace('from compact_norm_task_model_v1 import','from compact_norm_task_model_v2 import')
 s=s.replace('compact_norm_offload_small_attempt01','compact_norm_reference_lifetime_small_attempt01') if kind=='small' else s.replace('compact_norm_fullpatch_independent_attempt01','compact_norm_fullpatch_independent_attempt02')
 s=s.replace('COMPACT_NORM_OFFLOAD_SMALL_PROTOCOL_V1.md','COMPACT_REFERENCE_LIFETIME_PROTOCOL_V2.md').replace('COMPACT_NORM_FULLPATCH_INDEPENDENT_PROTOCOL_V1.md','COMPACT_REFERENCE_LIFETIME_PROTOCOL_V2.md')
 s=s.replace("STAGE/'compact_norm_task_model_v1.py',", "STAGE/'compact_norm_task_model_v1.py',STAGE/'compact_norm_task_model_v2.py',",1)
 s=s.replace("  gpuviews=[v.to('cuda:0') for v in views];gputarget=target.to('cuda:0')", "  gputarget=target.to('cuda:0')")
 if kind=='small':
  s=s.replace("outputs=[model(v) for v in (gpuviews if index==0 else views)]", "outputs=[model(v.to('cuda:0') if index==0 else v) for v in views]")
 else:
  s=s.replace("for viewindex,v in enumerate(gpuviews if index==0 else views):", "for viewindex,v in enumerate(views):").replace("outputs.append(model(v));check();", "outputs.append(model(v.to('cuda:0') if index==0 else v));check();")
  old="  prior_gpu=read(STAGE/'compact_norm_model_gpu_attempt01/receipt.json')"
  s=s.replace(old,"  prior_gpu=read(STAGE/'compact_norm_reference_lifetime_small_attempt01/receipt.json')")
  s=s.replace("entry(STAGE/'compact_norm_model_gpu_attempt01/receipt.json')", "entry(STAGE/'compact_norm_reference_lifetime_small_attempt01/receipt.json')")
 anchor=" except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()"
 new=" except Exception as e:\n  r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()\n  if 'audit' in locals() and audit.records and audit.unpacks:\n   r.update(audit.write(out/'failure_saved_tensor_journal.jsonl.gz'));r['failure_saved_tensor_journal']=entry(out/'failure_saved_tensor_journal.jsonl.gz')\n  if torch.cuda.is_initialized():r['GPU_peak_reserved_bytes_on_failure']=torch.cuda.max_memory_reserved()"
 assert anchor in s;s=s.replace(anchor,new);ast.parse(s)
 p=HERE/f'verify_compact_norm_reference_lifetime_{kind}_v2.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
