"""Explicit GPU opt-in for this process; frozen geometry continues on CPU."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='0'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import torch
_torch_cuda_initializer=torch.cuda._lazy_init
from mc_rc_global_local_task_cpu_support import GlobalLocalUNet,np,weight_hash
from vs_seg_task_cpu_support import resource_gate


def enable_authorized_gpu():
    # Existing CPU-only modules keep their own source and other processes unchanged.
    # Imports of these modules can set CUDA_VISIBLE_DEVICES=-1 locally; restore
    # this explicitly authorized adapter only after all CPU support imports.
    os.environ['CUDA_VISIBLE_DEVICES']='0'
    torch.cuda._lazy_init=_torch_cuda_initializer
    assert torch.cuda.is_available(), 'CUDA unavailable; preserve failed attempt.'
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.backends.cudnn.benchmark=False
    torch.backends.cudnn.deterministic=True
    torch.cuda.set_per_process_memory_fraction(.1,0)
    free,total=torch.cuda.mem_get_info(0)
    assert free>=8_000_000_000
    return dict(device='cuda:0',gpu_name=torch.cuda.get_device_name(0),
        torch_version=str(torch.__version__),free_bytes=free,total_bytes=total,
        allocator_fraction=.1,autocast_enabled=False,tf32_enabled=False,
        cudnn_benchmark=False,cudnn_deterministic=True,
        user_authorization='可以用gpu',cpu_geometry_preserved=True)


def gpu_resource_gate():
    values=resource_gate();free,total=torch.cuda.mem_get_info(0)
    peak=torch.cuda.max_memory_reserved(0)
    assert free>=4_000_000_000 and peak<=2_500_000_000
    values.update(gpu_free_bytes=free,gpu_total_bytes=total,gpu_peak_reserved_bytes=peak)
    return values


class CpuGeometryGpuBranches:
    """Return CPU tensors at both boundaries, retaining old context_tiles numerics."""
    def __init__(self,model):
        self.model=model.to('cuda:0');self.model.eval()

    @property
    def global_calls(self):return self.model.global_calls

    @property
    def local_calls(self):return self.model.local_calls

    def eval(self):self.model.eval();return self

    def global_forward(self,x):
        features,coarse=self.model.global_forward(x.to('cuda:0'))
        return features.cpu(),coarse.cpu()

    def local_forward(self,x,context):
        return self.model.local_forward(x.to('cuda:0'),context.to('cuda:0')).cpu()


def synthetic_device_preflight():
    rng=np.random.default_rng(20261003);torch.manual_seed(20261004)
    cpu=GlobalLocalUNet().eval();gpu=GlobalLocalUNet().eval()
    gpu.load_state_dict(cpu.state_dict(),strict=True)
    initial=weight_hash(cpu);assert weight_hash(gpu)==initial
    gpu.to('cuda:0')
    x=torch.from_numpy(rng.standard_normal((1,5,256,256)).astype(np.float32))
    patches=torch.from_numpy(rng.standard_normal((2,5,128,128)).astype(np.float32))
    context=torch.from_numpy(rng.standard_normal((2,9,128,128)).astype(np.float32))
    with torch.inference_mode():
        cf,cl=cpu.global_forward(x);cp=cpu.local_forward(patches,context)
        gf,gl=gpu.global_forward(x.to('cuda:0'));gp=gpu.local_forward(patches.to('cuda:0'),context.to('cuda:0'))
        gf2,gl2=gpu.global_forward(x.to('cuda:0'));gp2=gpu.local_forward(patches.to('cuda:0'),context.to('cuda:0'))
        comparisons=[]
        for name,a,b,repeat in (('global_features',cf,gf,gf2),('global_logits',cl,gl,gl2),('local_logits',cp,gp,gp2)):
            b=b.cpu();repeated=torch.equal(b,repeat.cpu())
            error=float((a-b).abs().max());probability_error=float((a.sigmoid()-b.sigmoid()).abs().max())
            assert error<=5e-4 and probability_error<=5e-5 and repeated
            comparisons.append(dict(tensor=name,max_absolute_error=error,max_sigmoid_error=probability_error,
                repeated_gpu_exactly_equal=repeated))
    result=dict(initial_weights_sha256=initial,comparisons=comparisons,
        cpu_global_forward_calls=cpu.global_calls,cpu_local_forward_calls=cpu.local_calls,
        gpu_global_forward_calls=gpu.global_calls,gpu_local_forward_calls=gpu.local_calls,
        patient_inputs_read=0,label_inputs_read=0,training_updates=0,
        interpretation='Synthetic runtime numerical check; not checkpoint or patient cross-device reproduction.')
    del cpu,gpu,x,patches,context,cf,cl,cp,gf,gl,gp,gf2,gl2,gp2
    torch.cuda.empty_cache()
    result['resource_guard']=gpu_resource_gate()
    return result
