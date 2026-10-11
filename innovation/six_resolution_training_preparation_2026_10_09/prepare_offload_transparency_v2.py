"""Preserve failed v1; restore authorized CUDA visibility after inherited CPU imports."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
old=HERE/'qualify_three_view_offload_transparency_v1.py'
before=hashlib.sha256(old.read_bytes()).hexdigest()
failure=json.loads((HERE/'three_view_offload_transparency_attempt01/receipt.json').read_text('utf-8'))
assert not failure['complete'] and failure['synthetic_GPU_optimizer_updates']==0 and not failure['branches']
assert 'torch.cuda.is_available()' in failure['traceback']
text=old.read_text('utf-8')
text=text.replace("three_view_offload_transparency_attempt01","three_view_offload_transparency_attempt02")
text=text.replace("THREE_VIEW_OFFLOAD_TRANSPARENCY_PROTOCOL_V1.md","THREE_VIEW_OFFLOAD_TRANSPARENCY_PROTOCOL_V2.md")
text=text.replace("def main():\n    torch.set_num_threads", "def main():\n    os.environ['CUDA_VISIBLE_DEVICES']='0'\n    torch.set_num_threads")
text=text.replace("        torch.cuda._lazy_init=original_cuda_initializer; assert torch.cuda.is_available()",
                  "        os.environ['CUDA_VISIBLE_DEVICES']='0'\n        torch.cuda._lazy_init=original_cuda_initializer; assert torch.cuda.is_available()")
text=text.replace("        torch.manual_seed(20261009); base=CheckpointedTaskUNet3D()",
                  "        r['source_bindings'].extend(entry(p) for p in (HERE/'qualify_three_view_offload_transparency_v1.py',HERE/'three_view_offload_transparency_attempt01/receipt.json',HERE/'prepare_offload_transparency_v2.py'))\n        torch.manual_seed(20261009); base=CheckpointedTaskUNet3D()")
new=HERE/'qualify_three_view_offload_transparency_v2.py'
with new.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
assert hashlib.sha256(old.read_bytes()).hexdigest()==before
print(json.dumps(dict(complete=True,v1_unchanged_sha256=before,v2_file=new.name,v2_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),v1_updates=0)))
