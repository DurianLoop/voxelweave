"""Append compressed members for a bounded export of actual cached tool returns."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
from inventory_frozen_text_storage import HERE,entry,dump
from mc_rc_reference_resources_2026_10_07 import resource_guard

resource_guard()
assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<1_950_000
name=sys.argv[1];assert name=='ACTUAL_TOOL_BUFFERS.json.gz'
path=HERE/name
if sys.argv[2]=='finish':
    decoded=gzip.decompress(path.read_bytes());value=json.loads(decoded)
    assert len(decoded)==int(sys.argv[3]) and isinstance(value['cached_tool_returns'],dict)
    dump(HERE/'TOOL_BUFFER_EXPORT_RECEIPT.json',dict(complete=True,tool_export=entry(path),
        decompressed_bytes=len(decoded),decompressed_sha256=hashlib.sha256(decoded).hexdigest(),
        cached_keys=len(value['cached_tool_returns']),all_compressed_members_valid=True,
        native_tool_output_truncation_not_repaired_or_fabricated=True,resource=resource_guard()))
    print(json.dumps(dict(complete=True,cached_keys=len(value['cached_tool_returns']),bytes=path.stat().st_size)),flush=True)
else:
    chunk=int(sys.argv[2]);data=base64.b64decode(sys.argv[3],validate=True);assert len(data)<=16_000
    with path.open('xb' if chunk==0 else 'ab') as f:f.write(gzip.compress(data,compresslevel=6,mtime=0))
