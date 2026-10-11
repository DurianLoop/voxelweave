"""Preserve first failure and complete six remaining checks after DOI repair."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SESSION_ARCHIVE_VERIFICATION_ORDER_RISK_AND_PHASE_2026-10-03_attempt_02.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');assert not OUT.exists();first=ROOT/'SESSION_ARCHIVE_VERIFICATION_ORDER_RISK_AND_PHASE_2026-10-03.json';old=json.loads(first.read_text(encoding='utf-8'))
 assert old['status']=='failed' and len(old['records'])==29 and all(x['returncode']==0 for x in old['records'][:28]) and old['records'][-1]['parsed']['errors']==['Primary DOI identity differs']
 report=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),first_audit=first.name,first_audit_sha256=sha(first),previous_historical_checks_passed=28,reason='Fix DOI case-sensitive static comparison; scientific inputs unchanged. Complete current two stages and final global evidence/link checks.',scope='6 remaining static write/read-only checks',status='in_progress',all_checks_passed=False,scientific_goal_complete=False,records=[])
 def save():OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 save()
 for script in ('literature/verify_order_risk_and_phase_stage_archive_2026_10_03.py','literature/verify_task_normalization_context_stage_archive_2026_10_03.py','verify_archive.py'):
  for write in (True,False):
   cmd=[sys.executable,'-X','utf8','-B',str(ROOT/script)]+(['--write'] if write else []);start=datetime.now(timezone.utc).isoformat();run=subprocess.run(cmd,cwd=ROOT.parent,capture_output=True,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));stdout=run.stdout.decode('utf-8',errors='replace');stderr=run.stderr.decode('utf-8',errors='replace')
   try:parsed=json.loads(stdout)
   except json.JSONDecodeError:parsed=None
   report['records'].append(dict(script=script,script_sha256=sha(ROOT/script),write=write,command=cmd,started_utc=start,finished_utc=datetime.now(timezone.utc).isoformat(),returncode=run.returncode,stdout=stdout,stderr=stderr,parsed=parsed));save();print(json.dumps(dict(script=script,write=write,returncode=run.returncode,errors=parsed.get('errors') if isinstance(parsed,dict) else 'unparsed')),flush=True)
   if run.returncode:report.update(status='failed');save();return run.returncode
 report.update(status='complete',all_checks_passed=True,finished_utc=datetime.now(timezone.utc).isoformat());save();return 0
if __name__=='__main__':raise SystemExit(main())
