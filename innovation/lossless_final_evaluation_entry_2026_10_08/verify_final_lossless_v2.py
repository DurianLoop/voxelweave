"""Complete functional FOV/coordinate/count verification; no new updates and no confirmation."""
import gc,itertools,json,math,sys,time,traceback
from fractions import Fraction
from final_eval_lossless_v2 import *
from mc_rc_3d_independent_replay_2026_10_07 import functional_forward,independent_starts,independent_weight,independent_native_resample
from torch.nn import functional as F

def numpy_native64(physical,shape):
    # Float64 result; independent RCZ planes and eight-corner pixel-center weights.
    physical=np.asarray(physical,dtype=np.float64)
    nz,nr,nc=physical.shape;rows=np.clip((np.arange(shape[0],dtype=np.float64)+.5)*nr/shape[0]-.5,0,nr-1)
    cols=np.clip((np.arange(shape[1],dtype=np.float64)+.5)*nc/shape[1]-.5,0,nc-1)
    r0=np.floor(rows).astype(int);r1=np.minimum(r0+1,nr-1);rf=rows-r0
    c0=np.floor(cols).astype(int);c1=np.minimum(c0+1,nc-1);cf=cols-c0;result=np.empty(shape,np.float64)
    for z in range(shape[2]):
        p=float(np.clip((z+.5)*nz/shape[2]-.5,0,nz-1));z0=int(math.floor(p));z1=min(z0+1,nz-1);zf=p-z0
        plane=np.zeros(shape[:2],np.float64)
        for zi,wz in ((z0,1-zf),(z1,zf)):
            for ri,wr in ((r0,1-rf),(r1,rf)):
                for ci,wc in ((c0,1-cf),(c1,cf)):plane+=physical[zi][np.ix_(ri,ci)]*wz*wr[:,None]*wc[None,:]
        result[:,:,z]=plane
    return result
def functional_fov(state,image,grid,native_shape,check):
    axes=independent_starts(image.shape,PATCH);locations=list(itertools.product(*axes));weight=independent_weight(PATCH)
    num=np.zeros(image.shape,np.float64);den=np.zeros(image.shape,np.float64)
    with torch.inference_mode():
        for begin in range(0,len(locations),2):
            check();chunks=locations[begin:begin+2];slabs=[tuple(slice(s,s+n) for s,n in zip(start,PATCH)) for start in chunks]
            x=torch.from_numpy(np.stack([image[sl] for sl in slabs])[:,None]);out=functional_forward(x,state)[0].sigmoid().numpy()[:,0]
            assert np.isfinite(out).all()
            for sl,p in zip(slabs,out):num[sl]+=p*weight;den[sl]+=weight
    assert den.min()>0
    full=num/den;crop=tuple(slice(int(lo),int(lo)+int(n)) for (lo,hi),n in zip(grid['padding'],grid['unpadded_shape_zrc']))
    physical=np.ascontiguousarray(full[crop],np.float32)
    f32=independent_native_resample(physical,native_shape);f64=numpy_native64(physical,native_shape)
    with torch.inference_mode():
        reference=F.interpolate(torch.from_numpy(physical.astype(np.float64))[None,None],
            size=(native_shape[2],native_shape[0],native_shape[1]),mode='trilinear',align_corners=False)[0,0].numpy().transpose(1,2,0)
    double_error=float(np.max(np.abs(reference-f64)));double_binary=int(np.count_nonzero((reference>=.5)!=(f64>=.5)))
    return f32,dict(total_tiles=len(locations),axis_starts=axes,coverage_min=float(den.min()),coverage_max=float(den.max()),
        coverage_sha256=array_sha(den),blend_weight_sha256=array_sha(weight),float64_coordinate_max_probability_error=double_error,
        float64_coordinate_threshold_disagreements=double_binary,float64_coordinate_gate_passed=double_error<=3e-12 and double_binary==0,
        neural_forward_precision='float32',float64_only_coordinate_arithmetic=True)
def independent_counts(pred,truth):
    # Separate flattened positions for domains; direct logical sets, not primary metrics helper.
    z=list(range(truth.shape[2]));obs=[j for j in z if j%4==0];last=obs[-1]
    indices=dict(full=z,anchors=obs,missing=[j for j in z if j%4 and j<last],tail=[j for j in z if j>last]);result={}
    for domain,iz in indices.items():
        p=pred[:,:,iz].reshape(-1);g=truth[:,:,iz].reshape(-1);tp=int(np.sum(p&g));fp=int(np.sum(p&~g));fn=int(np.sum(~p&g));tn=int(np.sum(~p&~g))
        n=tp+fn;s=tp+fp;c=dict(tp=tp,fp=fp,fn=fn,tn=tn,voxels=int(g.size),gt_foreground=n,pred_foreground=s,
            dice=2*tp/(s+n) if s+n else None,recall=tp/n if n else None,precision=tp/s if s else None,
            absRVE=abs(s-n)/n if n else None,absolute_relative_volume_error=abs(s-n)/n if n else None,
            signed_relative_volume_error=(s-n)/n if n else None,empty_prediction=s==0,empty_ground_truth=n==0)
        assert sum(c[k] for k in ('tp','fp','fn','tn'))==c['voxels'];result[domain]=c
    for k in ('tp','fp','fn','tn','voxels','gt_foreground','pred_foreground'):
        assert result['full'][k]==sum(result[d][k] for d in ('anchors','missing','tail'))
    return result
def rational_metric(c,f):
    n=c['tp']+c['fn'];s=c['tp']+c['fp']
    if f=='dice':return Fraction(2*c['tp'],n+s) if n+s else None
    if f=='precision':return Fraction(c['tp'],s) if s else None
    if f=='recall':return Fraction(c['tp'],n) if n else None
    if f=='signed_relative_volume_error':return Fraction(s-n,n) if n else None
    if f=='absolute_relative_volume_error':return Fraction(abs(s-n),n) if n else None
    raise ValueError(f)
def independent_aggregate(rows,people):
    assert set(people)=={r['patient'] for r in rows};groups={}
    for p in sorted(people):
        rr=[r for r in rows if r['patient']==p];v={}
        for d in DOMAINS:
            v[d]={}
            for f in FIELDS:
                values=[rational_metric(r['metrics'][d],f) for r in rr]
                v[d][f]=float(sum(values,Fraction())/len(values)) if all(x is not None for x in values) else None
                v[d][f+'_defined_series']=sum(x is not None for x in values)
        groups[p]=dict(series=len(rr),metrics=v)
    means={}
    # Rebuild exact per-patient fractions before averaging, avoiding source floating means.
    for d in DOMAINS:
        means[d]={}
        for f in FIELDS:
            pp=[]
            for p in sorted(people):
                vv=[rational_metric(r['metrics'][d],f) for r in rows if r['patient']==p]
                pp.append(sum(vv,Fraction())/len(vv) if all(x is not None for x in vv) else None)
            means[d][f]=float(sum(pp,Fraction())/len(pp)) if all(x is not None for x in pp) else None
            means[d][f+'_defined_patients']=sum(x is not None for x in pp)
    return dict(patients=groups,patient_first_means=means,
        complete_miss_series=[r['uid'] for r in rows if r['metrics']['full']['tp']==0],
        empty_prediction_series=[r['uid'] for r in rows if r['metrics']['full']['pred_foreground']==0])
def trees_close(a,b):
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(trees_close(a[k],b[k]) for k in a)
    if isinstance(a,list):return isinstance(b,list) and len(a)==len(b) and all(trees_close(x,y) for x,y in zip(a,b))
    if isinstance(a,float):return isinstance(b,(int,float)) and abs(a-b)<=1e-12
    return a==b
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();torch.set_num_threads(4)
    source=OUT/'evaluation_attempt01.json';q=read(source);ex=read(EVAL_EXIT)
    assert q['complete'] and not q['errors'] and q['status']=='completed' and q['prediction_files_saved']==56
    assert ex['evaluation_observed_tool_exit']==0 and ex['evaluation_result_sha256']==sha(source)
    path=OUT/'independent_all56_attempt01.json';assert not path.exists()
    r=dict(created_utc=now(),complete=False,errors=[],numerical_failures=[],arms=[],script_sha256=sha(__file__),
        source_file=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),actual_training_updates=0,actual_gpu_updates=0,
        confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    def save():atomic_json(path,r)
    dump_new(path,r)
    try:
        guard(started);checkpoints,sources=frozen_training();sources.extend((source,EVAL_EXIT,Path(__file__),
            ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py',HERE/'final_eval_lossless_v2.py'))
        for b in q['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        cases=roles()
        for qa,checkpoint in zip(q['arms'],checkpoints):
            assert qa['kind']==checkpoint['kind'] and len(qa['series'])==28 and qa['checkpoint_sha256']==checkpoint['sha256']
            cp=torch.load(ROOT/checkpoint['path'],map_location='cpu',weights_only=True);model=TaskUNet3D();model.load_state_dict(cp['state_dict']);model.eval()
            wrapped=GuardedModel(model,lambda:guard(started));arm=dict(kind=qa['kind'],complete=False,series=[]);r['arms'].append(arm);verifiedrows=[]
            by={s['uid']:s for s in qa['series']};assert len(by)==28 and set(by)=={c['uid'] for role,c,row in cases}
            for role,c,row in cases:
                guard(started);s=by[c['uid']];assert s['role']==role and s['patient']==c['patient']
                normalized,stats=source_image(c,row,qa['kind']);grid=lattice(c);image=physical_mr(normalized,grid)
                assert array_sha(image)==s['physical_input_sha256'] and stats==s['observed_statistics'];del normalized
                tick=time.perf_counter();production,meta=infer_full_fov(wrapped,image,grid,c['native_shape'])
                assert array_sha(production)==s['probability_sha256'] and meta==s['inference']
                prediction=unpack_prediction(ROOT/s['prediction_file']);assert sha(ROOT/s['prediction_file'])==s['prediction_file_sha256']
                assert array_sha(prediction)==s['prediction_sha256'] and np.array_equal(production>=.5,prediction)
                sources.append(ROOT/s['prediction_file']);ind,imeta=functional_fov(cp['state_dict'],image,grid,c['native_shape'],lambda:guard(started))
                assert imeta['total_tiles']==meta['total_tiles'] and imeta['axis_starts']==meta['axis_starts']
                error=float(np.max(np.abs(production-ind)));binary=int(np.count_nonzero((production>=.5)!=(ind>=.5)))
                strict=error<=3e-6 and binary==0 and imeta['float64_coordinate_gate_passed']
                if not strict:r['numerical_failures'].append(dict(kind=qa['kind'],patient=c['patient'],uid=c['uid'],
                    float32_max_probability_error=error,float32_threshold_disagreements=binary,
                    float64_coordinate_gate_passed=imeta['float64_coordinate_gate_passed']))
                gt=read_reference_label(c);assert array_sha(gt)==s['label_sha256'];counts=independent_counts(prediction,gt)
                assert trees_close(counts,s['metrics']);verifiedrows.append(dict(role=role,patient=c['patient'],uid=c['uid'],metrics=counts))
                arm['series'].append(dict(role=role,patient=c['patient'],uid=c['uid'],production_probability_hash_replayed=True,
                    full_packed_prediction_and_counts_verified=True,float32_max_probability_error=error,float32_threshold_disagreements=binary,
                    strict_gate_passed=strict,functional_FOV_and_float64_coordinate=imeta,whole_replay_seconds=time.perf_counter()-tick))
                save();del image,production,prediction,ind,gt;gc.collect();guard(started)
                print(json.dumps(dict(kind=qa['kind'],series_verified=len(arm['series']),strict_gate_passed=strict)),flush=True)
            for role,people in (('development',DEVELOPERS),('validation',VALIDATORS)):
                agg=independent_aggregate([v for v in verifiedrows if v['role']==role],people)
                assert trees_close(agg,qa[role+'_aggregate']);arm[role+'_aggregate']=agg
            # Gate contract is compared after exact independent count/mean reproduction.
            assert gates(arm['validation_aggregate'])==qa['validation_gates']
            arm.update(complete=True,patient_first_aggregates_verified=True,all_strict_numeric_gates_passed=all(s['strict_gate_passed'] for s in arm['series']))
            assert state_hash(model.state_dict())==checkpoint['state_hash'];del model,wrapped,cp;gc.collect();save()
        assert sha(source)==r['source_sha256']
        r.update(complete=len(r['arms'])==2 and all(a['complete'] for a in r['arms']),all56_prediction_files_and_metrics_verified=True,
            all_strict_numeric_gates_passed=not r['numerical_failures'],cuda_initialized=torch.cuda.is_initialized(),resources_after=guard(started),
            source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(sources))])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=now();r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','all_strict_numeric_gates_passed','elapsed_seconds')}),flush=True)
    return int(not r['complete'] or not r.get('all_strict_numeric_gates_passed',False))
if __name__=='__main__':raise SystemExit(main())
