"""Only task-local pinned wheels; never mutates the existing MRI environment."""
import hashlib,json,os,subprocess,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
from mc_rc_reference_resources_2026_10_07 import resource_guard
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tools/anchor_forest_runtime_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=False);started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        packages=['scikit-learn==1.7.2','joblib==1.5.2','threadpoolctl==3.6.0'],existing_environment_modified=False,system_proxy_modified=False,
        root_project_files_modified=False,other_processes_modified=False,preflight_sklearn_missing_tool_chunk='19d435',preflight_actual_exit=1)
    try:
        r['resources_before']=resource_guard();target=OUT/'site_packages';tmp=OUT/'tmp';tmp.mkdir()
        env=os.environ.copy()
        for k in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'):env.pop(k,None)
        env.update(TEMP=str(tmp),TMP=str(tmp),PYTHONDONTWRITEBYTECODE='1')
        args=[sys.executable,'-X','utf8','-B','-m','pip','install','--isolated','--no-cache-dir','--no-deps','--no-compile',
            '--only-binary=:all:','--target',str(target),'--index-url','https://pypi.org/simple']+r['packages']
        proc=subprocess.run(args,capture_output=True,env=env,timeout=180);(OUT/'pip_stdout.txt').write_bytes(proc.stdout);(OUT/'pip_stderr.txt').write_bytes(proc.stderr)
        r['pip_actual_subprocess_exit']=proc.returncode;assert proc.returncode==0,proc.stderr.decode('utf-8',errors='replace')[-1500:]
        code="import sys,json;sys.path.insert(0,sys.argv[1]);import sklearn,joblib,threadpoolctl;print(json.dumps({'sklearn':sklearn.__version__,'joblib':joblib.__version__,'threadpoolctl':threadpoolctl.__version__}))"
        check=subprocess.run([sys.executable,'-X','utf8','-B','-c',code,str(target)],capture_output=True,env=env,timeout=30)
        (OUT/'import_stdout.txt').write_bytes(check.stdout);(OUT/'import_stderr.txt').write_bytes(check.stderr);r['import_actual_subprocess_exit']=check.returncode;assert check.returncode==0
        versions=json.loads(check.stdout.decode('utf-8'));assert versions==dict(sklearn='1.7.2',joblib='1.5.2',threadpoolctl='3.6.0')
        files=[p for p in OUT.rglob('*') if p.is_file()];assert sum(p.stat().st_size for p in files)<100_000_000
        r.update(versions=versions,installed_files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(files)],
            total_saved_bytes=sum(p.stat().st_size for p in files),resources_after=resource_guard(),complete=True)
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-started,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'install_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','versions','total_saved_bytes','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
