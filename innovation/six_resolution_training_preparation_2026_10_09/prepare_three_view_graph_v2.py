"""Add missing full optimizer moment checks in a new version; keep executed v1 unchanged."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=HERE/'qualify_three_view_graph_synthetic_v1.py';target=HERE/'qualify_three_view_graph_synthetic_v2.py'
assert not target.exists();s=source.read_text(encoding='utf-8')
s=s.replace("out=HERE/'three_view_synthetic_attempt01'","out=HERE/'three_view_synthetic_attempt02'")
anchor='   assert parameter_error<=3e-6 and torch.equal(target,target_before)'
addition='''   moment_checks=[]
   for (name,a),(other,b) in zip(models[0].named_parameters(),models[1].named_parameters()):
    assert name==other
    ast=optimizers[0].state.get(a,{});bst=optimizers[1].state.get(b,{})
    assert ast.keys()==bst.keys()
    for key,av in ast.items():
     bv=bst[key];assert av.shape==bv.shape and av.dtype==bv.dtype
     error=float((av-bv).abs().max())
     if key=='step':assert torch.equal(av,bv)
     moment_checks.append(dict(name=name,optimizer_field=key,max_error=error))
   moment_error=max([v['max_error'] for v in moment_checks] or [0.])
   record.update(optimizer_state_checks=moment_checks,full_optimizer_state_max_error=moment_error,
                 optimizer_state_fields_compared=len(moment_checks))
   assert parameter_error<=3e-6 and moment_error<=3e-6 and torch.equal(target,target_before)'''
assert s.count(anchor)==1;s=s.replace(anchor,addition)
s=s.replace("sources=[Path(__file__),HERE/'THREE_VIEW_GRAPH_PREPARATION_PROTOCOL.md'", "sources=[Path(__file__),source_v1_path,HERE/'THREE_VIEW_GRAPH_PREPARATION_PROTOCOL.md'")
s=s.replace("def main():\n started=", "source_v1_path=HERE/'qualify_three_view_graph_synthetic_v1.py'\ndef main():\n started=")
s=s.replace("'post_AdamW_parameter_max_error']", "'post_AdamW_parameter_max_error','full_optimizer_state_max_error','optimizer_state_fields_compared']")
import ast
ast.parse(s);target.write_text(s,encoding='utf-8');print('prepared_v2_with_full_optimizer_moments')
