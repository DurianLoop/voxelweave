"""Capture dated live progress, without making mutable training JSON an immutable result."""
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    source=ROOT/'experiments/mc_rc_no_augmentation_all_development_cpu/attempt_01.json'
    raw=source.read_bytes();r=json.loads(raw.decode('utf-8'))
    output=ROOT/'literature/source_cache/no_augmentation_training_launch_observation_2026-10-03.json'
    assert not output.exists()
    record=dict(observed_utc=datetime.now(timezone.utc).isoformat(),live_session_id=4831,
        actual_poll_status='write_stdin returned session_id 4831; not process exit',
        source_file=source.relative_to(ROOT).as_posix(),source_sha256_at_observation=hashlib.sha256(raw).hexdigest(),
        source_is_mutable=True,completed_batch_sessions={'factorial':25480,'factorial_verifier':53787,'input_preflight':31096},
        completed_batch_sessions_actual_exit_codes=[0,0,0],training_state=r,
        scope='Dated observation only; do not infer completion or restart live training.',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(session=4831,complete=r['complete'],updates=r['updates_completed'],errors=r['errors'],
        first10_seconds_per_update=r.get('first10_updates_seconds_per_update'))))


if __name__=='__main__':
    main()
