"""Copy CPU-only independent readers; redirect every output into this patch."""
from pathlib import Path
P=Path(__file__).resolve().parents[1];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING'
names=['common.py','audit_statistics.py','reproduce_arrays.py','reproduce_new.py','reproduce_main.py','build.py','render.py']
for name in names:
 text=(B/'scripts'/name).read_text(encoding='utf-8')
 if name=='common.py':
  text=text.replace("P=Path(__file__).resolve().parents[1];PAPER=P.parent;ROOT=PAPER.parents[1];OUT=P/'outputs'","PATCH=Path(__file__).resolve().parents[1];P=PATCH.parent/'FINAL_SCIENTIFIC_STRENGTHENING';PAPER=P.parent;ROOT=PAPER.parents[1];BASEOUT=P/'outputs';OUT=PATCH/'outputs'")
 if name in ['reproduce_arrays.py','reproduce_new.py']:
  for arraydir in ['phase_arrays','acquired_responses','proposition_arrays','legacy_control_arrays','legacy_influence_arrays']:text=text.replace("OUT/'"+arraydir+"'","BASEOUT/'"+arraydir+"'")
  for f in ['acquired_only_summary.csv','proposition_summary.csv']:text=text.replace("pd.read_csv(OUT/'"+f+"')","pd.read_csv(BASEOUT/'"+f+"')")
 if name=='reproduce_main.py':text=text.replace("(P/'REPRODUCTION_CHECK.md').write_text","(PATCH/'HISTORICAL_REPRODUCTION_CHECK.md').write_text")
 (P/'scripts'/name).write_text(text,encoding='utf-8')
print('Independent CPU readers copied with immutable input roots and separate outputs')
