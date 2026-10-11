"""Known KNConv Eq5, three spatial dimensions, no dropout; preparation only."""
import torch
from torch.nn import functional as F

def local_kernel_conv3d(x,weight,bias=None,*,stride=(1,1,1),padding=(1,1,1),eps=1e-5):
    """Statistics are confined to exactly one convolution window across input channels.

    This implements the p=0 operator only, not the paper's stochastic training
    recipe or architecture. Moment subtraction and output subtraction can lose
    precision for nearly constant inputs; float32 is separately qualified.
    """
    assert x.ndim==5 and weight.ndim==5 and x.shape[1]==weight.shape[1]
    kernel=tuple(weight.shape[2:]);assert all(k%2==1 for k in kernel)
    assert x.dtype==weight.dtype and x.device==weight.device
    mean=F.avg_pool3d(x.mean(dim=1,keepdim=True),kernel_size=kernel,stride=stride,
                      padding=padding,count_include_pad=True)
    second=F.avg_pool3d(x.square().mean(dim=1,keepdim=True),kernel_size=kernel,stride=stride,
                        padding=padding,count_include_pad=True)
    variance=(second-mean.square()).clamp_min(0)
    convolution=F.conv3d(x,weight,bias=None,stride=stride,padding=padding)
    sums=weight.sum(dim=(1,2,3,4))[None,:,None,None,None]
    result=(convolution-mean*sums)/torch.sqrt(variance+eps)
    if bias is not None:result=result+bias[None,:,None,None,None]
    return result
