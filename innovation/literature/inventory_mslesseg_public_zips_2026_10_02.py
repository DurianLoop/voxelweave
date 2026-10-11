"""Bounded remote ZIP metadata only; reject ignored HTTP ranges."""
from __future__ import annotations
import hashlib
import io
import json
import re
import sys
import urllib.request
import urllib.parse
import zipfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT / 'literature/source_cache/mslesseg_public_zip_metadata_2026-10-02'
PLAN=ROOT / 'MSLESSEG_PUBLIC_ZIP_METADATA_PLAN_2026-10-02.md'
FILES={'registered':(52771814,1473284755,'cb30cfb13b0981443c300a5e51dd91cd'),
       'raw':(53623946,1295472528,'8bae58b902c8b6ce4afb0bc5fc227959')}
TOTAL_CAP=10_000_000
PER_RANGE_CAP=1_000_000

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class RemoteZip(io.RawIOBase):
    def __init__(self,key,file_id,size,ledger,attempt):
        self.key,self.size,self.position=key,size,0
        self.url=f'https://ndownloader.figshare.com/files/{file_id}'
        self.ledger,self.attempt=ledger,attempt
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.position
    def seek(self,offset,whence=io.SEEK_SET):
        p=offset if whence==io.SEEK_SET else self.position+offset if whence==io.SEEK_CUR else self.size+offset
        if not 0<=p<=self.size: raise ValueError('ZIP seek out of range')
        self.position=p
        return p
    def read(self,length=-1):
        length=min(self.size-self.position,self.size if length<0 else length)
        if length<=0: return b''
        if length>PER_RANGE_CAP or sum(r.get('bytes',0) for r in self.ledger)+length>TOTAL_CAP:
            raise ValueError('Metadata range budget exceeded')
        start,end=self.position,self.position+length-1
        entry={'source_archive':self.key,'url':self.url,'start':start,'end':end,'requested_bytes':length,
               'started_utc':datetime.now(timezone.utc).isoformat()}
        self.ledger.append(entry)
        request=urllib.request.Request(self.url,headers={'Range':f'bytes={start}-{end}','User-Agent':'MRI-source-header-audit/1.0'})
        try:
            with self.opener.open(request,timeout=30) as response:
                u=urllib.parse.urlsplit(response.url)
                entry.update(http_status=response.status,content_range=response.headers.get('Content-Range'),
                             final_url_without_query=urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,'','')),
                             temporary_redirect_query_omitted=bool(u.query),etag=response.headers.get('ETag'))
                if response.status!=206 or response.headers.get('Content-Range')!=f'bytes {start}-{end}/{self.size}':
                    raise ValueError('Server did not honor exact bounded ZIP range')
                raw=response.read(length+1)
            if len(raw)!=length: raise ValueError('Incomplete or oversized ZIP range')
            path=OUT / f'{self.key}_range_{len(self.ledger):03d}_attempt_{self.attempt:02d}.bin'
            path.write_bytes(raw)
            entry.update(raw_file=path.name,bytes=len(raw),sha256=sha(path))
            self.position+=length
            return raw
        except Exception as exc:
            entry['error']=f'{type(exc).__name__}: {exc}'
            raise

def summarize(members):
    paths=[m['path'] for m in members]
    modalities={name:[p for p in paths if re.search(r'(?:^|[_/])'+name+r'(?:\.nii(?:\.gz)?|\.dcm)$',p,re.I)] for name in ('T1','T2','FLAIR')}
    return {'files':len(paths),'extensions':dict(Counter(Path(p).suffix.lower() for p in paths)),
            'modalities_by_filename':{k:len(v) for k,v in modalities.items()},'first_paths':paths[:18]}

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    ledger=[]; records=[]; errors=[]
    for key,(file_id,size,public_md5) in FILES.items():
        try:
            remote=RemoteZip(key,file_id,size,ledger,attempt)
            with zipfile.ZipFile(remote) as archive:
                info=archive.infolist()
                members=[{'path':i.filename,'compressed_bytes':i.compress_size,'uncompressed_bytes':i.file_size,
                          'compression_method':i.compress_type,'crc32':f'{i.CRC:08x}','header_offset':i.header_offset}
                         for i in info if not i.is_dir()]
                selected=[i for i in info if not i.is_dir() and Path(i.filename).suffix.lower() in ('.csv','.json','.md','.txt','.xlsx') and i.file_size<=1_000_000][:6]
                selected_record=[i.filename for i in selected]
                (OUT / f'{key}_metadata_selection_attempt_{attempt:02d}.json').write_text(json.dumps(selected_record,indent=2)+'\n',encoding='utf-8')
                metadata=[]
                for i in selected:
                    raw=archive.read(i)
                    if len(raw)>1_000_000: raise ValueError('Non-image metadata exceeds cap')
                    path=OUT / f'{key}_metadata_{len(metadata):02d}_attempt_{attempt:02d}{Path(i.filename).suffix}'
                    path.write_bytes(raw)
                    metadata.append({'archive_path':i.filename,'file':path.name,'bytes':len(raw),'sha256':sha(path),
                                     'crc32_verified_by_zipfile':True})
            records.append({'key':key,'file_id':file_id,'archive_bytes':size,'public_full_md5_not_recomputed':public_md5,
                            'members':members,'nonimage_metadata':metadata,'summary':summarize(members),'directory_read_complete':True})
        except Exception as exc:
            errors.append(key+': '+type(exc).__name__+': '+str(exc))
            records.append({'key':key,'file_id':file_id,'directory_read_complete':False,'error':errors[-1]})
    url='https://ndownloader.figshare.com/files/54605609'
    readme={'url':url,'expected_bytes':2059,'expected_md5':'50ea39d80230c06b9bcd6018f3f4ab46'}
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-source-header-audit/1.0'}),timeout=30) as response:
            raw=response.read(2060)
            readme['http_status']=response.status
        path=OUT / f'official_readme_attempt_{attempt:02d}.md'
        path.write_bytes(raw)
        digest=hashlib.md5(raw).hexdigest()
        readme.update(file=path.name,bytes=len(raw),actual_md5=digest,sha256=sha(path))
        if len(raw)!=2059 or digest!=readme['expected_md5']:
            raise ValueError('Official README size/MD5 differs')
    except Exception as exc:
        readme['error']=f'{type(exc).__name__}: {exc}'
        errors.append('README: '+readme['error'])
    result={'attempt':attempt,'created_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha(__file__),'plan_sha256':sha(PLAN),
            'scope':'public ZIP directory/non-image metadata only; no pixel decoding or full archive MD5 assertion',
            'records':records,'requests':ledger,'readme':readme,'range_bytes_transferred':sum(r.get('bytes',0) for r in ledger),
            'patient_pixels_decoded':False,'full_archive_downloaded':False,'errors':errors}
    (OUT / f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('attempt','range_bytes_transferred','errors')},ensure_ascii=False))
    for r in records:
        print(json.dumps({k:r.get(k) for k in ('key','directory_read_complete','summary','nonimage_metadata','error')},ensure_ascii=False))
    if not readme.get('error'):
        print((OUT / readme['file']).read_text(encoding='utf-8'))
    return int(bool(errors))

if __name__=='__main__':
    raise SystemExit(main())
