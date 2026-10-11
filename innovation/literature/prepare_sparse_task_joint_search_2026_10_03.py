"""Generate next four direct prior-art queries without modifying completed searches."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=(ROOT/'search_task_adaptation_direct_2026_10_03.py').read_text(encoding='utf-8')
s=s.replace('task_adaptation_direct_search_2026-10-03','sparse_task_joint_search_2026-10-03').replace('2026-10-03_task_adaptation_direct_search_plan.md','2026-10-03_sparse_task_joint_search_plan.md')
start=s.index('QUERIES=');end=s.index('\ndef sha',start)
s=s[:start]+'''QUERIES=[
 '(MRI[Title/Abstract] OR "magnetic resonance"[Title/Abstract]) AND "super-resolution"[Title/Abstract] AND segmentation[Title/Abstract] AND (joint[Title/Abstract] OR "end-to-end"[Title/Abstract] OR multitask[Title/Abstract])',
 '(MRI[Title/Abstract] OR "magnetic resonance"[Title/Abstract]) AND segmentation[Title/Abstract] AND ("low resolution"[Title/Abstract] OR "thick slice"[Title/Abstract] OR anisotropic[Title/Abstract]) AND (training[Title/Abstract] OR "deep learning"[Title/Abstract])',
 '(MRI[Title/Abstract] OR "magnetic resonance"[Title/Abstract]) AND segmentation[Title/Abstract] AND "partial volume"[Title/Abstract] AND ("deep learning"[Title/Abstract] OR neural[Title/Abstract])',
 '(MRI[Title/Abstract] OR "magnetic resonance"[Title/Abstract]) AND reconstruction[Title/Abstract] AND segmentation[Title/Abstract] AND ("task-driven"[Title/Abstract] OR "task-specific"[Title/Abstract] OR "joint training"[Title/Abstract])'
]
'''+s[end:]
p=ROOT/'search_sparse_task_joint_2026_10_03.py';assert not p.exists();p.write_text(s,encoding='utf-8')
