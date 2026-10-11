"""Read-only PDF operation: render KNConv equations and reported resource table."""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT/'literature/source_cache/kernel_normalization_primary_2026-10-07/kernel_norm.pdf'
OUT = ROOT/'literature/source_cache/kernel_normalization_visual_review_2026-10-07'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(exist_ok=False)
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__),
        source_pdf=PDF.relative_to(ROOT).as_posix(), source_pdf_sha256=sha(PDF), rendered=[], actual_visual_review_completed=False)
    info = subprocess.run([shutil.which('pdfinfo'), str(PDF)], capture_output=True, timeout=20)
    assert info.returncode == 0; (OUT/'pdfinfo.txt').write_bytes(info.stdout)
    for page in (4, 6, 12, 21):
        prefix = OUT/f'kernel_norm_physical_page_{page:02d}'
        cmd = [shutil.which('pdftoppm'), '-f', str(page), '-l', str(page), '-r', '120', '-singlefile', '-png', str(PDF), str(prefix)]
        proc = subprocess.run(cmd, capture_output=True, timeout=40); assert proc.returncode == 0, proc.stderr
        png = prefix.with_suffix('.png')
        r['rendered'].append(dict(physical_page=page, image=png.relative_to(ROOT).as_posix(), sha256=sha(png),
            command=cmd, actual_view_image_completed=False))
    (OUT/'render_attempt01.json').write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(rendered_pages=len(r['rendered']), actual_visual_review_completed=False)))
if __name__ == '__main__': main()
