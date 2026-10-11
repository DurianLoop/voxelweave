"""Refresh existing static stages and this stage; log every actual check."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'SESSION_ARCHIVE_VERIFICATION_MC_RC_ANCHOR_2026-10-03.json'
SCRIPTS = ['literature/verify_author_ensure_mslesseg_stage_archive.py','literature/verify_task_throughplane_stage_archive.py','literature/verify_risk_action_stage_archive.py','literature/verify_local_action_and_operator_archive.py','literature/verify_action_crossmoda_stage_archive.py','literature/verify_mc_rc_native_stage_archive.py','literature/verify_mc_rc_action_batch_stage_archive.py','literature/verify_mc_rc_constrained_stage_archive.py','literature/verify_mc_rc_visible_stage_archive.py','literature/verify_mc_rc_anchor_stage_archive.py','verify_archive.py']
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    previous = None
    if OUT.exists():
        n = len(list(ROOT.glob('SESSION_ARCHIVE_VERIFICATION_MC_RC_ANCHOR_2026-10-03_attempt_*.json')))+1
        previous = OUT.with_name(OUT.stem + '_attempt_%02d.json'%n)
        previous.write_bytes(OUT.read_bytes())
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),prior_record=previous.name if previous else None,status='checks_in_progress',all_checks_passed=False,scientific_goal_complete=False,scope='22 static write/read-only checks; live queue excluded',records=[])
    def save():
        OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    for script in SCRIPTS:
        for write in (True,False):
            cmd = [sys.executable,'-B',str(ROOT/script)] + (['--write'] if write else [])
            started = datetime.now(timezone.utc).isoformat()
            run = subprocess.run(cmd,cwd=ROOT.parent,capture_output=True,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            stdout, stderr = run.stdout.decode('utf-8',errors='replace'),run.stderr.decode('utf-8',errors='replace')
            try:
                parsed = json.loads(stdout)
            except json.JSONDecodeError:
                parsed = None
            report['records'].append(dict(script=script,command=cmd,write=write,script_sha256=sha(ROOT/script),started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),returncode=run.returncode,stdout=stdout,stderr=stderr,parsed=parsed))
            save()
            print(json.dumps(dict(script=script,write=write,returncode=run.returncode,errors=parsed.get('errors') if isinstance(parsed,dict) else 'unparsed')),flush=True)
            if run.returncode:
                report['status'] = 'failed'
                save()
                return run.returncode
    report.update(status='complete',all_checks_passed=True,finished_utc=datetime.now(timezone.utc).isoformat())
    save()
    return 0
if __name__=='__main__':
    raise SystemExit(main())
