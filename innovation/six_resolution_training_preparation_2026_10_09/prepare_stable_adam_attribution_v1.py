"""Create a separate attribution script; never modify the old executed source."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'diagnose_synthetic_adam_v1.py').read_text(encoding='utf-8')
replacements={
 'from mc_rc_3d_baseline_2026_10_07 import loss':'from stable_reduction_task_model_v1 import StableReductionTaskUNet3D,stable_production_total_loss',
 'synthetic_adam_attribution_attempt01':'stable_reduction_adam_attribution_attempt01',
 'gin_cpu_reference_verification_attempt02/receipt.json':'stable_reduction_model_cpu_attempt01/receipt.json',
 'GIN_SYNTHETIC_ADAM_ATTRIBUTION_PROTOCOL_V1.md':'STABLE_REDUCTION_ADAM_ATTRIBUTION_PROTOCOL_V1.md',
 'verify_gin_cpu_reference_v2.py':'verify_stable_reduction_model_cpu_v1.py',
 'production=CheckpointedTaskUNet3D()':'production=StableReductionTaskUNet3D()',
 "value=(loss(outputs[0],target)+.1*mean_target_kl(torch.cat((torch.zeros_like(torch.stack([v[0] for v in outputs])),torch.stack([v[0] for v in outputs])),2))) if index==0 else independent_total_loss(outputs,target)":"value=stable_production_total_loss(outputs,target) if index==0 else independent_total_loss([tuple(z.to(torch.float64) for z in v) for v in outputs],target)",
 'production_FP32_norm':'production_FP64_var_mean_norm_loss',
 'reference_FP64_norm':'reference_FP64_explicit_norm_loss',
}
for old,new in replacements.items():
 assert old in s,old
 s=s.replace(old,new)
s=s.replace("HERE/'gin_reference_adapter_v1.py',ROOT/", "HERE/'gin_reference_adapter_v1.py',HERE/'stable_reduction_task_model_v1.py',ROOT/")
assert 'value=stable_production_total_loss' in s
p=HERE/'diagnose_stable_reduction_adam_v1.py';assert not p.exists()
p.write_text(s,encoding='utf-8');print(p)
