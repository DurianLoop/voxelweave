"""Reusable observed three-arm training/immutable segment commits; no data loader."""
import gc, json, os
from pathlib import Path
from dataclasses import asdict
import disk_resume_core as core
import three_arm_resource_worker as w
torch=w.torch

def commit(directory,arm,model,opt,step,history,initial_sha,plan_path,guard):
    guard(25_000_000)
    stem=f'{arm}_step{step:03d}'
    journal=directory/(stem+'_history.jsonl'); checkpoint=directory/(stem+'.pt'); metadata=directory/(stem+'_binding.json')
    for p in (journal,checkpoint,metadata): assert not p.exists(), 'Frozen segment must not be overwritten'
    data=''.join(json.dumps(h,ensure_ascii=False,separators=(',',':'))+'\n' for h in history).encode('utf-8')
    core.new_bytes(journal,data)
    payload=w.old.snapshot(model,opt,step,'cpu')
    payload.update(arm=arm,synthetic_only=True,plan_sha256=core.sha(plan_path),initial_weights_sha256=initial_sha)
    tmp=checkpoint.with_name(checkpoint.name+'.pending.tmp')
    with tmp.open('xb') as f: torch.save(payload,f); f.flush(); os.fsync(f.fileno())
    assert tmp.stat().st_size<25_000_000 and not checkpoint.exists()
    os.replace(tmp,checkpoint)
    q=dict(created_utc=core.now(),complete=True,errors=[],arm=arm,step=step,synthetic_only=True,
           plan_sha256=core.sha(plan_path),initial_weights_sha256=initial_sha,
           weights_sha256=w.old.statehash(model.state_dict()),checkpoint=core.entry(checkpoint),journal=core.entry(journal),
           source_bindings=[core.entry(plan_path)]+core.read(plan_path)['source_bindings'])
    core.new_json(metadata,q); del payload; guard()
    return dict(metadata=core.entry(metadata),checkpoint=core.entry(checkpoint),journal=core.entry(journal),step=step)

def execute_arm(arm,cache,plan,plan_path,initial,directory,guard,counters,resume_meta=None,progress=None):
    guard(); model=w.old.two_channel_model(initial)
    opt=torch.optim.AdamW(model.parameters(),lr=.0001,weight_decay=.0001)
    initial_sha=w.old.statehash(initial)
    assert sum(p.numel() for p in model.parameters())==1_401_795
    assert w.old.statehash(model.state_dict())==initial_sha
    history=[]; start=0; commits=[]
    if resume_meta:
        cp=torch.load(core.ROOT/resume_meta['checkpoint']['path'],map_location='cpu',weights_only=True)
        counters['synthetic_checkpoint_arrays_loaded_from_disk']+=1
        assert cp['arm']==arm and cp['synthetic_only'] and cp['plan_sha256']==core.sha(plan_path)
        assert cp['step']==resume_meta['step'] and cp['initial_weights_sha256']==initial_sha
        assert w.old.statehash(cp['model'])==resume_meta['weights_sha256']
        model.load_state_dict(cp['model']); opt.load_state_dict(cp['optimizer']); torch.set_rng_state(cp['torch_rng'])
        assert w.old.exact(w.old.snapshot(model,opt,cp['step'],'cpu'),{k:cp[k] for k in ('model','optimizer','step','torch_rng','batch_seed_recipe')})
        start=cp['step']; history=[json.loads(line) for line in (core.ROOT/resume_meta['journal']['path']).read_text(encoding='utf-8').splitlines()]
        del cp
    for index in range(start,plan['updates_per_arm']):
        guard(); item=plan['stream'][index]
        bundle=cache[item['uid']]
        draws=w.old.draw_training_batch(bundle['target'],w.np.random.default_rng(w.np.random.SeedSequence([w.SEED,813,index])))
        view,semantic,field=w.arm_view(bundle,arm)
        h=w.old.update(model,opt,view,draws,semantic,'cpu',guard,counters)
        h.update(arm=arm,step=index+1,patient=item['patient'],uid=item['uid'],draws=[asdict(d) for d in draws],
                 selected_field=field,augmentation_semantic=semantic,selected_full_field_sha256=w.array_sha(bundle[field]))
        history.append(h)
        if index+1 in (plan['resume_from_step'],plan['updates_per_arm']):
            commits.append(commit(directory,arm,model,opt,index+1,history,initial_sha,plan_path,guard))
        if progress: progress(arm,index+1)
    result=dict(arm=arm,complete=True,starting_step=start,ending_step=plan['updates_per_arm'],
                actual_new_updates=plan['updates_per_arm']-start,history=history,commits=commits,
                initial_weights_sha256=initial_sha,final_weights_sha256=w.old.statehash(model.state_dict()),parameter_count=1_401_795)
    del model,opt; gc.collect(); guard(); return result
