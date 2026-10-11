"""Run current new-stage and global write/read checks; retain exact command outputs."""
import hashlib,json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'SESSION_ARCHIVE_VERIFICATION_STATS_SWAP_AND_SOURCE_2026-10-03.json'
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not OUT.exists()
    ledger=dict(created_utc=now(),script_sha256=sha(__file__),complete=False,errors=[],checks=[],
                scope='Current stats-swap/source stage and refreshed global evidence/link manifest. Earlier stage manifests are historical snapshots; no neural reruns.',
                gpu_used=False,user_training_processes_modified=False,publication_claim_confirmed=False,scientific_goal_complete=False)
    def save():OUT.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    jobs=[('literature/verify_stats_swap_and_source_stage_archive_2026_10_03.py',True),('literature/verify_stats_swap_and_source_stage_archive_2026_10_03.py',False),('verify_archive.py',True),('verify_archive.py',False)]
    for script,write in jobs:
        p=ROOT/script;command=[sys.executable,'-X','utf8','-B',str(p)]+(['--write'] if write else [])
        row=dict(script=script,script_sha256=sha(p),command=command,write=write,started_utc=now())
        v=subprocess.run(command,cwd=ROOT.parent,capture_output=True,text=True,encoding='utf-8',timeout=120)
        row.update(returncode=v.returncode,stdout=v.stdout,stderr=v.stderr,finished_utc=now())
        try:row['parsed']=json.loads(v.stdout)
        except json.JSONDecodeError:row['parsed']=None
        ledger['checks'].append(row)
        if v.returncode or row['parsed'] is None or row['parsed'].get('errors'):ledger['errors'].append(script+' failed')
        save();print(json.dumps(dict(script=script,write=write,returncode=v.returncode,parsed=row['parsed']),ensure_ascii=False),flush=True)
        if ledger['errors']:break
    ledger.update(complete=len(ledger['checks'])==4 and not ledger['errors'],finished_utc=now());save();return int(not ledger['complete'])
if __name__=='__main__':raise SystemExit(main())
