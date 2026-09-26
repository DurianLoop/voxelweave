from pathlib import Path
import hashlib,json,datetime,shutil
P=Path(__file__).resolve().parents[1]; B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING'; ROOT=P.parents[2]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024**2),b''):h.update(chunk)
 return h.hexdigest()
def main():
 assert not (P/'freeze.json').exists(),'Do not overwrite a completed freeze'
 for d in ['outputs','logs','revised_manuscript','scripts','figures']:(P/d).mkdir(exist_ok=True)
 cv=P.parent/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'
 for target in [P/'original_snapshot/manuscript',P/'revised_manuscript']:shutil.copytree(cv,target,dirs_exist_ok=True)
 for f in list(B.glob('*.csv'))+list(B.glob('*.md'))+list(B.glob('*.json'))+list((B/'outputs').glob('*.csv')):
  d=P/'original_snapshot/accepted_evidence'/f.relative_to(B);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,d)
 arrays=set(B.rglob('*.npz'))|set(B.rglob('*.npy'))
 arrays.update((P.parent/'PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/outputs').glob('*real_arrays.npz'))
 arrays.update(ROOT/r['source'] for r in json.loads((B/'case_registry.json').read_text(encoding='utf-8')))
 rows=[]
 for i,f in enumerate(sorted(arrays)):
  rows.append(dict(path=str(f.relative_to(ROOT)).replace('\\','/'),bytes=f.stat().st_size,sha256=sha(f)))
  if i%200==0:print('Frozen array',i,'/',len(arrays),flush=True)
 (P/'ARRAY_FREEZE_MANIFEST.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 small=[]
 for f in sorted((P/'original_snapshot').rglob('*')):
  if f.is_file():small.append(dict(path=f.relative_to(P).as_posix(),sha256=sha(f)))
 (P/'SNAPSHOT_MANIFEST.json').write_text(json.dumps(small,indent=2),encoding='utf-8')
 record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),protocol_sha256=sha(P/'FINAL_SUBMISSION_PATCH_PROTOCOL.md'),array_manifest_sha256=sha(P/'ARRAY_FREEZE_MANIFEST.json'),snapshot_manifest_sha256=sha(P/'SNAPSHOT_MANIFEST.json'),arrays=len(rows),array_bytes=sum(r['bytes'] for r in rows))
 (P/'freeze.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(record,flush=True)
if __name__=='__main__':main()
