"""Sync historical static entrypoint hashes after this stage's new entrypoints."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from verify_mc_rc_anchor_all_archives_2026_10_03 import SCRIPTS
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SESSION_ARCHIVE_VERIFICATION_RESAMPLING_ORDER_2026-10-03.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8')
 if OUT.exists(): raise FileExistsError('Retain actual first archive audit')
 report=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),reason='README and EXPERIMENT_QUEUE were updated; refresh their bindings in historical static manifests. No scientific or neural computation repeated.',scope='30 static write/read-only checks; mutable post-task outputs excluded',status='in_progress',all_checks_passed=False,scientific_goal_complete=False,records=[])
 def save(): OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 save()
 scripts=[*SCRIPTS[:-1],'literature/verify_mc_rc_predicted_region_stage_archive.py','literature/verify_native_anchor_stage_archive_2026_10_03.py','literature/verify_complete_cohort_stage_archive_2026_10_03.py','literature/verify_resampling_order_stage_archive_2026_10_03.py',SCRIPTS[-1]]
 for script in scripts:
  for write in (True,False):
   cmd=[sys.executable,'-X','utf8','-B',str(ROOT/script)]+(['--write'] if write else []);start=datetime.now(timezone.utc).isoformat();run=subprocess.run(cmd,cwd=ROOT.parent,capture_output=True,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));stdout=run.stdout.decode('utf-8',errors='replace');stderr=run.stderr.decode('utf-8',errors='replace')
   try: parsed=json.loads(stdout)
   except json.JSONDecodeError: parsed=None
   report['records'].append(dict(script=script,script_sha256=sha(ROOT/script),write=write,command=cmd,started_utc=start,finished_utc=datetime.now(timezone.utc).isoformat(),returncode=run.returncode,stdout=stdout,stderr=stderr,parsed=parsed));save();print(json.dumps(dict(script=script,write=write,returncode=run.returncode,errors=parsed.get('errors') if isinstance(parsed,dict) else 'unparsed')),flush=True)
   if run.returncode: report.update(status='failed');save();return run.returncode
 report.update(status='complete',all_checks_passed=True,finished_utc=datetime.now(timezone.utc).isoformat());save();return 0
if __name__=='__main__': raise SystemExit(main())
