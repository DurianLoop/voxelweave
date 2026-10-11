"""No-update diagnosis of all tile/head outputs and loss gradients at initial/final fixed states."""
import json, sys, time, traceback
from datetime import datetime, timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (ROOT, read, sha, array_sha, resource_guard, torch, np, F,
    fixed_cases, lattice, source_image, physical_mr, physical_label, read_reference_label, TaskUNet3D, PATCH, tile_plan)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT = ROOT/'experiments/mc_rc_3d_backbone_collapse_diagnostic_2026_10_07'
def summary(values):
    v = np.asarray(values, dtype=np.float64)
    return dict(n=int(v.size), min=float(v.min()) if v.size else None,
        mean=float(v.mean()) if v.size else None, max=float(v.max()) if v.size else None)
def branch_norm(model):
    result = {}
    for name, module in [('encoder',model.encoders), ('decoder',model.decoders), ('primary_head',model.heads[-1])]:
        squares = [float(p.grad.double().square().sum()) for p in module.parameters() if p.grad is not None]
        result[name] = sum(squares)**.5
    return result
def main():
    sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(exist_ok=False); path=OUT/'attempt01.json'; started=time.perf_counter()
    fitpath = ROOT/'experiments/mc_rc_3d_backbone_context_refit_v2_2026_10_07/attempt01.json'
    proofpath = fitpath.parent/'independent_both1024_and_full_fov_attempt01.json'
    prod, proof = read(fitpath), read(proofpath)
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[], models=[],
        script_sha256=sha(__file__), source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in
            (fitpath,proofpath,ROOT/'MC_RC_3D_BACKBONE_COLLAPSE_DIAGNOSTIC_PROTOCOL_2026-10-07.md')],
        actual_training_updates=0, actual_gpu_updates=0, validation_effects_opened=False,
        confirmation_patients_opened=False, publication_claim_confirmed=False, intermediate_checkpoints_used=False)
    def save(): path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-started <= 300
        resource_guard()
    save()
    try:
        assert prod['complete'] and proof['complete'] and not prod['errors'] and not proof['errors']
        assert proof['result_sha256'] == sha(fitpath)
        torch.set_num_threads(4); guard(); role, case, row = fixed_cases()[0]
        assert role == 'development' and case['patient'] == 'VS-MC-RC-001' and case['uid'] == prod['series_uid']
        grid = lattice(case); target = physical_label(read_reference_label(case),grid); positions,_ = tile_plan(target.shape)
        assert len(positions) == 16; r['history_summaries'] = []
        for arm in prod['arms']:
            history = arm['history']; split = {}
            for name, rows in [('first32',history[:32]),('last64',history[-64:])]:
                split[name] = {key:summary([h['loss'] for h in rows if (sum(h['label_foreground'])>0)==force])
                    for key, force in [('contains_foreground',True),('empty_ground_truth',False)]}
            r['history_summaries'].append(dict(kind=arm['kind'],loss_by_window_and_foreground=split))
            normalized, stats = source_image(case,row,arm['kind']); image = physical_mr(normalized,grid)
            assert array_sha(image)==arm['physical_input_sha256']
            for phase, checkpoint_key, hash_key in [('initial','source_checkpoint_file','source_checkpoint_sha256'),
                                                     ('final','checkpoint_file','checkpoint_sha256')]:
                guard(); checkpoint = ROOT/arm[checkpoint_key]; assert sha(checkpoint)==arm[hash_key]
                state = torch.load(checkpoint,map_location='cpu',weights_only=True)['state_dict']
                model = TaskUNet3D(); model.load_state_dict(state,strict=True); model.eval()
                rec = dict(kind=arm['kind'],phase=phase,checkpoint_file=checkpoint.relative_to(ROOT).as_posix(),
                    checkpoint_sha256=sha(checkpoint), weights_sha256=state_hash(state), tiles=[],
                    primary_head_weight_summary=summary(state['heads.2.weight'].numpy()),
                    primary_head_bias_summary=summary(state['heads.2.bias'].numpy()))
                for at in range(0,16,2):
                    guard(); pair=positions[at:at+2]
                    slabs=[tuple(slice(s,s+p) for s,p in zip(start,PATCH)) for start in pair]
                    x=torch.from_numpy(np.stack([image[sl] for sl in slabs])[:,None]); y=torch.from_numpy(np.stack([target[sl] for sl in slabs])[:,None])
                    with torch.inference_mode(): outputs=model(x)
                    for slot, position in enumerate(pair):
                        heads=[]
                        for h, output in enumerate(outputs):
                            truth=F.interpolate(y,size=output.shape[2:],mode='nearest-exact'); probability=output.sigmoid()
                            p=probability[slot,0].numpy(); logit=output[slot,0].numpy(); gt=truth[slot,0].numpy()>=.5; pred=p>=.5
                            tp=int(np.count_nonzero(pred&gt)); fp=int(np.count_nonzero(pred&~gt)); fn=int(np.count_nonzero(~pred&gt))
                            gt_n=int(gt.sum()); pred_n=int(pred.sum())
                            bce=float(F.binary_cross_entropy_with_logits(output[slot],truth[slot]))
                            dice_loss=float(1-(2*(probability[slot]*truth[slot]).sum()+1)/(probability[slot].sum()+truth[slot].sum()+1))
                            heads.append(dict(head=h,output_shape=list(p.shape),gt_foreground=gt_n,pred_foreground=pred_n,
                                tp=tp,fp=fp,fn=fn,dice=2*tp/(gt_n+pred_n) if gt_n+pred_n else None,
                                bce=bce,soft_dice_loss=dice_loss,fg_probability=summary(p[gt]),bg_probability=summary(p[~gt]),
                                fg_logit=summary(logit[gt]),bg_logit=summary(logit[~gt])))
                        rec['tiles'].append(dict(tile_index=at+slot,position=list(position),heads=heads))
                # Fixed old qualification tile pair; each term is differentiated independently with zero updates.
                slabs=[tuple(slice(s,s+p) for s,p in zip(positions[i],PATCH)) for i in (4,5)]
                x=torch.from_numpy(np.stack([image[sl] for sl in slabs])[:,None]); y=torch.from_numpy(np.stack([target[sl] for sl in slabs])[:,None])
                rec['fixed_pair_gradient_diagnostic']=[]
                for term in ('bce','soft_dice'):
                    model.zero_grad(set_to_none=True); out=model(x)[0]; probability=out.sigmoid()
                    value=F.binary_cross_entropy_with_logits(out,y) if term=='bce' else 1-(2*(probability*y).sum()+1)/(probability.sum()+y.sum()+1)
                    assert torch.isfinite(value); value.backward()
                    assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
                    rec['fixed_pair_gradient_diagnostic'].append(dict(term=term,value=float(value.detach()),branch_L2_norm=branch_norm(model)))
                assert state_hash(model.state_dict())==rec['weights_sha256']
                r['models'].append(rec); save(); print(json.dumps(dict(kind=arm['kind'],phase=phase,tiles=16,updates=0)),flush=True)
                del state,model,outputs,x,y,out,probability,value
            del normalized,image
        r['cuda_initialized']=torch.cuda.is_initialized(); assert not r['cuda_initialized']; guard()
        r['complete']=len(r['models'])==4 and sha(fitpath)==proof['result_sha256']
        r['resources_after']=resource_guard()
    except Exception as e: r['errors'].append(type(e).__name__+': '+str(e)); r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started; r['finished_utc']=datetime.now(timezone.utc).isoformat(); save()
    assert path.stat().st_size < 5_000_000
    print(json.dumps({k:r.get(k) for k in ('complete','errors','elapsed_seconds','cuda_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__': raise SystemExit(main())
