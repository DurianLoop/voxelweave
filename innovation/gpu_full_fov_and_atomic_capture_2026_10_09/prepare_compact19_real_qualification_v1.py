"""Prepare separately versioned high-precision 19-series qualification from original frozen contract."""
import ast
from pathlib import Path
STAGE=Path(__file__).resolve().parent;ROOT=STAGE.parent;PREP=ROOT/'six_resolution_training_preparation_2026_10_09';ADAPT=ROOT/'adaptive_acquisition_primary_followup_2026_10_09'
s=(PREP/'qualify_gin19_real_graph_v2.py').read_text(encoding='utf-8')
old="HERE=Path(__file__).resolve().parent;ROOT=HERE.parent"
new="STAGE=Path(__file__).resolve().parent;ROOT=STAGE.parent;HERE=ROOT/'six_resolution_training_preparation_2026_10_09';ADAPT=ROOT/'adaptive_acquisition_primary_followup_2026_10_09';sys.path.insert(0,str(HERE));sys.path.insert(0,str(ADAPT))"
assert old in s;s=s.replace(old,new)
s=s.replace('from gin_cpu_differentiable_reference_v1 import','from high_precision_cpu_reference_v1 import')
anchor='from high_precision_cpu_reference_v1 import FunctionalCPUReference,independent_total_loss'
s=s.replace(anchor,anchor+'\nfrom compact_norm_task_model_v3 import HighPrecisionTaskUNet3D as CheckpointedTaskUNet3D,stable_production_total_loss\nfrom audited_saved_cpu_v1 import CpuSavedTensorAudit\nfrom resource_guard_v1 import guard as shared_stage_guard')
s=s.replace("out=HERE/'gin19_real_graph_attempt02'", "out=STAGE/'compact19_real_qualification_attempt01'")
start=s.index('        v=resource_guard();size=');end=s.index('        if journal.exists():',start)
s=s[:start]+"        v=shared_stage_guard(started,WALL);assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<1800000\n        assert torch.get_num_threads()==torch.get_num_interop_threads()==1\n"+s[end:]
s=s.replace("verifiedp=HERE/'gin_cpu_reference_verification_attempt01/receipt.json'", "verifiedp=ADAPT/'compact_norm_fullpatch_independent_attempt03/receipt.json'")
s=s.replace("verified['all_two_steps54_parameters162_optimizer_fields_strict_passed']", "verified['original_fullpatch_two_synthetic_steps_passed']")
anchor="        cases=development_cases();"
s=s.replace(anchor,"        fullreal=read(ROOT/'full_certified_schedule_2026_10_09/full_real_terminal_audit_attempt01/receipt.json');audit=read(HERE/'independent_round52_audit_attempt01/receipt.json');assert fullreal['complete'] and audit['complete'] and not fullreal['errors'] and not audit['errors']\n"+anchor,1)
s=s.replace("HERE/'GIN19_REAL_EXECUTION_PROTOCOL_V2.md'", "STAGE/'COMPACT19_REAL_QUALIFICATION_PROTOCOL_V1.md'")
s=s.replace("HERE/'gin_cpu_differentiable_reference_v1.py'", "HERE/'high_precision_cpu_reference_v1.py'")
anchor="        sources.update((HERE/'qualify_gin19_real_graph_v1.py'"
assert anchor in s
line="        sources.update((HERE/'qualify_gin19_real_graph_v1.py',HERE/'gin19_real_graph_attempt01/receipt.json',HERE/'prepare_gin19_real_graph_v2.py'))"
assert line in s;s=s.replace(line,line+"\n        sources.update((ADAPT/'compact_norm_task_model_v1.py',ADAPT/'compact_norm_task_model_v2.py',ADAPT/'compact_norm_task_model_v3.py',ADAPT/'compact_double_norm_v1.py',ADAPT/'audited_saved_cpu_v1.py',HERE/'independent_round52_audit_attempt01/receipt.json',ROOT/'full_certified_schedule_2026_10_09/full_real_terminal_audit_attempt01/receipt.json',HERE/'stable_reduction_task_model_v1.py'))")
s=s.replace("torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;r['status']", "torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.use_deterministic_algorithms(True);r['status']")
old="                            context=torch.autograd.graph.save_on_cpu(pin_memory=False) if device!='cpu' else __import__('contextlib').nullcontext()"
new="                            save_audit=CpuSavedTensorAudit(array_sha,guard) if device!='cpu' else None\n                            context=save_audit.context() if save_audit is not None else __import__('contextlib').nullcontext()"
assert old in s;s=s.replace(old,new)
old="                                else:\n                                    final=torch.stack([v[0] for v in outputs]);value=loss(outputs[0],label)+.1*mean_target_kl(torch.cat((torch.zeros_like(final),final),2))"
assert old in s;s=s.replace(old,"                                else:value=stable_production_total_loss(outputs,label)")
anchor="                            q['steps'].append({k:v for k,v in data.items() if k!='independent_NumPy_AdamW_checks'})"
assert anchor in s;s=s.replace(anchor,"                            if save_audit is not None:\n                                data['audited_CPU_saving']=dict(packed_tensors=len(save_audit.records),unpack_events=save_audit.unpacks,CPU_saved_peak_logical_bytes=save_audit.peak_bytes,all_actual_unpacks_bitwise_verified=True,raw_tensor_payloads_persisted=False);assert save_audit.records and save_audit.unpacks\n"+anchor)
s=s.replace("            blob=", "            blob=")
s=s.replace("                    probability_gradient_parameter_optimizer_gate=3e-6,confirmation_opened=False,", "                    probability_gradient_parameter_optimizer_gate=3e-6,binary_disagreements_gate=0,graph_precision='FP64',parameter_and_optimizer_state_precision='FP32',confirmation_opened=False,")
s=s.replace("           publication_claim_confirmed=False,goal_status='active')", "           original_FP32_production_qualified=False,separate_numeric_branch=True,publication_claim_confirmed=False,goal_status='active')")
s=s.replace("del inputs,label,outputs,value,tree,buf,restored,params,moments,gradients,probs;gc.collect();", "del inputs,label,outputs,value,tree,buf,restored,params,moments,gradients,probs,context,save_audit;gc.collect();")
ast.parse(s);p=STAGE/'qualify_compact19_real_graph_v1.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
