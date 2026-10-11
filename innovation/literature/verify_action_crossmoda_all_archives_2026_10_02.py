"""Refresh README-dependent static manifests and capture final archive checks."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SESSION_ARCHIVE_VERIFICATION_ACTION_CROSSMODA_2026-10-02.json'

def main():
    sys.stdout.reconfigure(encoding='utf-8');records=[]
    # Publish the linked record before the global Markdown existence check.
    prior_record=None
    if OUT.exists():
        previous=OUT.read_bytes();attempt=len(list(ROOT.glob('SESSION_ARCHIVE_VERIFICATION_ACTION_CROSSMODA_2026-10-02_attempt_*.json')))+1
        prior_record=OUT.with_name(OUT.stem+f'_attempt_{attempt:02d}.json')
        prior_record.write_bytes(previous)
    pending={'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'static archive checks only; no scientific success assertion','all_checks_passed':False,'status':'checks_in_progress','prior_record':prior_record.name if prior_record else None}
    OUT.write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    scripts=['literature/verify_author_ensure_mslesseg_stage_archive.py','literature/verify_task_throughplane_stage_archive.py','literature/verify_risk_action_stage_archive.py','literature/verify_local_action_and_operator_archive.py','literature/verify_action_crossmoda_stage_archive.py','verify_archive.py']
    if '--current-only' in sys.argv:scripts=scripts[-2:]
    for script in scripts:
        for write in (True,False):
            command=[sys.executable,'-B',str(ROOT/script)]+(['--write'] if write else [])
            started=datetime.now(timezone.utc).isoformat()
            r=subprocess.run(command,cwd=ROOT.parent,capture_output=True,timeout=180)
            stdout=r.stdout.decode('utf-8',errors='replace');stderr=r.stderr.decode('utf-8',errors='replace')
            try:parsed=json.loads(stdout)
            except json.JSONDecodeError:parsed=None
            records.append({'script':script,'write':write,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'returncode':r.returncode,'stdout':stdout,'stderr':stderr,'parsed':parsed})
            print(json.dumps({'script':script,'write':write,'returncode':r.returncode,'errors':parsed.get('errors') if isinstance(parsed,dict) else 'unparsed','summary':{k:parsed[k] for k in ('pdfs','evidence_files','local_links_checked','files','reading_anchors') if isinstance(parsed,dict) and k in parsed}},ensure_ascii=False),flush=True)
            if r.returncode:
                result={'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'static archive checks only; no inference restart or scientific success assertion','all_checks_passed':False,'prior_record':prior_record.name if prior_record else None,'records':records}
                OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return r.returncode
    result={'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'static archive checks only; retains failed source crosswalk and live queue','all_checks_passed':True,'prior_record':prior_record.name if prior_record else None,'records':records,'scientific_goal_complete':False}
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return 0

if __name__=='__main__':raise SystemExit(main())
