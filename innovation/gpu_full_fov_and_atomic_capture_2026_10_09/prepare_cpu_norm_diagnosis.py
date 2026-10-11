"""Create a new inference-only normalization device diagnostic; all original weights/sources preserved."""
import ast
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=HERE/'diagnose_failed_fov_layout_v2.py';text=source.read_text(encoding='utf-8')
text=text.replace('layout_diagnosis_attempt02','cpu_norm_diagnosis_attempt01')
text=text.replace("['contiguous','channels_last_3d']","['contiguous','cpu_instance_norm']")
old="   if layout=='channels_last_3d':model.to(memory_format=torch.channels_last_3d)"
new="""   if layout=='cpu_instance_norm':
    import types
    def cpu_normalize(self,x):
     assert not self.training and not torch.is_grad_enabled()
     guard()
     value=torch.nn.functional.instance_norm(x.cpu(),weight=self.weight.detach().cpu(),bias=self.bias.detach().cpu(),
      use_input_stats=True,eps=self.eps).to(x.device)
     guard();return value
    norm_count=0
    for module in model.modules():
     if isinstance(module,torch.nn.InstanceNorm3d):module.forward=types.MethodType(cpu_normalize,module);norm_count+=1
    assert norm_count==14
"""
assert old in text;text=text.replace(old,new)
text=text.replace("     if layout=='channels_last_3d':x=x.contiguous(memory_format=torch.channels_last_3d)",
 "     # Input/weight layout retained; only the specified norm execution device changes.")
text=text.replace("HERE/'FAILED_FOV_DIAGNOSIS_PROTOCOL.md',fp,tp,cpfile,pp",
 "HERE/'FAILED_FOV_DIAGNOSIS_PROTOCOL.md',HERE/'CPU_NORM_DIAGNOSIS_PROTOCOL.md',HERE/'prepare_cpu_norm_diagnosis.py',source,fp,tp,cpfile,pp")
# Bind the actual source path without relying on the generator variable at runtime.
text=text.replace(",source,fp,tp,cpfile,pp",",HERE/'diagnose_failed_fov_layout_v2.py',fp,tp,cpfile,pp")
ast.parse(text)
with (HERE/'diagnose_failed_fov_cpu_norm.py').open('x',encoding='utf-8') as f:f.write(text)
print('New hybrid CPU-normalization diagnostic AST parsed; original sources unchanged.')
