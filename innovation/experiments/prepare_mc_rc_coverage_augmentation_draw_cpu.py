"""Authenticate 4000 legacy draws and prepare four paired-support sampling conditions."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,json,traceback,hashlib
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT,SEED,read,sha,array_sha,load_authenticated_observed,sparse_image,physical_shape,
    resize_image,resize_training_label,np,torch,starts)
from mc_rc_observed_only_training_input import read_supervised_label
from mc_rc_coverage_augmentation_draw_cpu_support import ARMS,legacy_primitive,example_from_record,example_sha,record_sha
OUT=ROOT/'experiments/mc_rc_coverage_augmentation_draw_cpu'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    oldp=ROOT/'experiments/mc_rc_global_local_single_case_loss_cpu/attempt_01.json'
    qp=oldp.parent/'independent_metrics_draws_and_checkpoint_attempt_01.json';old,q=read(oldp),read(qp)
    assert old['complete'] and q['complete'] and not old['errors'] and not q['errors'] and q['result_sha256']==sha(oldp)
    oldarm=old['arms'][0];assert oldarm['name']=='bce_batch_dice' and oldarm['updates_completed']==4000
    prep=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json';prod=ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json'
    case=next(c for c in read(prep)['cases'] if c['uid']==old['uid']);assert case['patient']=='VS-MC-RC-012'
    row=next(e for e in read(prod)['series'] if e['uid']==case['uid']);protocol=ROOT/'MC_RC_COVERAGE_AUGMENTATION_DRAW_CPU_PROTOCOL_2026-10-03.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],resources=resources,
        protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),script_sha256=sha(__file__),
        draw_support_sha256=sha(ROOT/'experiments/mc_rc_coverage_augmentation_draw_cpu_support.py'),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (oldp,qp,prep,prod)],
        case_binding=case,seed=SEED,updates_planned=4000,draws_completed=0,arms=list(ARMS),
        rows=[],legacy_exact_matches=0,per_z_updates={},per_z_coverage_tile_exposure={},
        foreground_mass_by_arm={a:[] for a in ARMS},network_forward_calls=0,training_updates=0,
        native_hidden_MR_pixels_decoded=False,validation_patients_opened=False,confirmation_patients_opened=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,r)
    try:
        obs=load_authenticated_observed(case,row);native,_=sparse_image(obs,'raw_pchip',row);label=read_supervised_label(case)
        assert array_sha(label)==row['label_array_sha256'];shape,spacing=physical_shape(case)
        image=resize_image(native,shape);target=resize_training_label(label,shape)
        item=dict(image_zrc=image,label_zrc=target,native_foreground=np.argwhere(label),zspacing=spacing)
        r['input_binding']=dict(native_input_sha256=array_sha(native),physical_input_sha256=array_sha(image),
            native_label_sha256=array_sha(label),physical_label_sha256=array_sha(target),shape=list(image.shape))
        assert r['input_binding']['physical_input_sha256']==old['input_binding']['physical_input_sha256']
        rng=np.random.default_rng(SEED);cursors={};stream=hashlib.sha256()
        for step in range(4000):
            if step%100==0:resource_gate()
            record=legacy_primitive(item,rng,step,cursors);digests={}
            for arm in ARMS:
                example=example_from_record(item,record,arm);digests[arm]=example_sha(example)
                r['foreground_mass_by_arm'][arm].append(float(example[2].sum()))
            assert digests['legacy_aug']==oldarm['draw_sha256'][step];r['legacy_exact_matches']+=1
            record['example_sha256_by_arm']=digests;r['rows'].append(record);stream.update(record_sha(record).encode())
            z=str(record['z']);r['per_z_updates'][z]=r['per_z_updates'].get(z,0)+1
            exposure=r['per_z_coverage_tile_exposure'].setdefault(z,{})
            for tile in record['coverage_tile_ids']:exposure[str(tile)]=exposure.get(str(tile),0)+1
            r['draws_completed']=step+1
            if (step+1)%500==0:write(path,r);print(json.dumps(dict(draws_completed=step+1,legacy_exact_matches=r['legacy_exact_matches'])),flush=True)
        assert len(r['per_z_updates'])==case['native_shape'][2]
        r['record_stream_sha256']=stream.hexdigest();r['legacy_baseline_exact_reuse_eligible']=r['legacy_exact_matches']==4000
        r['legacy_baseline_initial_weights_sha256']=oldarm['initial_weights_sha256']
        r['legacy_baseline_checkpoint_file']=oldarm['checkpoint_file'];r['legacy_baseline_checkpoint_sha256']=oldarm['checkpoint_sha256']
        r['tiles_per_physical_plane']=len(starts(shape[0]))*len(starts(shape[1]))
        assert all(len(v)==r['tiles_per_physical_plane'] for v in r['per_z_coverage_tile_exposure'].values())
        r['gpu_initialized']=torch.cuda.is_initialized();assert not r['gpu_initialized'];r['complete']=True
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','draws_completed','legacy_exact_matches','legacy_baseline_exact_reuse_eligible','gpu_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
