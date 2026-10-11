"""Preserve pre-launch v1 size failure; compact duplicate metadata without changing scope."""
import json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;old=HERE/'qualify_gin19_real_graph_v1.py'
before=hashlib.sha256(old.read_bytes()).hexdigest();q=json.loads((HERE/'gin19_real_graph_attempt01/receipt.json').read_text('utf-8'))
assert not q['complete'] and q['GPU_optimizer_updates']==q['CPU_reference_optimizer_updates']==q['MRI_arrays_loaded']==q['GT_arrays_loaded']==0
assert '250_000' in q['traceback']
text=old.read_text('utf-8').replace('gin19_real_graph_attempt01','gin19_real_graph_attempt02').replace('GIN19_REAL_EXECUTION_PROTOCOL_V1.md','GIN19_REAL_EXECUTION_PROTOCOL_V2.md')
text=text.replace("blob=json.dumps(frozen,ensure_ascii=False,indent=2)+'\\n';assert len(blob.encode())<250_000",
                  "blob=json.dumps(frozen,ensure_ascii=False,separators=(',',':'))+'\\n';assert len(blob.encode())<250_000 and json.loads(blob)==frozen")
text=text.replace("        for b in oldcfg['source_bindings']:sources.add(bind(b))",
                  "        sources.update((HERE/'qualify_gin19_real_graph_v1.py',HERE/'gin19_real_graph_attempt01/receipt.json',HERE/'prepare_gin19_real_graph_v2.py'))\n        for b in oldcfg['source_bindings']:sources.add(bind(b))")
text=text.replace("                            q['steps'].append(data);record(dict(type='actual_two_step_optimizer',case=selected['case'],kind=kind,device=device,**data))",
                  "                            q['steps'].append({k:v for k,v in data.items() if k!='independent_NumPy_AdamW_checks'})\n                            q['steps'][-1]['all54_NumPy_checks_logged_in_journal']=True\n                            record(dict(type='actual_two_step_optimizer',case=selected['case'],kind=kind,device=device,**data))")
text=text.replace("                        r['step_comparisons'].append(comparison);record(dict(type='CPU_GPU_strict_comparison',**comparison));save()",
                  "                        r['step_comparisons'].append({k:v for k,v in comparison.items() if k!='all54_parameter_comparisons'})\n                        r['step_comparisons'][-1]['worst_parameter_rows']=sorted(checks,key=lambda v:v['parameter_error'],reverse=True)[:3]\n                        r['step_comparisons'][-1]['all54_comparison_rows_logged_in_journal']=True\n                        record(dict(type='CPU_GPU_strict_comparison',**comparison));save()")
assert text!=old.read_text('utf-8');compile(text,'qualify_gin19_real_graph_v2.py','exec')
new=HERE/'qualify_gin19_real_graph_v2.py'
with new.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
assert hashlib.sha256(old.read_bytes()).hexdigest()==before
print(json.dumps(dict(complete=True,v1_unchanged_sha256=before,v2_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),medical_arrays_or_updates_v1=0)))
