"""Build metadata-only complete-patient head folds with honest task exposure."""
import math

FEATURE_NAMES=(
 'observed_adjacent_spacing_mm','retained_adjacent_spacing_min_mm','retained_adjacent_spacing_max_mm',
 'observed_anchor_count','heldout_observed_plane_count','target_rows','target_cols','heldout_observed_pixel_count',
 'heldout_linear_MSE','heldout_pchip_MSE','heldout_MSE_pchip_minus_linear','heldout_linear_MAE','heldout_pchip_MAE',
 'retained_mean_min','retained_mean_max','retained_population_std_min','retained_population_std_max')

def require(value,message):
    if not value:raise ValueError(message)

def build_registry(table,config):
    require(table['complete'] is True and not table['errors'],'Feature table must be complete')
    require(config['frozen'] is True,'Task training config must be frozen')
    patients=config['patient_ids']
    require(patients and len(set(patients))==len(patients),'Unique training patients required')
    expected={(r['patient'],r['uid']) for r in config['series']}
    require(len(expected)==len(config['series']),'Duplicate configured series')
    require({p for p,u in expected}==set(patients),'Configured patient/series sets differ')
    require(len({u for p,u in expected})==len(expected),'Series UID belongs to multiple patients')
    records=[];seen=set()
    for row in table['rows']:
        key=(row['patient'],row['series_uid'])
        require(key in expected and key not in seen,'Extra, duplicate or wrong patient/UID feature row')
        require(set(row['features'])==set(FEATURE_NAMES),'Feature allowlist differs; IDs must not be features')
        require(all(type(v) in (int,float) and math.isfinite(v) for v in row['features'].values()),'Finite numeric features required')
        require(row['observed_reference_is_available_at_deployment'] is True,'Observed-only dependency required')
        require(all(row[k] is None for k in ('MRI_task_labels','action_utility_labels','full_action_cost')),
                'This preparation must use the frozen unlabeled feature table')
        digest=row['observed_package_sha256']
        require(isinstance(digest,str) and len(digest)==64 and set(digest)<=set('0123456789abcdef'),'Source SHA required')
        records.append(dict(patient=key[0],series_uid=key[1],observed_package_sha256=digest,
                            features={k:row['features'][k] for k in FEATURE_NAMES},
                            MRI_task_labels=None,action_utility_labels=None,full_action_cost=None))
        seen.add(key)
    require(seen==expected,'Missing complete series feature coverage')
    return dict(patient_ids=sorted(patients),series=sorted(records,key=lambda r:(r['patient'],r['series_uid'])),
                predictor_feature_names=list(FEATURE_NAMES),identifiers_used_only_for_join_and_group=True)

def validate_fold(registry,fold,task_training_patients):
    allpatients=set(registry['patient_ids']);heldout=fold['heldout_patient']
    require(heldout in allpatients,'Unknown heldout patient')
    train=set(fold['head_training_patients']);test=set(fold['head_heldout_patients'])
    require(len(train)==len(fold['head_training_patients']) and len(test)==len(fold['head_heldout_patients']),
            'Duplicate head patient membership')
    require(test=={heldout} and train==allpatients-test,'Head folds must exclude an entire patient')
    expected={(r['patient'],r['series_uid']) for r in registry['series']}
    sources={(r['patient'],r['series_uid']):r['observed_package_sha256'] for r in registry['series']}
    seen=set()
    for role,people in (('head_training_series',train),('head_heldout_series',test)):
        actual=set()
        for r in fold[role]:
            key=(r['patient'],r['series_uid'])
            require(key in expected and key not in seen,'Extra/duplicate/overlapping series membership')
            require(r['patient'] in people,'Patient series crosses head fold')
            require(r['observed_package_sha256']==sources[key],'Observed source binding changed')
            seen.add(key);actual.add(key)
        require(actual=={key for key in expected if key[0] in people},'Incomplete patient series group')
    require(seen==expected,'Incomplete fold series coverage')
    actual_excluded=heldout not in set(task_training_patients)
    require(fold['task_model_patient_excluded']==actual_excluded,'Incorrect task model exposure declaration')
    if not actual_excluded:
        require(fold['pipeline_patient_out'] is False,'Head-only exclusion cannot certify pipeline exclusion')
    else:
        require(fold['pipeline_patient_out'] is None,'Unknown other pipeline exposures must remain unresolved')
    return True

def build_folds(registry,task_training_patients):
    result=[]
    for p in registry['patient_ids']:
        keys=('patient','series_uid','observed_package_sha256')
        fold=dict(heldout_patient=p,head_training_patients=[q for q in registry['patient_ids'] if q!=p],
            head_heldout_patients=[p],head_training_series=[{k:r[k] for k in keys} for r in registry['series'] if r['patient']!=p],
            head_heldout_series=[{k:r[k] for k in keys} for r in registry['series'] if r['patient']==p],
            task_model_patient_excluded=p not in set(task_training_patients),
            pipeline_patient_out=False if p in set(task_training_patients) else None,
            label_scope='development_task_in_sample' if p in set(task_training_patients) else 'task_patient_out_other_components_unresolved',
            fitted_head=None,feature_scaler=None,selected_threshold=None,
            preprocessing_rule='Fit any learned scaler, head and threshold on head_training_patients only')
        validate_fold(registry,fold,task_training_patients);result.append(fold)
    return result

def training_readiness(registry,label_bundle=None):
    # Real labels need a separate source-bound complete-FOV adapter, not an invented placeholder label.
    if label_bundle is not None:
        raise ValueError('Actual task label adapter is not qualified; do not bypass final task gates')
    return dict(ready=False,complete_feature_rows=len(registry['series']),
        missing=['paired_complete_patient_action_task_endpoints','frozen_final_task_checkpoints_and_actual_exits',
                 'current_state_and_candidate_action_definitions','full_measured_action_and_shared_costs',
                 'checkpoint_and_other_learned_component_training_exposure'],
        actual_task_labels=0,head_fits=0,patient_out_pipeline_effect_measured=False)
