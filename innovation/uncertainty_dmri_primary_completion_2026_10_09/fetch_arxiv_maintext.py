"""Fixed2019 manuscript HTML; no inferred equivalence to publisher final."""
import sys,json,time,ssl,urllib.request,hashlib,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
sys.path.insert(0,str(ROOT/'full_support_oracle_and_vinn_followup_2026_10_08'))
from parse_vinn_html import DOM,Node
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def dump(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def guard():
 r=resource_guard();remaining=2_000_000-sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
 assert remaining>0 and r['workspace_free_bytes']-remaining-2_000_000-3_000_000-2_800_000-1_200_000>=8_000_000_000
 return r
class Redirect(urllib.request.HTTPRedirectHandler):
 max_redirections=3;max_repeats=1
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  assert newurl.startswith('https://');return super().redirect_request(req,fp,code,msg,headers,newurl)
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();guard();out=HERE/'arxiv_html_attempt01';out.mkdir(exist_ok=False)
 idxp=ROOT/'task_capacity_mechanism_audit_2026_10_09/tanno_arxiv_identity_attempt01/receipt.json';idx=json.loads(idxp.read_text(encoding='utf-8'))
 crp=ROOT/'conditional_uq_and_task_capacity_followup_2026_10_09/crossref_attempt01/00.json';cr=json.loads(crp.read_text(encoding='utf-8'))['message']
 record=next(v for v in idx['records'] if v['id']=='http://arxiv.org/abs/1907.13418v1')
 surnames=[a['family'] for a in cr['author']];assert surnames==['Tanno','Worrall','Kaden','Ghosh','Grussu','Bizzi','Sotiropoulos','Criminisi','Alexander']
 assert all(family in author for family,author in zip(surnames,record['authors'])) and len(record['authors'])==9
 url='https://arxiv.org/html/1907.13418v1';r=dict(complete=False,errors=[],requested_url=url,fulltexts_actually_read=0,version='1907.13418v1',final_publisher_version_read=False,manuscript_title=record['title'],journal_title=cr['title'][0],journal_DOI=cr['DOI'],all_nine_author_surnames_and_order_match=True,source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md'),entry(idxp),entry(crp)])
 try:
  ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
  op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),Redirect())
  with op.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'text/html'}),timeout=30) as res:
   data=res.read(1_000_001);assert len(data)<=1_000_000 and res.status==200;r.update(status=res.status,effective_url=res.geturl(),headers=dict(res.headers.items()))
  dom=DOM();dom.feed(data.decode('utf-8'));articles=[n for n in dom.root.nodes() if n.tag=='article'];assert len(articles)==1;article=articles[0]
  norm=lambda s:re.sub('[^a-z0-9]','',s.lower());assert norm(record['title']) in norm(article.text())
  for family in surnames:assert family in article.text()
  blocks=[]
  def walk(n,scope):
   if not isinstance(n,Node):return
   if n.tag in {'section','aside','div'} and n.attrs.get('id'):scope=scope+[n.attrs['id']]
   if n.tag in {'h1','h2','h3','h4','h5','h6','p','figure','table'}:
    text=n.text()
    if text:blocks.append(dict(index=len(blocks),kind='title' if n.tag.startswith('h') else n.tag,id=n.attrs.get('id'),scope=scope,text=text))
    return
   for child in n.children:walk(child,scope)
  walk(article,['article'])
  tables=[dict(id=n.attrs.get('id'),rows=[[c.text() for c in row.children if isinstance(c,Node) and c.tag in {'td','th'}] for row in n.nodes() if row.tag=='tr']) for n in article.nodes() if n.tag=='table']
  assert len(data)+len(json.dumps(blocks,ensure_ascii=False).encode('utf-8'))+len(json.dumps(tables,ensure_ascii=False).encode('utf-8'))+30000<2_000_000-sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
  p=out/'maintext.html'
  with p.open('xb') as f:f.write(data)
  dump(out/'blocks.json',blocks);dump(out/'tables.json',tables)
  r.update(complete=True,source=entry(p),extraction_sources=[entry(out/'blocks.json'),entry(out/'tables.json')],blocks=len(blocks),headings=[dict(index=v['index'],text=v['text']) for v in blocks if v['kind']=='title'],table_nodes=len(tables),figure_pixels_read=False)
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
 r.update(elapsed_seconds=time.perf_counter()-started,resources=guard());dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
