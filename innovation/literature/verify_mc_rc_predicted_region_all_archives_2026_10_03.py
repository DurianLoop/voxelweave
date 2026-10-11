"""Refresh and record existing stages plus new completed evidence once."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from verify_mc_rc_anchor_all_archives_2026_10_03 import SCRIPTS
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SESSION_ARCHIVE_VERIFICATION_MC_RC_PREDICTED_REGION_2026-10-03.json'
def main():
 sys.stdout.reconfigure(encoding='utf-8');prior=None
 if OUT.exists():
  number=len(list(ROOT.glob('SESSION_ARCHIVE_VERIFICATION_MC_RC_PREDICTED_REGION_2026-10-03_attempt_*.json')))+1;prior=OUT.with_name(OUT.stem+'_attempt_%02d.json'%number);prior.write_bytes(OUT.read_bytes())
 report=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),prior_record=prior.name if prior else None,scope='24 static write/read-only checks; live model/main-cohort outputs excluded',status='checks_in_progress',all_checks_passed=False,scientific_goal_complete=False,records=[])
 def save(): OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 save()
 for script in [*SCRIPTS[:-1],'literature/verify_mc_rc_predicted_region_stage_archive.py',SCRIPTS[-1]]:
  for write in (True,False):
   command=[sys.executable,'-B',str(ROOT/script)]+(['--write'] if write else []);run=subprocess.run(command,cwd=ROOT.parent,capture_output=True,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));stdout,stderr=run.stdout.decode('utf-8',errors='replace'),run.stderr.decode('utf-8',errors='replace')
   try: parsed=json.loads(stdout)
   except json.JSONDecodeError: parsed=None
   record=dict(script=script,command=command,write=write,finished_utc=datetime.now(timezone.utc).isoformat(),returncode=run.returncode,stdout=stdout,stderr=stderr,parsed=parsed);report['records'].append(record);save();print(json.dumps(dict(script=script,write=write,returncode=run.returncode,errors=parsed.get('errors') if isinstance(parsed,dict) else 'unparsed')),flush=True)
   if run.returncode: report['status']='failed';save();return run.returncode
 report.update(status='complete',all_checks_passed=True,finished_utc=datetime.now(timezone.utc).isoformat());save();return 0
if __name__=='__main__': raise SystemExit(main())
