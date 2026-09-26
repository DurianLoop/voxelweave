"""Verify handoff evidence, then create a new zip (exclusive create; no overwrite)."""
from pathlib import Path
import csv,hashlib,json,zipfile,math
import torch

OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parent
ZIP=ROOT/'HAT_SMamba_missing_evidence_handoff_2026-09-16.zip'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(name):
    with (OUT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def writecsv(name,rs):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)

assert not ZIP.exists(),f'Refusing to overwrite {ZIP}'
inventory=read('source_file_inventory.csv')
for r in inventory:
    p=Path(r['absolute_path'])
    assert p.stat().st_size==int(r['size_bytes']),str(p)
    assert sha(p)==r['sha256'],str(p)
    for packaged in filter(None,r['packaged_path'].split(';')):
        assert sha(OUT/packaged)==r['sha256'],packaged

cpindex=[]
for r in inventory:
    p=Path(r['absolute_path'])
    if p.suffix not in ['.pt','.pth']:continue
    d=torch.load(p,map_location='cpu',weights_only=True)
    # No forward pass; only inspect metadata keys on CPU.
    fields=[k for k in d if any(w in k.lower() for w in ['strict','seed','selection','normalization','val','epoch'])]
    meta={k:d[k] for k in fields if isinstance(d[k],(str,int,float,bool,type(None)))}
    cpindex.append({'checkpoint':str(p),'sha256':r['sha256'],'metadata_keys':';'.join(d.keys()),'selection_metadata':json.dumps(meta),'strict_metadata_fields':';'.join(k for k in fields if 'strict' in k.lower()),'training_seed':d.get('seed','unknown/unrecorded')})
writecsv('all_checkpoint_metadata_index.csv',cpindex)
assert all(not r['strict_metadata_fields'] for r in cpindex)

splitchecks=[]
for ds,path in [('IXI',ROOT/'dataset/IXI/splits/seed3407'),('fastMRI',ROOT/'dataset/fastMRI_brain_T2/processed/splits/nifti_seed3407')]:
    sets={k:set((path/f'{k}_cases.txt').read_text().split()) for k in ['train','val','test']}
    assert not (sets['train']&sets['val'] or sets['train']&sets['test'] or sets['val']&sets['test'])
    assert len(sets['test'])==({'IXI':115,'fastMRI':24}[ds])
    for method,package in [('HAT','hat_2p5d'),('SMamba','smamba_unet_2p5d')]:
        p=ROOT/('baseline/ixi_'+package+'/runs/full_test115/run_manifest.json' if ds=='IXI' else 'baseline/fastmri_brain_'+package+'/runs/full/run_manifest.json')
        manifest=json.loads(p.read_text())
        names={x['case'].removesuffix('.nii.gz') for x in manifest['eval_cases']}
        if ds=='IXI':names={x.split('-')[0] for x in names}
        assert names==sets['test'],(ds,method)
    splitchecks.append({'dataset':ds,'train':len(sets['train']),'val':len(sets['val']),'test':len(sets['test']),'disjoint':True,'both_methods_manifest_equals_test_split':True})

matrix=read('evidence_matrix.csv')
assert len(matrix)==8
assert {r['status'] for r in matrix}=={'INVALID','MISSING'}
for r in matrix:
    for s in r['evidence_paths'].split(';'):assert Path(s).exists(),s
allchecks=read('validation_checks.csv')
assert len(allchecks)==756 and all(x['passed']=='True' for x in allchecks)
history=read('historical_value_comparison.csv')
assert len(history)==20 and all(x['matches_4dp']=='True' for x in history)
for m in ['HAT','SMamba']:
    folds=read(m+'/NingXia_8fold/per_fold_metrics.csv')
    assert len(folds)==8 and sum(int(x['test_series']) for x in folds)==22
    sub=read(m+'/NingXia_4fold_exploratory/per_fold_metrics.csv')
    assert [x['fold'] for x in sub]==['fold_01','fold_03','fold_04','fold_06']
    agg=read(m+'/NingXia_4fold_exploratory/recomputed_fold_mean.csv')[0]
    for metric in ['psnr','ssim','mae','mse','ncc']:
        assert math.isclose(float(agg[metric]),sum(float(x[metric]) for x in sub)/4,rel_tol=1e-12)

validation={'source_files_rehashed_unchanged':len(inventory),'copied_source_files_verified':len(json.loads((OUT/'copy_map.json').read_text())),'all_checkpoints_metadata_scanned':len(cpindex),'strict_metadata_fields_found':0,'selected_run_checks_passed':len(allchecks),'historical_values_match_4dp':len(history),'split_checks':splitchecks,'matrix_rows':len(matrix),'training_executed':False,'inference_executed':False,'original_files_modified':False,'hash_manifest_self_exclusion':'sha256_manifest.csv excludes itself; external ZIP sha256 covers complete ZIP including this manifest','zip_verification':'CRC and all member SHA checked by verify_and_package.py after writing; see external .verification.json'}
(OUT/'package_validation.json').write_text(json.dumps(validation,indent=2,ensure_ascii=False),encoding='utf-8')
manifest=[{'relative_path':p.relative_to(OUT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='sha256_manifest.csv']
writecsv('sha256_manifest.csv',manifest)
with zipfile.ZipFile(ZIP,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(ZIP) as z:
    assert z.testzip() is None
    for r in manifest:
        data=z.read(OUT.name+'/'+r['relative_path'])
        assert hashlib.sha256(data).hexdigest()==r['sha256']
    assert z.read(OUT.name+'/sha256_manifest.csv')==(OUT/'sha256_manifest.csv').read_bytes()
    members=len(z.namelist())
digest=sha(ZIP)
side=ZIP.with_suffix('.zip.sha256')
with side.open('x',encoding='ascii') as f:f.write(digest+'  '+ZIP.name+'\n')
result={'zip_absolute_path':str(ZIP),'size_bytes':ZIP.stat().st_size,'sha256':digest,'zip_members':members,'zip_crc_ok':True,'zip_member_hashes_ok':True,'source_files_unchanged':True}
with ZIP.with_suffix('.zip.verification.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2),flush=True)
