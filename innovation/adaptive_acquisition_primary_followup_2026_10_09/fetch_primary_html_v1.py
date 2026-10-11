"""Fixed-version public HTML and lossless source/extraction for three selected prior papers."""
import sys,time,ssl,gzip,json,urllib.request,re
from html.parser import HTMLParser
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard
started=time.perf_counter()
def guard():
    v=resource_guard();remaining=22_800_000
    for p,cap in ((ROOT/'six_resolution_training_preparation_2026_10_09',7_000_000),(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',20_000_000),(ROOT/'gin_accepted_primary_followup_2026_10_09',6_000_000),(HERE,2_000_000)):
        size=sum(q.stat().st_size for q in p.rglob('*') if q.is_file());assert size<cap;remaining+=cap-size
    assert v['workspace_free_bytes']-remaining>=8_000_000_000 and time.perf_counter()-started<180
    v['remaining_all_stage_allowance_bytes']=remaining;return v

class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.article=0;self.stack=[];self.blocks=[];self.formulas=[];self.tables=[];self.title=[];self.in_title=False;self.images=[];self.meta=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='title':self.in_title=True
        if tag=='meta':self.meta.append(a)
        if tag=='article':self.article+=1
        if not self.article:return
        if tag=='img':self.images.append(a)
        if tag in ('h1','h2','h3','h4','p','figcaption','table','math'):
            self.stack.append(dict(tag=tag,id=a.get('id'),alttext=a.get('alttext'),text=[],raw=[self.get_starttag_text()]))
        for v in self.stack:
            if v['tag']=='math' and tag!='math':v['raw'].append(self.get_starttag_text())
    def handle_data(self,data):
        if self.in_title:self.title.append(data)
        for v in self.stack:
            v['text'].append(data)
            if v['tag']=='math':v['raw'].append(data)
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
        for v in self.stack:
            if v['tag']=='math':v['raw'].append('</'+tag+'>')
        indices=[i for i,v in enumerate(self.stack) if v['tag']==tag]
        if indices:
            v=self.stack.pop(indices[-1]);text=' '.join(''.join(v['text']).split())
            if tag=='math':self.formulas.append(dict(id=v['id'],alttext=v['alttext'],mathml=''.join(v['raw'])))
            elif tag=='table':self.tables.append(dict(id=v['id'],text=text))
            if tag!='math' and text and not (tag=='p' and any(x['tag'] in ('table','figcaption') for x in self.stack)):
                self.blocks.append(dict(index=len(self.blocks),tag=tag,id=v['id'],text=text))
        if tag=='article':self.article-=1

locator=read(HERE/'source_locator_attempt01/receipt.json');assert locator['complete']
identified={r['id'].rsplit('/',1)[-1]:r for row in locator['records'] for r in row['entries']}
selected=[('greedy','2010.16262v2'),('openmasc','2609.32343v1'),('active_fewshot','2607.22371v1')]
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
before=guard();out=HERE/'primary_html_attempt01';out.mkdir(exist_ok=False);records=[]
for name,version in selected:
    guard();expected=identified[version];url='https://arxiv.org/html/'+version;row=dict(name=name,version=version,requested_url=url,complete=False,text_actually_read=False,figure_pixels_actually_inspected=False)
    try:
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
            raw=response.read(1_200_001);assert len(raw)<=1_200_000;row.update(effective_url=response.url,http_status=response.status)
        parser=ArticleParser();parser.feed(raw.decode('utf-8'));assert parser.blocks and parser.title
        first_title=next(v['text'] for v in parser.blocks if v['tag']=='h1')
        normalize=lambda s:re.sub(r'[^a-z0-9]','',s.casefold())
        assert normalize(expected['title']) in normalize(first_title),(expected['title'],first_title)
        folder=out/name;folder.mkdir(exist_ok=False);(folder/'primary.html.gz').write_bytes(gzip.compress(raw,mtime=0))
        for n,body in (('blocks',parser.blocks),('formulas',parser.formulas),('tables',parser.tables),('images',parser.images),('meta',parser.meta)):
            (folder/(n+'.json.gz')).write_bytes(gzip.compress((json.dumps(body,ensure_ascii=False)+'\n').encode(),mtime=0))
        row.update(complete=True,title=first_title,blocks=len(parser.blocks),math_nodes=len(parser.formulas),HTML_table_nodes=len(parser.tables),images=len(parser.images),
            headings=[v for v in parser.blocks if v['tag'] in ('h1','h2','h3','h4')],source_files=[entry(p) for p in sorted(folder.iterdir())])
    except Exception as e:row.update(error_type=type(e).__name__,error=str(e),http_status=getattr(e,'code',None))
    records.append(row);guard();print(json.dumps(row,ensure_ascii=False),flush=True)
    if row.get('http_status')==429:break
r=dict(complete=all(v['complete'] for v in records) and len(records)==3,errors=[v['error'] for v in records if 'error' in v],records=records,
    primary_maintexts_actually_read=0,author_code_executed=False,patient_data_uploaded=False,
    source_bindings=[entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION.md',HERE/'source_locator_attempt01/receipt.json')],
    resources_before=before,resources_after=guard(),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r);raise SystemExit(int(not r['complete']))
