"""Read-only original-version locators; no primary reading count from search responses."""
import sys,ssl,urllib.request,urllib.parse,time,gzip,json,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard
started=time.perf_counter();out=HERE/'gin_author_locator_attempt01';out.mkdir(exist_ok=False)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
doi='10.1109/TMI.2022.3224067';title='Causality-Inspired Single-Source Domain Generalization for Medical Image Segmentation'
queries=[('arxiv','https://export.arxiv.org/api/query?'+urllib.parse.urlencode(dict(search_query='ti:"'+title+'"',max_results=2))),
 ('openalex','https://api.openalex.org/works/https://doi.org/'+doi)]
records=[]
for name,url in queries:
 row=dict(name=name,complete=False,requested_url=url,maintext_actually_read=False)
 try:
  v=resource_guard();assert v['workspace_free_bytes']-43_300_000>=8_000_000_000 and time.perf_counter()-started<180
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
   data=response.read(300_001);assert len(data)<=300_000;row.update(effective_url=response.url,http_status=response.status)
  path=out/(name+'.gz');path.write_bytes(gzip.compress(data,mtime=0));row['saved']=entry(path)
  if name=='arxiv':
   root=ET.fromstring(data);ns={'a':'http://www.w3.org/2005/Atom'};entries=[]
   for e in root.findall('a:entry',ns):
    entries.append(dict(id=e.findtext('a:id',namespaces=ns),title=' '.join(e.findtext('a:title',namespaces=ns).split()),
     published=e.findtext('a:published',namespaces=ns),updated=e.findtext('a:updated',namespaces=ns),
     authors=[n.findtext('a:name',namespaces=ns) for n in e.findall('a:author',ns)],
     links=[x.attrib for x in e.findall('a:link',ns)],summary=' '.join(e.findtext('a:summary',namespaces=ns).split())))
   row['entries']=entries
  else:
   obj=json.loads(data);assert obj['doi'].casefold()=='https://doi.org/'+doi.casefold()
   row.update(title=obj['title'],publication_year=obj['publication_year'],open_access=obj['open_access'],
    primary_location=obj['primary_location'],best_oa_location=obj['best_oa_location'],locations=obj['locations'],
    authors=[a['author']['display_name'] for a in obj['authorships']])
  row['complete']=True
 except Exception as e:row['error']=dict(type=type(e).__name__,message=str(e))
 records.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<500_000
dump(out/'receipt.json',dict(complete=all(r['complete'] for r in records),records=records,new_primary_maintexts_read=0,
 source_bindings=[entry(p) for p in [Path(__file__),HERE/'GIN_AUTHOR_VERSION_PROTOCOL.md',HERE/'gin_ssc_identity_attempt01/receipt.json']],
 medical_data_uploaded=False,elapsed_seconds=time.perf_counter()-started))
