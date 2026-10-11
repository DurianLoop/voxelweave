"""Generate new reference and verifier files, preserving all previous sources."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
reference=(HERE/'gin_cpu_differentiable_reference_v2.py').read_text(encoding='utf-8')
reference=reference.replace('FP32 convolution/parameters, FP64 norm','FP32 parameters, FP64 convolutions/activations/norm')
reference=reference.replace("self.whole_model_calls+=1;stored=[];heads=[]","self.whole_model_calls+=1;value=value.to(torch.float64);stored=[];heads=[]")
reference=reference.replace("self.state[f'{prefix}.layers.{first}.weight'],padding", "self.state[f'{prefix}.layers.{first}.weight'].to(torch.float64),padding")
reference=reference.replace("self.state[f'ups.{depth}.weight'],self.state[f'ups.{depth}.bias'],stride", "self.state[f'ups.{depth}.weight'].to(torch.float64),self.state[f'ups.{depth}.bias'].to(torch.float64),stride")
reference=reference.replace("self.state[f'heads.{depth}.weight'],self.state[f'heads.{depth}.bias']", "self.state[f'heads.{depth}.weight'].to(torch.float64),self.state[f'heads.{depth}.bias'].to(torch.float64)")
p=HERE/'high_precision_cpu_reference_v1.py';assert not p.exists();p.write_text(reference,encoding='utf-8')
s=(HERE/'verify_stable_reduction_model_cpu_v1.py').read_text(encoding='utf-8')
for old,new in {
 'from stable_reduction_task_model_v1 import StableReductionTaskUNet3D,stable_production_total_loss':'from high_precision_task_model_v1 import HighPrecisionTaskUNet3D,stable_production_total_loss',
 'from gin_cpu_differentiable_reference_v2 import':'from high_precision_cpu_reference_v1 import',
 'stable_reduction_model_cpu_attempt01':'high_precision_model_cpu_attempt01',
 'STABLE_REDUCTION_MODEL_SYNTHETIC_PROTOCOL_V1.md':'HIGH_PRECISION_SYNTHETIC_PROTOCOL_V1.md',
 "HERE/'stable_reduction_task_model_v1.py',HERE/'gin_cpu_differentiable_reference_v2.py'":"HERE/'high_precision_task_model_v1.py',HERE/'high_precision_cpu_reference_v1.py',HERE/'stable_reduction_task_model_v1.py',HERE/'gin_cpu_differentiable_reference_v2.py'",
 'production=StableReductionTaskUNet3D()':'production=HighPrecisionTaskUNet3D()',
 'assert z.dtype==torch.float32':'assert z.dtype==torch.float64',
}.items():assert old in s,old;s=s.replace(old,new)
s=s.replace('original_FP32_production_qualified=False,', 'original_FP32_production_qualified=False,graph_precision="FP64",parameter_precision="FP32",')
p=HERE/'verify_high_precision_model_cpu_v1.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
