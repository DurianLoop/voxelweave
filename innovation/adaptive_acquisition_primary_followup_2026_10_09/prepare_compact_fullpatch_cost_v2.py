"""Fix generator-local destination name; preserve failed v1 source."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'prepare_compact_fullpatch_cost_v1.py').read_text(encoding='utf-8')
assert s.count("p=STAGE/'probe_compact_norm_fullpatch_cost_v1.py'")==1
s=s.replace("p=STAGE/'probe_compact_norm_fullpatch_cost_v1.py'", "p=HERE/'probe_compact_norm_fullpatch_cost_v1.py'")
exec(compile(s,str(HERE/'prepare_compact_fullpatch_cost_v1.py')+'-separate-v2','exec'))
