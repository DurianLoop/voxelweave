"""Read the omitted Algorithm1 text, math table identities and actual public-code links from saved HTML."""
import gzip,sys,json,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
HERE=Path(__file__).resolve().parent
class Inspect(HTMLParser):
 def __init__(self):super().__init__();self.figures=[];self.current=None;self.links=[];self.tables=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='figure':self.current=dict(attrs=a,text=[])
  if tag=='table':self.tables.append(a)
  if a.get('href') and ('github' in a['href'].lower() or 'gitlab' in a['href'].lower()):self.links.append(a['href'])
 def handle_data(self,data):
  if self.current is not None:self.current['text'].append(data)
 def handle_endtag(self,tag):
  if tag=='figure' and self.current is not None:
   self.current['text']=' '.join(''.join(self.current['text']).split());self.figures.append(self.current);self.current=None
p=Inspect();p.feed(gzip.decompress((HERE/'gin_primary_html_attempt02/primary.html.gz').read_bytes()).decode())
print('Algorithm1:',json.dumps([v for v in p.figures if 'Algorithm 1' in v['text']],ensure_ascii=False))
print('Table identities:',json.dumps(p.tables,ensure_ascii=False));print('Public-code links:',json.dumps(sorted(set(p.links))))
root=ET.fromstring(gzip.decompress((HERE/'gin_author_locator_attempt01/arxiv.gz').read_bytes()))
print('arXiv comment:',[e.text for e in root.iter() if e.tag.rsplit('}',1)[-1]=='comment'])
