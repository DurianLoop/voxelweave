"""Receive numbered ASCII base64 chunks over stdin; save only actual accessible tool returns."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,dump
path=HERE/'ACTUAL_AVAILABLE_TOOL_RETURNS.json.gz';assert not path.exists()
print('ready',flush=True);expected=0
for line in sys.stdin:
    fields=line.strip().split(' ',1);assert len(fields)==2
    number,value=fields
    if number=='finish':
        data=gzip.decompress(path.read_bytes());v=json.loads(data)
        assert len(data)==int(value) and isinstance(v['cached_tool_returns'],dict)
        dump(HERE/'TOOL_EXPORT_RECEIPT.json',dict(complete=True,source=entry(path),chunks=expected,
            decompressed_bytes=len(data),decompressed_sha256=hashlib.sha256(data).hexdigest(),
            cached_keys=len(v['cached_tool_returns']),native_truncation_preserved=True,hidden_reasoning_included=False,
            unavailable_earlier_raw_returns_recreated=False))
        print(json.dumps(dict(complete=True,cached_keys=len(v['cached_tool_returns']),compressed_bytes=path.stat().st_size)),flush=True)
        break
    assert int(number)==expected;chunk=base64.b64decode(value,validate=True);assert len(chunk)<=16000
    res=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    assert size+len(chunk)+20_000<2_000_000 and res['workspace_free_bytes']-16_800_000-(2_000_000-size)>=8_000_000_000
    with path.open('xb' if expected==0 else 'ab') as f:f.write(gzip.compress(chunk,compresslevel=6,mtime=0))
    expected+=1;print(json.dumps(dict(chunk=expected)),flush=True)
else:raise AssertionError('stream ended before explicit finish')
