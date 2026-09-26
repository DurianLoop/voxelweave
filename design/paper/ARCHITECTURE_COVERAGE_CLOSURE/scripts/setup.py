from pathlib import Path
import json,hashlib,shutil,datetime,csv
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING';S=P.parent/'FINAL_SUBMISSION_PREPARATION'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
for n in ['outputs','logs','original_snapshot','revised_manuscript']: (P/n).mkdir(exist_ok=True)
cv=P.parent/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'
if not (P/'original_snapshot/manuscript').exists():
 shutil.copytree(cv,P/'original_snapshot/manuscript');shutil.copytree(cv,P/'revised_manuscript',dirs_exist_ok=True)
for src in [B,S]:
 dst=P/'original_snapshot'/src.name;dst.mkdir(exist_ok=True)
 for f in src.iterdir():
  if f.is_file() and f.suffix in ['.json','.csv','.md'] and not (dst/f.name).exists():shutil.copy2(f,dst/f.name)
ledger=ROOT/'docx/experiment/experiment_master_table.md'
shutil.copy2(ledger,P/'original_snapshot/experiment_master_table.md')
bank=list(csv.DictReader((P.parent/'PLAN15_BASELINE_INTEGRATION/outputs/baseline_all_verified.csv').open(encoding='utf-8')))
write(P/'bank_ledger.json',bank)
core=json.loads((B/'model_registry.json').read_text());registry=core.copy()
names={'acvtt':'acvtt','ressrdiff':'ressrdiff','arssr':'arssr','resunet':'resunet','gan_2p5d':'gan','smamba_unet':'smamba_unet'}
for r in bank:
 if r['dataset'] not in ['IXI','fastMRI'] or r['model'] not in names or r['budget']!='master' or r['scale']!='4':continue
 ds={'IXI':'ixi','fastMRI':'fastmri'}[r['dataset']];model=r['model'];run=(ROOT/json.loads(r['source_paths'])[0]).parents[1]
 ck=run/'checkpoints'/f'{names[model]}_epoch_best.pth'
 if not ck.exists():
  alt={'arssr':ROOT/'baseline/ixi_arssr/runs/full/checkpoints/arssr_epoch_best.pth','resunet':ROOT/'pre/ixi_diffusion/runs/resunet_full_t2/checkpoints/resunet_epoch_best.pth'}
  ck=alt.get(model,ck)
 assert ck.exists(),ck
 registry.append({'dataset':ds,'model':model,'checkpoint':ck.relative_to(ROOT).as_posix(),'sha256':sha(ck),'benchmark_profile':r['profile'],'benchmark_sources':json.loads(r['source_paths'])})
for r in registry:assert sha(ROOT/r['checkpoint'])==r['sha256'],r
write(P/'model_registry.json',registry)
sources=set()
for r in bank:
 for s in json.loads(r['source_paths']):
  src=ROOT/s;assert src.exists();sources.add(src)
for base in [ROOT/'baseline',ROOT/'pre/ixi_diffusion']:
 for f in base.rglob('*.py'):
  if 'runs' not in f.parts:sources.add(f)
sources.add(ledger)
for f in [B/'FINAL_ITERATION_PROTOCOL.md',B/'case_registry.json',B/'proposition_case_registry.json',B/'prepared_input_manifest.json',S/'ARRAY_FREEZE_MANIFEST.json',P/'PROTOCOL.md']:sources.add(f)
for f in (P/'original_snapshot').rglob('*'):
 if f.is_file():sources.add(f)
write(P/'SOURCE_MANIFEST.json',[{'path':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(sources)])
old=json.loads((S/'ARRAY_FREEZE_MANIFEST.json').read_text());print('old manifest type',type(old).__name__,flush=True)
write(P/'freeze.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha(P/'PROTOCOL.md'),'source_manifest_sha256':sha(P/'SOURCE_MANIFEST.json'),'registry_sha256':sha(P/'model_registry.json'),'prior_array_manifest_sha256':sha(S/'ARRAY_FREEZE_MANIFEST.json'),'new_inference_permitted_only_after_array_verification':True})
print('SETUP',len(registry),'checkpoints',len(bank),'bank rows',len(sources),'sources',flush=True)
