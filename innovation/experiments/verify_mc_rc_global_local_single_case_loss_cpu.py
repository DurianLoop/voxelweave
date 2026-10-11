"""Verify fixed one-case comparison, all4000 draw replays and six complete planes."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,hashlib,sys,traceback
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT,SEED,GlobalLocalUNet,weight_hash,read,sha,array_sha,load_authenticated_observed,
    sparse_image,physical_shape,resize_image,resize_training_label,training_example,np,torch)
from mc_rc_task_metrics_cpu import independent_label,independent_counts,independent_surface
from verify_mc_rc_global_local_task_validation_cpu import replay_plane
OUT=ROOT/'experiments/mc_rc_global_local_single_case_loss_cpu'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def input_digest(example):
    values=example[:4];h=hashlib.sha256()
    for value in values:h.update(array_sha(value.numpy()).encode())
    h.update(json.dumps(dict(locations=example[4],shape=example[5],record=example[6]),sort_keys=True).encode())
    return h.hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();source=OUT/'attempt_01.json';r=read(source)
    assert r['complete'] and not r['errors'];path=OUT/'independent_metrics_draws_and_checkpoint_attempt_01.json';assert not path.exists()
    code=['mc_rc_global_local_task_cpu_support.py','mc_rc_task_metrics_cpu.py','verify_mc_rc_global_local_task_validation_cpu.py']
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),result_sha256=sha(source),
        code_bindings=[dict(path='experiments/'+s,sha256=sha(ROOT/'experiments'/s)) for s in code],
        arms=[],training_draws_replayed=0,checkpoint_replayed_planes=0,training_updates=0,
        sampler_replay_shares_production_sampler=True,same_architecture_replay=True,
        second_independently_trained_generalization_model=False,native_hidden_MR_pixels_decoded=False,
        validation_patients_opened=False,confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,q)
    try:
        assert r['training_patient_ids']==['VS-MC-RC-012'] and r['training_series_uids']==[r['uid']]
        assert r['seed']==SEED and r['updates_per_arm']==4000 and len(r['arms'])==2
        assert [a['name'] for a in r['arms']]==['bce_batch_dice','asymmetric_unified_focal']
        assert r['matched_initialization_verified'] and r['all_4000_training_draws_matched']
        for binding in r['source_bindings']+r['code_bindings']:assert sha(ROOT/binding['path'])==binding['sha256']
        assert sha(ROOT/r['protocol_file'])==r['protocol_sha256']
        assert sha(ROOT/'experiments/run_mc_rc_global_local_single_case_loss_cpu.py')==r['script_sha256']
        case=next(c for c in read(ROOT/r['source_bindings'][0]['path'])['cases'] if c['uid']==r['uid'])
        assert case==r['case_binding'] and case['patient']=='VS-MC-RC-012'
        row=next(e for e in read(ROOT/r['source_bindings'][1]['path'])['series'] if e['uid']==r['uid'])
        obs=load_authenticated_observed(case,row);native,stats=sparse_image(obs,'raw_pchip',row)
        shape,spacing=physical_shape(case);image=resize_image(native,shape);label=independent_label(case)
        target=resize_training_label(label,shape);b=r['input_binding']
        assert b['native_input_sha256']==array_sha(native) and b['physical_input_sha256']==array_sha(image)
        assert b['native_label_sha256']==array_sha(label) and b['physical_label_sha256']==array_sha(target)
        item=dict(image_zrc=image,label_zrc=target,native_foreground=np.argwhere(label),zspacing=spacing)
        rng=np.random.default_rng(SEED);stream=hashlib.sha256()
        for step in range(4000):
            if step%100==0:resource_gate()
            rng.integers(1);rng.integers(1);digest=input_digest(training_example(item,rng));stream.update(digest.encode())
            for arm in r['arms']:assert arm['draw_sha256'][step]==digest
            q['training_draws_replayed']+=1
            if (step+1)%1000==0:write(path,q);print(json.dumps(dict(draws_replayed=step+1)),flush=True)
        assert all(a['draw_stream_sha256']==stream.hexdigest() and len(a['draw_sha256'])==4000 for a in r['arms'])
        for arm in r['arms']:
            resource_gate();assert arm['complete'] and arm['updates_completed']==4000 and arm['model_parameters']==981602
            torch.manual_seed(SEED);model=GlobalLocalUNet();assert weight_hash(model)==arm['initial_weights_sha256']
            cp=ROOT/arm['checkpoint_file'];assert sha(cp)==arm['checkpoint_sha256']
            checkpoint=torch.load(cp,map_location='cpu',weights_only=True)
            for key in ('initial_weights_sha256','final_weights_sha256','draw_stream_sha256'):assert checkpoint[key]==arm[key]
            assert checkpoint['arm']==arm['name'] and checkpoint['updates_completed']==4000
            assert checkpoint['training_patient_ids']==r['training_patient_ids'] and checkpoint['training_series_uids']==r['training_series_uids']
            model.load_state_dict(checkpoint['state_dict'],strict=True);model.eval();assert weight_hash(model)==arm['final_weights_sha256']
            e=arm['evaluation'];pp=ROOT/e['prediction_file'];assert sha(pp)==e['prediction_file_sha256']
            with np.load(pp,allow_pickle=False) as data:pred=data['prediction_rcz'].copy()
            assert pred.shape==label.shape and pred.dtype==bool and array_sha(pred)==e['prediction_array_sha256']
            n=pred.shape[2];last=(n-1)//4*4;domains=dict(full=list(range(n)),anchors=list(range(0,n,4)),missing=[z for z in range(last) if z%4],tail=list(range(last+1,n)))
            counts={}
            for domain,zs in domains.items():
                value=independent_counts(pred[:,:,zs],label[:,:,zs]);assert all(e['metrics'][domain][k]==v for k,v in value.items());counts[domain]=value
            surface=independent_surface(pred,label,case['affine_rcz_ras'])
            for key,value in surface.items():
                assert (e['metrics']['full_surface'][key] is None) if value is None else abs(e['metrics']['full_surface'][key]-value)<.0001
            checks=dict(full_dice=counts['full']['dice']>=.9,missing_dice=counts['missing']['dice']>=.9,
                full_recall=counts['full']['recall']>=.9,full_absRVE=counts['full']['absolute_relative_volume_error']<=.1)
            assert checks==e['fit_gate_checks'] and all(checks.values())==e['fit_gate_passed']
            planes=[]
            for z in (0,n//2,n-1):
                direct,cov,axes=replay_plane(model,image,z,spacing,case['native_shape'])
                assert np.array_equal(direct,pred[:,:,z]) and array_sha(cov)==e['coverage']['coverage_sha256']
                assert axes==[e['coverage']['row_starts'],e['coverage']['col_starts']];planes.append(z);q['checkpoint_replayed_planes']+=1
            q['arms'].append(dict(name=arm['name'],independent_counts=counts,independent_surface=surface,
                fit_gate_passed_verified=e['fit_gate_passed'],checkpoint_replayed_planes=planes,
                global_forward_calls=model.global_calls,local_forward_calls=model.local_calls));write(path,q)
            print(json.dumps(dict(arm=arm['name'],independent_metrics_verified=True,complete_planes_replayed=3)),flush=True)
        q['global_forward_calls']=sum(a['global_forward_calls'] for a in q['arms']);q['local_forward_calls']=sum(a['local_forward_calls'] for a in q['arms'])
        q['gpu_initialized']=torch.cuda.is_initialized();assert not q['gpu_initialized']
        q['complete']=q['training_draws_replayed']==4000 and q['checkpoint_replayed_planes']==6 and len(q['arms'])==2
    except Exception as error:q['errors'].append(type(error).__name__+': '+str(error));q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,q)
    print(json.dumps({k:q.get(k) for k in ('complete','errors','training_draws_replayed','checkpoint_replayed_planes','global_forward_calls','local_forward_calls')}),flush=True)
    return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
