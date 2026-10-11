"""Create separately versioned CPU/GPU validators from the frozen full-scope protocols."""
import ast
from pathlib import Path
STAGE=Path(__file__).resolve().parent;PREP=STAGE.parent/'six_resolution_training_preparation_2026_10_09'
for device,name in [('cpu','verify_high_precision_model_cpu_v1.py'),('gpu','verify_high_precision_model_gpu_v4.py')]:
 s=(PREP/name).read_text(encoding='utf-8')
 old="HERE=Path(__file__).resolve().parent;ROOT=HERE.parent"
 assert old in s;s=s.replace(old,"STAGE=Path(__file__).resolve().parent;ROOT=STAGE.parent;HERE=ROOT/'six_resolution_training_preparation_2026_10_09';sys.path.insert(0,str(HERE))")
 s=s.replace('from high_precision_task_model_v1 import','from compact_norm_task_model_v1 import').replace('from high_precision_task_model_v2 import','from compact_norm_task_model_v1 import')
 s=s.replace("out=HERE/'high_precision_model_cpu_attempt01'","out=STAGE/'compact_norm_model_cpu_attempt01'").replace("out=HERE/'high_precision_model_gpu_attempt04'","out=STAGE/'compact_norm_model_gpu_attempt01'")
 s=s.replace("HERE/'HIGH_PRECISION_SYNTHETIC_PROTOCOL_V1.md'","STAGE/'COMPACT_NORM_GRAPH_PROTOCOL_V1.md'").replace("HERE/'HIGH_PRECISION_GPU_SYNTHETIC_PROTOCOL_V4.md'","STAGE/'COMPACT_NORM_GRAPH_PROTOCOL_V1.md'")
 s=s.replace("HERE/'high_precision_model_cpu_attempt01/receipt.json'","STAGE/'compact_norm_model_cpu_attempt01/receipt.json'")
 anchor="r['resources_before']=check();"
 assert anchor in s;s=s.replace(anchor,anchor+"math_check=read(STAGE/'compact_double_norm_cpu_attempt02/receipt.json');assert math_check['complete'] and not math_check['errors'];",1)
 anchor="r['source_bindings']=[entry(p) for p in (Path(__file__),"
 assert anchor in s;s=s.replace(anchor,anchor+"STAGE/'compact_norm_task_model_v1.py',STAGE/'compact_double_norm_v1.py',STAGE/'compact_double_norm_cpu_attempt02/receipt.json',",1)
 ast.parse(s);p=STAGE/f'verify_compact_norm_model_{device}_v1.py';assert not p.exists();p.write_text(s,encoding='utf-8')
 print(p)
