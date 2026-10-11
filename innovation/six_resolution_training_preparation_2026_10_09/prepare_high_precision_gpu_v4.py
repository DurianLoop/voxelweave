from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'verify_high_precision_model_gpu_v3.py').read_text(encoding='utf-8')
s=s.replace('high_precision_model_gpu_attempt03','high_precision_model_gpu_attempt04').replace('HIGH_PRECISION_GPU_SYNTHETIC_PROTOCOL_V3.md','HIGH_PRECISION_GPU_SYNTHETIC_PROTOCOL_V4.md')
s=s.replace('from high_precision_task_model_v1 import','from high_precision_task_model_v2 import')
s=s.replace("HERE/'high_precision_task_model_v1.py',HERE/'high_precision_cpu_reference_v1.py'","HERE/'high_precision_task_model_v1.py',HERE/'high_precision_task_model_v2.py',HERE/'disjoint_pool_cpu_attempt01/receipt.json',HERE/'high_precision_cpu_reference_v1.py'")
s=s.replace("  for step in prior['steps']:","  pool=read(HERE/'disjoint_pool_cpu_attempt01/receipt.json');assert pool['complete'] and not pool['errors']\n  for step in prior['steps']:")
p=HERE/'verify_high_precision_model_gpu_v4.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
