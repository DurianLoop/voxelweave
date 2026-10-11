"""Fetch public original PDFs and official NeurIPS discovery page, retain provenance."""
import hashlib,json,sys,urllib.request,re,importlib.util
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/masked_normalization_primary_2026-10-03'
REQUESTS=[
 ('region_normalization','https://ojs.aaai.org/index.php/AAAI/article/download/6967/6821','pdf'),
 ('partial_convolution','https://openaccess.thecvf.com/content_ECCV_2018/papers/Guilin_Liu_Image_Inpainting_for_ECCV_2018_paper.pdf','pdf'),
 ('neurips_2023_index','https://proceedings.neurips.cc/paper_files/paper/2023','html')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);rows=[];opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for key,url,kind in REQUESTS:
  row=dict(key=key,url=url,kind=kind,fulltext_acquired=False,actual_reading_completed=False)
  try:
   with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=25) as resp:raw=resp.read(20000001);row.update(http_status=resp.status,final_url=resp.url)
   path=OUT/(key+'.'+kind);path.write_bytes(raw);row.update(raw_file=path.name,raw_sha256=sha(path),bytes=len(raw));assert len(raw)<=20000000
   if kind=='pdf':
    assert raw.startswith(b'%PDF');from pypdf import PdfReader
    reader=PdfReader(path);texts=[p.extract_text() for p in reader.pages];textpath=OUT/(key+'_pages.json');textpath.write_text(json.dumps([dict(page=i+1,text=t) for i,t in enumerate(texts)],ensure_ascii=False,indent=2)+'\n',encoding='utf-8');flat=OUT/(key+'_maintext.txt');flat.write_text('\n\n'.join('[PAGE %d]\n%s'%(i+1,t) for i,t in enumerate(texts))+'\n',encoding='utf-8');row.update(fulltext_acquired=True,pages=len(texts),page_text_file=textpath.name,page_text_sha256=sha(textpath),text_file=flat.name,text_sha256=sha(flat),first_page_preview=texts[0][:300])
   else:
    s=raw.decode('utf-8');matches=re.findall(r'<a[^>]+href="([^"]+)"[^>]*>\s*Normalization.Equivariant Neural Networks with Application to Image Denoising\s*</a>',s,re.I);row['matching_links']=matches
  except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)
  rows.append(row);(OUT/'attempt_01.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),scope='Public publisher/conference primary sources; acquisition only, no reading claim yet.',requests=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:row.get(k) for k in ('key','fulltext_acquired','pages','matching_links','first_page_preview','error')},ensure_ascii=False),flush=True)
 print('PDF_DEPENDENCIES',json.dumps({k:bool(importlib.util.find_spec(k)) for k in ('fitz','pdfplumber','pypdf')},ensure_ascii=False))
if __name__=='__main__':main()
