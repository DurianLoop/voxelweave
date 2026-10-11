"""Prepare new immutable checkpointed-graph attempt; retain original memory failure."""
import sys,ast,difflib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,sha,dump,resource_guard
resource_guard();qual=read(HERE/'checkpointed_cpu_qualification_attempt01/receipt.json');assert qual['complete'] and qual['all_outputs_loss_and_parameter_gradients_bitwise_equal']
failed=read(HERE/'ACTUAL_GPU_SMOKE_V2_FAILED_TERMINAL_TOOL.json');assert failed['exit_code']==1 and 'session_id' not in failed
src=HERE/'run_gpu_graph_smoke_v2.py';before=sha(src);old=src.read_text(encoding='utf-8');new=old
pairs=[("out=HERE/'attempt02'","out=HERE/'attempt03'"),
("PATCH=(64,128,128);KINDS=","from checkpointed_model import CheckpointedTaskUNet3D\nPATCH=(64,128,128);KINDS="),
("        training_updates=0,GPU_forwards=0,","        activation_checkpointing=True,backward_includes_recomputation=True,training_updates=0,GPU_forwards=0,"),
("sources={Path(__file__),HERE/'PROTOCOL.md',HERE/'V2_RUNTIME_REPAIR.md',HERE/'V2_PREPARATION.json',rp,jp,tp,QPATH,configpath,",
 "sources={Path(__file__),HERE/'PROTOCOL.md',HERE/'V2_RUNTIME_REPAIR.md',HERE/'V2_PREPARATION.json',HERE/'CHECKPOINTED_GRAPH_PROTOCOL.md',HERE/'V3_PREPARATION.json',HERE/'checkpointed_cpu_qualification_attempt01/receipt.json',rp,jp,tp,QPATH,configpath,"),
("model=TaskUNet3D();model.load_state_dict(cp['state_dict'])","model=CheckpointedTaskUNet3D();model.load_state_dict(cp['state_dict'])")]
for a,b in pairs:assert new.count(a)==1;new=new.replace(a,b)
ast.parse(new);dest=HERE/'run_gpu_graph_smoke_v3.py';assert not dest.exists();dest.write_text(new,encoding='utf-8')
diff=HERE/'V3_EXACT_DIFF.patch';assert not diff.exists();diff.write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=src.name,tofile=dest.name)),encoding='utf-8')
assert sha(src)==before
dump(HERE/'V3_PREPARATION.json',dict(complete=True,AST_parsed=True,actual_GPU_execution=False,original_v2_unchanged=True,changes=5,
    source_bindings=[entry(p) for p in [Path(__file__),src,dest,diff,HERE/'CHECKPOINTED_GRAPH_PROTOCOL.md',HERE/'checkpointed_model.py',HERE/'checkpointed_cpu_qualification_attempt01/receipt.json',HERE/'ACTUAL_GPU_SMOKE_V2_FAILED_TERMINAL_TOOL.json']]))
print(json.dumps(dict(complete=True,AST_parsed=True,original_v2_unchanged=True,actual_GPU_execution=False)))
