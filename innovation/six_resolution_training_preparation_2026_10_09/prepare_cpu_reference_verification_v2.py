"""Create new two-step synthetic whole-model check, preserving v1 and its results."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
src=(HERE/'verify_gin_cpu_reference_v1.py').read_text(encoding='utf-8')
def replace(a,b):
    global src
    assert src.count(a)==1,(a,src.count(a));src=src.replace(a,b)
replace('from gin_cpu_differentiable_reference_v1 import','from gin_cpu_differentiable_reference_v2 import')
replace("out=HERE/'gin_cpu_reference_verification_attempt01'","out=HERE/'gin_cpu_reference_verification_attempt02'")
replace("HERE/'GIN_CPU_REFERENCE_VERIFICATION_PROTOCOL_V1.md'","HERE/'GIN_HIGH_PRECISION_CPU_REFERENCE_PROTOCOL_V2.md',HERE/'stable_norm_math_v2_attempt01/receipt.json',HERE/'prepare_cpu_reference_verification_v2.py'")
replace("HERE/'gin_cpu_differentiable_reference_v1.py'","HERE/'gin_cpu_differentiable_reference_v2.py'")
replace("        r['resources_before']=guard();r['source_bindings']=","        r['resources_before']=guard();assert __import__('json').loads((HERE/'stable_norm_math_v2_attempt01/receipt.json').read_text(encoding='utf-8'))['complete'];r['reference_precision']='FP32 operators with explicit FP64 norm reductions';r['source_bindings']=")
replace("        assert v['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000","        paper=ROOT/'gin_accepted_primary_followup_2026_10_09';ps=sum(p.stat().st_size for p in paper.rglob('*') if p.is_file());assert ps<6_000_000\n        assert v['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)-(6_000_000-ps)>=8_000_000_000")
target=HERE/'verify_gin_cpu_reference_v2.py';assert not target.exists();compile(src,str(target),'exec');target.write_text(src,encoding='utf-8')
print({'complete':True,'new_bytes':target.stat().st_size})
