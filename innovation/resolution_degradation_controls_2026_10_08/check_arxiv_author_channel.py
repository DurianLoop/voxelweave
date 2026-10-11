"""Exactly three bounded official arXiv title queries for already queued MRI papers."""
import sys,time,json,gzip,hashlib,urllib.request,urllib.parse,urllib.error,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
QUERIES=[('10.1016/j.jneumeth.2026.110834','ti:"3D segmentation framework for whole-brain segmentation from thick-slice brain MRI"'),
         ('10.1109/tmi.2026.3662706','ti:"LRD-ESR-Net"'),
         ('10.1016/j.compmedimag.2026.102786','ti:"Self-supervised isotropic reconstruction for abnormality detection in anisotropic MRI"')]


def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    journal=HERE/'full_real_pipeline_attempt01/fields.jsonl.gz'
    def guard():
        resource_guard();assert time.perf_counter()-started<180
        size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        reserve=max(0,1_500_000-journal.stat().st_size)+150_000+100_000
        assert size+reserve+100_000<5_000_000
    guard();out=HERE/'arxiv_author_channel_attempt01';out.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r=dict(complete=False,errors=[],records=[],new_maintexts_acquired=0,new_maintexts_actually_read=0,
           new_medical_effects=0,user_data_sent=False,confirmation_patients_opened=False,goal_status='active')
    ns={'a':'http://www.w3.org/2005/Atom','x':'http://arxiv.org/schemas/atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
    for i,(doi,query) in enumerate(QUERIES):
        guard();url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode(dict(search_query=query,start=0,max_results=3,sortBy='submittedDate',sortOrder='descending'))
        v=dict(doi_target=doi,query=query,url=url,candidates=[],actually_read_maintext=False);at=time.perf_counter()
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'MRI-research-public-literature-audit/1.0'})
            try:response=opener.open(request,timeout=30)
            except urllib.error.HTTPError as exc:response=exc
            with response:v['HTTP_status']=response.getcode();body=response.read(500_001)
            assert len(body)<=500000
            packed=gzip.compress(body,mtime=0);p=out/f'query_{i:02d}.xml.gz'
            assert sum(x.stat().st_size for x in out.glob('*.gz'))+len(packed)<=80000
            with p.open('xb') as f:f.write(packed)
            v.update(raw_response=entry(p),uncompressed_bytes=len(body),uncompressed_sha256=hashlib.sha256(body).hexdigest())
            assert v['HTTP_status']==200,f'HTTP status {v["HTTP_status"]}'
            feed=ET.fromstring(body);v['total_results']=int(feed.findtext('o:totalResults',default='0',namespaces=ns))
            for e in feed.findall('a:entry',ns):
                candidate=dict(id=e.findtext('a:id',namespaces=ns),title=' '.join((e.findtext('a:title',default='',namespaces=ns)).split()),
                    authors=[x.findtext('a:name',namespaces=ns) for x in e.findall('a:author',ns)],
                    DOI=e.findtext('x:doi',namespaces=ns),published=e.findtext('a:published',namespaces=ns),
                    links=[dict(x.attrib) for x in e.findall('a:link',ns)])
                candidate['exact_DOI_match']=candidate['DOI'] is not None and candidate['DOI'].lower()==doi.lower()
                v['candidates'].append(candidate)
        except Exception as exc:
            v['error']=type(exc).__name__+': '+str(exc);r['errors'].append(dict(doi=doi,error=v['error']))
        v['elapsed_seconds']=time.perf_counter()-at;r['records'].append(v)
        print(json.dumps(v,ensure_ascii=False),flush=True)
        if i<2:time.sleep(3)
    r.update(complete=len(r['records'])==3,elapsed_seconds=time.perf_counter()-started,
             source_bindings=[entry(p) for p in [Path(__file__),HERE/'ARXIV_AUTHOR_CHANNEL_PROTOCOL_TURN29.md',
                 HERE/'public_author_routes_attempt01/receipt.json',
                 ROOT/'literature/source_cache/recent_thickslice_primary_availability_attempt02_2026-10-07/doi2_metadata.response']])
    dump(out/'receipt.json',r);guard()
    print(json.dumps({k:v for k,v in r.items() if k not in ['records','source_bindings']},ensure_ascii=False),flush=True)
    return int(bool(r['errors']))


if __name__=='__main__':raise SystemExit(main())
