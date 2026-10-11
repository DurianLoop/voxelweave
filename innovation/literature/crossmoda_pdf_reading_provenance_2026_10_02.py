"""Record prior PDF extraction and render additional relevant source pages."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parent/'source_cache/action_crossmoda_adaptive_2026-10-02'
PDF=BASE/'crossmoda_author_pdf_attempt_01.pdf'
TOOLS=Path('C:/Users/user/AppData/Local/Programs/MiKTeX/miktex/bin/x64')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    records=[]
    for number in (8,23):
        prefix=BASE/f'crossmoda_page{number:02d}_attempt_03'
        command=[str(TOOLS/'pdftoppm.exe'),'-f',str(number),'-l',str(number),'-scale-to','1600','-singlefile','-png',str(PDF),str(prefix)]
        r=subprocess.run(command,capture_output=True,timeout=30)
        err=BASE/f'crossmoda_render_page{number:02d}_attempt_03.stderr';err.write_bytes(r.stderr)
        png=prefix.with_suffix('.png')
        row={'pdf_page':number,'argv':command,'returncode':r.returncode,'stderr_file':err.name,'stderr_sha256':sha(err)}
        if png.exists():row.update(png_file=png.name,png_sha256=sha(png),png_bytes=png.stat().st_size)
        records.append(row)
    versions=[]
    for name in ('pdftotext','pdftoppm'):
        r=subprocess.run([str(TOOLS/(name+'.exe')),'-v'],capture_output=True,timeout=15)
        versions.append({'path':str(TOOLS/(name+'.exe')),'returncode':r.returncode,'version_output':(r.stdout+r.stderr).decode('utf-8',errors='replace')})
    files=[p for p in BASE.glob('crossmoda*') if p.is_file() and p.suffix in ('.pdf','.txt','.png','.stderr')]
    result={'script_sha256':sha(__file__),'source_pdf_sha256':sha(PDF),'extraction_tool':str(TOOLS/'pdftotext.exe'),'extraction_method':'prior pdftotext -layout; pages split by form feed','actual_nonempty_pdf_pages':len([p for p in (BASE/'crossmoda_author_pdf_attempt_01_layout.txt').read_text(encoding='utf-8').split(chr(12)) if p.strip()]),'versions':versions,'new_render_records':records,'prior_render_note':'First PowerShell wrapper reported exit1 with MiKTeX log stderr but wrote pages04-07; later Python subprocess render Table1 returned0. No user config edited.','files':[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)]}
    (BASE/'crossmoda_pdf_provenance_2026-10-02.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'actual_nonempty_pdf_pages':result['actual_nonempty_pdf_pages'],'new_renders':records},indent=2))

if __name__=='__main__':main()
