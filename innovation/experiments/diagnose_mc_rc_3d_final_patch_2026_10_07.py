"""Frozen four-variant diagnostic of two last checkpoints; no parameter update."""
import json,sys,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,physical_mr,
    lattice,physical_label,read_reference_label,sample_batch,TaskUNet3D,torch,np,F,SEED,PATCH)
from mc_rc_3d_independent_replay_2026_10_07 import logical_counts
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_final_patch_diagnostic_2026_10_07'
FIT=ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07'
VARIANTS=['training_augmented','flips_only','intensity_only','identity']

def build(image,target,primitive,variant):
    xs=[];ys=[]
    for entry in primitive:
        crop=tuple(slice(s,s+p) for s,p in zip(entry['start'],PATCH))
        x=image[crop].copy();y=target[crop].copy()
        if variant in ('training_augmented','flips_only'):
            for axis,flag in enumerate(entry['flips']):
                if flag:x=np.flip(x,axis);y=np.flip(y,axis)
        if variant in ('training_augmented','intensity_only'):
            x=x*entry['intensity_scale']+entry['intensity_shift']
        xs.append(np.ascontiguousarray(x));ys.append(np.ascontiguousarray(y))
    return torch.from_numpy(np.stack(xs)[:,None]),torch.from_numpy(np.stack(ys)[:,None])

def pstats(p):
    if p.numel()==0:return dict(n=0,min=None,max=None,mean=None,median=None)
    return dict(n=p.numel(),min=float(p.min()),max=float(p.max()),mean=float(p.mean()),median=float(p.median()))

def summarize_grad(grad,truth):
    row={}
    for key,mask in [('foreground',truth.bool()),('background',~truth.bool())]:
        g=grad[mask]
        row[key]=dict(n=g.numel(),l1=float(g.abs().sum()),negative=int((g<0).sum()),
                      positive=int((g>0).sum()),zero=int((g==0).sum()))
    return row

def head_diagnostic(output,target,index):
    logit=output.detach().clone().requires_grad_(True)
    truth=F.interpolate(target,size=output.shape[2:],mode='nearest-exact')
    probability=logit.sigmoid();A=2*(probability*truth).sum()+1;B=probability.sum()+truth.sum()+1
    ce=F.binary_cross_entropy_with_logits(logit,truth);dice=1-A/B
    gce=torch.autograd.grad(ce,logit,retain_graph=True)[0]
    gdice=torch.autograd.grad(dice,logit)[0]
    p=probability.detach();closed_ce=(p-truth)/p.numel()
    closed_dice=(A.detach()-2*truth*B.detach())/B.detach().square()*p*(1-p)
    assert torch.allclose(gce,closed_ce,atol=1e-9,rtol=1e-5)
    assert torch.allclose(gdice,closed_dice,atol=1e-9,rtol=1e-5)
    total=gce+gdice;cn=float(torch.linalg.vector_norm(gce));dn=float(torch.linalg.vector_norm(gdice))
    return dict(head_index=index,shape=list(logit.shape),foreground=int(truth.sum()),
                foreground_fraction=float(truth.mean()),bce=float(ce.detach()),soft_dice=float((A/B).detach()),
                loss=float((ce+dice).detach()),hard_metrics=[logical_counts(a>=.5,b>=.5)
                    for a,b in zip(p.numpy()[:,0],truth.numpy()[:,0])],
                foreground_probability=pstats(p[truth.bool()]),background_probability=pstats(p[~truth.bool()]),
                per_sample_foreground=[int(t.sum()) for t in truth],
                bce_gradient=summarize_grad(gce,truth),dice_gradient=summarize_grad(gdice,truth),
                combined_gradient=summarize_grad(total,truth),
                logit_gradient_l2_norms=dict(bce=cn,dice=dn,dice_over_bce=None if cn==0 else dn/cn),
                gradient_closed_form_max_error=dict(bce=float((gce-closed_ce).abs().max()),dice=float((gdice-closed_dice).abs().max())),
                gradient_scope='unweighted head logits, not model parameter gradients')

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],arms=[],
           variants=VARIANTS,actual_training_updates=0,actual_gpu_updates=0,
           validation_effects_opened=False,confirmation_patients_opened=False,scientific_confirmation_patients=0,
           publication_claim_confirmed=False,script_sha256=sha(__file__),
           protocol_sha256=sha(ROOT/'MC_RC_3D_FINAL_PATCH_DIAGNOSTIC_PROTOCOL_2026-10-07.md'))
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        prod=read(FIT/'attempt_01.json');replay=read(FIT/'independent_both512_and_full_fov_2026_10_07.json')
        assert prod['complete'] and not prod['errors'] and prod['total_updates_completed']==1024
        assert replay['complete'] and not replay['errors'] and replay['result_sha256']==sha(FIT/'attempt_01.json')
        r['fit_result_sha256']=sha(FIT/'attempt_01.json');r['replay_sha256']=sha(FIT/'independent_both512_and_full_fov_2026_10_07.json')
        r['source_bindings']=prod['source_bindings']
        for entry in prod['source_bindings']:assert sha(ROOT/entry['path'])==entry['sha256']
        resource_guard();role,case,row=fixed_cases()[0];assert role=='development' and case['patient']=='VS-MC-RC-001'
        r['training_patient_ids']=[case['patient']];r['series_uid']=case['uid']
        grid=lattice(case);target=physical_label(read_reference_label(case),grid)
        assert array_sha(target)==prod['physical_label_sha256']
        for arm in prod['arms']:
            resource_guard();kind=arm['kind'];normalized,stats=source_image(case,row,kind);image=physical_mr(normalized,grid)
            assert array_sha(image)==arm['physical_input_sha256'] and stats==arm['observed_statistics']
            checkpoint=ROOT/arm['checkpoint_file'];assert sha(checkpoint)==arm['checkpoint_sha256']
            stored=torch.load(checkpoint,map_location='cpu',weights_only=True)
            assert state_hash(stored['state_dict'])==arm['final_weights_sha256']
            model=TaskUNet3D();model.load_state_dict(stored['state_dict'],strict=True);model.eval();model.requires_grad_(False)
            rx,ry,primitive=sample_batch(image,target,np.random.default_rng(SEED));assert primitive==arm['primitive']
            assert array_sha(rx.numpy())==arm['input_batch_sha256'] and array_sha(ry.numpy())==arm['label_batch_sha256']
            dest=dict(kind=kind,checkpoint_sha256=sha(checkpoint),variants=[])
            r['arms'].append(dest)
            for variant in VARIANTS:
                resource_guard();x,y=build(image,target,primitive,variant)
                if variant=='training_augmented':
                    assert torch.equal(x,rx) and torch.equal(y,ry)
                with torch.no_grad():outputs=model(x)
                heads=[head_diagnostic(o,y,i) for i,o in enumerate(outputs)]
                record=dict(variant=variant,input_batch_sha256=array_sha(x.numpy()),
                            label_batch_sha256=array_sha(y.numpy()),heads=heads,
                            combined_loss=sum(h['loss']*w for h,w in zip(heads,(4/7,2/7,1/7))))
                dest['variants'].append(record);save()
                print(json.dumps(dict(kind=kind,variant=variant,loss=record['combined_loss'],
                                      foreground_patch_dice=heads[0]['hard_metrics'][0]['dice'])),flush=True)
                del x,y,outputs,heads
            dest['complete']=True;save();del model,stored,image,normalized,rx,ry
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        r['resources_after']=resource_guard();r['complete']=len(r['arms'])==2 and all(a['complete'] for a in r['arms'])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    assert path.stat().st_size<=5_000_000
    print(json.dumps({k:r.get(k) for k in ('complete','errors','actual_training_updates','cuda_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
