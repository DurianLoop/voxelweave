"""NumPy-only independent replay of recorded synthetic inputs/draws and FOV geometry."""
import hashlib,itertools,json,math,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07'
SOURCE=OUT/'attempt01.json'
PROTOCOL=ROOT/'PAIRED_RESOURCE_WORKFLOW_INDEPENDENT_PROTOCOL_2026-10-07.md'
PATCH=(64,128,128)
SEED=20261007
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ah(a):
    a=np.ascontiguousarray(a)
    h=hashlib.sha256(json.dumps(dict(shape=list(a.shape),dtype=a.dtype.str),sort_keys=True).encode())
    h.update(memoryview(a).cast('B'));return h.hexdigest()
def main():
    global np
    sys.stdout.reconfigure(encoding='utf-8');at=time.perf_counter()
    dest=OUT/'independent_attempt01.json';assert not dest.exists()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        script_sha256=sha(__file__),source_file=SOURCE.relative_to(ROOT).as_posix(),source_sha256=sha(SOURCE),
        source_bindings=[dict(path=PROTOCOL.relative_to(ROOT).as_posix(),sha256=sha(PROTOCOL))],
        MRI_data_reads=0,neural_modules_imported=False,model_forward_calls=0,training_updates=0,
        independent_neural_weight_or_probability_replay=False,publication_claim_confirmed=False)
    denied=[];reads=set()
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        try:p=Path(args[0]).resolve()
        except (ValueError,TypeError,OSError):return
        mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT.parent):
            rel=p.relative_to(ROOT.parent).as_posix()
            if p.name.endswith(('.nii','.nii.gz','.zip','.npz','.npy','.pt')) or '/data/' in '/'+rel:
                denied.append(rel);raise PermissionError('Independent synthetic verifier denies binary MRI/weight IO')
            reads.add(rel)
    sys.addaudithook(audit)
    try:
        import numpy as np
        c=json.loads(SOURCE.read_text(encoding='utf-8'))
        assert c['complete'] and not c['errors'] and all(c['gate'].values())
        assert c['synthetic_only'] and not c['CUDA_initialized'] and not c['updated_weights_saved']
        assert c['MRI_arrays_loaded']==c['MRI_forwards']==c['MRI_training_updates']==c['GPU_forwards']==0
        assert c['io_audit']['MRI_data_reads']==0 and not c['io_audit']['denied_read_attempts']
        bindings=[]
        for b in c['source_bindings']:
            p=(ROOT/b['path']).resolve();assert p.is_relative_to(ROOT)
            snap=OUT/(p.name+'.source_snapshot')
            assert sha(p)==sha(snap)==b['sha256']
            bindings.append(dict(**b,snapshot_file=snap.relative_to(ROOT).as_posix(),snapshot_sha256=sha(snap)))
        assert len(bindings)==8
        rng=np.random.default_rng(SEED+710);core=(65,129,133);pad=((1,2),(2,1),(1,2))
        dense=rng.normal(size=core).astype(np.float32)
        mask=np.repeat(np.resize(np.array([0,.25,.75,1],np.float32),65),129*133).reshape(core)
        gt=np.zeros(core,np.float32);gt[9:14,40:45,30:37]=1;gt[54:57,118:121,122:125]=1
        f={k:np.pad(v,pad) for k,v in dict(dense=dense,numerator=dense*mask,availability=mask,
            valid_grid=np.ones(core,np.float32),target=gt).items()}
        g=dict(f,dense=(f['dense']*.7+f['valid_grid']*.2).astype(np.float32))
        g['numerator']=(g['dense']*g['availability']).astype(np.float32)
        cache={'SYNTHETIC_UID_1':f,'SYNTHETIC_UID_2':g}
        assert [{k:ah(b[k]) for k in f} for b in (f,g)]==c['input_array_sha256']
        assert c['patch']==list(PATCH) and c['batch_size']==2 and c['synthetic_shape_zrc']==[68,132,136]
        assert c['synthetic_grid']==dict(unpadded_shape_zrc=list(core),padding=[list(v) for v in pad])
        stream=[dict(step=i+1,round_index=i,patient='SYNTHETIC_PATIENT',uid=u)
            for i,u in enumerate(('SYNTHETIC_UID_1','SYNTHETIC_UID_2','SYNTHETIC_UID_1'))]
        assert c['frozen_stream']==stream
        draws=[]
        for i,item in enumerate(stream):
            target=cache[item['uid']]['target'];random=np.random.default_rng(np.random.SeedSequence([SEED,813,i]))
            fg=np.argwhere(target==1);ds=[]
            for force in (True,False):
                center=fg[int(random.integers(len(fg)))] if force else np.array([random.integers(n) for n in target.shape])
                start=[max(0,min(int(q)-p//2,n-p)) for q,p,n in zip(center,PATCH,target.shape)]
                flips=[bool(random.random()<.5) for _ in range(3)]
                scale=float(random.uniform(.9,1.1));shift=float(random.uniform(-.1,.1))
                sl=tuple(slice(s,s+p) for s,p in zip(start,PATCH))
                ds.append(dict(forced_foreground=force,center=list(map(int,center)),start=start,flips=flips,
                    intensity_scale=scale,intensity_shift=shift,target_foreground=int(target[sl].sum())))
            draws.append(dict(**item,draws=ds))
        assert draws==c['shared_training_draws']
        replays=[]
        assert [a['kind'] for a in c['arms']]==['dense','direct']
        for arm in c['arms']:
            assert arm['complete'] and len(arm['history'])==3 and arm['actual_resource_updates']==4
            assert arm['initial_weights_sha256']==c['canonical_two_channel_state_sha256']
            assert arm['discarded_final_weights_sha256']!=arm['initial_weights_sha256']
            assert arm['checkpoint_storage']=='memory_only' and not arm['updated_weights_saved']
            for item,h in zip(draws,arm['history']):
                b=cache[item['uid']];xs=[];ys=[];kind=arm['kind'];key='dense' if kind=='dense' else 'numerator'
                for d in item['draws']:
                    sl=tuple(slice(s,s+p) for s,p in zip(d['start'],PATCH))
                    image=b[key][sl].copy();avail=b['availability'][sl].copy();label=b['target'][sl].copy()
                    support=b['valid_grid'][sl] if kind=='dense' else avail
                    image=np.float32(d['intensity_scale'])*image+np.float32(d['intensity_shift'])*support
                    image[b['valid_grid'][sl]==0]=0
                    for axis,flip in enumerate(d['flips']):
                        if flip:
                            reverse=np.arange(PATCH[axis]-1,-1,-1)
                            image=np.take(image,reverse,axis);avail=np.take(avail,reverse,axis);label=np.take(label,reverse,axis)
                    xs.append(np.stack((image,avail)));ys.append(label[None])
                x=np.stack(xs);y=np.stack(ys)
                assert ah(x)==h['input_batch_sha256'] and ah(y)==h['label_batch_sha256']
                assert [int(v.sum()) for v in y]==h['label_foreground']==[d['target_foreground'] for d in item['draws']]
                assert all(h[k]==item[k] for k in ('step','round_index','patient','uid'))
                assert math.isfinite(h['loss']) and h['mask_gradient_max']>0
                assert all(math.isfinite(v) and v>0 for v in h['gradient_groups'].values())
                replays.append(dict(kind=kind,step=item['step'],input_batch_sha256=ah(x),label_batch_sha256=ah(y)))
            resume=arm['resume_check'];h=arm['history'][1]
            assert resume['full_model_optimizer_RNG_tree_exact'] and resume['extra_resource_updates']==1 and resume['replayed_step']==2
            assert resume['replay_input_batch_sha256']==h['input_batch_sha256']
            assert resume['replay_label_batch_sha256']==h['label_batch_sha256'] and resume['replay_loss']==h['loss']
        axes=[]
        for n,p in zip(f['dense'].shape,PATCH):
            starts=list(range(0,n-p+1,p//2))
            if starts[-1]!=n-p:starts.append(n-p)
            axes.append(starts)
        starts=list(itertools.product(*axes));assert len(starts)==8
        factors=[np.exp(-((np.arange(p,dtype=float)-(p-1)/2)**2)/(2*(p/8)**2)) for p in PATCH]
        weight=factors[0][:,None,None]*factors[1][None,:,None]*factors[2][None,None,:]
        weight=np.maximum(weight/weight.max(),1e-4).astype(np.float32)
        coverage=np.zeros(f['dense'].shape,np.float64)
        for start in starts:coverage[tuple(slice(s,s+p) for s,p in zip(start,PATCH))]+=weight
        for arm in c['arms']:
            a,b=arm['FOV_passes'];assert a['metadata']==b['metadata'] and arm['FOV_repeat_exact']
            for j,v in enumerate((a,b)):
                m=v['metadata'];assert v['repeat']==j+1 and v['uid']=='SYNTHETIC_UID_1'
                assert not v['probability_arrays_saved'] and not v['task_effects_scored']
                assert m['axis_starts']==axes and m['total_tiles']==8 and m['forward_calls']==4
                assert [t['start'] for t in m['tiles']]==[list(s) for s in starts]
                assert m['coverage_sha256']==ah(coverage) and m['blend_weight_sha256']==ah(weight)
                assert m['coverage_min']==float(coverage.min()) and m['coverage_max']==float(coverage.max())
                assert m['full_fov'] and not m['label_used_for_inference'] and m['threshold']==.5
                assert m['input_channels']==2 and m['shape_zrc']==[68,132,136]
        assert all(a['label_batch_sha256']==b['label_batch_sha256'] and a['input_batch_sha256']!=b['input_batch_sha256']
            for a,b in zip(c['arms'][0]['history'],c['arms'][1]['history']))
        assert c['actual_resource_updates']==8 and c['completed_model_forward_calls']==c['attempted_model_forward_calls']==24
        assert c['counts']==dict(synthetic_updates=8,training_forward_calls=8,FOV_forward_calls=16,FOV_tiles=32)
        assert 'torch' not in sys.modules and not denied
        r.update(complete=True,source_snapshots_verified=bindings,independent_training_batch_replays=replays,
            independent_draw_batches=3,independent_coverage_SHA_exact=True,recorded_neural_checks_consistent=True,
            documented_synthetic_updates=8,documented_forward_calls=24,
            limitation='Weights/probabilities absent: no independent neural forward, gradient or checkpoint tree replay claimed.')
    except Exception as e:
        r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-at,io_audit=dict(workspace_read_paths=sorted(reads),denied_read_attempts=denied))
    with dest.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','independent_draw_batches','independent_coverage_SHA_exact','elapsed_seconds')}))
    return 0 if r['complete'] and not r['errors'] else 1
if __name__=='__main__':raise SystemExit(main())
