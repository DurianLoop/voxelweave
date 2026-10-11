import ast
from pathlib import Path
HERE=Path(__file__).resolve().parent
for kind in ('small','fullpatch'):
 s=(HERE/f'verify_compact_norm_reference_lifetime_{kind}_v2.py').read_text(encoding='utf-8')
 s=s.replace('from compact_norm_task_model_v2 import','from compact_norm_task_model_v3 import')
 s=s.replace('compact_norm_reference_lifetime_small_attempt01','compact_norm_segmented_small_attempt01').replace('compact_norm_fullpatch_independent_attempt02','compact_norm_fullpatch_independent_attempt03')
 s=s.replace('COMPACT_REFERENCE_LIFETIME_PROTOCOL_V2.md','COMPACT_SEGMENT_CHECKPOINT_PROTOCOL_V3.md')
 s=s.replace("STAGE/'compact_norm_task_model_v2.py',", "STAGE/'compact_norm_task_model_v2.py',STAGE/'compact_norm_task_model_v3.py',",1)
 ast.parse(s);p=HERE/f'verify_compact_norm_segmented_{kind}_v3.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
