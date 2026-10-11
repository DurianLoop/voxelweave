"""Standard-library disk bindings and resource guards, before neural imports."""
import ctypes, hashlib, json, os, shutil, time
from pathlib import Path
from datetime import datetime, timezone
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARMS = ('legacy_dense', 'direct', 'common_projected_dense')
MAX_BYTES = 200_000_000
RESERVE = 8_000_000_000

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(p):
    p = Path(p).resolve()
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))
def new_json(p, v):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
def new_bytes(p, v):
    with Path(p).open('xb') as f: f.write(v); f.flush(); os.fsync(f.fileno())
def atomic_json(p, v):
    p = Path(p); tmp = p.with_name(p.name+'.working.tmp')
    new_json(tmp, v); os.replace(tmp, p)
def saved_bytes(): return sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
def guard(start, limit=600, additional_write_bytes=0):
    assert time.perf_counter()-start < limit, 'Frozen qualification wall limit exceeded'
    free = shutil.disk_usage(ROOT).free
    assert free >= RESERVE + additional_write_bytes, '8GB disk reserve including pending write failed'
    assert saved_bytes()+additional_write_bytes <= MAX_BYTES, 'Stage output limit exceeded'
    class M(ctypes.Structure):
        _fields_ = [('length',ctypes.c_ulong), ('load',ctypes.c_ulong)] + [(k,ctypes.c_ulonglong) for k in ('total','avail','tp','ap','tv','av','ex')]
    m=M(); m.length=ctypes.sizeof(m)
    k=ctypes.windll.kernel32
    assert k.GlobalMemoryStatusEx(ctypes.byref(m)) and m.avail >= RESERVE, '8GB RAM reserve failed'
    k.GetCurrentProcess.restype=ctypes.c_void_p
    k.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
    assert k.SetPriorityClass(k.GetCurrentProcess(),0x4000)
    return dict(observed_utc=now(),workspace_free_bytes=free,available_ram_bytes=int(m.avail),
                stage_saved_bytes=saved_bytes(),additional_write_bytes=additional_write_bytes,
                own_process_below_normal=True,other_processes_modified=False)
def verify_bindings(bindings):
    for b in bindings:
        p=(ROOT/b['path']).resolve()
        assert p.is_relative_to(ROOT.resolve()) and p.is_file(), 'Binding path missing/outside innovation'
        assert sha(p)==b['sha256'], 'Binding SHA mismatch: '+b['path']
        if 'bytes' in b: assert p.stat().st_size==b['bytes'], 'Binding size mismatch'
def verify_plan(path):
    path=Path(path).resolve(); assert path.is_relative_to(HERE) and path.is_file()
    q=read(path); assert q['synthetic_only'] and q['arms']==list(ARMS)
    assert q['updates_per_arm']==3 and q['resume_from_step']==1 and q['patch']==[64,128,128] and q['batch_size']==2
    verify_bindings(q['source_bindings']); return q
def verify_resume(meta_path,expected_meta_sha,arm,plan_path):
    assert arm in ARMS, 'Unknown arm'
    plan=verify_plan(plan_path); meta_path=Path(meta_path).resolve()
    assert meta_path.is_relative_to(HERE) and sha(meta_path)==expected_meta_sha, 'Metadata SHA mismatch'
    q=read(meta_path)
    assert q['synthetic_only'] and q['arm']==arm, 'Arm mismatch'
    assert type(q['step']) is int and q['step']==plan['resume_from_step'], 'Resume step mismatch'
    assert q['plan_sha256']==sha(plan_path), 'Checkpoint plan mismatch'
    verify_bindings(q['source_bindings'])
    for key in ('checkpoint','journal'):
        b=q[key]; p=(ROOT/b['path']).resolve()
        assert p.is_relative_to(HERE) and p.is_file(), 'Synthetic checkpoint/journal missing or outside stage'
        assert sha(p)==b['sha256'] and p.stat().st_size==b['bytes'], key+' SHA/size mismatch'
    payload=(ROOT/q['journal']['path']).read_bytes()
    assert payload.endswith(b'\n'), 'Journal lacks terminal newline'
    lines=payload.decode('utf-8').splitlines()
    assert len(lines)==q['step'], 'Journal step count mismatch'
    for i,line in enumerate(lines,1):
        h=json.loads(line); item=plan['stream'][i-1]
        assert h['step']==i and h['arm']==arm, 'Journal arm/step mismatch'
        assert h['uid']==item['uid'] and h['patient']==item['patient'], 'Journal schedule mismatch'
    return q
