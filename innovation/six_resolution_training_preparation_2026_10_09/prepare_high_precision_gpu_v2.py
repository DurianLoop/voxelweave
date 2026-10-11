from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'verify_high_precision_model_gpu_v1.py').read_text(encoding='utf-8')
s=s.replace('high_precision_model_gpu_attempt01','high_precision_model_gpu_attempt02').replace('HIGH_PRECISION_GPU_SYNTHETIC_PROTOCOL_V1.md','HIGH_PRECISION_GPU_SYNTHETIC_PROTOCOL_V2.md')
old=" def save():dump(out/'receipt.json',r)"
new=" def save():\n  temp=out/'receipt.json.tmp';temp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\\n',encoding='utf-8');temp.replace(out/'receipt.json')"
assert old in s;s=s.replace(old,new)
p=HERE/'verify_high_precision_model_gpu_v2.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
