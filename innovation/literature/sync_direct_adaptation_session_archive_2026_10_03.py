"""Update final archive after adding last public message; no scientific rerun."""
import json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
path=ROOT/'SESSION_ARCHIVE_FINAL_SYNC_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.json';assert not path.exists()
r=dict(created_utc=datetime.now(timezone.utc).isoformat(),scope='Final sync after recording all six public updates; no experiments rerun',complete=False,errors=[],checks=[],scientific_confirmation_patients=0,publication_claim_confirmed=False)
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for script,args in [('literature/verify_direct_adaptation_and_identity_stage_2026_10_03.py',['--write']),('literature/verify_direct_adaptation_and_identity_stage_2026_10_03.py',[]),('verify_archive.py',['--write']),('verify_archive.py',[])]:
    proc=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/script)]+args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    entry=dict(script=script,args=args,exit_code=proc.returncode,output=proc.stdout.decode('utf-8',errors='replace'));r['checks'].append(entry);print(json.dumps(entry,ensure_ascii=False),flush=True)
    if proc.returncode:r['errors'].append(script+' failed');break
r['complete']=len(r['checks'])==4 and not r['errors'];r['finished_utc']=datetime.now(timezone.utc).isoformat()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raise SystemExit(int(not r['complete']))
