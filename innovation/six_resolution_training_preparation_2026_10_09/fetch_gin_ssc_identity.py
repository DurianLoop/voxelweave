"""DOI-exact original GIN/SSC metadata; public full text only if identity verified."""
import sys,time,ssl,urllib.request,urllib.parse,json,gzip,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,dump
ITEMS=[('gin','10.1109/TMI.2022.3224067'),('ssc','10.1007/978-3-642-40811-3_24')]
started=time.perf_counter();out=HERE/'gin_ssc_identity_attempt01';out.mkdir(exist_ok=False)
def guard():
 r=resource_guard();size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
 assert time.perf_counter()-started<180 and size<500_000
 assert r['workspace_free_bytes']-42_800_000-(500_000-size)>=8_000_000_000
 return r
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
def fetch(url,name,limit):
 guard()
 with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
  data=response.read(limit+1);assert len(data)<=limit;record=dict(requested_url=url,effective_url=response.url,http_status=response.status)
 p=out/(name+'.gz')
 with p.open('xb') as f:f.write(gzip.compress(data,mtime=0))
 record['saved']=entry(p);return data,record
records=[]
for key,doi in ITEMS:
 row=dict(key=key,doi=doi,complete=False,maintext_actually_read=False)
 try:
  query='DOI:"'+doi+'"';url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query,format='json',resultType='core',pageSize=3))
  data,record=fetch(url,key+'_metadata.json',120_000);meta=json.loads(data);hits=meta['resultList']['result']
  assert len(hits)==1 and hits[0]['doi'].casefold()==doi.casefold();hit=hits[0]
  row.update(complete=True,metadata=record,identity=hit)
  pmcid=hit.get('pmcid')
  if pmcid and hit.get('isOpenAccess')=='Y':
   raw,source=fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML',key+'_full.xml',280_000)
   root=ET.fromstring(raw);ids={e.get('pub-id-type'):''.join(e.itertext()) for e in root.findall('./front/article-meta/article-id')}
   assert ids.get('doi','').casefold()==doi.casefold();row['public_primary_source']=source
 except Exception as e:row['error']=dict(type=type(e).__name__,message=str(e));row['complete']=False
 records.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
result=dict(complete=all(v['complete'] for v in records),errors=[],records=records,new_maintexts_actually_read=0,
 medical_data_uploaded=False,author_code_executed=False,source_bindings=[entry(p) for p in [Path(__file__),HERE/'GIN_PRIMARY_SOURCE_PROTOCOL.md',
 ROOT/'acquisition_action_generalization_author_2026_10_09/primary_xml_attempt01/dgtta.xml.gz']],resources=guard(),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',result)
