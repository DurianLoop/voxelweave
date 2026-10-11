"""Generate three authenticated JATS requests in a new immutable batch directory."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=(ROOT/'fetch_task_normalization_context_2026_10_03.py').read_text(encoding='utf-8')
s=s.replace('task_normalization_context_fulltexts_2026-10-03','sparse_task_joint_fulltexts_2026-10-03').replace('2026-10-03_task_normalization_context_selection.md','2026-10-03_sparse_task_joint_selection.md')
start=s.index('PAPERS=');end=s.index('\ndef sha',start)
s=s[:start]+"PAPERS=[('joint_scar','PMC10959501','10.1109/isbi53787.2023.10230541'),\n ('soft_spinal','PMC13110827','10.1016/j.media.2025.103473'),\n ('drips','PMC12633610','10.1101/2025.10.22.25337423')]\n"+s[end:]
p=ROOT/'fetch_sparse_task_joint_fulltexts_2026_10_03.py';assert not p.exists();p.write_text(s,encoding='utf-8')
