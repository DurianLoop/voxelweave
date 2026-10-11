"""Read previously omitted raw-HTML Algorithm S.1 without extra dependencies."""
import gzip,re,json
from html.parser import HTMLParser
from resource_guard_v1 import HERE,guard,entry,dump
class Text(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.parts=[]
 def handle_data(self,data):self.parts.append(data)
guard();p=HERE/'foundation_primary_html_attempt01/swin_pretraining/primary.html.gz'
s=gzip.decompress(p.read_bytes()).decode('utf-8');lines=[]
for ident,raw in re.findall(r'<div id="(algx1\.l\d+)" class="ltx_listingline">(.*?)</div>',s,re.S):
 t=Text();t.feed(raw);lines.append(dict(id=ident,text=' '.join(''.join(t.parts).split())))
assert len(lines)>15 and len({v['id'] for v in lines})==len(lines)
out=HERE/'swin_algorithm_exposure_attempt01';out.mkdir(exist_ok=False)
dump(out/'receipt.json',dict(complete=True,errors=[],source=entry(p),reader_source=entry(__import__('pathlib').Path(__file__)),lines=lines,text_actually_read=False,scope='Exposure only; actual inspected returned chunk bound separately',author_code_executed=False))
for v in lines:print(v['id']+' '+v['text'])
print(json.dumps(dict(lines_exposed=len(lines),HTML_source_binding=entry(p)),ensure_ascii=False))
