from pathlib import Path
import json,hashlib,shutil,datetime,re,zipfile,sys,platform,importlib.metadata
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];CV=P/'revised_manuscript';CANON=P.parent/'CVPR/CVPR_ARCH_GENERALIZED/PAPER';B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING';S=P.parent/'FINAL_SUBMISSION_PREPARATION'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(8*1024**2),b''):h.update(x)
 return h.hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def closure():
 files=set()
 def add(path):
  path=path.resolve();assert path.is_relative_to(CV.resolve()),path
  if path in files:return
  assert path.exists(),path;files.add(path)
  if path.suffix!='.tex':return
  text=path.read_text(encoding='utf-8')
  for child in re.findall(r'\\input\{([^}]+)\}',text):add(CV/(child if Path(child).suffix else child+'.tex'))
  for child in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',text):
   candidates=[base/child for base in [CV,CV/'figures']]
   found=next((q for q in candidates if q.is_file()),None) if Path(child).suffix else next((q.with_suffix(s) for q in candidates for s in ['.pdf','.png','.jpg','.jpeg'] if q.with_suffix(s).exists()),None)
   assert found,child;add(found)
 for name in ['main.tex','supplement.tex','references.bib','cvpr.sty','ieeenat_fullname.bst','main.pdf','supplement.pdf']:add(CV/name)
 return sorted(files)
def protect():
 failures=[];count=0
 for label,rows in [('prior_arrays',json.loads((S/'ARRAY_FREEZE_MANIFEST.json').read_text())),('closure_sources',json.loads((P/'SOURCE_MANIFEST.json').read_text())),('inherited_sources',json.loads((B/'source_manifest.json').read_text()))]:
  for i,r in enumerate(rows):
   f=ROOT/r['path'];count+=1
   if not f.exists() or sha(f)!=r['sha256']:failures.append(r['path'])
   if i%500==0:print('PROTECT',label,i,flush=True)
 for base in [B,S]:
  snap=P/'original_snapshot'/base.name
  for f in snap.iterdir():
   if f.is_file():
    count+=1
    if sha(base/f.name)!=sha(f):failures.append(str(base/f.name))
 for r in json.loads((P/'model_registry.json').read_text()):
  count+=1
  if sha(ROOT/r['checkpoint'])!=r['sha256']:failures.append(r['checkpoint'])
 assert sha(P/'PROTOCOL.md')==json.loads((P/'freeze.json').read_text())['protocol_sha256']
 result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=count,failures=failures,status='PASS' if not failures else 'FAIL');write(P/'outputs/final_protection.json',result);assert not failures,failures;print(result,flush=True)
def install():
 assert json.loads((P/'outputs/final_protection.json').read_text())['status']=='PASS'
 assert json.loads((P/'outputs/reproduction_checks.json').read_text())['status']=='PASS'
 assert json.loads((P/'outputs/expanded_independent_checks.json').read_text())['status']=='PASS'
 assert json.loads((P/'outputs/delivery_checks.json').read_text())['status']=='PASS'
 build=json.loads((P/'build_logs/build_audit.json').read_text());assert all(r['success'] and not r['issues'] for r in build)
 required=['MODEL_EVIDENCE_ELIGIBILITY.csv','MODEL_EVIDENCE_ELIGIBILITY.md','FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.csv','FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.md','EXPANDED_PHENOMENON_BREADTH.csv','EXPANDED_PHENOMENON_BREADTH.md','UPDATED_MIRA_REPORT_CARD.csv','UPDATED_CLAIM_EVIDENCE_MATRIX.md','ARCHITECTURE_COVERAGE_CHANGELOG.md','VISUAL_REVIEW.md','REPRODUCTION_CHECK.md','DELIVERY_NOTES_ZH.md']
 assert all((P/x).exists() for x in required)
 for snap in (P/'original_snapshot/manuscript').rglob('*'):
  if snap.is_file():
   dest=CANON/snap.relative_to(P/'original_snapshot/manuscript');assert dest.exists() and sha(dest)==sha(snap),('Original changed since freeze',dest)
 records=[]
 for f in closure():
  dest=CANON/f.relative_to(CV);before=sha(dest) if dest.exists() else None;after=sha(f)
  if before==after:continue
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest);assert sha(dest)==after
  records.append(dict(path=dest.relative_to(ROOT).as_posix(),before_sha256=before,after_sha256=after))
 write(P/'outputs/installed_files.json',records);print('Installed',len(records),'reviewed CVPR files',flush=True)
 package=P/'CVPR_ARCHITECTURE_COVERAGE_REVIEW_PACKAGE.zip'
 with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for f in closure():z.write(f,'PAPER/'+f.relative_to(CV).as_posix())
  z.writestr('README.txt','Local review package only; no external submission. Includes main/supplement and reachable LaTeX/figure sources; excludes clinical arrays and private manifests. Author must resolve authentic ethics, consent/de-identification, release and permission records and submission metadata. Rebuild main with pdflatex, bibtex and pdflatex twice; supplement with pdflatex three times.\n')
 write(P/'outputs/environment.json',dict(python=sys.version,platform=platform.platform(),packages={k:importlib.metadata.version(k) for k in ['numpy','pandas','scipy','matplotlib','nibabel','torch','Pillow']}))
 manifest=[]
 for f in sorted(P.rglob('*')):
  if not f.is_file() or 'original_snapshot' in f.parts or f.name=='DELIVERY_MANIFEST.json' or 'page_renders' in f.parts:continue
  manifest.append(dict(path=f.relative_to(P).as_posix(),bytes=f.stat().st_size,sha256=sha(f)))
 write(P/'DELIVERY_MANIFEST.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=manifest,zip_sha256=sha(package),zip_entries=len(zipfile.ZipFile(package).namelist())))
if __name__=='__main__':
 if '--protect' in sys.argv:protect()
 elif '--install' in sys.argv:install()
 else:raise SystemExit('Use --protect or --install')
