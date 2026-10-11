"""Authenticated text acquisition; independent of any experimental score."""
import hashlib,json,sys,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/anchor_representation_fulltexts_2026-10-03'
PAPERS=[('sparse_overfit_2023','PMC10434268','10.1117/1.jmi.10.4.044007'),('contour_interpolation_2022','PMC9768435','10.1117/1.jmi.9.6.064003'),('iterative_contours_2023','PMC9889459','10.1007/s11548-022-02730-z')]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def txt(e): return ' '.join(''.join(e.itertext()).split())
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);rows=[];opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for key,pmcid,doi in PAPERS:
  row=dict(key=key,pmcid=pmcid,expected_doi=doi,started_utc=datetime.now(timezone.utc).isoformat(),fulltext_acquired=False,actual_reading_completed=False);p=OUT/(key+'_attempt_01.xml')
  row['url']='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode(dict(db='pmc',id=pmcid[3:],rettype='full',retmode='xml'))
  try:
   with opener.open(urllib.request.Request(row['url'],headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:
    raw=response.read(12000001);row.update(http_status=response.status,final_url=response.url)
   p.write_bytes(raw)
   if len(raw)>12000000: raise ValueError('12 MB cap exceeded')
   root=ET.fromstring(raw);article=root if root.tag=='article' else root.find('.//article')
   if article is None or article.find('body') is None: raise ValueError('Authenticated body missing')
   dois=[txt(e) for e in article.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi']
   if doi.lower() not in [x.lower() for x in dois]: raise ValueError('DOI mismatch')
   segments=[(e.tag,txt(e)) for e in article.find('body').iter() if e.tag in ('title','p','table-wrap','fig','disp-formula')]
   floats=article.find('floats-group')
   if floats is not None: segments += [(e.tag,txt(e)) for e in floats if e.tag in ('table-wrap','fig')]
   out=OUT/(key+'_maintext.txt');out.write_text('\n\n'.join('[%04d %s] %s'%(i,tag,text) for i,(tag,text) in enumerate(segments))+'\n',encoding='utf-8');perms=article.find('.//permissions')
   row.update(fulltext_acquired=True,title=txt(article.find('.//article-title')),dois=dois,paragraphs=len(segments),text_file=out.name,text_sha256=sha(out),permissions=txt(perms) if perms is not None else None,extraction_warning='Flattened MathML/tables and captions; no supplementary or visual image review')
  except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
  if p.exists(): row.update(raw_file=p.name,raw_sha256=sha(p),bytes=p.stat().st_size)
  row['finished_utc']=datetime.now(timezone.utc).isoformat();rows.append(row);print(json.dumps({k:row.get(k) for k in ('key','title','fulltext_acquired','paragraphs','error')},ensure_ascii=False),flush=True)
 with (OUT/'attempt_01.json').open('x',encoding='utf-8') as f: json.dump(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),plan_sha256=sha(ROOT/'2026-10-03_anchor_representation_fulltext_selection.md'),papers=rows),f,ensure_ascii=False,indent=2)
 query='(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:lesion AND (TITLE_ABS:"random forest" OR TITLE_ABS:"decision forest") AND TITLE_ABS:segmentation AND FIRST_PDATE:[1900-01-01 TO 2020-12-31]'
 row=dict(query=query,started_utc=datetime.now(timezone.utc).isoformat());p=OUT/'historical_forest_attempt_01.response';row['url']='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query,format='json',resultType='core',pageSize=8))
 try:
  with opener.open(urllib.request.Request(row['url'],headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response: raw=response.read(5000001);row.update(http_status=response.status,final_url=response.url)
  p.write_bytes(raw)
  if len(raw)>5000000: raise ValueError('5 MB cap exceeded')
  data=json.loads(raw);row.update(reported_total=data['hitCount'],items=data['resultList']['result'])
 except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
 if p.exists(): row.update(raw_file=p.name,raw_sha256=sha(p),bytes=p.stat().st_size)
 row['finished_utc']=datetime.now(timezone.utc).isoformat()
 with (OUT/'historical_forest_attempt_01.json').open('x',encoding='utf-8') as f: json.dump(row,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(historical_forest_returned=len(row.get('items',[])),error=row.get('error'))),flush=True)
if __name__=='__main__': main()
