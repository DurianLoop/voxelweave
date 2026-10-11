"""Expose previously omitted HTML algorithm; actual reading registered later."""
import gzip,json,time
from html.parser import HTMLParser
from resource_guard_v1 import HERE,guard,entry,dump
class Lines(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.depth=0;self.active=None;self.rows=[]
 def handle_starttag(self,tag,attrs):
  if tag=='span':
   self.depth+=1;a=dict(attrs)
   if 'ltx_listingline' in a.get('class','').split():
    assert self.active is None;self.active=dict(depth=self.depth,id=a.get('id'),parts=[])
 def handle_data(self,data):
  if self.active is not None:self.active['parts'].append(data)
 def handle_endtag(self,tag):
  if tag=='span':
   if self.active is not None and self.depth==self.active['depth']:
    self.rows.append(dict(id=self.active['id'],text=' '.join(''.join(self.active['parts']).split())));self.active=None
   self.depth-=1
started=time.perf_counter();before=guard(started)
p=HERE/'primary_html_attempt01/greedy/primary.html.gz';parser=Lines();parser.feed(gzip.decompress(p.read_bytes()).decode('utf-8'))
assert parser.rows and all(v['id'].startswith('algorithm1.') for v in parser.rows)
out=HERE/'algorithm_exposure_attempt01';out.mkdir(exist_ok=False)
dump(out/'receipt.json',dict(complete=True,errors=[],source=entry(p),lines=parser.rows,
 actual_reading_completed=False,source_bindings=[entry(__import__('pathlib').Path(__file__)),entry(HERE/'CPU_EXPLORATION_PROTOCOL.md')],resources_before=before,resources_after=guard(started)))
for row in parser.rows:print(row['id']+' '+row['text'])
