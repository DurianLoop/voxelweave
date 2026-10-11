"""V3: reuse two verified wheels; curl Schannel for the remaining public package."""
import concurrent.futures,hashlib,io,json,subprocess,sys,time,traceback,urllib.request,zipfile
from datetime import datetime,timezone
from pathlib import Path
from mc_rc_reference_resources_2026_10_07 import resource_guard
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tools/anchor_forest_runtime_v3_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fetch(job):
    project,version,suffix=job;opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def get(url,limit):
        name=OUT/(project+('_metadata' if url.endswith('/json') else '_wheel')+'_curl_stderr.txt')
        proc=subprocess.run(['curl.exe','--noproxy','*','--fail','--silent','--show-error','--max-time','25','--max-filesize',str(limit),url],capture_output=True,timeout=30)
        name.write_bytes(proc.stderr);assert proc.returncode==0,(url,proc.returncode,proc.stderr.decode('utf-8',errors='replace'))
        assert len(proc.stdout)<=limit
        return proc.stdout,dict(url=url,http_backend='Windows curl Schannel',curl_actual_subprocess_exit=proc.returncode,bytes=len(proc.stdout))
    prior=ROOT/'tools/anchor_forest_runtime_v2_2026_10_07';previous=prior/(project+'_version.json')
    if previous.exists():data=previous.read_bytes();meta=dict(reused_metadata=previous.relative_to(ROOT).as_posix(),sha256=sha(previous))
    else:data,meta=get(f'https://pypi.org/pypi/{project}/{version}/json',2_000_000)
    path=OUT/(project+'_version.json');path.write_bytes(data)
    package=json.loads(data);matches=[v for v in package['urls'] if v['filename'].endswith(suffix)];assert len(matches)==1
    selected=matches[0];assert selected['url'].startswith('https://files.pythonhosted.org/')
    previous_wheel=prior/selected['filename']
    if previous_wheel.exists():raw=previous_wheel.read_bytes();response=dict(reused_wheel=previous_wheel.relative_to(ROOT).as_posix(),sha256=sha(previous_wheel))
    else:raw,response=get(selected['url'],32_000_000)
    assert hashlib.sha256(raw).hexdigest()==selected['digests']['sha256']
    wheel=OUT/selected['filename'];wheel.write_bytes(raw)
    return dict(project=project,version=version,metadata_response=meta,wheel_response=response,wheel_file=wheel.relative_to(ROOT).as_posix(),
        wheel_sha256=sha(wheel),official_sha256=selected['digests']['sha256'])
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=False);started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        previous_failure_files=['tools/anchor_forest_runtime_2026_10_07/install_attempt01.json','tools/anchor_forest_runtime_v2_2026_10_07/install_attempt02.json'],existing_environment_modified=False,
        system_proxy_modified=False,root_project_files_modified=False,other_processes_modified=False,public_GET_only=True)
    try:
        r['resources_before']=resource_guard()
        jobs=[('scikit-learn','1.7.2','cp312-cp312-win_amd64.whl'),('joblib','1.5.2','py3-none-any.whl'),('threadpoolctl','3.6.0','py3-none-any.whl')]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,jobs))
        r['acquisitions']=rows;target=OUT/'site_packages';target.mkdir();total=0
        for v in rows:
            with zipfile.ZipFile(ROOT/v['wheel_file']) as archive:
                for member in archive.infolist():
                    assert member.file_size<=32_000_000;total+=member.file_size;assert total<100_000_000
                    path=(target/member.filename).resolve();assert path.is_relative_to(target.resolve())
                    if member.is_dir():path.mkdir(parents=True,exist_ok=True);continue
                    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(archive.read(member))
        code="import sys,json;sys.path.insert(0,sys.argv[1]);import sklearn,joblib,threadpoolctl;print(json.dumps({'sklearn':sklearn.__version__,'joblib':joblib.__version__,'threadpoolctl':threadpoolctl.__version__}))"
        check=subprocess.run([sys.executable,'-X','utf8','-B','-c',code,str(target)],capture_output=True,timeout=30)
        (OUT/'import_stdout.txt').write_bytes(check.stdout);(OUT/'import_stderr.txt').write_bytes(check.stderr);r['import_actual_subprocess_exit']=check.returncode;assert check.returncode==0,check.stderr.decode('utf-8',errors='replace')[-1500:]
        versions=json.loads(check.stdout.decode('utf-8'));assert versions==dict(sklearn='1.7.2',joblib='1.5.2',threadpoolctl='3.6.0')
        files=[p for p in OUT.rglob('*') if p.is_file()];assert sum(p.stat().st_size for p in files)<100_000_000
        r.update(versions=versions,installed_files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(files)],
            total_saved_bytes=sum(p.stat().st_size for p in files),resources_after=resource_guard(),complete=True)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-started,finished_utc=datetime.now(timezone.utc).isoformat());(OUT/'install_attempt03.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','versions','total_saved_bytes','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
