"""Test native transparent compression only on a newly created non-patient text fixture."""
import sys,time,ctypes,subprocess,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard


def physical_size(p):
    fn=ctypes.windll.kernel32.GetCompressedFileSizeW
    fn.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_uint32)];fn.restype=ctypes.c_uint32
    high=ctypes.c_uint32();low=fn(str(p),ctypes.byref(high))
    assert low!=0xffffffff
    return (high.value<<32)|low


def attributes(p):
    fn=ctypes.windll.kernel32.GetFileAttributesW
    fn.argtypes=[ctypes.c_wchar_p];fn.restype=ctypes.c_uint32
    value=int(fn(str(p)));assert value!=0xffffffff
    return value


def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    journal=HERE/'full_real_pipeline_attempt01/fields.jsonl.gz'
    size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    assert size+max(0,1_500_000-journal.stat().st_size)+150_000+100_000+12_000<5_000_000
    out=HERE/'transparent_storage_probe_attempt01';out.mkdir(exist_ok=False)
    p=out/'new_text_fixture.txt';assert p.resolve().is_relative_to(HERE)
    data=(b'Offline research evidence compression fixture; no patient data.\n'*140)[:8192]
    assert len(data)==8192
    with p.open('xb') as f:f.write(data)
    before=dict(logical_bytes=p.stat().st_size,physical_bytes=physical_size(p),attributes=attributes(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    result=subprocess.run(['compact.exe','/C','/I','/Q',str(p.resolve())],capture_output=True,text=True,timeout=30)
    after=dict(logical_bytes=p.stat().st_size,physical_bytes=physical_size(p),attributes=attributes(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    assert before['logical_bytes']==after['logical_bytes'] and before['sha256']==after['sha256']
    r=dict(complete=True,errors=[],new_fixture_only=True,compact_exit=result.returncode,
           compact_stdout=result.stdout,compact_stderr=result.stderr,before=before,after=after,
           compressed_attribute_set=bool(after['attributes']&0x800),
           physical_bytes_saved=before['physical_bytes']-after['physical_bytes'],
           old_source_bytes_or_paths_modified=False,other_PIDs_enumerated=False,other_PIDs_modified=False,
           MRI_arrays_loaded=0,model_arrays_loaded=0,confirmation_patients_opened=False,
           source_bindings=[entry(x) for x in [Path(__file__),HERE/'NTFS_STORAGE_PROBE_PROTOCOL_TURN29.md',p]],
           elapsed_seconds=time.perf_counter()-started,resources=resource_guard(),goal_status='active')
    assert r['elapsed_seconds']<60
    dump(out/'receipt.json',r);print(r,flush=True)
    return int(result.returncode!=0 or not r['compressed_attribute_set'])


if __name__=='__main__':raise SystemExit(main())
