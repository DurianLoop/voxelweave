"""Independent batch/dispatch proof; does not import the new worker or run networks."""
import hashlib,json,sys,time,traceback
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
OUT=HERE/'independent_attempt01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);tick=time.perf_counter();denied=[]
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        try:p=Path(args[0]).resolve()
        except (ValueError,TypeError,OSError):return
        mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT.parent) and (p.name.endswith(('.zip','.nii','.nii.gz','.npy','.npz','.pt')) or p.is_relative_to(ROOT.parent/'data')):
            denied.append(str(p));raise PermissionError('Independent synthetic proof rejects medical/weight IO')
    sys.addaudithook(audit)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],synthetic_only=True,
        new_worker_imported=False,neural_forwards=0,GPU_forwards=0,training_updates=0,
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,independent_network_resume_reexecuted=False,
        independent_FOV_neural_forward_reexecuted=False,publication_claim_confirmed=False,goal_status='active')
    try:
        from mc_rc_3d_direct_observed_2026_10_07 import physical_fields,canonical_states,array_sha,torch
        from mc_rc_common_projected_observed_2026_10_08 import shared_source,projected_pair_fields
        from mc_rc_reference_resources_2026_10_07 import resource_guard
        from synthetic_case import fixture
        import numpy as np
        resource_guard();torch.set_num_threads(1)
        source=HERE/'synthetic_attempt01/receipt.json';q=json.loads(source.read_text(encoding='utf-8'))
        assert q['complete'] and not q['errors'] and all(q['gate'].values()) and q['unknown_arm_rejected']
        for b in q['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        _,initial=canonical_states();h=hashlib.sha256()
        for k,v in initial.items():h.update(k.encode());h.update(array_sha(v.detach().numpy()).encode())
        assert h.hexdigest()==q['canonical_two_channel_state_sha256']
        assert sum(v.numel() for v in initial.values())==1401795
        cache={}
        for which in (1,2):
            observed,grid,target=fixture(which)
            legacy,st,_=physical_fields(observed,grid)
            shared,_=shared_source(observed,grid);common,_=projected_pair_fields(shared,grid)
            assert np.array_equal(legacy['availability'],common['availability']) and np.array_equal(legacy['valid_grid'],common['valid_grid'])
            uid='SYNTHETIC_UID_'+str(which);cache[uid]=dict(legacy,common_dense=common['dense'],target=target)
            saved=next(v for v in q['factory_records'] if v['uid']==uid)
            assert {k:array_sha(v) for k,v in cache[uid].items()}==saved['array_sha256']
        specifications={'legacy_dense':('dense','dense'),'direct':('numerator','direct'),'common_projected_dense':('common_dense','dense')}
        assert {a['kind'] for a in q['arms']}==set(specifications) and len(q['arms'])==3
        checks=[]
        for arm in q['arms']:
            field,semantic=specifications[arm['kind']]
            assert arm['complete'] and arm['initial_weights_sha256']==h.hexdigest() and arm['parameter_count']==1401795
            assert len(arm['history'])==3 and arm['planned_updates']==3 and arm['actual_resource_updates']==4
            assert arm['resume_check']['full_model_optimizer_RNG_tree_exact'] and arm['resume_check']['extra_resource_updates']==1
            for record,shared in zip(arm['history'],q['shared_training_draws']):
                assert all(record[k]==shared[k] for k in ('step','round_index','patient','uid'))
                bundle=cache[record['uid']];xs=[];ys=[]
                for draw in shared['draws']:
                    cut=tuple(slice(s,s+p) for s,p in zip(draw['start'],(64,128,128)))
                    signal=bundle[field][cut].copy();mask=bundle['availability'][cut].copy();label=bundle['target'][cut].copy()
                    support=mask if semantic=='direct' else bundle['valid_grid'][cut]
                    signal=np.float32(draw['intensity_scale'])*signal+np.float32(draw['intensity_shift'])*support
                    signal[bundle['valid_grid'][cut]==0]=0
                    for axis,flip in enumerate(draw['flips']):
                        if flip:
                            indices=np.arange(signal.shape[axis]-1,-1,-1)
                            signal=np.take(signal,indices,axis=axis);mask=np.take(mask,indices,axis=axis);label=np.take(label,indices,axis=axis)
                    assert int(label.sum())==draw['target_foreground']
                    xs.append(np.stack((signal,mask)));ys.append(label[None])
                x=np.stack(xs);y=np.stack(ys)
                assert array_sha(x)==record['input_batch_sha256'] and array_sha(y)==record['label_batch_sha256']
                assert record['selected_field']==field and record['augmentation_semantic']==semantic
                assert record['selected_full_field_sha256']==array_sha(bundle[field])
                assert record['mask_gradient_max']>0 and all(record['gradient_groups'][v]>0 for v in ('encoders','decoders','ups','heads'))
                checks.append(dict(arm=arm['kind'],step=record['step'],uid=record['uid'],input_and_label_hash_exact=True,
                    selected_field=field,augmentation_semantic=semantic,mask_batch_sha256=array_sha(x[:,1])))
            f0,f1=arm['FOV_passes'];assert f0['metadata']==f1['metadata'] and f0['selected_field']==f1['selected_field']==field
            assert f0['selected_full_field_sha256']==f1['selected_full_field_sha256']==array_sha(cache[f0['uid']][field])
            meta=f0['metadata'];assert meta['full_fov'] and not meta['label_used_for_inference'] and meta['input_channels']==2
            assert meta['total_tiles']==8 and meta['forward_calls']==4 and meta['coverage_min']>0
            assert arm['discarded_final_weights_sha256']!=arm['initial_weights_sha256'] and not arm['updated_weights_saved']
        for step in (1,2,3):assert len({v['mask_batch_sha256'] for v in checks if v['step']==step})==1
        assert q['actual_resource_updates']==12 and q['completed_model_forward_calls']==q['attempted_model_forward_calls']==36
        assert not q['CUDA_initialized'] and not q['task_effects_scored'] and not q['updated_weights_saved']
        assert not denied and not q['io_audit']['denied_read_attempts'] and 'three_arm_resource_worker' not in sys.modules
        result.update(complete=True,source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md'),entry(HERE/'synthetic_case.py'),entry(source)],
            input_factory_records_reconstructed=2,independent_batch_checks=checks,independent_batch_count=9,
            three_arm_mask_and_label_sharing_verified=True,canonical_weights_and_capacity_verified=True,
            three_resume_record_proofs_verified=True,three_FOV_dispatch_and_repeat_record_proofs_verified=True,
            synthetic_updates_in_source=12,neural_forward_calls_in_source=36,denied_reads=denied,CUDA_initialized=False)
    except Exception as e:result['errors'].append(type(e).__name__+': '+str(e));result['traceback']=traceback.format_exc()
    result['elapsed_seconds']=time.perf_counter()-tick
    with (OUT/'receipt.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:result.get(k) for k in ('complete','errors','independent_batch_count','synthetic_updates_in_source','neural_forward_calls_in_source','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not result['complete'] or bool(result['errors']))
if __name__=='__main__':raise SystemExit(main())
