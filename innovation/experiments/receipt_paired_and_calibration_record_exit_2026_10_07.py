"""Bind the observed metadata recorder exit only; never invent formal training exit."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ledger=ROOT/'SESSION_EXECUTION_LEDGER_PAIRED_AND_CALIBRATION_2026-10-07.json'
    r=json.loads(ledger.read_text(encoding='utf-8'));assert r['complete'] and not r['errors']
    data=dict(record_observed_tool_chunk='3ddaae',record_observed_tool_exit=0,
        ledger_file=ledger.relative_to(ROOT).as_posix(),ledger_sha256=sha(ledger),
        progress_file='SESSION_EXECUTION_PROGRESS_PAIRED_AND_CALIBRATION_2026-10-07.json',
        progress_sha256=sha(ROOT/'SESSION_EXECUTION_PROGRESS_PAIRED_AND_CALIBRATION_2026-10-07.json'),
        formal_training_observed_tool_exit=None,own_live_training_session=99542,goal_status='active')
    with (ROOT/'SESSION_OBSERVED_EXITS_PAIRED_AND_CALIBRATION_RECORD_2026-10-07.json').open('x',encoding='utf-8') as f:
        json.dump(data,f,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,record_tool_exit=0,formal_training_tool_exit=None)));return 0
if __name__=='__main__':raise SystemExit(main())

