"""Native CPU pooling vs disjoint windows, including ties and full VJP."""
import sys,time,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'))
from resource_guard_v1 import guard,entry,dump
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch
from high_precision_task_model_v2 import disjoint_max_pool3d
start=time.perf_counter();before=guard(start);torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
torch.use_deterministic_algorithms(True);records=[];shape=(2,3,4,6,8)
for dtype in (torch.float32,torch.float64):
 for kind in ('random','all_equal','repeated_maxima'):
  if kind=='random':a=torch.randn(shape,dtype=dtype,generator=torch.Generator().manual_seed(511))
  elif kind=='all_equal':a=torch.zeros(shape,dtype=dtype)
  else:a=(torch.arange(1152).reshape(shape)%3).to(dtype)
  a.requires_grad_();b=a.detach().clone().requires_grad_();x=torch.nn.functional.max_pool3d(a,2);y=disjoint_max_pool3d(b)
  u=torch.randn(x.shape,dtype=dtype,generator=torch.Generator().manual_seed(512));x.backward(u);y.backward(u)
  assert torch.equal(x,y) and torch.equal(a.grad,b.grad)
  records.append(dict(dtype=str(dtype),kind=kind,output_max_error=float((x-y).abs().max()),input_VJP_max_error=float((a.grad-b.grad).abs().max()),tie_selection_bitwise_equal=True))
assert not torch.cuda.is_initialized()
out=HERE/'disjoint_pool_cpu_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=True,errors=[],records=records,source_bindings=[entry(Path(__file__)),entry(HERE/'high_precision_task_model_v2.py')],CPU_optimizer_updates=0,GPU_calls=0,MRI_arrays_loaded=0,GT_arrays_loaded=0,CUDA_initialized=False,resources_before=before,resources_after=guard(start),elapsed_seconds=time.perf_counter()-start)
dump(out/'receipt.json',r);print(json.dumps(dict(complete=True,records=records)))
