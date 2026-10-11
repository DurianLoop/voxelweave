"""Prepare separate fetch source while preserving previously executed three-paper fetch."""
from pathlib import Path
from resource_guard_v1 import HERE,guard
guard();s=(HERE/'fetch_primary_html_v1.py').read_text(encoding='utf-8');p=HERE/'fetch_foundation_primary_html_v1.py';assert not p.exists()
changes=[("HERE/'source_locator_attempt01/receipt.json'","HERE/'strong_task_source_locator_attempt01/receipt.json'"),
 ("selected=[('greedy','2010.16262v2'),('openmasc','2609.32343v1'),('active_fewshot','2607.22371v1')]","selected=[('brainsegfounder','2406.10395v3'),('swin_pretraining','2111.14791v2')]"),
 ("out=HERE/'primary_html_attempt01'","out=HERE/'foundation_primary_html_attempt01'"),
 ("len(records)==3","len(records)==2"),
 ("HERE/'PRIMARY_SELECTION.md'","HERE/'STRONG_TASK_FOUNDATION_SELECTION.md'")]
for old,new in changes:assert old in s,old;s=s.replace(old,new)
compile(s,str(p),'exec');p.write_text(s,encoding='utf-8');print(str(p),len(s.encode('utf-8')))
