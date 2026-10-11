"""Finish archive receipts and independently rehash stage files, retaining first link failure."""
import hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SUMMARY=ROOT/'SESSION_ARCHIVE_VERIFICATION_COVERAGE_AUGMENTATION_2026-10-03.json'


def write(path,record):
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    failure=ROOT/'SESSION_ARCHIVE_VERIFICATION_COVERAGE_AUGMENTATION_2026-10-03_failed_attempt_01.json'
    assert not failure.exists() and not SUMMARY.exists()
    write(failure,dict(actual_tool_exit_code=1,pdfs=29,evidence_files=2172,local_links_checked=2669,
        errors=['Broken local link in SESSION_UPDATE_COVERAGE_AUGMENTATION_2026-10-03.md: SESSION_ARCHIVE_VERIFICATION_COVERAGE_AUGMENTATION_2026-10-03.json'],
        reason='Receipt had not been created before first global check; experiments unchanged.'))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,checks=[],errors=[],
        original_failed_global_check=failure.relative_to(ROOT).as_posix(),
        source='Actual subprocess exit/stdout/stderr plus full stage-file rehash; no scientific inference.')
    write(SUMMARY,result)
    jobs=[('completed_stage',[str(ROOT/'literature/verify_coverage_augmentation_stage_2026_10_03.py')]),
          ('global_archive_write',[str(ROOT/'verify_archive.py'),'--write']),
          ('global_archive_read',[str(ROOT/'verify_archive.py')])]
    for name,args in jobs:
        proc=subprocess.run([sys.executable,'-X','utf8','-B',*args],cwd=ROOT.parent,capture_output=True,text=True,encoding='utf-8')
        row=dict(name=name,exit_code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr)
        try:row['parsed_stdout']=json.loads(proc.stdout)
        except ValueError:pass
        result['checks'].append(row)
        if proc.returncode:result['errors'].append(name+' failed')
        write(SUMMARY,result);print(json.dumps(row,ensure_ascii=False),flush=True)
        if proc.returncode:return proc.returncode
    stage=ROOT/'literature/coverage_augmentation_stage_manifest_2026-10-03.json'
    manifest=json.loads(stage.read_text(encoding='utf-8'));mismatches=[]
    for record in manifest['files']:
        path=ROOT/record['path'];h=hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
        if path.stat().st_size!=record['bytes'] or h.hexdigest()!=record['sha256']:mismatches.append(record['path'])
    row=dict(name='independent_stage_file_hash_recheck',files_checked=len(manifest['files']),mismatches=mismatches,exit_code=int(bool(mismatches)))
    result['checks'].append(row)
    if mismatches:result['errors'].append('Stage files changed')
    result.update(complete=not result['errors'],finished_utc=datetime.now(timezone.utc).isoformat(),
                  stage_manifest_sha256=hashlib.sha256(stage.read_bytes()).hexdigest(),
                  global_manifest_sha256=hashlib.sha256((ROOT/'literature/archive_manifest.json').read_bytes()).hexdigest())
    write(SUMMARY,result);print(json.dumps(row,ensure_ascii=False),flush=True)
    return int(not result['complete'])


if __name__=='__main__':
    raise SystemExit(main())
