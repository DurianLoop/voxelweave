"""Metadata-only ordinary baseline preparation; requires real full-schedule audit."""
import sys, time, json, gzip, collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    auditpath=HERE/'full_schedule_audit_attempt01/receipt.json'
    audit=read(auditpath)
    assert audit['complete'] and not audit['errors']
    assert audit['all5984_journal_rows_verified'] and audit['all2992_original_sample_batch_geometry_and_mother_labels_matched']
    for b in audit['source_bindings']:bind(b)
    receiptpath=HERE/'full_schedule_attempt01/receipt.json';r=read(receiptpath)
    assert r['complete'] and r['status']=='completed' and r['geometry_patches_completed']==5984
    journal=ROOT/r['journal_path'];assert sha(journal)==r['journal_sha256']
    with gzip.open(journal,'rt',encoding='utf-8') as f:rows=[json.loads(x) for x in f]
    assert len(rows)==5984
    out=HERE/'whole_patch_policy_attempt01';out.mkdir(exist_ok=False)
    totals=collections.Counter();patients=collections.defaultdict(collections.Counter);series=collections.defaultdict(collections.Counter)
    groups=collections.defaultdict(collections.Counter);decisions=[]
    for row in sorted(rows,key=lambda x:(x['step'],x['patch'])):
        assert row['support_stats']['voxels']==1048576
        active=row['active'];all_support=row['support_stats']['fully_supported_voxels']==1048576
        eligible=bool(active and all_support)
        decision='roundtrip' if eligible else 'identity'
        category='roundtrip_eligible' if eligible else ('active_identity_fallback' if active else 'primitive_identity')
        for v in [totals,patients[row['patient']],series[row['uid']],groups[str(row['geometry']['forced_foreground'])]]:
            v['patches']+=1;v['active']+=int(active);v['all_target_supported']+=int(all_support);v[category]+=1
        decisions.append(dict(step=row['step'],patch=row['patch'],patient=row['patient'],uid=row['uid'],
                              enabled_nonidentity=active,all_target_voxels_supported=all_support,decision=decision,
                              support_binary_sha256=row['support_stats']['fully_supported_mask_sha256'],
                              label_SHA_preserved=row['target_label_sha256']))
    assert totals['patches']==5984 and totals['active']==audit['active_patches']
    assert totals['roundtrip_eligible']+totals['active_identity_fallback']==totals['active']
    assert len(patients)==11 and all(v['patches']==544 for v in patients.values())
    assert len(series)==19
    decisionpath=out/'decisions.jsonl.gz'
    with decisionpath.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
        for x in decisions:f.write((json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8'))
    result=dict(complete=True,errors=[],policy='whole_target_support_or_identity',totals=dict(totals),
                patients={k:dict(v) for k,v in sorted(patients.items())},series={k:dict(v) for k,v in sorted(series.items())},
                forced_foreground_groups={k:dict(v) for k,v in groups.items()},decisions=entry(decisionpath),
                decision_generation_additional_GT_read=False,support_fields_reexecuted=False,training_ready=False,
                MRI_arrays_loaded=0,GT_arrays_loaded=0,checkpoint_arrays_loaded=0,training_updates=0,
                publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-started,
                source_bindings=[entry(p) for p in [Path(__file__),HERE/'ORDINARY_WHOLE_PATCH_POLICY_PREPARATION.md',auditpath,receiptpath,journal]])
    dump(out/'receipt.json',result);resource_guard()
    assert time.perf_counter()-started<120 and sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings','series','patients']}),flush=True)

if __name__=='__main__':main()
