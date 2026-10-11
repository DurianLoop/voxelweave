"""Validate future registry and completed reading records; no GPU, images or train entry."""
import json,time
from pathlib import Path
from resource_guard_v1 import HERE,ROOT,guard,read,entry,bind,dump
started=time.perf_counter();before=guard(started);p=HERE/'FUTURE_EXPERIMENT_REGISTRY.json';v=read(p)
assert v['GPU_authorized'] and not v['automatic_launch'] and not v['publication_claim_confirmed']
assert v['cohort']['strict_LOPO_initialization']=='cold_init_all_arms' and not v['cohort']['confirmation_opened'] and not v['cohort']['locked_IXI_opened']
assert [(v['cohort'][p],v['cohort'][s]) for p,s in [('development_patients','development_series'),('previously_seen_validation_patients','previously_seen_validation_series'),('unseen_confirmation_patients','unseen_confirmation_series')]]==[(11,19),(4,9),(8,12)]
assert len(v['experiments'])==4 and not any(e['execute_now'] for e in v['experiments'])
e=v['experiments'][0];assert e['steps_per_resolution_arm']*e['resolution_arms']==e['development_updates_planned']==17952
assert (ROOT/e['protocol_path']).is_file()
g=v['unchanged_gates'];assert g==dict(patient_mean_full_Dice_min=.7,patient_mean_missing_Dice_min=.65,patient_mean_recall_min=.7,patient_mean_abs_RVE_max=.5,each_patient_full_and_missing_Dice_positive=True,no_series_zero_TP=True,numeric_max_error=3e-6,coordinate_max_error=3e-12,binary_disagreements=0)
assert v['resources']['unchanged_existing_six_arm_budget_bytes']==104156359 and not v['resources']['new_medical_family_storage_budget_frozen']
reading=read(HERE/'reading_provenance_attempt01/receipt.json');assert reading['complete'] and not reading['errors'] and reading['new_distinct_primary_text_papers_read']==3
for b in reading['source_bindings']:bind(b)
assert [r['blocks'] for r in reading['records']]==[59,120,178] and reading['greedy_omitted_Algorithm1_lines_actually_read']==37
for rec in reading['records']:
 bind(rec['source']);assert not rec['figure_pixels_actually_inspected'] and not rec['bibliography_items_actually_read']
 for r in rec['ranges']:bind(r['exposure_receipt']);assert r['actual_text_read'] and r['actual_exit']==0
out=HERE/'preparation_reading_validation_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=True,errors=[],source_bindings=[entry(Path(__file__)),entry(p),entry(ROOT/e['protocol_path']),entry(HERE/'reading_provenance_attempt01/receipt.json')],
 all_future_experiments_pending_and_nonlaunching=True,original_gates_cohorts_and_budget_preserved=True,three_primary_reading_records_and_chunks_bound=True,
 code_preparation_is_not_clinical_validation=True,MRI_arrays_loaded=0,GT_arrays_loaded=0,GPU_calls=0,optimizer_updates=0,
 publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r);print(json.dumps({k:r[k] for k in ('complete','all_future_experiments_pending_and_nonlaunching','original_gates_cohorts_and_budget_preserved','three_primary_reading_records_and_chunks_bound')}))
