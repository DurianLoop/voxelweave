"""One exact DOI PMC route; acquisition is not reading."""
import sys,json,ssl,urllib.request,urllib.parse,time,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
DOI='10.1016/j.neuroimage.2020.117366'
def dump(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def guard():
 r=resource_guard();remaining=1_200_000-sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());assert remaining>500_000
 assert r['workspace_free_bytes']-2_000_000-3_000_000-2_800_000-remaining>=8_000_000_000
def fetch(url,p,limit):
 guard();context=ssl.create_default_context();assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
 class Redirect(urllib.request.HTTPRedirectHandler):
  max_redirections=3;max_repeats=1
  def redirect_request(self,req,fp,code,msg,headers,newurl):
   assert urllib.parse.urlsplit(newurl).scheme=='https'
   return super().redirect_request(req,fp,code,msg,headers,newurl)
 op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context),Redirect())
 with op.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0'}),timeout=30) as res:
  data=res.read(limit+1);assert len(data)<=limit and res.status==200
  provenance=dict(requested_url=url,effective_url=res.geturl(),status=res.status,headers=dict(res.headers.items()))
 with p.open('xb') as f:f.write(data)
 provenance['source']=entry(p);return data,provenance
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();guard();out=HERE/'tanno_pmc_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],requests=[],DOI=DOI,fulltext_obtained=False,actual_reading_completed=False,publication_claim_confirmed=False,goal_status='active')
 try:
  url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode(dict(db='pmc',term=DOI+'[Article Identifier]',retmode='json',retmax=2))
  data,provenance=fetch(url,out/'index.json',20000);r['requests'].append(provenance);index=json.loads(data)
  ids=index['esearchresult']['idlist'];assert len(ids)==1 and index['esearchresult']['count']=='1','Unique exact-DOI public PMC article not found'
  url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode(dict(db='pmc',id=ids[0],retmode='xml'))
  data,provenance=fetch(url,out/'article.xml',450000);r['requests'].append(provenance);tree=ET.fromstring(data)
  articles=[tree] if tree.tag=='article' else tree.findall('.//article');assert len(articles)==1;article=articles[0]
  title=' '.join(''.join(article.find('./front/article-meta/title-group/article-title').itertext()).split())
  dois=[n.text for n in article.findall('./front/article-meta/article-id') if n.attrib.get('pub-id-type')=='doi']
  first=article.find('./front/article-meta/contrib-group/contrib/name/surname');assert first is not None and first.text=='Tanno'
  assert DOI in dois and title=='Uncertainty modelling in deep learning for safer neuroimage enhancement: Demonstration in diffusion MRI'
  body=article.find('body');assert body is not None and len(body)>0
  blocks=[]
  for node in body.iter():
   if node.tag in ('title','p','caption','table-wrap','disp-formula'):
    txt=' '.join(''.join(node.itertext()).split())
    if txt:blocks.append(dict(index=len(blocks),kind=node.tag,text=txt))
  dump(out/'blocks.json',blocks)
  r.update(complete=True,fulltext_obtained=True,title=title,PMCID='PMC'+ids[0],body_blocks=len(blocks),sources=[entry(out/'article.xml'),entry(out/'blocks.json')])
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
 r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
