"""Preserve the CPU-import CUDA environment failure, make a new layout diagnostic."""
import ast
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=HERE/'diagnose_failed_fov_layout.py';text=source.read_text(encoding='utf-8')
assert "def main():\n torch.set_num_threads(1)" in text
text=text.replace("def main():\n torch.set_num_threads(1)","def main():\n os.environ['CUDA_VISIBLE_DEVICES']='0'\n torch.set_num_threads(1)")
text=text.replace('layout_diagnosis_attempt01','layout_diagnosis_attempt02')
ast.parse(text)
with (HERE/'diagnose_failed_fov_layout_v2.py').open('x',encoding='utf-8') as f:f.write(text)
print('New diagnostic v2 AST parsed; reset CUDA visibility after inherited CPU imports; v1 preserved.')
