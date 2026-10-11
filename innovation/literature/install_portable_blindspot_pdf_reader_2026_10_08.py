"""Workspace-only PDF text/render runtime; no global environment or user process control."""
import hashlib
import json
import urllib.request
import zipfile
import sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tools/blindspot_pdf_reader_2026_10_08'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    target=OUT/'site_packages'
    target.mkdir()
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    packages=[]
    for name in ('pypdf','pypdfium2'):
        metadata_url='https://pypi.org/pypi/'+name+'/json'
        with opener.open(metadata_url,timeout=30) as response:
            data=response.read(2_000_001)
            assert len(data)<=2_000_000
        meta=OUT/(name+'_metadata_attempt01.json')
        with meta.open('xb') as f:
            f.write(data)
        record=json.loads(data)
        suffix='-py3-none-any.whl' if name=='pypdf' else '-py3-none-win_amd64.whl'
        wheels=[w for w in record['urls'] if w['filename'].endswith(suffix)]
        assert len(wheels)==1,(name,[w['filename'] for w in record['urls']])
        info=wheels[0]
        with opener.open(info['url'],timeout=30) as response:
            archive=response.read(8_000_001)
            assert len(archive)<=8_000_000
        digest=hashlib.sha256(archive).hexdigest()
        assert digest==info['digests']['sha256']
        wheel=OUT/info['filename']
        with wheel.open('xb') as f:
            f.write(archive)
        with zipfile.ZipFile(wheel) as z:
            for member in z.infolist():
                resolved=(target/member.filename).resolve()
                assert resolved.is_relative_to(target.resolve()),member.filename
                if member.is_dir():
                    resolved.mkdir(parents=True,exist_ok=True)
                else:
                    assert not resolved.exists(),member.filename
                    resolved.parent.mkdir(parents=True,exist_ok=True)
                    with z.open(member) as src,resolved.open('xb') as dest:
                        dest.write(src.read())
        packages.append(dict(name=name,version=record['info']['version'],metadata_url=metadata_url,
            wheel_URL=info['url'],wheel_file=wheel.relative_to(ROOT).as_posix(),wheel_sha256=digest,
            downloaded_wheel_bytes=len(archive),PyPI_digest_verified=True))
    files=[]
    for p in sorted(target.rglob('*')) if target.exists() else []:
        if p.is_file():
            files.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,
                              sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    saved=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    assert saved<25_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),packages=packages,
        installed_files=files,saved_runtime_bytes=saved,global_MRI_environment_modified=False,
        pip_not_invoked=True,direct_public_wheels_without_cache=True,bytecode_disabled=True,
        temporary_directory_inside_workspace=True,
        other_processes_enumerated=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    with (OUT/'installation_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps(dict(complete=result['complete'],errors=result['errors'],packages=packages,
                         installed_files=len(files),saved_runtime_bytes=saved)),flush=True)
    return int(not result['complete'])


if __name__=='__main__':
    raise SystemExit(main())
