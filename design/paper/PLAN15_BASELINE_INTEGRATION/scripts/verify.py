"""Verify source preservation, complete baseline coverage, and paired analyses."""
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
P=Path(__file__).resolve().parents[1];ROOT=P.parent.parents[1];O=P/'outputs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
for phase in ['PLAN13_EVIDENCE_UPGRADE','PLAN14_SCIENTIFIC_STRENGTHENING','PLAN15_BASELINE_INTEGRATION']:
    base=P.parent/phase;m=json.loads((base/'original_manifest.json').read_text())
    assert all(sha(base/'original_snapshot'/r['path'])==r['sha256'] for r in m['files'])
    checks.append({'check':phase+'_protected_snapshot','files':len(m['files']),'passed':True})
s=json.loads((O/'source_manifest.json').read_text());master=s['master']
assert sha(ROOT/master['path'])==master['sha256'] and sha(P/'master_table_original.md')==master['sha256']
assert all(sha(ROOT/r['path'])==r['sha256'] for r in s['summary_files'])
checks.append({'check':'master_and_full_summary_sources_unchanged','summary_files':len(s['summary_files']),'passed':True})
m=json.loads((O/'analysis_manifest.json').read_text());r=json.loads((O/'saint_recovery_manifest.json').read_text())
assert all(sha(ROOT/x['path'])==x['sha256'] for x in m['per_case_source_files']+r['sources'])
assert sha(P/'scripts/recover_saint.py')==r['script_sha256'] and sha(P/'scripts/analyze_baselines.py')==m['script_sha256']
assert sha(P/'PROTOCOL.md')==m['protocol_sha256']==r['protocol_sha256']
assert sha(ROOT/'pre/topcow_diffusion/metrics.py')==r['metric_source_sha256']
checks.append({'check':'case_metrics_SAINT_predictions_scripts_protocol_unchanged','source_records':len(m['per_case_source_files'])+len(r['sources']),'passed':True})
a=pd.read_csv(O/'baseline_all_verified.csv');assert len(a)==111 and a.status.isin(['MATCH','RECOVERED_FROM_PREDICTIONS']).all()
assert (a.max_rounding_difference<=.000051).all()
assert len(a[(a.budget=='master')&(a.scale==4)])==39
assert len(a[(a.budget=='master')&(a.scale!=4)])==52
assert len(a[a.budget!='master'])==20
assert not a.duplicated(['dataset','model','scale','budget']).any()
for ds in ['IXI','fastMRI','NingXia']:assert a[(a.dataset==ds)&(a.budget=='master')&(a.scale==4)].model.nunique()==13
assert max(x['max_summary_reproduction_error'] for x in m['per_row_checks'])<1e-8
checks.append({'check':'all_111_configurations_555_metric_cells_verified','passed':True,'max_rounding_error':float(a.max_rounding_difference.max()),'per_case_rows':m['native_case_rows']})
support=pd.read_csv(O/'target_support_audit.csv');assert support.cases_with_unequal_model_target_counts.eq(0).all()
c=pd.read_csv(O/'all13_error_dependence_pairs.csv');assert len(c)==234 and c.groupby('dataset').size().eq(78).all()
checks.append({'check':'case_count_support_and_all_234_model_pairs','passed':True})
b=pd.read_csv(O/'training_budget_paired.csv');assert len(b)==20
for metric in ['psnr','ssim','mae','mse','ncc']:
    assert np.allclose(b[metric+'_delta'],b[metric+'_extended']-b[metric+'_standard'],rtol=1e-10,atol=1e-8)
assert np.allclose(b.mae_gain,-b.mae_delta)
positive=int((b.mae_gain_sim_low>0).sum());uncertain=int(((b.mae_gain_sim_low<=0)&(b.mae_gain_sim_high>=0)).sum());assert (positive,uncertain)==(15,5)
checks.append({'check':'all_20_paired_budget_effects_and_interval_directions','positive_simultaneous':positive,'cross_zero':uncertain,'passed':True})
build=json.loads((P/'build_logs/build_audit.json').read_text());assert all(x['success'] and not x['issues'] for x in build)
cv=(P/'build_logs/cvpr_text.txt').read_text(encoding='utf-8').split(chr(12));assert 'References' in cv[8] and 'References' not in ''.join(cv[:8])
checks.append({'check':'four_documents_compile_and_CVPR_eight_technical_pages','passed':True,'documents':build})
(O/'verification.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
