import ast
from pathlib import Path
HERE=Path(__file__).resolve().parent;PREP=HERE.parent/'six_resolution_training_preparation_2026_10_09'
s=(PREP/'probe_high_precision_fullpatch_cost_v1.py').read_text(encoding='utf-8')
old="HERE=Path(__file__).resolve().parent;ROOT=HERE.parent"
assert old in s;s=s.replace(old,"STAGE=Path(__file__).resolve().parent;ROOT=STAGE.parent;HERE=ROOT/'six_resolution_training_preparation_2026_10_09';sys.path.insert(0,str(HERE))")
s=s.replace('from high_precision_task_model_v2 import','from audited_saved_cpu_v1 import CpuSavedTensorAudit\nfrom compact_norm_task_model_v1 import')
s=s.replace("out=HERE/'high_precision_fullpatch_cost_attempt01'","out=STAGE/'compact_norm_fullpatch_cost_attempt01'")
s=s.replace("HERE/'HIGH_PRECISION_FULLPATCH_COST_PROTOCOL_V1.md'","STAGE/'COMPACT_NORM_FULLPATCH_COST_PROTOCOL_V1.md'")
s=s.replace("q=read(HERE/'high_precision_model_gpu_attempt04/receipt.json')","q=read(STAGE/'compact_norm_offload_small_attempt01/receipt.json')")
s=s.replace("HERE/'high_precision_model_gpu_attempt04/receipt.json'","STAGE/'compact_norm_offload_small_attempt01/receipt.json'")
s=s.replace("HERE/'high_precision_task_model_v2.py',", "HERE/'high_precision_task_model_v2.py',STAGE/'compact_norm_task_model_v1.py',STAGE/'compact_double_norm_v1.py',STAGE/'audited_saved_cpu_v1.py',",1)
start=s.index('  for index,view in enumerate(views):');end=s.index("  r['phase']='GPU_AdamW';",start)
block=s[start:end];s=s[:start]+"  audit=CpuSavedTensorAudit(array_sha,check)\n  with audit.context():\n"+'\n'.join(' '+line for line in block.splitlines())+'\n'+s[end:]
s=s.replace("  r.update(fullpatch_graph_completed=True,GPU_full_graph_seconds=time.perf_counter()-tick)", "  r.update(fullpatch_graph_completed=True,GPU_full_graph_seconds=time.perf_counter()-tick);r.update(audit.write(out/'saved_tensor_journal.jsonl.gz'));r['saved_tensor_journal']=entry(out/'saved_tensor_journal.jsonl.gz')")
anchor="  if torch.cuda.is_initialized():r['GPU_peak_reserved_bytes_on_failure']"
s=s.replace(anchor,"  if 'audit' in locals() and audit.records and audit.unpacks:\n   r.update(audit.write(out/'failure_saved_tensor_journal.jsonl.gz'));r['failure_saved_tensor_journal']=entry(out/'failure_saved_tensor_journal.jsonl.gz')\n"+anchor)
ast.parse(s);p=STAGE/'probe_compact_norm_fullpatch_cost_v1.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
