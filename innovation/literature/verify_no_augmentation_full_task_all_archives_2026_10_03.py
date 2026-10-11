"""Save actual stage/global check receipts and separately rehash all stage files."""
import hashlib,json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SESSION_ARCHIVE_VERIFICATION_NO_AUGMENTATION_2026-10-03.json'


def write(record):OUT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not OUT.exists()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],checks=[],
        scope='Artifact/source/code/link integrity; no publication claim inference.')
    write(r)
    for name,args in [('completed_stage',[str(ROOT/'literature/verify_no_augmentation_full_task_stage_2026_10_03.py')]),
        ('global_archive_write',[str(ROOT/'verify_archive.py'),'--write']),('global_archive_read',[str(ROOT/'verify_archive.py')])]:
        p=subprocess.run([sys.executable,'-X','utf8','-B',*args],cwd=ROOT.parent,capture_output=True,text=True,encoding='utf-8')
        row=dict(name=name,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr)
        try:row['parsed_stdout']=json.loads(p.stdout)
        except ValueError:pass
        r['checks'].append(row)
        if p.returncode:r['errors'].append(name+' failed')
        write(r);print(json.dumps(row,ensure_ascii=False),flush=True)
        if p.returncode:return p.returncode
    manifest=ROOT/'literature/no_augmentation_full_task_stage_manifest_2026-10-03.json'
    files=json.loads(manifest.read_text(encoding='utf-8'))['files'];mismatches=[]
    for row in files:
        path=ROOT/row['path'];h=hashlib.sha256(path.read_bytes()).hexdigest()
        if path.stat().st_size!=row['bytes'] or h!=row['sha256']:mismatches.append(row['path'])
    row=dict(name='independent_stage_rehash',files=len(files),mismatches=mismatches,exit_code=int(bool(mismatches)))
    r['checks'].append(row)
    if mismatches:r['errors'].append('Stage file hash changed')
    r.update(complete=not r['errors'],finished_utc=datetime.now(timezone.utc).isoformat(),
        stage_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        global_manifest_sha256=hashlib.sha256((ROOT/'literature/archive_manifest.json').read_bytes()).hexdigest())
    write(r);print(json.dumps(row,ensure_ascii=False));return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
