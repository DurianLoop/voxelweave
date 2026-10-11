"""Windows-safe entrypoint; own one-thread torch only."""
import os,runpy,sys
from pathlib import Path
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import torch
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here))
runpy.run_path(str(here/'qualify_all_patient_stress.py'),run_name='__main__')
