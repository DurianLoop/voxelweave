"""Authenticate all19 native inputs and608 same-RNG/whole-patch sampler references."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import copy, json, sys, traceback
from datetime import datetime, timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT, SEED, DEVELOPERS, read, sha, array_sha, load_authenticated_observed, sparse_image,
    physical_shape, resize_image, resize_training_label, training_example, np, torch)
from mc_rc_task_metrics_cpu import independent_label
from mc_rc_coverage_augmentation_draw_cpu_support import example_from_record, example_sha
from mc_rc_global_local_no_augmentation_cpu_support import no_augmentation_training_example
from verify_mc_rc_coverage_augmentation_draw_cpu import reference_example, spatial
OUT=ROOT/'experiments/mc_rc_no_augmentation_development_cpu_preflight'


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate()
    prepfile=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json'
    inputfile=ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json'
    proof=inputfile.parent/'independent_all19_observed_inputs_and_label_axes_attempt_01.json'
    prep,prod,prior=[read(p) for p in (prepfile,inputfile,proof)]
    assert all(r['complete'] and not r['errors'] for r in (prep,prod,prior))
    assert prior['result_sha256']==sha(inputfile)
    cases=prep['cases'];assert len(cases)==19 and {c['patient'] for c in cases}==DEVELOPERS
    OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    protocol=ROOT/'MC_RC_NO_AUGMENTATION_DEVELOPMENT_INPUT_PREFLIGHT_CPU_PROTOCOL_2026-10-03.md'
    code=('mc_rc_global_local_task_cpu_support.py','mc_rc_global_local_no_augmentation_cpu_support.py',
          'mc_rc_coverage_augmentation_draw_cpu_support.py','verify_mc_rc_coverage_augmentation_draw_cpu.py',
          'mc_rc_task_metrics_cpu.py')
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],resources=resources,
        script_sha256=sha(__file__),protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (prepfile,inputfile,proof)],
        code_bindings=[dict(path='experiments/'+s,sha256=sha(ROOT/'experiments'/s)) for s in code],
        series=[],seed=SEED,old_aug_input_sha_matches=0,new_none_reference_sha_matches=0,
        same_rng_final_state_matches=0,full_patch_source_mapping_checks=0,network_forward_calls=0,
        training_updates=0,validation_patients_opened=False,confirmation_patients_opened=False,
        native_hidden_MR_pixels_decoded=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,r)
    try:
        by={s['uid']:s for s in prod['series']}
        for c in cases:
            resource_gate();row=by[c['uid']];obs=load_authenticated_observed(c,row)
            native,stats=sparse_image(obs,'raw_pchip',row);label=independent_label(c)
            assert array_sha(label)==row['label_array_sha256']
            shape,spacing=physical_shape(c);image=resize_image(native,shape);target=resize_training_label(label,shape)
            item=dict(image_zrc=image,label_zrc=target,native_foreground=np.argwhere(label),zspacing=spacing)
            numbered=np.arange(shape[0]*shape[1],dtype=np.int32).reshape(shape)
            rng=np.random.default_rng(SEED);records=[]
            for step in range(32):
                before=copy.deepcopy(rng.bit_generator.state)
                oldrng=np.random.default_rng();oldrng.bit_generator.state=copy.deepcopy(before)
                oldexample=training_example(item,oldrng)
                newexample,record=no_augmentation_training_example(item,rng,step)
                assert oldrng.bit_generator.state==rng.bit_generator.state
                r['same_rng_final_state_matches']+=1
                assert example_sha(oldexample)==example_sha(example_from_record(item,record,'legacy_aug'))
                r['old_aug_input_sha_matches']+=1
                reference=reference_example(item,record,'legacy_none')
                assert example_sha(newexample)==example_sha(reference)
                r['new_none_reference_sha_matches']+=1
                augmented=spatial(numbered,record)
                for native_at,aug_at in zip(record['legacy_native_locations'],record['legacy_augmented_locations']):
                    nr,nc=native_at;ar,ac=aug_at
                    plain=numbered[nr:nr+128,nc:nc+128];transformed=augmented[ar:ar+128,ac:ac+128]
                    assert plain.shape==transformed.shape==(128,128) and np.array_equal(spatial(plain,record),transformed)
                    r['full_patch_source_mapping_checks']+=1
                records.append(dict(step=step,z=record['z'],augmentation=record,
                    old_aug_example_sha256=example_sha(oldexample),new_none_example_sha256=example_sha(newexample),
                    new_none_patch_foreground_mass=float(newexample[2].sum())))
            r['series'].append(dict(patient=c['patient'],uid=c['uid'],native_input_sha256=array_sha(native),
                native_label_sha256=array_sha(label),physical_image_sha256=array_sha(image),
                physical_label_sha256=array_sha(target),physical_shape=list(image.shape),zspacing_mm=spacing,
                observed_statistics=stats,draws=records))
            write(path,r);print(json.dumps(dict(patient=c['patient'],series_verified=len(r['series']),draws_verified=r['same_rng_final_state_matches'])),flush=True)
            del obs,native,label,image,target,item,numbered
        r['gpu_initialized']=torch.cuda.is_initialized();assert not r['gpu_initialized']
        r['complete']=len(r['series'])==19 and r['same_rng_final_state_matches']==r['old_aug_input_sha_matches']==r['new_none_reference_sha_matches']==608 and r['full_patch_source_mapping_checks']==1216
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','same_rng_final_state_matches','full_patch_source_mapping_checks','network_forward_calls','training_updates')}),flush=True)
    return int(not r['complete'])


if __name__=='__main__':
    raise SystemExit(main())
