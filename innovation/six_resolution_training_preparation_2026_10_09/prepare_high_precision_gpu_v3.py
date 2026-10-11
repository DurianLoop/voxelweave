from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'verify_high_precision_model_gpu_v2.py').read_text(encoding='utf-8')
s=s.replace('high_precision_model_gpu_attempt02','high_precision_model_gpu_attempt03').replace('HIGH_PRECISION_GPU_SYNTHETIC_PROTOCOL_V2.md','HIGH_PRECISION_GPU_SYNTHETIC_PROTOCOL_V3.md')
old="  assert not torch.cuda.is_initialized();torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()"
new="  assert not torch.cuda.is_initialized();r['CUDA_VISIBLE_DEVICES_after_CPU_imports']=os.environ.get('CUDA_VISIBLE_DEVICES');os.environ['CUDA_VISIBLE_DEVICES']='0';r['CUDA_VISIBLE_DEVICES_at_GPU_admission']=os.environ['CUDA_VISIBLE_DEVICES'];r['torch_version']=str(torch.__version__);r['torch_CUDA_version']=torch.version.cuda;torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()"
assert s.count(old)==1;s=s.replace(old,new)
p=HERE/'verify_high_precision_model_gpu_v3.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
