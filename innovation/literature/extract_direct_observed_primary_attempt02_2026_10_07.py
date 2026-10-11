"""Recover extraction from saved PDFs; preserve failed attempt and raw diagnostics."""
import concurrent.futures,hashlib,json,re,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/direct_observed_primary_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def extract(key):
    pdf=OUT/(key+'.pdf');assert pdf.read_bytes().startswith(b'%PDF-')
    proc=subprocess.run([shutil.which('pdfinfo'),str(pdf)],capture_output=True,timeout=30)
    (OUT/(key+'_pdfinfo_attempt02.raw')).write_bytes(proc.stdout+proc.stderr)
    assert proc.returncode==0
    n=int(re.search(rb'^Pages:\s+(\d+)',proc.stdout,re.M)[1]);rows=[]
    for page in range(1,n+1):
        p=OUT/(key+f'_page{page:02d}.txt');assert not p.exists()
        q=subprocess.run([shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(pdf),str(p)],capture_output=True,timeout=30)
        assert q.returncode==0 and p.exists()
        rows.append(dict(page=page,file=p.relative_to(ROOT).as_posix(),sha256=sha(p),characters=len(p.read_text(encoding='utf-8'))))
    return dict(key=key,pdf_sha256=sha(pdf),pdf_bytes=pdf.stat().st_size,physical_pages=n,texts=rows,extraction_success=True,reading_performed=False)
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(extract,('sparsity_invariant','confidence_propagation')))
    with (OUT/'extraction_attempt02.json').open('x',encoding='utf-8') as f:
        json.dump(dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,records=rows,script_sha256=sha(__file__),environment_unchanged=True),f,indent=2)
    print(json.dumps([{k:r[k] for k in ('key','physical_pages','pdf_bytes','extraction_success')} for r in rows]));return 0
if __name__=='__main__':raise SystemExit(main())
