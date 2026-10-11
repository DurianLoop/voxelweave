"""Refresh static historical manifests after new current entrypoints; no inference."""
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from verify_mc_rc_anchor_all_archives_2026_10_03 import SCRIPTS
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SESSION_ARCHIVE_VERIFICATION_COMPLETE_COHORT_2026-10-03.json'

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if OUT.exists(): raise FileExistsError('Retain actual earlier audit; no overwrite')
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),status='in_progress',all_checks_passed=False,scientific_goal_complete=False,records=[])
    def save(): OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    for script in [*SCRIPTS[:-1],'literature/verify_mc_rc_predicted_region_stage_archive.py','literature/verify_native_anchor_stage_archive_2026_10_03.py','literature/verify_complete_cohort_stage_archive_2026_10_03.py',SCRIPTS[-1]]:
        for write in (True,False):
            command=[sys.executable,'-B',str(ROOT/script)]+(['--write'] if write else []);run=subprocess.run(command,cwd=ROOT.parent,capture_output=True,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));stdout,stderr=run.stdout.decode('utf-8',errors='replace'),run.stderr.decode('utf-8',errors='replace')
            try: parsed=json.loads(stdout)
            except json.JSONDecodeError: parsed=None
            report['records'].append(dict(script=script,write=write,command=command,returncode=run.returncode,stdout=stdout,stderr=stderr,parsed=parsed,finished_utc=datetime.now(timezone.utc).isoformat()));save();print(json.dumps(dict(script=script,write=write,returncode=run.returncode,errors=parsed.get('errors') if isinstance(parsed,dict) else 'unparsed')),flush=True)
            if run.returncode: report['status']='failed';save();return run.returncode
    report.update(status='complete',all_checks_passed=True,finished_utc=datetime.now(timezone.utc).isoformat());save();return 0

if __name__=='__main__': raise SystemExit(main())
