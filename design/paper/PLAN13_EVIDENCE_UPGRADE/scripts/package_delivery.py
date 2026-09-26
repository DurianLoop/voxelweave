"""Create local draft source bundles; never publish or include raw MRI data."""
from pathlib import Path
import zipfile, hashlib, json, re

P13=Path(__file__).resolve().parents[1]; PAPER=P13.parent
OUT=P13/'delivery'; OUT.mkdir(exist_ok=True)
packages={}
for name,root in [('CVPR',PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'),('TMI',PAPER/'TMI/TMI_ARCH_GENERALIZED')]:
    selected={p for p in root.iterdir() if p.suffix.lower() in {'.tex','.bib','.sty','.cls','.bst'}}
    for p in list(selected):
        if p.suffix!='.tex': continue
        for target in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',p.read_text(encoding='utf-8')):
            candidates=[root/target,root/'figures'/target]
            if not Path(target).suffix:
                candidates=[p.with_suffix(ext) for p in candidates for ext in ['.pdf','.png','.jpg']]
            match=next((p for p in candidates if p.exists()),None)
            if match is None: raise RuntimeError('Missing image: '+target)
            selected.add(match)
    selected.add(root/'main.pdf')
    if name=='CVPR': selected.add(root/'supplement.pdf')
    path=OUT/(name+'_Plan13_DRAFT_sources.zip')
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('DRAFT_README.txt','Plan 13 research draft, finalized 2026-09-09. NOT SUBMITTED.\n'
            'Ethics and author fields, scientific overlap and final venue template need resolution.\n'
            'Build main: pdflatex main; bibtex main; pdflatex main; pdflatex main.\n'
            'CVPR supplement: pdflatex supplement (twice). Requires installed TeX packages.\n'
            'Full evidence and Chinese report: design/paper/PLAN13_EVIDENCE_UPGRADE/.\n')
        for p in sorted(selected): z.write(p,p.relative_to(root).as_posix())
    with zipfile.ZipFile(path) as z: assert z.testzip() is None
    packages[path.name]={'files':len(selected)+1,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

# Explicit source and output inventory excludes the protected snapshot and page previews.
files=[]
for base in [P13/'scripts',P13/'outputs',P13/'figures',P13/'build_logs',P13/'delivery']:
    files.extend(p for p in base.rglob('*') if p.is_file())
files += list(P13.glob('*.md'))+[P13/'original_manifest.json']
records=[{'path':p.relative_to(P13).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))]
(P13/'FINAL_ARTIFACT_MANIFEST.json').write_text(json.dumps({'date':'2026-09-09','packages':packages,'files':records},indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'packages':packages,'manifest_files':len(records)},indent=2))
