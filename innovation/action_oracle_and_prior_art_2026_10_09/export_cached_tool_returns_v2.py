"""Persist numbered actual buffers via safe base64 arguments after closed-stdin failure."""
import sys,base64,gzip,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,dump
res=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
assert size+40_000<2_000_000 and res['workspace_free_bytes']-16_800_000-(2_000_000-size)>=8_000_000_000
path=HERE/'ACTUAL_AVAILABLE_TOOL_RETURNS.json.gz'
if sys.argv[1]=='finish':
    data=gzip.decompress(path.read_bytes());v=json.loads(data)
    assert len(data)==int(sys.argv[2]) and isinstance(v['cached_tool_returns'],dict)
    dump(HERE/'TOOL_EXPORT_RECEIPT.json',dict(complete=True,source=entry(path),decompressed_bytes=len(data),
        decompressed_sha256=hashlib.sha256(data).hexdigest(),cached_keys=len(v['cached_tool_returns']),
        native_truncation_preserved=True,hidden_reasoning_included=False,unavailable_earlier_raw_returns_recreated=False))
    print(json.dumps(dict(complete=True,cached_keys=len(v['cached_tool_returns']),compressed_bytes=path.stat().st_size)))
else:
    n=int(sys.argv[1]);chunk=base64.b64decode(sys.argv[2],validate=True);assert len(chunk)<=16_000
    with path.open('xb' if n==0 else 'ab') as f:f.write(gzip.compress(chunk,compresslevel=6,mtime=0))
