"""Keep failed auditor v1 immutable; normalize bold mathematical Greek labels in v2."""
from pathlib import Path
from resource_guard_v1 import HERE,guard
guard();source=HERE/'audit_primary_and_cpu_v1.py';target=HERE/'audit_primary_and_cpu_v2.py';assert not target.exists()
s=source.read_text(encoding='utf-8')
old="gamma=next(row for label,row in g.items() if 'γ' in label)"
new="gamma=next(row for label,row in g.items() if 'γ' in __import__('unicodedata').normalize('NFKC',label))"
assert s.count(old)==1 and s.count("independent_primary_cpu_audit_attempt01")==1
s=s.replace(old,new).replace('independent_primary_cpu_audit_attempt01','independent_primary_cpu_audit_attempt02')
target.write_text(s,encoding='utf-8');print(str(target),len(s.encode('utf-8')))
