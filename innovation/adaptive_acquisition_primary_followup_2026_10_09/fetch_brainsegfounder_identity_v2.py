"""Retain known title variation and verify fixed arXiv version plus author front matter."""
import ast,gzip,json,re,ssl,time,urllib.request,html,traceback
from html.parser import HTMLParser
from pathlib import Path
from resource_guard_v1 import HERE,guard,read,entry,dump
started=time.perf_counter();before=guard(started);out=HERE/'brainsegfounder_identity_html_attempt02';out.mkdir(exist_ok=False)
locator=read(HERE/'strong_task_source_locator_attempt01/receipt.json');expected=next(row for v in locator['records'] for row in v['entries'] if row['id'].endswith('2406.10395v3'))
r=dict(complete=False,errors=[],requested_version='2406.10395v3',metadata_title=expected['title'],text_actually_read=False,figure_pixels_actually_inspected=False)
normalize=lambda x:re.sub('[^a-z0-9]','',x.casefold())
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
try:
 url='https://arxiv.org/html/2406.10395v3'
 with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
  data=response.read(1200001);assert len(data)<=1200000;r.update(http_status=response.status,effective_url=response.url)
 rawpath=out/'primary.html.gz';rawpath.write_bytes(gzip.compress(data,mtime=0));r['saved_primary_before_identity_check']=entry(rawpath)
 s=data.decode('utf-8');source=HERE/'fetch_primary_html_v1.py';tree=ast.parse(source.read_text(encoding='utf-8'));node=next(v for v in tree.body if isinstance(v,ast.ClassDef) and v.name=='ArticleParser')
 ns={'HTMLParser':HTMLParser};exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),ns)
 parser=ns['ArticleParser']();parser.feed(s);first=next(v['text'] for v in parser.blocks if v['tag']=='h1')
 assert normalize(first) in {normalize(expected['title']),normalize('BrainSegFounder: Towards Foundation Models for Neuroimage Segmentation')}
 am=re.search(r'<div[^>]*class="[^"]*ltx_authors[^"]*"',s);assert am
 abstract=re.search(r'<div[^>]*class="[^"]*ltx_abstract[^"]*"',s[am.end():]);assert abstract
 front=html.unescape(re.sub('<[^>]+>',' ',s[am.start():am.end()+abstract.start()]));found=[a for a in expected['authors'] if normalize(a) in normalize(front)]
 assert len(found)==len(expected['authors'])==8,(found,front[:1000])
 assert r['effective_url']==url
 for name,body in [('blocks',parser.blocks),('formulas',parser.formulas),('tables',parser.tables),('images',parser.images),('meta',parser.meta)]:
  (out/(name+'.json.gz')).write_bytes(gzip.compress((json.dumps(body,ensure_ascii=False)+'\n').encode(),mtime=0))
 r.update(complete=True,title=first,all8_expected_authors_in_front_matter=found,known_metadata_HTML_title_variation_retained=True,blocks=len(parser.blocks),
  headings=[v for v in parser.blocks if v['tag'] in ('h1','h2','h3','h4')],source_files=[entry(p) for p in sorted(out.iterdir())],
  identity_basis='Fixed official version URL + exact accepted title variant + all8 metadata authors in front matter; title variation preserved, not silently overwritten')
except Exception as e:r.update(error_type=type(e).__name__,error_http_status=getattr(e,'code',None));r['errors'].append(str(e));r['traceback']=traceback.format_exc()
r.update(source_bindings=[entry(Path(__file__)),entry(HERE/'fetch_primary_html_v1.py'),entry(HERE/'strong_task_source_locator_attempt01/receipt.json'),entry(HERE/'foundation_primary_html_attempt01/receipt.json')],
 protocol_amendment='Accept two explicitly enumerated title variants only when fixed official URL and all8 front-matter authors match; save raw response before identity assertion.',
 resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True);raise SystemExit(int(not r['complete']))
