"""Authenticate the new terminal20k checkpoint and fixed developer/validator inputs."""
from mc_rc_global_local_task_cpu_support import (
    ROOT, SEED, DEVELOPERS, VALIDATORS, GlobalLocalUNet, weight_hash, read, sha, torch)


def frozen_bindings():
    files={
        'training':ROOT/'experiments/mc_rc_intensity_only_gpu_capability/attempt_01.json',
        'training_verifier':ROOT/'experiments/mc_rc_intensity_only_gpu_capability/independent_all20000_draws_and_checkpoint_attempt_01.json',
        'development':ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json',
        'development_inputs':ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json',
        'development_proof':ROOT/'experiments/mc_rc_development_training_input_cpu/independent_all19_observed_inputs_and_label_axes_attempt_01.json',
        'validation':ROOT/'experiments/mc_rc_validation_task_case_preparation/attempt_01.json',
        'validation_inputs':ROOT/'experiments/mc_rc_validation_task_input_cpu/attempt_01.json',
        'validation_proof':ROOT/'experiments/mc_rc_validation_task_input_cpu/independent_all9_observed_inputs_and_label_axes_attempt_01.json',
        'geometry':ROOT/'experiments/mc_rc_global_local_geometry_cpu/attempt_01.json'}
    records={key:read(path) for key,path in files.items()}
    assert all(r['complete'] and not r['errors'] for r in records.values())
    raw,q=records['training'],records['training_verifier']
    assert raw['arm_order']==['intensity_only'] and len(raw['arms'])==1 and raw['total_updates_completed']==20000
    arm=raw['arms'][0];assert arm['name']=='intensity_only' and arm['complete']
    t=dict(raw,**arm)
    t.update(updates_planned=raw['planned_updates_per_arm'],training_patient_ids=q['training_patient_ids'],
        training_series_uids=q['training_series_uids'],model_parameters=q['model_parameters'],
        validation_neural_forwards_before_final_checkpoint=raw['validation_neural_forwards_before_all_checkpoints'])
    records['training']=t
    assert q['result_sha256']==sha(files['training']) and q['checkpoint_authenticated']
    assert q['intensity_reference_example_checks']==q['original_aug_example_checks']==q['same_rng_end_state_checks']==20000
    assert q['full_patch_source_mapping_checks']==40000 and q['network_forward_calls']==q['training_updates']==0
    assert t['updates_completed']==t['updates_planned']==20000 and t['seed']==SEED and t['device']=='cuda:0'
    assert not t['pretrained_weights_loaded'] and t['gpu_initialized']
    assert t['validation_neural_forwards_before_final_checkpoint']==0 and not t['confirmation_patients_opened']
    assert not t['native_hidden_MR_pixels_decoded'] and not t['publication_claim_confirmed']
    assert t['scientific_confirmation_patients']==0 and t['model_parameters']==981602
    assert t['global_forward_calls']==t['local_forward_calls']==20000
    for item in t['source_bindings']+t['code_bindings']+q['code_bindings']:
        assert sha(ROOT/item['path'])==item['sha256']
    assert sha(ROOT/t['protocol_file'])==t['protocol_sha256']
    assert sha(ROOT/'experiments/run_mc_rc_intensity_only_gpu_capability.py')==t['script_sha256']
    assert sha(ROOT/'experiments/verify_mc_rc_intensity_only_gpu_training_cpu.py')==q['script_sha256']
    dev,val=records['development']['cases'],records['validation']['cases']
    assert len(dev)==19 and len(val)==9
    assert {c['patient'] for c in dev}==DEVELOPERS and {c['patient'] for c in val}==VALIDATORS
    assert not (DEVELOPERS & VALIDATORS) and set(t['training_patient_ids'])==DEVELOPERS
    assert t['training_series_uids']==[c['uid'] for c in dev]
    for prefix,n,inputs in (('development',19,76),('validation',9,36)):
        production,proof=records[prefix+'_inputs'],records[prefix+'_proof']
        assert proof['result_sha256']==sha(files[prefix+'_inputs'])
        assert proof['labels_verified']==n and proof['sparse_inputs_verified']==inputs
        assert {c['uid'] for c in records[prefix]['cases']}=={s['uid'] for s in production['series']}
    vp=records['validation_inputs'];assert vp['preparation_sha256']==sha(files['validation'])
    geometry=records['geometry']
    assert geometry['support_sha256']==sha(ROOT/'experiments/mc_rc_global_local_task_cpu_support.py')
    assert geometry['neural_forward_calls']==0 and not geometry['validation_task_effects_read']
    for binding in geometry['source_bindings']:assert sha(ROOT/binding['path'])==binding['sha256']
    for key,filename,record in (
        ('script_sha256','audit_mc_rc_validation_task_input_cpu.py',vp),
        ('loader_sha256','mc_rc_task_roles_input_cpu.py',vp),
        ('script_sha256','verify_mc_rc_validation_task_input_cpu.py',records['validation_proof']),
        ('script_sha256','audit_mc_rc_global_local_geometry_cpu.py',geometry)):
        assert record[key]==sha(ROOT/'experiments'/filename)
    cp=ROOT/t['checkpoint_file'];assert sha(cp)==t['checkpoint_sha256']
    torch.manual_seed(SEED);model=GlobalLocalUNet()
    assert weight_hash(model)==t['initial_weights_sha256']
    checkpoint=torch.load(cp,map_location='cpu',weights_only=True)
    for key in ('updates_completed','seed','initial_weights_sha256','final_weights_sha256',
                'training_patient_ids','training_series_uids','protocol_sha256','draw_stream_sha256'):
        assert checkpoint[key]==t[key]
    model.load_state_dict(checkpoint['state_dict'],strict=True);model.eval()
    assert weight_hash(model)==t['final_weights_sha256'] and model.global_calls==model.local_calls==0
    bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in files.values()]
    bindings.append(dict(path=cp.relative_to(ROOT).as_posix(),sha256=sha(cp)))
    return model,records,bindings


def aggregate_group(rows,patients,methods):
    fields=('dice','precision','recall','signed_relative_volume_error','absolute_relative_volume_error')
    result={}
    for method in methods:
        groups={}
        for patient in sorted(patients):
            entries=[e for e in rows if e['method']==method and e['patient']==patient];assert entries
            values={}
            for domain in ('full','missing','anchors','tail'):
                values[domain]={}
                for field in fields:
                    data=[e['metrics'][domain][field] for e in entries]
                    values[domain][field]=sum(data)/len(data) if all(v is not None for v in data) else None
                    values[domain][field+'_defined_series']=sum(v is not None for v in data)
            groups[patient]=dict(series=len(entries),metrics=values)
        means={}
        for domain in ('full','missing','anchors','tail'):
            means[domain]={}
            for field in fields:
                data=[v['metrics'][domain][field] for v in groups.values()]
                means[domain][field]=sum(data)/len(patients) if all(v is not None for v in data) else None
                means[domain][field+'_defined_patients']=sum(v is not None for v in data)
        result[method]=dict(patients=groups,patient_first_means=means,
            complete_miss_series=[e['uid'] for e in rows if e['method']==method and e['metrics']['full']['tp']==0],
            empty_prediction_series=[e['uid'] for e in rows if e['method']==method and e['metrics']['full']['empty_prediction']])
    return result


def validation_gates(aggregate):
    primary=aggregate['raw_pchip'];f=primary['patient_first_means']['full'];m=primary['patient_first_means']['missing']
    return dict(mean_full_dice_ge_070=f['dice'] is not None and f['dice']>=.70,
        mean_missing_dice_ge_065=m['dice'] is not None and m['dice']>=.65,
        mean_full_recall_ge_070=f['recall'] is not None and f['recall']>=.70,
        mean_full_absRVE_le_050=f['absolute_relative_volume_error'] is not None and f['absolute_relative_volume_error']<=.50,
        all_four_patient_full_missing_dice_positive=all(v['metrics'][d]['dice'] is not None and v['metrics'][d]['dice']>0
            for v in primary['patients'].values() for d in ('full','missing')),
        no_series_complete_miss=not primary['complete_miss_series'])
