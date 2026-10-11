"""Persist actual available tool-return buffers without shell interpolation of their contents."""
import sys,base64,gzip,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,dump
resource_guard();assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<1_950_000
path=HERE/'ACTUAL_AVAILABLE_TOOL_RETURNS.json.gz'
if sys.argv[1]=='finish':
    data=gzip.decompress(path.read_bytes());value=json.loads(data)
    assert len(data)==int(sys.argv[2]) and isinstance(value['cached_tool_returns'],dict)
    dump(HERE/'TOOL_EXPORT_RECEIPT.json',dict(complete=True,source=entry(path),decompressed_bytes=len(data),decompressed_sha256=hashlib.sha256(data).hexdigest(),
        cached_keys=len(value['cached_tool_returns']),native_truncation_preserved=True,hidden_reasoning_included=False,unavailable_earlier_raw_returns_recreated=False))
    print(json.dumps(dict(complete=True,cached_keys=len(value['cached_tool_returns']),compressed_bytes=path.stat().st_size)))
else:
    number=int(sys.argv[1]);chunk=base64.b64decode(sys.argv[2],validate=True);assert len(chunk)<=16_000
    with path.open('xb' if number==0 else 'ab') as f:f.write(gzip.compress(chunk,compresslevel=6,mtime=0))
