"""Fetch an index-identified preprint HTML and extract text, without counting it read."""
import sys,time,json,re,urllib.request,ssl
from pathlib import Path
import search_primary_candidates as h
sys.path.insert(0,str(h.ROOT/'full_support_oracle_and_vinn_followup_2026_10_08'))
from parse_vinn_html import DOM,Node
HERE=Path(__file__).resolve().parent
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();h.guard();out=HERE/'hallucination_primary_attempt01';out.mkdir(exist_ok=False)
 idx=json.loads((HERE/'arxiv_index_attempt01/receipt.json').read_text(encoding='utf-8'));entry=idx['entries'][0]
 norm=lambda s:re.sub('[^a-z0-9]','',s.lower())
 cr=json.loads((HERE/'crossref_attempt01/01.json').read_text(encoding='utf-8'))['message']
 assert norm(cr['title'][0])==norm(entry['title']) and [a['family'] for a in cr['author']]==['Bhadra','Kelkar','Brooks','Anastasio']
 assert entry['id']=='http://arxiv.org/abs/2012.00646v3';url='https://arxiv.org/html/2012.00646v3';row=dict(requested_url=url,complete=False,index_source_sha256=h.sha(HERE/'arxiv_index_attempt01/receipt.json'),doi_metadata_sha256=h.sha(HERE/'crossref_attempt01/01.json'))
 try:
  ctx=ssl.create_default_context();op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),h.Redirect());req=urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'text/html'})
  with op.open(req,timeout=30) as response:
   data=response.read(2_000_001);assert len(data)<=2_000_000 and response.status==200
   row.update(status=response.status,effective_url=response.geturl(),headers=dict(response.headers.items()))
  dom=DOM();dom.feed(data.decode('utf-8'));nodes=list(dom.root.nodes());articles=[n for n in nodes if n.tag=='article'];assert len(articles)==1
  article=articles[0];assert norm(entry['title']) in norm(article.text())
  for author in ['Bhadra','Kelkar','Brooks','Anastasio']:assert author in article.text()
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
  remaining=2_000_000-sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
  assert len(data)+len(json.dumps(blocks,ensure_ascii=False).encode('utf-8'))+len(json.dumps(tables,ensure_ascii=False).encode('utf-8'))+30000<remaining,'Whole stage 2MB bound before writes'
  p=out/'maintext.html'
  with p.open('xb') as f:f.write(data)
  h.dump(out/'blocks.json',blocks);h.dump(out/'tables.json',tables)
  row.update(complete=True,source=dict(path=p.relative_to(h.ROOT).as_posix(),bytes=len(data),sha256=h.sha(p)),version='2012.00646v3',doi=cr['DOI'],identity_title_and_four_authors_match=True,blocks=len(blocks),headings=[dict(index=v['index'],text=v['text']) for v in blocks if v['kind']=='title'],tables=len(tables),fulltexts_actually_read=0,figure_pixels_read=False,final_publisher_version_read=False)
 except Exception as e:row['error']=repr(e)
 row.update(elapsed_seconds=time.perf_counter()-started,resources=h.guard());h.dump(out/'receipt.json',row);print(json.dumps(row,ensure_ascii=False),flush=True);return int(not row['complete'])
if __name__=='__main__':raise SystemExit(main())
