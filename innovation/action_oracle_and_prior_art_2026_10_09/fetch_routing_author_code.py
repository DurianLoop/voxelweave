"""Verify author-listed17KB archive and save bounded text only; never execute archive code."""
import sys,time,json,gzip,ssl,urllib.request,hashlib,io,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,read,bind,entry,dump
started=time.perf_counter();resource_guard();out=HERE/'routing_author_code_attempt01';out.mkdir(exist_ok=False)
metadata=HERE/'author_metadata_attempt01/receipt.json';r=read(metadata);row=next(x for x in r['records'] if x['kind']=='routing_implementation');assert row['complete']
bind(row['source']['saved']);record=json.loads(gzip.decompress((ROOT/row['source']['saved']['path']).read_bytes()))
item=record['files'][0];assert item['size']==17555 and item['checksum']=='md5:0631d0422de239e7175884dc406c63eb'
url=item['links']['self'];assert url.startswith('https://zenodo.org/api/records/18331077/')
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
    data=response.read(17556);assert len(data)==17555;http=dict(requested_url=url,effective_url=response.url,http_status=response.status)
assert hashlib.md5(data).hexdigest()==item['checksum'].split(':')[1]
archive=out/'author_original.zip';archive.write_bytes(data);members=[];saved=[];total=0
with zipfile.ZipFile(io.BytesIO(data)) as z:
    for i,m in enumerate(z.infolist()):
        members.append(dict(member=m.filename,uncompressed_bytes=m.file_size,compressed_bytes=m.compress_size))
        if m.is_dir() or Path(m.filename).suffix.lower() not in ['.py','.md','.txt','.json','.yml','.yaml']:continue
        assert m.file_size<=150000;raw=z.read(m);total+=len(raw);assert total<=500000
        text=raw.decode('utf-8');p=out/(f'member{i:03d}_'+Path(m.filename).name);p.write_bytes(raw)
        saved.append(dict(member=m.filename,source=entry(p),lines=len(text.splitlines())))
result=dict(complete=True,errors=[],http=http,archive=entry(archive),author_MD5_matched=True,members=members,saved_text=saved,
    source_bindings=[entry(Path(__file__)),entry(metadata),row['source']['saved']],archive_extracted_to_paths=False,author_code_executed=False,
    files_actually_read_as_code=False,medical_arrays_loaded=0,patient_information_uploaded=False,elapsed_seconds=time.perf_counter()-started,goal_status='active')
dump(out/'receipt.json',result);print(json.dumps(dict(complete=True,author_MD5_matched=True,saved_text=saved,members=members)),flush=True)
