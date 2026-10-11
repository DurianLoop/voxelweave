"""Create an explicit second attempt; preserve the failed first script/output."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'experiments/anchor_normalization_control_cpu.py'
new=ROOT/'experiments/anchor_normalization_control_cpu_attempt_02.py'
assert not new.exists()
s=old.read_text(encoding='utf-8')
s=s.replace('Three fixed source-volume normalization controls, no torch or network import.','Second attempt: same controls, record indirect torch import; forbid CUDA initialization.')
s=s.replace("OUT=ROOT/'experiments/anchor_normalization_control_cpu'","OUT=ROOT/'experiments/anchor_normalization_control_cpu_attempt_02'")
s=s.replace("ROOT/'ANCHOR_NORMALIZATION_CONTROL_CPU_PLAN_2026-10-03.md',source,","ROOT/'ANCHOR_NORMALIZATION_CONTROL_CPU_PLAN_2026-10-03.md',ROOT/'ANCHOR_NORMALIZATION_CONTROL_CPU_REPAIR_2026-10-03.md',ROOT/'experiments/anchor_normalization_control_cpu.py',ROOT/'experiments/anchor_normalization_control_cpu/attempt_01.json',source,")
s=s.replace("torch_imported=False,new_neural_forwards=0","torch_imported=None,new_neural_forwards=0")
s=s.replace("assert len(r['patients'])==3 and 'torch' not in sys.modules;r.update(","assert len(r['patients'])==3;r['torch_imported']='torch' in sys.modules;r['cuda_initialized']=sys.modules['torch'].cuda.is_initialized() if r['torch_imported'] else False;assert not r['cuda_initialized'];r.update(")
new.write_text(s,encoding='utf-8')
print(new)
