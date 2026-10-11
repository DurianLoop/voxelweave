"""Separate Schannel attempt; verified public wheels confined to innovation."""
import hashlib
import json
import subprocess
import sys
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def get(url, name, limit):
    assert url.startswith(('https://pypi.org/', 'https://files.pythonhosted.org/'))
    proc = subprocess.run(['curl.exe', '--noproxy', '*', '--fail', '--silent',
        '--show-error', '--max-time', '30', '--max-filesize', str(limit), url],
        capture_output=True, timeout=35)
    (OUT/(name+'_curl_stderr.txt')).write_bytes(proc.stderr)
    assert proc.returncode == 0, (url, proc.returncode, proc.stderr.decode('utf-8', errors='replace'))
    assert len(proc.stdout) <= limit
    return proc.stdout, dict(url=url, backend='Windows curl Schannel',
        TLS_certificate_verification_disabled=False, actual_subprocess_exit=proc.returncode,
        bytes=len(proc.stdout))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    target = OUT/'site_packages'
    target.mkdir()
    started = time.perf_counter()
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[],
        source_bindings=[dict(path=Path(__file__).relative_to(ROOT).as_posix(), sha256=sha(Path(__file__))),
            dict(path='literature/install_portable_blindspot_pdf_reader_2026_10_08.py',
                 sha256=sha(ROOT/'literature/install_portable_blindspot_pdf_reader_2026_10_08.py'))],
        prior_attempt_tool_chunk='4f7373', prior_attempt_actual_exit=1,
        prior_attempt_failure='Schannel SEC_E_NO_CREDENTIALS in default sandbox; v1 urllib TLS failure retained',
        prior_attempt_retained=True, global_MRI_environment_modified=False,
        pip_not_invoked=True, public_GET_only=True, TLS_certificate_verification_disabled=False,
        other_processes_enumerated=False, medical_arrays_loaded=0, neural_forwards=0,
        GPU_forwards=0, training_updates=0, packages=[])
    try:
        total = 0
        for name in ('pypdf', 'pypdfium2'):
            data, response = get('https://pypi.org/pypi/'+name+'/json', name+'_metadata', 2_000_000)
            metadata = OUT/(name+'_metadata_attempt02.json')
            metadata.write_bytes(data)
            record = json.loads(data)
            suffix = '-py3-none-any.whl' if name == 'pypdf' else '-py3-none-win_amd64.whl'
            selected = [w for w in record['urls'] if w['filename'].endswith(suffix)]
            assert len(selected) == 1
            info = selected[0]
            raw, wheel_response = get(info['url'], name+'_wheel', 8_000_000)
            assert hashlib.sha256(raw).hexdigest() == info['digests']['sha256']
            wheel = OUT/info['filename']
            wheel.write_bytes(raw)
            with zipfile.ZipFile(wheel) as archive:
                for member in archive.infolist():
                    path = (target/member.filename).resolve()
                    assert path.is_relative_to(target.resolve())
                    total += member.file_size
                    assert member.file_size <= 15_000_000 and total <= 20_000_000
                    if member.is_dir():
                        path.mkdir(parents=True, exist_ok=True)
                        continue
                    assert not path.exists(), member.filename
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open('xb') as dest:
                        dest.write(archive.read(member))
            r['packages'].append(dict(name=name, version=record['info']['version'],
                metadata_response=response, wheel_response=wheel_response,
                metadata_file=metadata.relative_to(ROOT).as_posix(), metadata_sha256=sha(metadata),
                wheel_file=wheel.relative_to(ROOT).as_posix(), wheel_sha256=sha(wheel),
                official_PyPI_sha256=info['digests']['sha256'], official_digest_verified=True))
        code = "import sys,json;sys.path.insert(0,sys.argv[1]);import pypdf,pypdfium2;from importlib.metadata import version;print(json.dumps({'pypdf':pypdf.__version__,'pypdfium2':version('pypdfium2')}))"
        proc = subprocess.run([sys.executable, '-X', 'utf8', '-B', '-c', code, str(target)],
            capture_output=True, timeout=30)
        (OUT/'import_stdout.txt').write_bytes(proc.stdout)
        (OUT/'import_stderr.txt').write_bytes(proc.stderr)
        r['import_actual_subprocess_exit'] = proc.returncode
        assert proc.returncode == 0, proc.stderr.decode('utf-8', errors='replace')
        r['versions'] = json.loads(proc.stdout.decode('utf-8'))
        assert r['versions'] == {p['name']:p['version'] for p in r['packages']}
        files = [p for p in sorted(OUT.rglob('*')) if p.is_file()]
        r['installed_files'] = [dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                                    sha256=sha(p)) for p in files]
        r['saved_runtime_bytes'] = sum(p.stat().st_size for p in files)
        assert r['saved_runtime_bytes'] < 25_000_000
        r['complete'] = True
    except Exception as exc:
        r['errors'].append(type(exc).__name__+': '+str(exc))
        r['traceback'] = traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-started, finished_utc=datetime.now(timezone.utc).isoformat())
    with (OUT/'installation_attempt03.json').open('x', encoding='utf-8') as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','versions','saved_runtime_bytes','elapsed_seconds')}, ensure_ascii=False), flush=True)
    return int(not r['complete'])


if __name__ == '__main__':
    raise SystemExit(main())
