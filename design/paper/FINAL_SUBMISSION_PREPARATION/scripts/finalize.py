"""Verify protected inputs, install only reviewed reachable paper assets, package locally."""
from pathlib import Path
import json,hashlib,shutil,datetime,re,zipfile,sys,platform,importlib.metadata
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];CV=P/'revised_manuscript';CANON=P.parent/'CVPR/CVPR_ARCH_GENERALIZED/PAPER';B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING'
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
 for i,r in enumerate(json.loads((P/'ARRAY_FREEZE_MANIFEST.json').read_text())):
  f=ROOT/r['path'];ok=f.exists() and sha(f)==r['sha256'];count+=1
  if not ok:failures.append(r['path'])
  if i%500==0:print('Final protected arrays',i,flush=True)
 for r in json.loads((P/'SNAPSHOT_MANIFEST.json').read_text()):
  f=P/r['path'];count+=1
  if sha(f)!=r['sha256']:failures.append(r['path'])
 # Original accepted CSV/MD/JSON files must still match their snapshots.
 for snap in (P/'original_snapshot/accepted_evidence').rglob('*'):
  if not snap.is_file():continue
  original=B/snap.relative_to(P/'original_snapshot/accepted_evidence');count+=1
  if sha(snap)!=sha(original):failures.append(str(original.relative_to(ROOT)))
 # All inherited used scientific assets, including checkpoints, remain protected.
 for r in json.loads((B/'source_manifest.json').read_text()):
  f=ROOT/r['path'];count+=1
  if not f.exists() or sha(f)!=r['sha256']:failures.append(r['path'])
 freeze=json.loads((P/'freeze.json').read_text());assert sha(P/'FINAL_SUBMISSION_PATCH_PROTOCOL.md')==freeze['protocol_sha256']
 result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=count,failures=failures,status='PASS' if not failures else 'FAIL');write(P/'outputs/final_protection.json',result)
 assert not failures,'Protected file mismatch; originals not installed';print(result,flush=True)
def install():
 assert json.loads((P/'outputs/final_protection.json').read_text())['status']=='PASS'
 assert json.loads((P/'outputs/final_reproduction_summary.json').read_text())['all_pass']
 run=json.loads((P/'outputs/reproduction_run.json').read_text());assert len(run)==6 and all(r['returncode']==0 for r in run),'Complete final raw-array replay required'
 build=json.loads((P/'build_logs/build_audit.json').read_text());assert all(r['success'] and not r['issues'] for r in build)
 required=['FINAL_SUBMISSION_PATCH_PROTOCOL.md','CROSS_ARCH_SUPPORT_SENSITIVITY.csv','CROSS_ARCH_SUPPORT_SENSITIVITY.md','CROSS_ARCH_GEOMETRY_SENSITIVITY.csv','CROSS_ARCH_GEOMETRY_SENSITIVITY.md','CROSS_ARCH_FAMILY_ROBUSTNESS.md','TITLE_DECISION.md','DATA_ETHICS_CITATION_AUDIT.md','UPDATED_CLAIM_EVIDENCE_MATRIX.md','REPRODUCTION_CHECK.md','FINAL_SUBMISSION_CHANGELOG.md','FINAL_HOSTILE_REVIEW.md','VISUAL_REVIEW.md']
 assert all((P/x).exists() for x in required)
 # Reject concurrent changes to originals rather than overwriting user work.
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
 # No clinical source arrays or local identity/path manifests enter the paper source package.
 package=P/'CVPR_SUBMISSION_REVIEW_PACKAGE.zip'
 with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for f in closure():z.write(f,'PAPER/'+f.relative_to(CV).as_posix())
  z.writestr('README.txt','Local review package: main and supplement with reachable LaTeX/figure assets. Raw arrays and private provenance are excluded. This is a review candidate: outstanding release, ethics, image-publication permission and submission metadata require author confirmation. Rebuild PAPER/main.tex with pdflatex, bibtex, pdflatex twice; rebuild supplement.tex with pdflatex three times. No submission has been sent.\n')
 write(P/'outputs/environment.json',{'python':sys.version,'platform':platform.platform(),'packages':{k:importlib.metadata.version(k) for k in ['numpy','pandas','scipy','matplotlib','nibabel','Pillow']}})
 manifest=[]
 for f in sorted(P.rglob('*')):
  if not f.is_file() or 'original_snapshot' in f.parts or f.name=='DELIVERY_MANIFEST.json':continue
  if any(x.startswith('final_page_renders_') for x in f.parts):continue
  manifest.append(dict(path=f.relative_to(P).as_posix(),bytes=f.stat().st_size,sha256=sha(f)))
 write(P/'DELIVERY_MANIFEST.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=manifest,zip_sha256=sha(package),zip_entries=len(zipfile.ZipFile(package).namelist())))
if __name__=='__main__':
 if '--protect' in sys.argv:protect()
 elif '--install' in sys.argv:install()
 else:raise SystemExit('Use --protect or --install')
