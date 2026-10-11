"""Create separately versioned process-local CUDA visibility repair; preserve failed v1 bytes."""
import sys,ast,difflib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,sha,dump,resource_guard
resource_guard();failed=read(HERE/'ACTUAL_GPU_SMOKE_FAILED_TERMINAL_TOOL.json');r=read(HERE/'attempt01/receipt.json')
assert failed['exit_code']==1 and 'session_id' not in failed and not r['CUDA_initialized']
assert r['GPU_forwards']==r['GPU_backwards']==r['MRI_input_arrays_loaded']==r['model_arrays_loaded']==0
src=HERE/'run_gpu_graph_smoke.py';before=sha(src);old=src.read_text(encoding='utf-8');new=old
pairs=[("out=HERE/'attempt01'","out=HERE/'attempt02'"),
("sources={Path(__file__),HERE/'PROTOCOL.md',rp,jp,tp,QPATH,configpath,","sources={Path(__file__),HERE/'PROTOCOL.md',HERE/'V2_RUNTIME_REPAIR.md',HERE/'V2_PREPARATION.json',rp,jp,tp,QPATH,configpath,"),
("        torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()",
"        r['CUDA_VISIBLE_DEVICES_after_CPU_imports']=os.environ.get('CUDA_VISIBLE_DEVICES')\n        os.environ['CUDA_VISIBLE_DEVICES']='0'\n        r['CUDA_VISIBLE_DEVICES_at_GPU_admission']=os.environ['CUDA_VISIBLE_DEVICES']\n        r['torch_version']=str(torch.__version__);r['torch_CUDA_version']=torch.version.cuda\n        torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()")]
for a,b in pairs:assert new.count(a)==1;new=new.replace(a,b)
ast.parse(new);dest=HERE/'run_gpu_graph_smoke_v2.py';assert not dest.exists();dest.write_text(new,encoding='utf-8')
diff=HERE/'V2_EXACT_DIFF.patch';assert not diff.exists();diff.write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=src.name,tofile=dest.name)),encoding='utf-8')
assert sha(src)==before
result=dict(complete=True,AST_parsed=True,actual_GPU_execution=False,original_v1_unchanged=True,changes=3,
    sources=[entry(p) for p in [Path(__file__),src,dest,diff,HERE/'PROTOCOL.md',HERE/'V2_RUNTIME_REPAIR.md',HERE/'ACTUAL_GPU_SMOKE_FAILED_TERMINAL_TOOL.json',HERE/'attempt01/receipt.json']])
dump(HERE/'V2_PREPARATION.json',result);print(json.dumps(dict(complete=True,AST_parsed=True,original_v1_unchanged=True,actual_GPU_execution=False)))
