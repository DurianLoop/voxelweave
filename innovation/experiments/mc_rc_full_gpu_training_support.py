"""GPU training kernels, same CPU-created coordinates and preassembled examples."""
from mc_rc_authorized_gpu_adapter import enable_authorized_gpu,gpu_resource_gate
from mc_rc_global_local_task_cpu_support import torch,np,context_tiles,segmentation_loss


def full_gpu_context(global_features,locations,shape):
    rows=torch.arange(128,dtype=torch.float32)+.5
    cols=torch.arange(128,dtype=torch.float32)+.5
    grids=[]
    for r,c in locations:
        rr=2*(rows+r)/shape[0]-1;cc=2*(cols+c)/shape[1]-1
        y,x=torch.meshgrid(rr,cc,indexing='ij');grids.append(torch.stack((x,y),-1))
    grid=torch.stack(grids).to(global_features.device)
    return torch.nn.functional.grid_sample(global_features.expand(len(locations),-1,-1,-1),grid,
        mode='bilinear',padding_mode='border',align_corners=False)


def synthetic_full_gpu_preflight():
    rng=np.random.default_rng(20261003);shape=(513,499)
    locations=[(0,0),(192,180),(shape[0]-128,shape[1]-128)]
    features=torch.from_numpy(rng.standard_normal((1,9,256,256)).astype(np.float32)).requires_grad_()
    gpu_features=features.detach().to('cuda:0').requires_grad_()
    cpu=context_tiles(features,locations,shape);gpu=full_gpu_context(gpu_features,locations,shape)
    error=float((cpu.detach()-gpu.detach().cpu()).abs().max());assert error<=5e-5
    cpu.square().mean().backward();gpu.square().mean().backward()
    assert torch.isfinite(features.grad).all() and torch.isfinite(gpu_features.grad).all()
    gradient_error=float((features.grad-gpu_features.grad.cpu()).abs().max())
    logits=torch.from_numpy(rng.standard_normal((2,1,128,128)).astype(np.float32))
    label=torch.from_numpy(rng.uniform(size=(2,1,128,128)).astype(np.float32))
    a=segmentation_loss(logits,label);b=segmentation_loss(logits.to('cuda:0'),label.to('cuda:0'))
    loss_error=abs(float(a)-float(b));assert loss_error<=5e-5
    return dict(context_max_absolute_error=error,gradient_max_absolute_error=gradient_error,
        cpu_gpu_segmentation_loss_absolute_error=loss_error,finite_context_gradients=True,
        locations=locations,shape=list(shape),patient_inputs_read=0,optimizer_updates=0,
        cuda_grid_sample_backward_bitwise_determinism_not_guaranteed=True,resources=gpu_resource_gate())
