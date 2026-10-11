"""Bind actual evidence recorder exit; this is not a formal training exit receipt."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    names=['SESSION_OBSERVED_EXITS_DIRECT_OBSERVED_2026-10-07.json','SESSION_EXECUTION_LEDGER_DIRECT_OBSERVED_2026-10-07.json',
           'SESSION_EXECUTION_PROGRESS_DIRECT_OBSERVED_2026-10-07.json','literature/source_cache/direct_observed_primary_2026-10-07/reading_provenance.json']
    r=dict(observed_tool_chunk='086f28',observed_tool_exit=0,full_training_observed_tool_exit=None,
           own_live_training_session=99542,publication_claim_confirmed=False,
           outputs=[dict(path=n,sha256=hashlib.sha256((ROOT/n).read_bytes()).hexdigest()) for n in names])
    with (ROOT/'SESSION_OBSERVED_EXITS_DIRECT_OBSERVED_EVIDENCE_2026-10-07.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2)
    print(json.dumps(dict(complete=True,outputs=len(names),recorder_exit=0)));return 0
if __name__=='__main__':raise SystemExit(main())
