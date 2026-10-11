"""Exact output-assignment matching; preserve MoEDiff's already-frozen V2 identity."""
from pathlib import Path
from archive_completed_stage_v2 import source
HERE=Path(__file__).resolve().parent
replacements=[
 ("indexpath=HERE/'APPEND_INDEX_V2.json';proofpath=HERE/'APPEND_PROOF_V2.json'", "indexpath=HERE/'APPEND_INDEX_V4.json';proofpath=HERE/'APPEND_PROOF_V4.json'"),
 ("scanned.add(p)","scanned.add(p)\n            if p.relative_to(ROOT).as_posix() in existing:continue  # Already byte-verified; retain historical time scope."),
 ("live=pilot/'attempt01';assert not any(p.is_relative_to(live) for p in sources)", "live=pilot/'evaluation_attempt01';assert not any(p.is_relative_to(live) for p in sources)\n    pilot_exit=read(pilot/'ACTUAL_PILOT_EXIT.json');assert pilot_exit['observed_tool_exit']==0 and pilot_exit['result_sha256']==sha(pilot/'attempt01/receipt.json')\n    sources.update(p for p in (pilot/'attempt01').rglob('*') if p.is_file())"),
 ("former_original_rolling_training_files_now_frozen_after_actual_exit=True,", "prior5535_documents_byte_verified_without_reinterpreting_historical_observations=True,former_original_rolling_training_files_now_frozen_after_actual_exit=True,")
]
for old,new in replacements:
 assert source.count(old)==1,old
 source=source.replace(old,new)
if __name__=='__main__':exec(compile(source,str(HERE/'archive_completed_stage.py'),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
