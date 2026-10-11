"""Bounded anonymous public arXiv metadata; no search result counts as primary reading."""
import sys,time,ssl,urllib.request,urllib.parse,gzip,json,xml.etree.ElementTree as ET,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
started=time.perf_counter()
def guard():
    r=resource_guard();remaining=22_800_000
    for p,cap in ((ROOT/'six_resolution_training_preparation_2026_10_09',7_000_000),(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',20_000_000),(ROOT/'gin_accepted_primary_followup_2026_10_09',6_000_000),(HERE,2_000_000)):
        size=sum(v.stat().st_size for v in p.rglob('*') if v.is_file());assert size<cap;remaining+=cap-size
    assert r['workspace_free_bytes']-remaining>=8_000_000_000 and time.perf_counter()-started<180
    r['remaining_all_stage_allowance_bytes']=remaining;return r
out=HERE/'source_locator_attempt01';out.mkdir(exist_ok=False);before=guard()
queries=[dict(name='greedy_exact',search_query='ti:"Experimental design for MRI by greedy policy search"',max_results=2),
 dict(name='MRI_RL_sampling',search_query='all:"MRI" AND all:"sampling" AND all:"reinforcement"',max_results=6,sortBy='submittedDate',sortOrder='descending')]
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
rows=[]
for query in queries:
    guard();params={k:v for k,v in query.items() if k!='name'};url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode(params)
    row=dict(name=query['name'],query=params,requested_url=url,complete=False,maintext_actually_read=False)
    try:
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
            data=response.read(300_001);assert len(data)<=300_000;row.update(http_status=response.status,effective_url=response.url)
        p=out/(query['name']+'.xml.gz');p.write_bytes(gzip.compress(data,mtime=0));row['saved']=entry(p)
        atom=ET.fromstring(data);ns={'a':'http://www.w3.org/2005/Atom'};found=[]
        for node in atom.findall('a:entry',ns):
            found.append(dict(id=node.findtext('a:id',namespaces=ns),title=' '.join(node.findtext('a:title',namespaces=ns).split()),
                authors=[n.findtext('a:name',namespaces=ns) for n in node.findall('a:author',ns)],published=node.findtext('a:published',namespaces=ns),
                updated=node.findtext('a:updated',namespaces=ns),summary=' '.join(node.findtext('a:summary',namespaces=ns).split()),links=[n.attrib for n in node.findall('a:link',ns)]))
        row.update(complete=True,entries=found)
    except Exception as e:row.update(error_type=type(e).__name__,error=str(e),http_status=getattr(e,'code',None))
    rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
    if row.get('http_status')==429:break
r=dict(complete=all(v['complete'] for v in rows) and len(rows)==2,errors=[v['error'] for v in rows if 'error' in v],records=rows,
    primary_papers_read=0,source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md')],resources_before=before,resources_after=guard(),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r);raise SystemExit(int(not r['complete']))
