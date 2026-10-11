"""Losslessly persist exact returned buffers without shell interpolation."""
import sys,json,gzip,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    sys.stdout.reconfigure(encoding='utf-8');rows=[]
    for raw in sorted(HERE.glob('ACTUAL_TOOL_OBSERVATIONS*.raw.json')):
        assert raw.resolve().parent==HERE
        data=raw.read_bytes();obj=json.loads(data);dest=raw.with_name(raw.name.replace('.raw.json','.json.gz'));assert not dest.exists()
        with dest.open('xb') as stream,gzip.GzipFile(fileobj=stream,mode='wb',compresslevel=9,mtime=0,filename='') as f:f.write(data)
        with gzip.open(dest,'rb') as f:assert f.read()==data
        rows.append(dict(path=dest.name,bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
            uncompressed_bytes=len(data),uncompressed_sha256=hashlib.sha256(data).hexdigest(),keys=list(obj['observations']),exact_decoded_bytes_verified=True))
        raw.unlink()
    assert rows
    n=len(list(HERE.glob('OBSERVATION_COMPRESSION_RECEIPT_*.json')))+1
    receipt=HERE/('OBSERVATION_COMPRESSION_RECEIPT_'+str(n).zfill(2)+'.json')
    with receipt.open('x',encoding='utf-8') as f:json.dump(dict(complete=True,errors=[],records=rows,only_own_verified_new_buffers_removed=True),f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,receipt=receipt.name,records=[{k:v for k,v in r.items() if k!='keys'} for r in rows])),flush=True)
if __name__=='__main__':main()
