"""One bounded Schannel alternative for all first-attempt TLS failures."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import re
import struct
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
import read_mslesseg_raw_t2_headers_2026_10_02 as helper

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/mslesseg_raw_t2_headers_2026-10-02'
PLAN=ROOT/'MSLESSEG_SEVEN_HEADER_SCHANNEL_FOLLOWUP_PLAN_2026-10-02.md'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    source_path=OUT/'attempt_01.json';source=json.loads(source_path.read_text(encoding='utf-8'))
    failed=[r for r in source['records'] if not r['header_complete']]
    if len(failed)!=7 or any('UNEXPECTED_EOF_WHILE_READING' not in r.get('error','') for r in failed):
        raise ValueError('Declared all-seven TLS failure set differs')
    attempt=len(list(OUT.glob('schannel_attempt_*.json')))+1
    selection={'source_sha256':sha(source_path),'plan_sha256':sha(PLAN),'members':failed}
    selected=OUT/f'schannel_selection_attempt_{attempt:02d}.json'
    selected.write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8')
    ledger=[];lock=threading.Lock();reserved=[0]
    version=subprocess.run(['curl.exe','--version'],capture_output=True,text=True,timeout=10).stdout
    if 'Schannel' not in version:raise ValueError('Expected separate Schannel TLS backend')
    def fetch(index,label,start,length):
        if length<=0 or length>65536:raise ValueError('Invalid range')
        with lock:
            if reserved[0]+length>256*1024:raise ValueError('Followup budget exceeded')
            reserved[0]+=length
        path=OUT/f'schannel_{index:03d}_{label}_attempt_{attempt:02d}.bin'
        headers=OUT/f'schannel_{index:03d}_{label}_attempt_{attempt:02d}.headers'
        entry={'member_index':index,'label':label,'start':start,'end':start+length-1,'requested_bytes':length}
        with lock:ledger.append(entry)
        try:
            proc=subprocess.run(['curl.exe','--silent','--show-error','--location','--noproxy','*',
                                 '--max-time','30','--connect-timeout','10','--max-filesize','65536',
                                 '--header','Accept-Encoding: identity','--range',f'{start}-{start+length-1}',
                                 '--output',str(path),'--dump-header',str(headers),'--write-out','%{http_code}',helper.URL],
                                capture_output=True,text=True,timeout=35)
            entry.update(curl_exit=proc.returncode,stderr=proc.stderr,http_status=int(proc.stdout.strip() or 0))
            if headers.exists():
                h=headers.read_text(encoding='latin1');ranges=re.findall(r'^Content-Range:\s*(.*)$',h,re.M|re.I)
                entry.update(headers_file=headers.name,headers_sha256=sha(headers),content_range=ranges[-1].strip() if ranges else None)
            if path.exists():entry.update(file=path.name,bytes=path.stat().st_size,sha256=sha(path))
            if proc.returncode!=0 or entry['http_status']!=206 or entry.get('content_range')!=f'bytes {start}-{start+length-1}/{helper.SIZE}' or entry.get('bytes')!=length:
                raise ValueError('curl/exact range validation failed')
            return path.read_bytes()
        except Exception as exc:
            entry['error']=f'{type(exc).__name__}: {exc}';raise
    def one(source_row):
        index=source_row['member_index'];member=source_row['central_directory']
        row={'member_index':index,'path':source_row['path'],'central_directory':member,'header_complete':False}
        try:
            offset=member['header_offset'];raw=fetch(index,'lfh',offset,30);fields=struct.unpack('<4s5H3I2H',raw)
            if fields[0]!=b'PK\x03\x04' or fields[3]!=8 or fields[2]&1:raise ValueError('ZIP local header differs')
            n,e=fields[-2:]
            if n+e>16384:raise ValueError('ZIP name/extra exceeds cap')
            name=fetch(index,'name_extra',offset+30,n+e)[:n].decode('utf-8' if fields[2]&2048 else 'cp437')
            if name!=row['path']:raise ValueError('ZIP member name differs')
            data_start=offset+30+n+e
            header=helper.header_only(fetch(index,'prefix8192',data_start,min(8192,member['compressed_bytes'])))
            if header is None:raise ValueError('Header unavailable within one prefix')
            decoded=helper.parse_header(header)
            path=OUT/f'schannel_{index:03d}_nifti_header_attempt_{attempt:02d}.bin';path.write_bytes(header)
            row.update(header_complete=True,header_file=path.name,header_bytes=len(header),header_sha256=sha(path),decoded=decoded,
                       data_start=data_start,member_full_crc_verified=False,gzip_trailer_verified=False)
        except Exception as exc:row['error']=f'{type(exc).__name__}: {exc}'
        print(json.dumps({k:row.get(k) for k in ('member_index','path','header_complete','error')}),flush=True)
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(one,failed))
    result={'attempt':attempt,'created_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha(__file__),
            'helper_sha256':sha(helper.__file__),'plan_sha256':sha(PLAN),'original_source_sha256':sha(source_path),
            'selection_file':selected.name,'selection_sha256':sha(selected),'curl_version':version,'records':records,'requests':ledger,
            'requested_range_bytes':reserved[0],'transferred_range_bytes':sum(r.get('bytes',0) for r in ledger),
            'complete_headers':sum(r['header_complete'] for r in records),'patient_pixels_decoded':False,
            'errors':[r['path']+': '+r['error'] for r in records if 'error' in r]}
    (OUT/f'schannel_attempt_{attempt:02d}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','requests','curl_version')},indent=2),flush=True)
    return int(bool(result['errors']))

if __name__=='__main__':
    raise SystemExit(main())
