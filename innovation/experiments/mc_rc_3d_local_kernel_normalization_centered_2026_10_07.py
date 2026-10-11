"""Explicit, pivot-centered known KNConv with p=0; synthetic preparation only."""
import math
import torch
from torch.nn import functional as F


def local_kernel_conv3d_centered(x, weight, bias=None, *, stride=(1, 1, 1), padding=(1, 1, 1), eps=1e-5):
    assert x.ndim == 5 and weight.ndim == 5 and x.shape[1] == weight.shape[1]
    assert x.dtype == weight.dtype and x.device == weight.device and eps > 0
    assert len(stride) == len(padding) == 3 and all(s > 0 for s in stride)
    kernel = tuple(weight.shape[2:])
    output_shape = tuple((n + 2*p-k)//s+1 for n, p, k, s in zip(x.shape[2:], padding, kernel, stride))
    assert min(output_shape) > 0
    count = x.shape[0] * math.prod(output_shape) * x.shape[1] * math.prod(kernel)
    assert count <= 10_000_000, 'Explicit prototype exceeds frozen window element budget'
    padded = F.pad(x, (padding[2], padding[2], padding[1], padding[1], padding[0], padding[0]))
    windows = padded.unfold(2, kernel[0], stride[0]).unfold(3, kernel[1], stride[1]).unfold(4, kernel[2], stride[2])
    # N,D,H,W,C,Kd,Kh,Kw; each output position has one independent local unit.
    units = windows.permute(0, 2, 3, 4, 1, 5, 6, 7).reshape(x.shape[0], -1, weight[0].numel())
    residual = units - units[..., :1]
    centered = residual - residual.mean(dim=-1, keepdim=True)
    variance = centered.square().mean(dim=-1, keepdim=True)
    normalized = centered / torch.sqrt(variance + eps)
    out = normalized @ weight.reshape(weight.shape[0], -1).T
    if bias is not None:
        assert bias.dtype == x.dtype and bias.device == x.device
        out = out + bias
    assert out.dtype == x.dtype
    return out.reshape(x.shape[0], *output_shape, weight.shape[0]).permute(0, 4, 1, 2, 3).contiguous()
