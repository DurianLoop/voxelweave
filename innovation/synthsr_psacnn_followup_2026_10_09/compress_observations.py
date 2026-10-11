"""Losslessly gzip only newly created exact tool-return buffers; verify before removing buffers."""
import sys,json,gzip,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    sys.stdout.reconfigure(encoding='utf-8');rows=[]
    for raw in sorted(HERE.glob('ACTUAL_TOOL_OBSERVATIONS*.raw.json')):
        resolved=raw.resolve();assert resolved.parent==HERE and resolved.name.endswith('.raw.json')
        original=raw.read_bytes();obj=json.loads(original)
        dest=raw.with_name(raw.name.replace('.raw.json','.json.gz'));assert not dest.exists()
        with dest.open('xb') as stream,gzip.GzipFile(fileobj=stream,mode='wb',compresslevel=9,mtime=0,filename='') as f:f.write(original)
        with gzip.open(dest,'rb') as f:recovered=f.read()
        assert recovered==original and json.loads(recovered)==obj
        rows.append(dict(path=dest.name,bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
            uncompressed_bytes=len(original),uncompressed_sha256=hashlib.sha256(original).hexdigest(),keys=list(obj['observations']),
            exact_decoded_bytes_verified=True,actual_native_truncation_and_live_fields_preserved=True))
        raw.unlink()
    assert rows
    receipt=HERE/('OBSERVATION_COMPRESSION_RECEIPT_'+str(len(list(HERE.glob('OBSERVATION_COMPRESSION_RECEIPT_*.json')))+1).zfill(2)+'.json')
    receipt.write_text(json.dumps(dict(complete=True,errors=[],records=rows,only_own_verified_new_buffers_removed=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(complete=True,receipt=receipt.name,records=[{k:v for k,v in r.items() if k!='keys'} for r in rows]),ensure_ascii=False))
if __name__=='__main__':main()
