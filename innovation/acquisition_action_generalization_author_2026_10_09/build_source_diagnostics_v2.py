"""Separate version after literal dictionary-key failure; preserve all failed sources."""
from pathlib import Path
import hashlib,json,difflib
HERE=Path(__file__).resolve().parent
old=HERE/'run_source_diagnostics.py';new=HERE/'run_source_diagnostics_v2.py';assert not new.exists()
before=old.read_text(encoding='utf-8');after=before
changes={"'source_diagnostics_attempt01'":"'source_diagnostics_attempt02'","gates['1.']":"gates['1.0']","gates['-1.']":"gates['-1.0']","gates['0.']":"gates['0.0']",'np.array([.9,.1],np.float64)':'np.array([.75,.25],np.float64)'}
for a,b in changes.items():assert after.count(a)==1;after=after.replace(a,b)
with new.open('x',encoding='utf-8') as f:f.write(after)
with (HERE/'SOURCE_DIAGNOSTIC_V2_DIFF.patch').open('x',encoding='utf-8') as f:f.writelines(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=old.name,tofile=new.name))
with (HERE/'SOURCE_DIAGNOSTIC_ATTEMPT01_FAILED.json').open('x',encoding='utf-8') as f:json.dump(dict(complete=False,actual_tool_chunk='76d56e',actual_tool_exit=1,error_type='KeyError',error_message='1.',
    failure_location='gates dictionary lookup',source_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),original_source_preserved=True,
    failed_attempt_not_counted_as_four_passes=True,v2_explicit_changes=changes,dyadic_probability_fixture_reason='exactly representable d2 algebra without irrelevant summation roundoff',
    publication_claim_confirmed=False,goal_status='active'),f,ensure_ascii=False,indent=2)
