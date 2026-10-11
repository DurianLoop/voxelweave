"""Prepare the independent terminal auditor for the actual recorded session-key schema."""
import sys,ast,difflib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard
resource_guard();session=read(HERE/'ACTUAL_FULL_REAL_PIPELINE_SESSION.json')
assert session['observed_unified_exec_session']==session['session_id']==44317 and not session['terminal_observed']
src=HERE/'audit_full_real_terminal.py';h=sha(src);old=src.read_text(encoding='utf-8')
assert old.count("['actual_unified_exec_session']")==1
new=old.replace("['actual_unified_exec_session']","['observed_unified_exec_session']");ast.parse(new)
dst=HERE/'audit_full_real_terminal_v2.py';assert not dst.exists();dst.write_text(new,encoding='utf-8')
patch=HERE/'AUDITOR_SESSION_KEY_V2_DIFF.patch';assert not patch.exists();patch.write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=src.name,tofile=dst.name)),encoding='utf-8')
assert sha(src)==h
r=dict(complete=True,errors=[],syntax_parsed=True,executed=False,qualification_passed=False,original_auditor_unchanged=True,
    source_bindings=[entry(p) for p in [Path(__file__),src,dst,patch,HERE/'AUDITOR_SESSION_KEY_ADDENDUM.md',HERE/'ACTUAL_FULL_REAL_PIPELINE_SESSION.json']])
dump(HERE/'AUDITOR_SESSION_KEY_V2_PREPARATION.json',r);print(json.dumps(dict(complete=True,original_auditor_unchanged=True,executed=False)))
