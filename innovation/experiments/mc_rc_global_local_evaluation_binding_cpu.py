"""Require a completed frozen training run and authenticated nine-series validation inputs."""
from mc_rc_global_local_task_cpu_support import (
    ROOT, SEED, DEVELOPERS, VALIDATORS, GlobalLocalUNet, weight_hash, read, sha, torch)


def frozen_bindings():
    files = {
        'training': ROOT/'experiments/mc_rc_global_local_task_training_cpu/attempt_01.json',
        'development': ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json',
        'preparation': ROOT/'experiments/mc_rc_validation_task_case_preparation/attempt_01.json',
        'production': ROOT/'experiments/mc_rc_validation_task_input_cpu/attempt_01.json',
        'proof': ROOT/'experiments/mc_rc_validation_task_input_cpu/independent_all9_observed_inputs_and_label_axes_attempt_01.json',
        'geometry': ROOT/'experiments/mc_rc_global_local_geometry_cpu/attempt_01.json',
    }
    records = {k:read(p) for k,p in files.items()}
    assert all(x['complete'] and not x['errors'] for x in records.values())
    training, dev, prep, prod, proof, geometry = [records[k] for k in files]
    assert training['updates_completed'] == training['updates_planned'] == 20000
    assert sum(training['training_sampling_counts'].values()) == 20000
    assert set(training['training_patient_ids']) == DEVELOPERS
    assert set(training['training_series_uids']) == {x['uid'] for x in dev['cases']}
    assert len(dev['cases']) == 19 and len(prep['cases']) == len(prod['series']) == 9
    assert {x['patient'] for x in prep['cases']} == VALIDATORS
    assert {x['uid'] for x in prod['series']} == {x['uid'] for x in prep['cases']}
    assert not (DEVELOPERS & VALIDATORS)
    assert training['device'] == 'cpu' and training['seed'] == SEED
    assert not training['pretrained_weights_loaded'] and not training['gpu_initialized']
    assert training['validation_neural_forwards_before_final_checkpoint'] == 0
    assert not training['confirmation_patients_opened'] and not training['native_hidden_MR_pixels_decoded']
    assert training['scientific_confirmation_patients'] == 0 and not training['publication_claim_confirmed']
    assert training['protocol_sha256'] == sha(ROOT/training['protocol_file'])
    assert training['support_sha256'] == sha(ROOT/'experiments/mc_rc_global_local_task_cpu_support.py')
    assert training['script_sha256'] == sha(ROOT/'experiments/run_mc_rc_global_local_task_training_cpu.py')
    for source in training['source_bindings'] + geometry['source_bindings']:
        assert sha(ROOT/source['path']) == source['sha256']
    assert prod['preparation_sha256'] == sha(files['preparation'])
    assert proof['result_sha256'] == sha(files['production'])
    assert proof['sparse_inputs_verified'] == 36 and proof['labels_verified'] == 9
    assert geometry['support_sha256'] == training['support_sha256']
    assert geometry['neural_forward_calls'] == 0 and not geometry['validation_task_effects_read']
    assert len(geometry['real_inputs']) == 9
    for key, filename, record in (
        ('script_sha256', 'audit_mc_rc_validation_task_input_cpu.py', prod),
        ('loader_sha256', 'mc_rc_task_roles_input_cpu.py', prod),
        ('script_sha256', 'verify_mc_rc_validation_task_input_cpu.py', proof),
        ('script_sha256', 'audit_mc_rc_global_local_geometry_cpu.py', geometry),
    ):
        assert record[key] == sha(ROOT/'experiments'/filename)
    checkpoint_file = ROOT/training['checkpoint_file']
    assert sha(checkpoint_file) == training['checkpoint_sha256']
    torch.manual_seed(SEED)
    model = GlobalLocalUNet()
    assert weight_hash(model) == training['initial_weights_sha256']
    assert sum(p.numel() for p in model.parameters()) == training['model_parameters'] == 981602
    checkpoint = torch.load(checkpoint_file, map_location='cpu', weights_only=True)
    for key in ('updates_completed', 'initial_weights_sha256', 'final_weights_sha256',
                'training_patient_ids', 'training_series_uids', 'protocol_sha256', 'support_sha256', 'seed'):
        assert checkpoint[key] == training[key]
    model.load_state_dict(checkpoint['state_dict'], strict=True)
    assert weight_hash(model) == training['final_weights_sha256']
    model.eval()
    bindings = [dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in files.values()]
    bindings.append(dict(path=checkpoint_file.relative_to(ROOT).as_posix(), sha256=sha(checkpoint_file)))
    return model, records, bindings


def aggregate(evaluations):
    fields = ('dice', 'recall', 'precision', 'absolute_relative_volume_error')
    result = {}
    for method in ('raw_pchip', 'raw_linear'):
        groups = {}
        for patient in sorted(VALIDATORS):
            rows = [e for e in evaluations if e['method']==method and e['patient']==patient]
            assert rows
            values = {}
            for domain in ('full', 'missing', 'anchors', 'tail'):
                values[domain] = {}
                for field in fields:
                    data = [e['metrics'][domain][field] for e in rows]
                    values[domain][field] = (sum(data)/len(data) if all(x is not None for x in data) else None)
                    values[domain][field+'_defined_series'] = sum(x is not None for x in data)
            groups[patient] = dict(series=len(rows), metrics=values)
        mean = {}
        for domain in ('full', 'missing', 'anchors', 'tail'):
            mean[domain] = {}
            for field in fields:
                data = [v['metrics'][domain][field] for v in groups.values()]
                mean[domain][field] = sum(data)/4 if all(x is not None for x in data) else None
                mean[domain][field+'_defined_patients'] = sum(x is not None for x in data)
        result[method] = dict(patient_first_means=mean, patients=groups,
            series_complete_misses=[e['uid'] for e in evaluations
                                    if e['method']==method and e['metrics']['full']['tp']==0])
    primary = result['raw_pchip']
    f, m = primary['patient_first_means']['full'], primary['patient_first_means']['missing']
    gates = dict(
        mean_full_dice_ge_070=f['dice'] is not None and f['dice']>=.70,
        mean_missing_dice_ge_065=m['dice'] is not None and m['dice']>=.65,
        mean_full_recall_ge_070=f['recall'] is not None and f['recall']>=.70,
        mean_full_absRVE_le_050=f['absolute_relative_volume_error'] is not None and f['absolute_relative_volume_error']<=.50,
        all_four_patient_full_missing_dice_positive=all(
            g['metrics'][d]['dice'] is not None and g['metrics'][d]['dice']>0
            for g in primary['patients'].values() for d in ('full','missing')),
        no_series_complete_miss=not primary['series_complete_misses'])
    return result, gates, all(gates.values())
