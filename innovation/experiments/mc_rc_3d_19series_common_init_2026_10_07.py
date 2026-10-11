"""Frozen common-init CPU training utilities. No MRI evaluation or confirmation reads."""
import collections,copy,gc,json,os,time
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,lattice,physical_mr,
    physical_label,read_reference_label,sample_batch,TaskUNet3D,loss,SEED,PATCH,torch,np)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
PROTOCOL=ROOT/'MC_RC_3D_19SERIES_COMMON_INIT_CPU_PROTOCOL_2026-10-07.md'
QPATH=ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json'
BUDGET=19998
MAX_SECONDS=90000
MAX_BYTES=250000000
ARM_KINDS=('native_reference','raw_pchip')

def now():return datetime.now(timezone.utc).isoformat()
def dump_new(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def atomic_json(path,value):
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('w',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
def atomic_torch(path,value):
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('wb') as f:torch.save(value,f);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
def saved_bytes():return sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
def guard():
    r=resource_guard();r['cpu_threads']=torch.get_num_threads()
    assert r['cpu_threads']==4 and torch.get_num_interop_threads()==1
    assert not torch.cuda.is_initialized() and saved_bytes()<=MAX_BYTES
    r['stage_saved_bytes']=saved_bytes();return r
def development_cases():
    cases=sorted([(c,row) for role,c,row in fixed_cases() if role=='development'],key=lambda cr:(cr[0]['patient'],cr[0]['uid']))
    assert len(cases)==19 and len({c['patient'] for c,row in cases})==11
    assert {c['patient'].rsplit('-',1)[-1] for c,row in cases}=={'001','002','004','005','006','007','009','010','011','012','013'}
    return cases
def sources(cases):
    closure=ROOT/'SESSION_CLOSING_RECEIPT_LOW_LR_CONTEXT_2026-10-07.json';cl=read(closure)
    assert cl['complete'] and cl['archive_observed_tool_exit']==0
    assert sha(ROOT/cl['manifest_file'])==cl['manifest_sha256'] and sha(ROOT/cl['archive_file'])==cl['archive_sha256']
    q=read(QPATH);qp=QPATH.parent/'independent_stream_and_batch_attempt01.json';p=read(qp)
    e=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_CPU_RESOURCE_2026-10-07.json')
    assert q['complete'] and p['complete'] and not q['errors'] and not p['errors'] and all(q['gate'].values())
    assert p['source_sha256']==sha(QPATH) and e['qualification_observed_tool_exit']==e['independent_verifier_observed_tool_exit']==0
    result={closure,QPATH,qp,PROTOCOL,ROOT/'SESSION_EXECUTION_LEDGER_LOW_LR_CONTEXT_2026-10-07.json',
        ROOT/'SESSION_LOW_LR_19SERIES_TRAINING_BUDGET_PREPARATION_2026-10-07.json',
        ROOT/'experiments/mc_rc_3d_19series_common_init_2026_10_07.py',
        ROOT/'experiments/preflight_mc_rc_3d_19series_common_init_2026_10_07.py',
        ROOT/'experiments/run_mc_rc_3d_19series_common_init_cpu_2026_10_07.py'}
    result.update(ROOT/b['path'] for b in q['source_bindings'])
    for b in q['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    for c,row in cases:
        result.update(ROOT/c[k] for k in ('header_file','mr_zip_file','label_file'))
        result.add(ROOT/row['observed_package'])
    return [dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(result)]
def schedule(cases):
    patients=sorted({c['patient'] for c,row in cases})
    members=[[i for i,(c,row) in enumerate(cases) if c['patient']==p] for p in patients]
    rngs=[np.random.default_rng(np.random.SeedSequence([SEED,610,i])) for i in range(len(patients))]
    order=np.random.default_rng(np.random.SeedSequence([SEED,611]));decks=[[] for p in patients]
    draws=[]
    for r in range(BUDGET//len(patients)):
        for p in order.permutation(len(patients)):
            p=int(p)
            if not decks[p]:decks[p]=rngs[p].permutation(members[p]).tolist()
            i=int(decks[p].pop(0));draws.append((p,i))
    draws=np.asarray(draws,dtype=np.int32);assert draws.shape==(BUDGET,2)
    return draws,patients,members
def make_initial():
    torch.manual_seed(SEED);m=TaskUNet3D();state={k:v.detach().clone() for k,v in m.state_dict().items()}
    del m;return state
def optimizer_for(model):return torch.optim.AdamW(model.parameters(),lr=.0001,weight_decay=.0001)
def equal_tree(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(equal_tree(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)):return isinstance(b,type(a)) and len(a)==len(b) and all(equal_tree(x,y) for x,y in zip(a,b))
    return a==b
def batch_rng(step):return np.random.default_rng(np.random.SeedSequence([SEED,612,step]))
def load_cache(kind,cases):
    q=read(QPATH);qa=next(a for a in q['arms'] if a['kind']==kind)
    old={s['uid']:s for s in qa['cache_records']};cache={};records=[];start=time.perf_counter()
    for c,row in cases:
        guard();at=time.perf_counter();normalized,stats=source_image(c,row,kind);g=lattice(c)
        image=physical_mr(normalized,g);gt=read_reference_label(c);target=physical_label(gt,g)
        image_hash,label_hash=array_sha(image),array_sha(target);previous=old[c['uid']]
        assert image_hash==previous['input_sha256'] and label_hash==previous['label_sha256']
        assert image.dtype==target.dtype==np.float32 and image.shape==target.shape
        assert np.isfinite(image).all() and np.isfinite(target).all() and target.sum()>0
        cache[c['uid']]=(image,target)
        records.append(dict(patient=c['patient'],uid=c['uid'],shape_zrc=list(image.shape),input_sha256=image_hash,
            label_sha256=label_hash,label_foreground=int(target.sum()),image_bytes=int(image.nbytes),label_bytes=int(target.nbytes),
            observed_statistics=stats,load_seconds=time.perf_counter()-at))
        del normalized,gt;guard()
    assert sum(i.nbytes+t.nbytes for i,t in cache.values())==1909712000
    return cache,records,time.perf_counter()-start
