"""Metadata schedule audit, all-head functional check and exact AdamW resume check; no MRI pixels."""
import argparse,ast,collections,gc,json,sys,time,traceback
from pathlib import Path
from mc_rc_3d_19series_common_init_2026_10_07 import *
from mc_rc_3d_independent_replay_2026_10_07 import functional_forward

def independent_schedule(cases):
    # Separate cursor implementation; no production deck/pop function used.
    people=sorted(set(c['patient'] for c,row in cases));order_rng=np.random.default_rng([SEED,611])
    groups={p:[j for j,(c,row) in enumerate(cases) if c['patient']==p] for p in people}
    rngs={p:np.random.default_rng([SEED,610,i]) for i,p in enumerate(people)}
    permutations={p:[] for p in people};used={p:0 for p in people};result=[]
    for rnd in range(1818):
        for pi in order_rng.permutation(11):
            p=people[int(pi)]
            if used[p]==len(permutations[p]):permutations[p]=list(rngs[p].permutation(groups[p]));used[p]=0
            result.append((int(pi),int(permutations[p][used[p]])));used[p]+=1
    return np.asarray(result,dtype=np.int32)
def synthetic_step(model,opt,k):
    rng=np.random.default_rng([SEED,613,k]);x=torch.from_numpy(rng.normal(size=(2,1,16,16,16)).astype(np.float32))
    y=torch.from_numpy((rng.random((2,1,16,16,16))>.92).astype(np.float32))
    opt.zero_grad(set_to_none=True);out=model(x);v=loss(out,y);assert torch.isfinite(v);v.backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    if k==1:assert all(max(float(p.grad.abs().max()) for p in module.parameters())>0 for module in (model.encoders,model.decoders,model.ups,model.heads))
    opt.step();assert all(torch.isfinite(p).all() for p in model.parameters())
    return float(v.detach())
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();OUT.mkdir(exist_ok=False)
    r=dict(created_utc=now(),complete=False,errors=[],script_sha256=sha(__file__),real_MRI_or_GT_files_loaded=0,
        formal_training_updates=0,actual_gpu_updates=0,synthetic_optimizer_updates=0,publication_claim_confirmed=False)
    try:
        torch.set_num_threads(4);r['resources_before']=guard();cases=development_cases();bindings=sources(cases)
        for name in ('mc_rc_3d_19series_common_init_2026_10_07.py','preflight_mc_rc_3d_19series_common_init_2026_10_07.py',
                     'run_mc_rc_3d_19series_common_init_cpu_2026_10_07.py'):
            ast.parse((ROOT/'experiments'/name).read_text(encoding='utf-8'))
        draws,patients,members=schedule(cases);ind=independent_schedule(cases);assert np.array_equal(draws,ind)
        for group in draws.reshape(1818,11,2):assert sorted(map(int,group[:,0]))==list(range(11))
        counts=collections.Counter(map(int,draws[:,1]));pc=collections.Counter(map(int,draws[:,0]))
        assert all(v==1818 for v in pc.values()) and len(counts)==19
        assert all(max(counts[j] for j in group)-min(counts[j] for j in group)<=1 for group in members)
        np.save(OUT/'frozen_schedule.npy',draws,allow_pickle=False)
        initial=make_initial();initialhash=state_hash(initial);torch.save(dict(state_dict=initial,seed=SEED,
            initial_weights_sha256=initialhash,protocol_sha256=sha(PROTOCOL)),OUT/'common_random_initial.pt')
        a=TaskUNet3D();a.load_state_dict(initial);a.train();oa=optimizer_for(a)
        b=TaskUNet3D();b.load_state_dict(initial);b.train();ob=optimizer_for(b)
        assert state_hash(a.state_dict())==state_hash(b.state_dict())==initialhash
        xx=torch.from_numpy(np.random.default_rng([SEED,614]).normal(size=(2,1,16,16,16)).astype(np.float32))
        with torch.inference_mode():
            mo=a(xx);fo=functional_forward(xx,initial)
        errors=[float((x-y).abs().max()) for x,y in zip(mo,fo)]
        assert len(errors)==3 and max(errors)<=3e-6
        uninterrupted=[synthetic_step(a,oa,k) for k in range(1,13)];r['synthetic_optimizer_updates']+=12
        first=[synthetic_step(b,ob,k) for k in range(1,7)];r['synthetic_optimizer_updates']+=6
        resumep=OUT/'synthetic_resume_after6.pt';torch.save(dict(state_dict=b.state_dict(),optimizer_state_dict=ob.state_dict(),
            torch_rng_state=torch.get_rng_state(),updates=6),resumep);del b,ob;gc.collect()
        state=torch.load(resumep,map_location='cpu',weights_only=True);b=TaskUNet3D();b.load_state_dict(state['state_dict']);b.train()
        ob=optimizer_for(b);ob.load_state_dict(state['optimizer_state_dict']);torch.set_rng_state(state['torch_rng_state'])
        second=[synthetic_step(b,ob,k) for k in range(7,13)];r['synthetic_optimizer_updates']+=6
        assert uninterrupted==first+second and equal_tree(a.state_dict(),b.state_dict()) and equal_tree(oa.state_dict(),ob.state_dict())
        r.update(common_initial_weights_sha256=initialhash,all_three_head_max_logit_errors=errors,
            uninterrupted_vs_resume_exact_weights=True,uninterrupted_vs_resume_exact_optimizer=True,uninterrupted_vs_resume_exact_losses=True,
            independent_schedule_equal=True,schedule_array_sha256=array_sha(draws),all1818_patient_rounds_balanced=True,
            all19_series_present=True,patient_updates={p:int(pc[i]) for i,p in enumerate(patients)},
            series_updates={c['uid']:int(counts[i]) for i,(c,row) in enumerate(cases)},
            synthetic_resume_final_weights_sha256=state_hash(a.state_dict()),source_bindings=bindings)
        config=dict(created_utc=now(),frozen=True,protocol_file=PROTOCOL.relative_to(ROOT).as_posix(),protocol_sha256=sha(PROTOCOL),
            seed=SEED,planned_updates_per_arm=BUDGET,planned_total_updates=2*BUDGET,arm_order=list(ARM_KINDS),
            patient_ids=patients,series=[dict(patient=c['patient'],uid=c['uid']) for c,row in cases],
            initial_file='common_random_initial.pt',initial_file_sha256=sha(OUT/'common_random_initial.pt'),
            initial_weights_sha256=initialhash,schedule_file='frozen_schedule.npy',schedule_file_sha256=sha(OUT/'frozen_schedule.npy'),
            schedule_array_sha256=array_sha(draws),optimizer=dict(name='AdamW',learning_rate=.0001,weight_decay=.0001),
            cumulative_train_wall_seconds_limit=MAX_SECONDS,max_saved_bytes=MAX_BYTES,
            cpu_intraop_threads=4,cpu_interop_threads=1,device='cpu',dtype='float32',task_effects_scored=False,
            validation_pixels_opened=False,confirmation_patients_opened=False,source_bindings=bindings)
        dump_new(OUT/'frozen_config.json',config)
        r['frozen_config_sha256']=sha(OUT/'frozen_config.json');r['resources_after']=guard();r['complete']=True
        assert time.perf_counter()-started<=120,'Preflight wall budget exceeded'
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=now();r['elapsed_seconds']=time.perf_counter()-started
    dump_new(OUT/'preflight_attempt01.json',r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','synthetic_optimizer_updates','elapsed_seconds','common_initial_weights_sha256')},ensure_ascii=False))
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
