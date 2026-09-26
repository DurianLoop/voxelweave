"""Ensure historical table data and unreplaced figure assets remain reachable."""
from pathlib import Path
import re,hashlib,json
P=Path(__file__).resolve().parents[1]
def closure(root):
 visited=set();texts=[];figures={}
 def visit(path):
  if path in visited:return
  visited.add(path);text=path.read_text(encoding='utf-8');texts.append(text)
  for child in re.findall(r'\\input\{([^}]+)\}',text):
   p=root/(child if Path(child).suffix else child+'.tex')
   if p.exists():visit(p)
  for child in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',text):
   p=root/child
   candidates=[base/child for base in [root,root/'figures']]
   p=next((q for q in candidates if q.is_file()),None) if Path(child).suffix else next((q.with_suffix(s) for q in candidates for s in ['.pdf','.png','.jpg'] if q.with_suffix(s).exists()),None)
   assert p is not None,child
   figures[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
 for name in ['main.tex','supplement.tex']:visit(root/name)
 tables=[re.sub(r'\s+','',t) for s in texts for t in re.findall(r'\\begin\{tabular\}(.*?)\\end\{tabular\}',s,re.S)]
 return tables,figures
a,af=closure(P/'original_snapshot/manuscript');b,bf=closure(P/'revised_manuscript');missing=[hashlib.sha256(t.encode()).hexdigest() for t in a if t not in b]
regenerated={'final_fig1_physical_anchors.pdf','final_fig2_original_control.pdf','final_fig3_acquired_influence.pdf','final_fig4_cross_architecture.pdf','final_proposition_validation.pdf'}
fig_missing=[name for name,h in af.items() if name not in regenerated and bf.get(name)!=h]
r=dict(accepted_reachable_table_bodies=len(a),revised_reachable_table_bodies=len(b),missing_accepted_tables=missing,unchanged_historical_figures=sum(n not in regenerated for n in af),missing_or_changed_historical_figures=fig_missing,status='PASS' if not missing and not fig_missing else 'FAIL')
(P/'outputs/historical_retention.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(r)
assert r['status']=='PASS','Qualified historical evidence no longer reachable'
