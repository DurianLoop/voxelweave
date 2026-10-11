"""Verify prior immutable bytes once; do not reinterpret old observations of then-live files."""
from pathlib import Path
from archive_completed_stage_v2 import source
HERE=Path(__file__).resolve().parent
replacements=[
 ("APPEND_INDEX_V2.json","APPEND_INDEX_V3.json"),
 ("APPEND_PROOF_V2.json","APPEND_PROOF_V3.json"),
 ("scanned.add(p)","scanned.add(p)\n            if p.relative_to(ROOT).as_posix() in existing:continue  # Already immutable-byte-verified; historical observations keep their original time scope."),
 ("former_original_rolling_training_files_now_frozen_after_actual_exit=True,", "prior5535_documents_byte_verified_without_reinterpreting_historical_observations=True,former_original_rolling_training_files_now_frozen_after_actual_exit=True,")
]
for old,new in replacements:
 assert source.count(old)==1,old
 source=source.replace(old,new)
if __name__=='__main__':exec(compile(source,str(HERE/'archive_completed_stage.py'),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
