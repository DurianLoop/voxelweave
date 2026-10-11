"""Use installed Poppler; do not modify MRI environment or overwrite first failure."""
import hashlib,json,sys,urllib.request,re,subprocess,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/masked_normalization_primary_2026-10-03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');proof=OUT/'extraction_attempt_03.json';assert not proof.exists();opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[];pdftotext=shutil.which('pdftotext');assert pdftotext
 abstract='https://proceedings.neurips.cc/paper_files/paper/2023/hash/12143893d9d37c3569dda800b95cabd9-Abstract-Conference.html'
 html=(OUT/'normalization_equivariance_official_abstract.html').read_bytes();assert b'Normalization-Equivariant Neural Networks with Application to Image Denoising' in html
 from html.parser import HTMLParser
 class Links(HTMLParser):
  def __init__(self):super().__init__();self.hrefs=[]
  def handle_starttag(self,tag,attrs):
   if tag=='a':self.hrefs.extend(v for k,v in attrs if k=='href' and v.endswith('.pdf'))
 parser=Links();parser.feed(html.decode('utf-8'));paper=[x for x in parser.hrefs if 'Paper-Conference.pdf' in x];assert len(paper)==1
 from urllib.parse import urljoin
 url=urljoin(abstract,paper[0]);pdf=OUT/'normalization_equivariance.pdf'
 with opener.open(url,timeout=30) as response:raw=response.read(20000001)
 assert raw.startswith(b'%PDF') and len(raw)<=20000000;pdf.write_bytes(raw)
 for key,source in [('region_normalization','https://ojs.aaai.org/index.php/AAAI/article/download/6967/6821'),('partial_convolution','https://openaccess.thecvf.com/content_ECCV_2018/papers/Guilin_Liu_Image_Inpainting_for_ECCV_2018_paper.pdf'),('normalization_equivariance',url)]:
  pdf=OUT/(key+'.pdf');assert pdf.read_bytes().startswith(b'%PDF');text=OUT/(key+'_poppler_layout.txt');cmd=[pdftotext,'-layout','-enc','UTF-8',str(pdf),str(text)];run=subprocess.run(cmd,capture_output=True,timeout=40,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));assert run.returncode==0,run.stderr
  pages=text.read_text(encoding='utf-8').split('\f')
  if not pages[-1].strip():pages.pop()
  pagepath=OUT/(key+'_pages.json');pagepath.write_text(json.dumps([dict(page=i+1,text=t) for i,t in enumerate(pages)],ensure_ascii=False,indent=2)+'\n',encoding='utf-8');rows.append(dict(key=key,source_url=source,pdf_file=pdf.name,pdf_sha256=sha(pdf),text_file=text.name,text_sha256=sha(text),page_text_file=pagepath.name,page_text_sha256=sha(pagepath),pages=len(pages),fulltext_extracted=True,actual_reading_completed=False,command=cmd,first_page_preview=pages[0][:200]));print(json.dumps(rows[-1],ensure_ascii=False),flush=True)
 report=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),first_fetch_manifest_sha256=sha(OUT/'attempt_01.json'),pdftotext=pdftotext,pdftotext_sha256=sha(pdftotext),official_neurips_abstract_url=abstract,official_neurips_abstract_sha256=sha(OUT/'normalization_equivariance_official_abstract.html'),papers=rows,dependencies_installed_or_root_environment_modified=False)
 proof.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
