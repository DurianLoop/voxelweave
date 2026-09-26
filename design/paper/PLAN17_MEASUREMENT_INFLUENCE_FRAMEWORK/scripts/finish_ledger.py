from common import *
ledger=json.loads((P/'research_ledger.json').read_text(encoding='utf-8'))
ning=[]
for fold in range(8):
 for model in ['hat','swinir']:
  q=ROOT/'baseline'/f'ningxia_t2_{model}_2p5d_cv'/'runs'/f'fold_{fold:02d}'/'full/checkpoints'/f'{model}_epoch_best.pth'
  ning.append({'dataset':'ningxia','model':model,'fold':f'fold_{fold:02d}','checkpoint':q.relative_to(ROOT).as_posix(),'exists':q.exists(),'sha256':sha(q) if q.exists() else None,'source':'CVPR_UPGRADE/DATA_MANIFEST.csv and plan6_neural_shared_influence.py checkpoint()'})
ledger['ningxia_primary_influence_checkpoint_bindings']=ning
ledger['critical_findings'] += ['Original clean ranking pools planes/models against fixed phase0 error; cluster bootstrap does not make the point estimate case-level.','Historical broad influence includes 966 self-pairs; the new explicitly post-hoc non-self sensitivity retains all six positive simultaneous advantages.']
ledger['new_iteration']={'protocol':'PROTOCOL.md','score_formula':'outputs/score_formula_freeze.json','geometry_note':'PROTOCOL_EXECUTION_NOTE.md','posthoc_integrity_addendum':'INTEGRITY_ADDENDUM.md','new_experiment_registry':'experiment_registry.csv','new_sources':['outputs/neural_score_manifest.json','outputs/qualitative_inference.json','outputs/practical_proxy_manifest.json','outputs/nonself_influence_manifest.json'],'new_untouched_holdout':False,'score_search_stopped_after_candidates':1}
(P/'research_ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
regs=[
 ('P17-E00','scientific_provenance_audit','completed','all discoverable historical sources','source artifact',0,'outputs/source_inventory.json','research_audit.md','mutable timestamps; chronology not fully recoverable'),
 ('P17-E01','local_covariance_numerical_check','completed','12 synthetic covariance settings','mathematical simulation',12,'outputs/proposition_numerical_check.csv','outputs/proposition_verification.json','not natural-image generalization'),
 ('P17-E02-ENV','score_metric_dependency','technical_failure_resolved','Python environment','not an experiment',0,'scripts/analyze_scores.py','outputs/score_analysis_status.json','sklearn unavailable; replaced by verified direct AP/AUC definitions, no score change'),
 ('P17-E02','single_dependency_guard','completed_no_superiority','fastMRI development12/eval12; IXI115','examination',139,'outputs/neural_pair_per_case.csv','outputs/score_evaluation.csv','no fastMRI positives; two IXI positives/pair; all12 simultaneous contrasts include zero; cohorts previously seen'),
 ('P17-E03A','median_and_random_qualitative','completed','fastMRI SwinIR two selected cases','illustrative examination',2,'outputs/qualitative_selection_before_inference.json','outputs/qualitative_inference.json','CPU float32 differs from historical GPU mixed precision'),
 ('P17-E03B-TECH','analytic_proxy_geometry_gate','technical_failure_recorded','first fastMRI case then full eligibility scan','examination',24,'PROTOCOL_EXECUTION_NOTE.md','outputs/practical_proxy_geometry_exclusions.csv','depth16 cannot provide both full-support residue classes; no relaxed boundary rule'),
 ('P17-E03B','two_member_variance_sharing','completed','IXI115; fastMRI24 geometrically ineligible','examination',115,'outputs/practical_proxy_per_plane.csv','outputs/practical_proxy_summary.csv','analytic ensemble only; variance and pair difference are dependent constructions'),
 ('P17-E04','framework_invariance_and_integrity','completed','generic frozen linear estimator and new tables','software/numerical check',0,'scripts/mira.py','outputs/framework_verification.json','tests validate contracts not clinical utility'),
 ('P17-E05','non_MRI_transfer_feasibility','skipped_not_qualified','no matched non-MRI source established','none',0,'research_audit.md','PROTOCOL.md','do not count synthetic covariance checks as natural-image generalization'),
 ('P17-E06','nonself_influence_sensitivity','completed_posthoc','fastMRI24 IXI115 NingXia8 patients/22series','examination/patient',161,'outputs/nonself_influence_summary.csv','outputs/nonself_influence_manifest.json','966 self-pairs removed; six-stratum simultaneous intervals positive; fixed-count NingXia failure retained')]
cols=['experiment_id','name','status','cohort_or_source','independent_unit','examinations_or_series','input_or_protocol','output','limitations_or_failure']
df=pd.DataFrame(regs,columns=cols);df['registry_written_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();df.to_csv(P/'experiment_registry.csv',index=False)
print('NingXia',sum(r['exists'] for r in ning),'/16 checkpoints; registry',len(df),'records')
