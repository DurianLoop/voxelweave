from adapters import *
from audit_statistics import rho,partial,weighted_rho,weighted_partial,bootstrap_indices,simultaneous
import pandas as pd,datetime,time,argparse
ALL=['linear','cubic','acvtt','ressrdiff','arssr','cycleinr','resunet','gan_2p5d','swinir','saint','i3net','hat','smamba_unet']
TESTED=['linear','acvtt','resunet','smamba_unet','arssr','hat','swinir','saint']
INELIGIBLE={'cubic':'Native two-anchor fallback becomes linear','ressrdiff':'Additional stochastic sampler noise outside frozen response contract','cycleinr':'Frozen four-anchor x4 context contract','gan_2p5d':'Fixed x4 channels cannot express every target fraction','i3net':'Frozen four-slice stride4 input window'}
def observations(ds,m):
    if m in ['hat','swinir','saint']:
        source=C/'outputs/saint_acquired_observations.csv' if m=='saint' else B/'acquired_only_influence.csv'
        expected=read(P/'OLD_OBSERVATION_MANIFEST.json');assert sha(source)==expected[str(source.relative_to(ROOT)).replace('\\','/')]
        g=pd.read_csv(source);g=g[(g.dataset==ds)&(g.model==m)].copy();return g,dict(source='reused existing responses and observations',rows=len(g),source_sha256=sha(source))
    rows=[];maxdiff=0.;paths=sorted((P/'outputs/responses').glob(f'{ds}_{m}_*.npz'))
    expected=(24 if ds=='fastmri' else 115)*3;assert len(paths)==expected,(ds,m,len(paths))
    for i,path in enumerate(paths):
        meta=read(path.with_suffix('.json'));assert sha(path)==meta['sha256'];z=meta['z'];case=meta['case']
        with np.load(path) as f, np.load(B/'inputs'/f'{ds}_{case}_z{z}.npz') as inp:
            assert sha(B/'inputs'/f'{ds}_{case}_z{z}.npz')==meta['input_sha256']
            assert np.array_equal(f['contexts'],CONTEXTS) and np.array_equal(f['mask'],inp['mask'])
            assert float(f['lo'])==float(inp['lo']) and float(f['scale'])==float(inp['scale']) and z not in inp['anchor_ids']
            y=np.load(B/'targets'/f'{ds}_{case}_z{z}.npy');mask=f['mask'];base=f['base'].astype(float)[:,mask];response=f['response'].astype(float)
            assert response.shape[:4]==(4,9,2,4) and np.isfinite(response).all()
            for ei,eps in enumerate(f['epsilons']):
                # Independently embed each response in its physical-anchor identity slots.
                emb=np.zeros((9,6,4,response.shape[-1]),float)
                for ci,ctx in enumerate(CONTEXTS):
                    for j,off in enumerate(ctx):emb[ci,[-3,-2,-1,1,2,3].index(off)]=response[ei,ci,j]
                norm=np.sqrt(np.square(emb).sum(axis=(1,2,3)))
                for ci,ctx in enumerate(CONTEXTS[1:],1):
                    val=np.sum(emb[0]*emb[ci])/(norm[0]*norm[ci]) if norm[0]*norm[ci]>0 else np.nan
                    alternate=influence(response[ei],ci)
                    assert np.isclose(val,alternate,atol=1e-12,rtol=0,equal_nan=True)
                    if np.isfinite(val):maxdiff=max(maxdiff,abs(val-alternate))
                    ea=base[0]-y[mask].astype(float);eb=base[ci]-y[mask].astype(float);dd=ea-eb;aa=ea@ea;bb=eb@eb
                    measurements=dict(alignment=ea@eb/np.sqrt(aa*bb) if aa*bb>0 else np.nan,observable=(dd@dd)/(2*(aa+bb)) if aa+bb>0 else np.nan,disagreement=np.mean(abs(dd)),reference_error=np.mean(abs(ea)),companion_error=np.mean(abs(eb)),paired_error=.5*np.mean(abs(ea)+abs(eb)))
                    rows.append(dict(dataset=ds,model=m,case=case,z=z,epsilon=eps,context=str(ctx),span=ctx[1]-ctx[0],asymmetry=abs(sum(ctx)),overlap_count=len(set(REF)&set(ctx)),influence=val,source_hash=meta['sha256'],**measurements))
        if i%40==0:print('ARRAY AUDIT',ds,m,i,'/',len(paths),flush=True)
    return pd.DataFrame(rows),dict(source='new raw arrays; independent embedded-space recomputation',arrays=len(paths),rows=len(rows),maximum_influence_difference=maxdiff)

def process(ds,m):
    g,check=observations(ds,m);g.to_csv(P/f'outputs/observations_{ds}_{m}.csv',index=False)
    assert len(g)==(24 if ds=='fastmri' else 115)*3*8*4
    base=g[g.epsilon==.01].sort_values(['case','z','context']).reset_index(drop=True)
    threshold=.85 if m in ['hat','swinir'] else .90;stable=[]
    for eps in [.005,.02,-.01]:
        a=base[base.overlap_count==1].influence.to_numpy();b=g[(g.epsilon==eps)&(g.overlap_count==1)].sort_values(['case','z','context']).influence.to_numpy()
        value=float(rho(a,b));stable.append(dict(epsilon=eps,rank_stability=value))
    cases=sorted(base.case.unique());idx=bootstrap_indices(len(cases),18003 if ds=='ixi' else 18004);counts=np.stack([np.bincount(i,minlength=len(cases)) for i in idx])
    endpoints=[];saved={};crosschecks=[]
    for ep in ['beyond_count','fixed_count']:
        q=base if ep=='beyond_count' else base[base.overlap_count==1].reset_index(drop=True)
        codes=pd.Categorical(q.case,categories=cases).codes;x=q.influence.to_numpy();y=q.alignment.to_numpy();cc=q.overlap_count.to_numpy();geo=q[['span','asymmetry']].to_numpy();case=q.case.to_numpy()
        if not np.isfinite(x).all() or not np.isfinite(y).all():
            point=np.nan;reps=np.full(5000,np.nan)
        else:
            point=abs(float(rho(x,y)))-abs(float(rho(cc,y))) if ep=='beyond_count' else partial(x,y,geo,case);rep=[]
            for start in range(0,5000,125):
                w=counts[start:start+125][:,codes]
                vals=abs(weighted_rho(x,y,w))-abs(weighted_rho(cc,y,w)) if ep=='beyond_count' else weighted_partial(x,y,geo,case,w)
                rep.extend(vals)
            reps=np.asarray(rep)
            for k in range(3):
                inds=np.concatenate([np.flatnonzero(codes==i) for i in idx[k]]);newcase=np.concatenate([np.repeat(j,(codes==i).sum()) for j,i in enumerate(idx[k])])
                direct=abs(float(rho(x[inds],y[inds])))-abs(float(rho(cc[inds],y[inds]))) if ep=='beyond_count' else partial(x[inds],y[inds],geo[inds],newcase)
                assert np.isclose(direct,reps[k],atol=1e-10,rtol=0,equal_nan=True)
                crosschecks.append(dict(endpoint=ep,draw=k,error=float(abs(direct-reps[k]))))
        saved[ep]=reps;endpoints.append(dict(endpoint=ep,estimate=float(point),rho_influence=float(rho(x,y)),rho_count=float(rho(cc,y)) if ep=='beyond_count' else None,observations=len(q)))
    secondary=[]
    for eps,q in g.groupby('epsilon'):
        for ep in ['alignment','observable','disagreement','paired_error','reference_error','companion_error']:
            one=q[q.overlap_count==1];ri=float(rho(q.influence,q[ep]));rc=float(rho(q.overlap_count,q[ep]));fc=partial(one.influence.to_numpy(),one[ep].to_numpy(),one[['span','asymmetry']].to_numpy(),one.case.to_numpy())
            secondary.append(dict(dataset=ds,model=m,epsilon=eps,endpoint=ep,rho_influence=ri,rho_count=rc,beyond_count=abs(ri)-abs(rc),fixed_count=fc,inference='descriptive'))
    pd.DataFrame(secondary).to_csv(P/f'outputs/secondary_{ds}_{m}.csv',index=False)
    np.savez_compressed(P/f'outputs/bootstrap_{ds}_{m}.npz',**saved)
    result=dict(dataset=ds,model=m,threshold=threshold,stability=stable,stability_status='PASS' if all(np.isfinite(r['rank_stability']) and r['rank_stability']>=threshold for r in stable) else 'FAIL',endpoints=endpoints,checks=check,bootstrap_crosschecks=crosschecks,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    write(P/f'outputs/summary_{ds}_{m}.json',result);print('ANALYZED',ds,m,result['stability_status'],[(x['endpoint'],x['estimate']) for x in endpoints],flush=True)

def aggregate():
    family={}
    for ds in ['fastmri','ixi']:
        for ep in ['beyond_count','fixed_count']:
            points=[];reps=[];names=[]
            for m in TESTED:
                path=P/f'outputs/summary_{ds}_{m}.json'
                if not path.exists():continue
                d=read(path);points.append(next(r['estimate'] for r in d['endpoints'] if r['endpoint']==ep));reps.append(np.load(P/f'outputs/bootstrap_{ds}_{m}.npz')[ep]);names.append(m)
            ci,nvalid=simultaneous(points,np.column_stack(reps));size=int(np.isfinite(points).sum())
            for i,m in enumerate(names):family[ds,m,ep]=dict(low=float(ci[i,0]),high=float(ci[i,1]),nominal_family=8,estimable_family=size,joint_valid_draws=nvalid)
    old=pd.read_csv(C/'FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.csv');rows=[]
    for m in ALL:
        for ds in ['fastmri','ixi']:
            row=dict(model=m,dataset=ds,examinations=24 if ds=='fastmri' else 115,information_contract='acquired-only response formation; targets only for evaluation',technical_status='INELIGIBLE' if m in INELIGIBLE else 'ELIGIBLE',reason=INELIGIBLE.get(m,''),stability='NA',claim_status='INELIGIBLE' if m in INELIGIBLE else 'NOT RUN')
            path=P/f'outputs/summary_{ds}_{m}.json'
            if path.exists():
                d=read(path);row.update(stability=d['stability_status'],threshold=d['threshold'],source='reused' if m in ['hat','swinir','saint'] else 'new',rank_stability_min=min(r['rank_stability'] for r in d['stability']))
                for eps,label in [(.005,'half'),(.02,'double'),(-.01,'negative')]:row['stability_'+label]=next(r['rank_stability'] for r in d['stability'] if r['epsilon']==eps)
                for ep in ['beyond_count','fixed_count']:
                    r=next(r for r in d['endpoints'] if r['endpoint']==ep);c=family[ds,m,ep];row[ep]=r['estimate'];row[ep+'_low']=c['low'];row[ep+'_high']=c['high'];row[ep+'_family_n']=c['estimable_family'];row[ep+'_valid_draws']=c['joint_valid_draws']
                for ep in ['beyond_count','fixed_count']:
                    row[ep+'_effect_status']='UNDEFINED' if not np.isfinite(row[ep]) else ('POSITIVE' if row[ep+'_low']>0 else ('NEGATIVE' if row[ep+'_high']<0 else 'NULL/INCONCLUSIVE'))
                row['claim_status']='NUMERICAL FAIL' if row['stability']!='PASS' else ('UNDEFINED' if not np.isfinite(row['beyond_count']) else ('SUPPORTED' if row['beyond_count_low']>0 else ('NEGATIVE EFFECT' if row['beyond_count_high']<0 else 'NULL/INCONCLUSIVE')))
                row['inference_family']='new eight scheduled models per cohort/endpoint; retained regardless of stability/sign'
            elif m not in INELIGIBLE:
                row.update(technical_status='INTERFACE VALIDATION FAIL',reason='See frozen-interface validation record',claim_status='INELIGIBLE')
            if m in ['hat','swinir','saint']:
                q=old[(old.model==m)&(old.dataset==ds)].iloc[0]
                for ep in ['beyond_count','fixed_count']:
                    assert abs(row[ep]-q[ep+'_estimate'])<1e-12,(ds,m,ep)
                    row[ep+'_legacy_low']=q[ep+'_simultaneous_low'];row[ep+'_legacy_high']=q[ep+'_simultaneous_high']
                row['legacy_family']=q.inference_family
            rows.append(row)
    df=pd.DataFrame(rows);df.to_csv(P/'CONTINUOUS_INFLUENCE_BIG_TABLE.csv',index=False,na_rep='NA')
    sec=pd.concat([pd.read_csv(f) for f in sorted((P/'outputs').glob('secondary_*.csv'))],ignore_index=True);sec.to_csv(P/'ALL_SECONDARY_SIGNS.csv',index=False,na_rep='NA')
    write(P/'outputs/analysis_complete.json',dict(status='PASS',rows=len(df),tested_rows=int((df.technical_status=='ELIGIBLE').sum()),all_secondary_rows=len(sec),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    print('AGGREGATION COMPLETE',len(df),'rows',flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--watch',action='store_true');args=ap.parse_args()
    pending={(ds,m) for ds in ['fastmri','ixi'] for m in TESTED}
    while pending:
        progress=False
        for ds,m in sorted(pending):
            if (P/f'outputs/summary_{ds}_{m}.json').exists():pending.remove((ds,m));continue
            v=P/f'outputs/validation_{ds}_{m}.json'
            if v.exists() and read(v)['status']=='FAIL':pending.remove((ds,m));continue
            ready=m in ['hat','swinir','saint'] or len(list((P/'outputs/responses').glob(f'{ds}_{m}_*.json')))==(72 if ds=='fastmri' else 345)
            if not ready:continue
            process(ds,m);pending.remove((ds,m));progress=True
        if pending:
            if not args.watch:print('PENDING',sorted(pending),flush=True);return
            if not progress:time.sleep(15)
    aggregate()
if __name__=='__main__':main()
