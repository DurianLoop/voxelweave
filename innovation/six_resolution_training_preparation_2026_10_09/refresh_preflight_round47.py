"""Call immutable v3 read-only checks in a new output directory; do not train."""
import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run_six_resolution_training_v3 as runner
runner.resource_guard();out=HERE/'preflight_round47_attempt01';out.mkdir(exist_ok=False)
report=runner.checks();assert report['MRI_arrays_loaded']==report['GT_arrays_loaded']==report['model_arrays_loaded']==0
assert not report['CUDA_initialized'] and not report['new_training_launched']
report['source_bindings'].append(runner.entry(Path(__file__)))
runner.dump(out/'receipt.json',report)
print(json.dumps({k:report[k] for k in ['complete','ready','checks','pending','required_above_reserve_bytes','disk_shortfall_bytes','MRI_arrays_loaded','GT_arrays_loaded','model_arrays_loaded','CUDA_initialized']},ensure_ascii=False),flush=True)
