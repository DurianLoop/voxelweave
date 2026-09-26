"""Read-only source audit; all writes confined to this new handoff directory.
No model inference, training, checkpoint selection, or original result writes.
"""
from pathlib import Path
import csv, hashlib, json, math, shutil, statistics, zipfile, re
import torch

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent
METRICS = ['psnr','ssim','mae','mse','ncc']
sources = {}
copied = {}
checks = []

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def add(p, role='candidate', dst=None):
    p=Path(p).resolve()
    if not p.is_file(): return None
    key=str(p)
    if key not in sources:
        st=p.stat()
        sources[key]={'absolute_path':key,'size_bytes':st.st_size,'sha256':sha(p),'role':role,'packaged_path':'','mtime_ns_at_audit':st.st_mtime_ns}
    elif role!='candidate': sources[key]['role']=role
    if dst:
        target=OUT/dst
        assert target.resolve().is_relative_to(OUT)
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            assert sha(target)==sources[key]['sha256'], str(target)
        else: shutil.copyfile(p,target)
        assert sha(target)==sources[key]['sha256']
        copied[str(target.relative_to(OUT))]=key
        sources[key]['packaged_path']=';'.join(sorted(set(filter(None,[sources[key]['packaged_path'],str(target.relative_to(OUT))]))))
    return sources[key]

def write_csv(path, rows, fields=None):
    path=OUT/path;path.parent.mkdir(parents=True,exist_ok=True)
    if fields is None: fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def write_json(path,obj):
    path=OUT/path;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str),encoding='utf-8')

def note(path,text):
    path=OUT/path;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')

def rows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def check(name,ok,source,detail=''):
    checks.append(dict(check=name,passed=bool(ok),source=str(source),detail=str(detail)))
    if not ok: raise ValueError(f'{name}: {source}: {detail}')

# Inventory all filename candidates, including excluded scales, alternate runs and checkpoints.
for s in (OUT/'search_candidates.txt').read_text(encoding='utf-8').splitlines(): add(s)

# Scan archives without extracting executable content or unrelated personal files.
archive_rows=[]
for s in (OUT/'archive_candidates.txt').read_text(encoding='utf-8').splitlines():
    add(s,'searched_archive')
    with zipfile.ZipFile(s) as z:
        names=z.namelist()
        for n in names:
            archive_rows.append({'archive':s,'member':n,'size_bytes':z.getinfo(n).file_size})
        if 'transfer_hat_baseline' in s:
            for n in names:
                if n.endswith(('/ixi_hat_2p5d/train.py','/fastmri_brain_hat_2p5d/train.py','/ixi_diffusion/data.py','/fastmri_brain_hat_2p5d/data.py','/topcow_diffusion/metrics.py','/README_HAT_BASELINE_CODE.md')):
                    dest=OUT/'archive_reference'/Path(n)
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    data=z.read(n)
                    if dest.exists():assert dest.read_bytes()==data
                    else:dest.write_bytes(data)
write_csv('archive_member_inventory.csv',archive_rows)

small_sources=[ROOT/'environment.yml',ROOT/'requirements.txt',ROOT/'env_setup_MRI.log',
 ROOT/'docx/experiment/experiment_master_table.md',ROOT/'docx/experiment_notes/hat_smamba_run_status_20260629.md',
 ROOT/'docx/experiment_notes/other/hat_smamba_ixit2_screening_notes.md',
 ROOT/'docx/experiment_notes/other/baseline_exposed_problems_for_model_design.md',
 ROOT/'pre/ixi_diffusion/common.py',ROOT/'pre/ixi_diffusion/data.py',ROOT/'pre/ixi_diffusion/settings.py',
 ROOT/'pre/topcow_diffusion/metrics.py',ROOT/'pre/topcow_diffusion/common.py',
 ROOT/'processing/run_ningxia_case_cv.py',ROOT/'processing/summarize_case_cv.py',
 ROOT/'processing/ningxia_case_cv.py',ROOT/'processing/fastmri_brain_nifti_index.py']
for package in ['ixi_hat_2p5d','ixi_smamba_unet_2p5d','fastmri_brain_hat_2p5d','fastmri_brain_smamba_unet_2p5d']:
    small_sources.extend((ROOT/'baseline'/package).glob('*.py'))
for p in small_sources:add(p,'source_code_or_document','reference/'+p.relative_to(ROOT).as_posix())
for s in (OUT/'search_candidates.txt').read_text(encoding='utf-8').splitlines():
    p=Path(s)
    if p.suffix in ['.log','.ps1'] and ('hat_smamba' in s or 'ixi_hat' in s):add(p,'historical_log_or_command','reference/'+p.relative_to(ROOT).as_posix())
for p in (ROOT/'logs').glob('*hat_smamba*/status.tsv'):add(p,'historical_command_log','reference/'+p.relative_to(ROOT).as_posix())
user_request=Path('C:/Users/user/.codex/attachments/834ec0bc-1c0f-45e1-8d3b-68ba1309097b/pasted-text.txt')
add(user_request,'audit_requirements','reference/user_request.txt')
desktop=Path('C:/Users/user/Desktop/baseline_exposed_problems_for_model_design.md')
add(desktop,'alternate_required_document','reference/desktop_baseline_exposed_problems_for_model_design.md')

cvroot=ROOT/'dataset/NingXiaData/processed_saint_cv'
cv=json.loads((cvroot/'case_cv_summary.json').read_text())
for p in [cvroot/'case_cv_summary.json',cvroot/'case_cv_summary.csv']:
    add(p,'data_manifest','reference/'+p.relative_to(ROOT).as_posix())
data_roots=[ROOT/'dataset/IXI',ROOT/'dataset/fastMRI_brain_T2/processed']+[cvroot/f'fold_{i:02d}' for i in range(8)]
for dr in data_roots:
    for p in (dr/'splits').rglob('*'):
        if p.is_file() and p.suffix in ['.txt','.json','.csv']:add(p,'split_manifest','reference/'+p.relative_to(ROOT).as_posix())
    for filename in ['metadata/ixi_cases.csv','metadata/fastmri_brain_nifti_cases.csv']:
        p=dr/filename;add(p,'data_index','reference/'+p.relative_to(ROOT).as_posix())

run_records=[]; checkpoint_rows=[]; numeric_checks=[]; metadata_all={}; selected=[]; all_recomputed={}
def audit_run(method,key,run,dest):
    manifest=run/'run_manifest.json'; per=run/'metrics/per_case_metrics.csv'; summary=run/'metrics/summary_metrics.csv'
    d=json.loads(manifest.read_text()); rr=[r for r in rows(per) if r['method']==key]
    ss=[r for r in rows(summary) if r['method']==key]
    check('single_summary_row',len(ss)==1,summary)
    check('case_count',int(ss[0]['cases'])==len(rr),per)
    names=[r['case'] for r in rr]
    check('unique_series',len(names)==len(set(names)),per)
    check('manifest_matches_per_case',set(names)=={x['case'] for x in d['eval_cases']},manifest)
    check('stride_4',d['stride']==4,manifest)
    for m in METRICS:
        vals=[float(r[m]) for r in rr]
        check('finite_'+m,all(math.isfinite(x) for x in vals),per)
        mean=statistics.mean(vals);given=float(ss[0][m+'_mean'])
        numeric_checks.append({'method':method,'run':str(run),'metric':m,'per_case_mean':mean,'saved_summary_mean':given,'difference':mean-given})
        check('summary_matches_'+m,math.isclose(mean,given,rel_tol=1e-12,abs_tol=1e-9),summary)
    byname={x['case']:x for x in d['eval_cases']}
    for row in rr:
        depth=int(byname[row['case']]['target_depth']); expected=sum(i%4!=0 for i in range(depth))
        check('generated_slice_count',int(row['generated_slices'])==expected,per,row['case'])
    for p in run.glob('*'):
        if p.is_file() and p.suffix in ['.csv','.json','.txt','.yaml','.yml']:add(p,'selected_run_evidence',dest+'/'+p.name)
    for p in (run/'metrics').glob('*'):
        if p.suffix in ['.csv','.json','.md']:add(p,'selected_run_evidence',dest+'/metrics/'+p.name)
    history=rows(run/'training_history.csv')
    best=min(history,key=lambda x:float(x['val_loss']))
    cps=list((run/'checkpoints').glob('*.pth'))+list((run/'checkpoints').glob('*.pt'))
    for p in cps:
        info=add(p,'selected_run_checkpoint')
        payload=torch.load(p,map_location='cpu',weights_only=True)
        metadata={k:v for k,v in payload.items() if k not in ['model_state_dict','optimizer_state_dict','scheduler_state_dict','state_dict']}
        meta_key=p.relative_to(ROOT).as_posix();metadata_all[meta_key]=metadata
        isbest='best' in p.name
        if isbest:
            check('best_epoch_equals_min_ordinary_val_loss',int(payload['epoch'])==int(best['epoch']),p)
            check('best_loss_equals_min_ordinary_val_loss',math.isclose(float(payload['best_val_loss']),float(best['val_loss']),rel_tol=1e-10),p)
            add(p,'ordinary_val_best_checkpoint',dest+'/checkpoints/'+p.name)
        checkpoint_rows.append({'method':method,'run':str(run),'checkpoint':str(p),'sha256':info['sha256'],'size_bytes':info['size_bytes'],'epoch':payload.get('epoch'),'best_val_loss':payload.get('best_val_loss'),'history_min_loss_epoch':best['epoch'],'selection':'ordinary sliding-window validation loss; NOT strict-val' if isbest else 'final checkpoint; excluded','training_seed':metadata.get('seed','unknown/unrecorded'),'included_in_zip':isbest})
    means={m:statistics.mean(float(r[m]) for r in rr) for m in METRICS}
    result={'method':method,'run':str(run),'cases':len(rr),'stride':4,'status':'INVALID','training_seed':'unknown/unrecorded','manifest':str(manifest),'per_case_csv':str(per),'summary_csv':str(summary),'checkpoint':str(next(p for p in cps if 'best' in p.name)),'selection':'ordinary validation loss, not strict friend-protocol',**means}
    run_records.append(result);selected.append(run);all_recomputed[str(run)]=means
    return result,rr

fold_rows=[]; mapping=[]; summaries=[]; historical=[]
targets={'HAT':{'fastMRI':[22.7858,.7536,49.6702,10454.4878,.9079],'NingXia_8fold':[23.9499,.7519,86.1449,32226.9860,.8933]},'SMamba':{'fastMRI':[22.7322,.7618,49.4487,10826.4468,.9051],'NingXia_8fold':[23.9126,.7500,86.8152,32498.3175,.8917]}}
method_runs={}
for method,package,key in [('HAT','hat_2p5d','hat'),('SMamba','smamba_unet_2p5d','smamba_unet')]:
    for ds in ['fastMRI','IXI_n25','NingXia_8fold','NingXia_4fold_exploratory']:(OUT/method/ds).mkdir(parents=True,exist_ok=True)
    fr=ROOT/f'baseline/fastmri_brain_{package}/runs/full'
    fast,rr=audit_run(method,key,fr,method+'/fastMRI/full')
    for k,v in zip(METRICS,targets[method]['fastMRI']):historical.append({'method':method,'dataset':'fastMRI','metric':k,'historical_4dp':v,'recomputed':fast[k],'difference':fast[k]-v,'matches_4dp':f'{fast[k]:.4f}'==f'{v:.4f}','source':str(fr/'metrics/per_case_metrics.csv')})
    ix=ROOT/f'baseline/ixi_{package}/runs/full_test115'
    audit_run(method,key,ix,method+'/IXI_n115_EXCLUDED/full_test115')
    fs=[]
    for i in range(8):
        fold=f'fold_{i:02d}';run=ROOT/f'baseline/ningxia_t2_{package}_cv/runs/{fold}/full'
        result,rr=audit_run(method,key,run,method+'/NingXia_8fold/'+fold+'/full')
        cases={r['case'].split('_')[0] for r in rr}
        expected=cv['folds'][i]['test_case']
        check('fold_subject',cases=={expected},run,expected)
        splitroot=cvroot/fold/'splits/nifti_seed3407'
        sets={split:set((splitroot/f'{split}_cases.txt').read_text().split()) for split in ['train','val','test']}
        check('fold_splits_disjoint',not(sets['train']&sets['val'] or sets['train']&sets['test'] or sets['val']&sets['test']),splitroot)
        check('fold_test_split_matches_csv',sets['test']==cases,splitroot)
        row={'method':method,'fold':fold,'requested_alias':fold.replace('_',''),'test_case':expected,'test_series':len(rr),'status':'INVALID',**{m:result[m] for m in METRICS},'source_per_case_csv':str(run/'metrics/per_case_metrics.csv')}
        fs.append(row);fold_rows.append(row)
        mapping.append({'method':method,'fold':fold,'requested_alias':fold.replace('_',''),'train_cases':';'.join(sorted(sets['train'])),'val_case':';'.join(sorted(sets['val'])),'test_case':expected,'test_series':len(rr),'series_ids':';'.join(r['case'] for r in rr),'split_source':str(splitroot),'source_manifest':str(run/'run_manifest.json')})
    check('8_folds_8_subjects_22_series',len(fs)==8 and len({x['test_case'] for x in fs})==8 and sum(x['test_series'] for x in fs)==22,ROOT/f'baseline/ningxia_t2_{package}_cv/runs')
    agg={'method':method,'dataset':'NingXia_8fold','folds':8,'subjects':8,'series':22,'aggregation':'equal weight per fold','status':'INVALID',**{m:statistics.mean(x[m] for x in fs) for m in METRICS}}
    summaries.append(agg);write_csv(method+'/NingXia_8fold/recomputed_fold_mean.csv',[agg]);write_csv(method+'/NingXia_8fold/per_fold_metrics.csv',fs)
    write_csv(method+'/NingXia_8fold/fold_case_mapping.csv',[x for x in mapping if x['method']==method])
    for k,v in zip(METRICS,targets[method]['NingXia_8fold']):historical.append({'method':method,'dataset':'NingXia_8fold','metric':k,'historical_4dp':v,'recomputed':agg[k],'difference':agg[k]-v,'matches_4dp':f'{agg[k]:.4f}'==f'{v:.4f}','source':';'.join(x['source_per_case_csv'] for x in fs)})
    four=[x for x in fs if x['fold'] in ['fold_01','fold_03','fold_04','fold_06']]
    check('specified_4fold_subjects',{x['test_case'] for x in four}=={'NX002','NX004','NX005','NX007'},method)
    sub={'method':method,'dataset':'NingXia_4fold_exploratory','folds':4,'subjects':4,'series':sum(x['test_series'] for x in four),'aggregation':'equal weight per fold (NOT series weighted)','status':'INVALID','scope':'Post-hoc exploratory subset only. Not a replacement for the formal 8-fold result.',**{m:statistics.mean(x[m] for x in four) for m in METRICS}}
    summaries.append(sub);write_csv(method+'/NingXia_4fold_exploratory/recomputed_fold_mean.csv',[sub]);write_csv(method+'/NingXia_4fold_exploratory/per_fold_metrics.csv',four)
    note(method+'/NingXia_4fold_exploratory/README.md','Post-hoc exploratory subset only.\nNot a replacement for the formal 8-fold result.\n\n仅由既有 CSV 复算；每 fold 等权，13 series。源 checkpoint 非 strict-val 选择，状态 INVALID，不能作为 friend-protocol 正式结果。\n')
    note(method+'/IXI_n25/README.md','状态：MISSING。未发现该方法独立的 IXI n=25 结果；找到的是 full_test115（115 个病例），已单列在 IXI_n115_EXCLUDED。未将 115 改写为 25，亦未从 115 结果派生替代值。\n\n证据：../../search_candidates.txt；../IXI_n115_EXCLUDED/full_test115/run_manifest.json；../../run_candidate_audit.csv。\n')
    method_runs[method]={'fastMRI':fr,'IXI_n25':ix,'NingXia_8fold':ROOT/f'baseline/ningxia_t2_{package}_cv/runs','NingXia_4fold_exploratory':ROOT/f'baseline/ningxia_t2_{package}_cv/runs'}

# The newer HAT full_extend60 is a separate historical profile, never selected by test score here.
extended=ROOT/'baseline/fastmri_brain_hat_2p5d/runs/full_extend60'
extended_result,_=audit_run('HAT','hat',extended,'HAT/fastMRI/full_extend60_ALTERNATE')
write_csv('numeric_consistency_checks.csv',numeric_checks)
write_csv('historical_value_comparison.csv',historical)
check('all_historical_values_match_4dp',all(x['matches_4dp'] for x in historical),'historical_value_comparison.csv')
write_csv('recomputed_summaries.csv',summaries)
write_csv('run_level_audit.csv',run_records)
write_csv('checkpoint_audit.csv',checkpoint_rows)
write_json('checkpoint_metadata.json',metadata_all)

# Every discovered run manifest in target baseline packages: includes scales/profiles rejected from comparison.
candidates=[]
for package in (ROOT/'baseline').iterdir():
    if not package.is_dir() or not ('hat' in package.name or 'smamba' in package.name):continue
    for p in sorted(package.glob('runs/**/run_manifest.json')):
        d=json.loads(p.read_text());n=len(d.get('eval_cases',[]));stride=d.get('stride')
        candidates.append({'run':str(p.parent),'manifest':str(p),'profile':p.parent.name,'stride':stride,'eval_series':n,'included_in_historical_audit':p.parent in selected,'disposition':'audited original historical profile' if p.parent in selected else 'excluded: other scale/profile; not promoted on test score','strict_checkpoint_files':';'.join(str(x) for x in p.parent.rglob('*strict*'))})
write_csv('run_candidate_audit.csv',candidates)

# Evidence matrix: missing certification fields are kept separate from code-level properties.
matrix=[];seeds=[]
for method,package in [('HAT','hat_2p5d'),('SMamba','smamba_unet_2p5d')]:
    for ds in ['fastMRI','IXI_n25','NingXia_8fold','NingXia_4fold_exploratory']:
        missing=ds=='IXI_n25';nx=ds.startswith('NingXia');run=method_runs[method][ds]
        code=ROOT/'baseline'/('ixi_'+package if missing else 'fastmri_brain_'+package)
        split='N/A (deterministic case-level CV; nifti_seed3407 is directory label only)' if nx else ('3407 (split_manifest.json)' if missing else '3407 (directory label and split code; original seed log unavailable)')
        paths=[str(run/'run_manifest.json'),str(run/'training_history.csv')] if not nx else [str(run/f'fold_{i:02d}/full/run_manifest.json') for i in ([1,3,4,6] if '4fold' in ds else range(8))]
        evidence=';'.join(paths+[str(code/'train.py'),str(code/'data.py') if (code/'data.py').exists() else str(ROOT/'pre/ixi_diffusion/data.py')])
        if missing:evidence=str(OUT/'search_scope.json')+';'+str(OUT/'search_candidates.txt')+';'+str(run/'run_manifest.json')
        matrix.append({'method':method,'dataset':ds,'status':'MISSING' if missing else 'INVALID','formal_main_table_eligible':False,'training_config':'n25 run absent; code profile only' if missing else 'partial run_manifest + checkpoint model_config; full runtime config not frozen','training_seed':'unknown/unrecorded','split_seed':split,'data_manifest':str(cvroot/'case_cv_summary.json') if nx else str(ROOT/'dataset/IXI/splits/seed3407/split_manifest.json') if missing else str(run/'run_manifest.json'),'code_version_or_sha256':str(OUT/'source_file_inventory.csv')+' (current code SHA-256; historical execution commit unknown)','environment':'repository environment.yml/requirements.txt only; per-run environment unknown/unrecorded','training_history':'absent for n25' if missing else 'present; see run_level_audit.csv','strict_val_history':'not found','strict_val_best_checkpoint':'not found','existing_checkpoint':'n115 checkpoint excluded' if missing else 'ordinary val-loss best; see checkpoint_audit.csv','checkpoint_sha256':'checkpoint_audit.csv / source_file_inventory.csv','final_test_run_manifest':'absent for n25' if missing else 'run_manifest present; does not bind test to checkpoint SHA or selection protocol','per_case_csv':'absent for n25' if missing else 'present; see run_level_audit.csv','summary_csv_json':'absent for n25' if missing else 'present; recomputed from per-case CSV','five_metrics':'absent for n25' if missing else 'PSNR/SSIM/MAE/MSE/NCC; see numeric_consistency_checks.csv','normalization_mode':'n25 execution absent' if missing else 'sparse-input min/max in inference code; mode not recorded in original manifest','stride':4,'generated_slices_only':'n25 execution absent' if missing else 'code idx % 4 != 0; CSV counts verified','test_only_strict_checkpoint':False,'reason':'IXI n=25 result missing; n=115 is separate' if missing else 'checkpoint matches minimum ordinary sliding-window val_loss; dense-volume normalization in validation, not strict sparse x4 validation','evidence_paths':evidence})
        seeds.append({'method':method,'dataset':ds,'training_seed':'unknown/unrecorded','split_seed':split,'seed_evidence':evidence,'note':'Do not infer training seed from data split directory or seed3407.'})
write_csv('evidence_matrix.csv',matrix);write_csv('seed_audit.csv',seeds)

write_csv('validation_checks.csv',checks)
write_csv('source_file_inventory.csv',list(sources.values()))
write_json('copy_map.json',copied)
print(json.dumps({'selected_runs':len(run_records),'checks':len(checks),'source_files':len(sources),'copied_files':len(copied),'checkpoints_packaged':sum(x['included_in_zip'] for x in checkpoint_rows),'summaries':summaries,'extended_hat':extended_result},ensure_ascii=False,indent=2),flush=True)
