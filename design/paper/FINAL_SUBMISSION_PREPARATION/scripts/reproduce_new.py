"""Independent CPU reconstruction of all three new analyses from saved arrays.
Original observation/summary CSVs are comparison targets only.
"""
from common import *
from audit_statistics import rho,weighted_rho,weighted_partial,partial
from reproduce_arrays import array,compare,CHECKS,BINDINGS,DEST

def freshmetric(a,b,y,m):
    a=a[m].astype(float);b=b[m].astype(float);y=y[m].astype(float)
    ea=a-y;eb=b-y;total=(np.mean(ea**2)+np.mean(eb**2))/2
    return dict(observable=np.mean((ea-eb)**2)/(4*total),alignment=np.mean(ea*eb)/np.sqrt(np.mean(ea**2)*np.mean(eb**2)),disagreement=np.mean(abs(a-b)),reference_error=np.mean(abs(ea)),paired_error=(np.mean(abs(ea))+np.mean(abs(eb)))/2,companion_error=np.mean(abs(eb)))

def sim(point,boot):
    boot=boot[np.isfinite(boot).all(axis=1)];sd=boot.std(axis=0,ddof=1)
    z=np.divide(abs(boot-point),sd,out=np.zeros_like(boot),where=sd>0)
    radius=np.quantile(z.max(axis=1),.95)*sd
    return np.stack([point-radius,point+radius],axis=1)

def cross():
    rows=[]
    for r in read(P/'case_registry.json'):
        ds,c=r['dataset'],r['case'];v={}
        for model in MODELS:
            f,meta=array(BASEOUT/'phase_arrays'/f'{ds}_{model}_{c}.npz')
            with f:
                a,b=f['p0'],f['p2'];v[model]=(np.moveaxis(a[:,:,r['targets']],2,0),np.moveaxis(b[:,:,np.array(r['targets'])-2],2,0)) if bool(f['full_arrays']) else (a,b)
        with np.load(P/r['cross_targets']) as f:y,m=f['gt'],f['mask']
        for a in MODELS:
            for b in MODELS:
                if a==b:continue
                for condition,ci in [('shared',0),('disjoint',1)]:
                    for j,z in enumerate(r['targets']):rows.append(dict(dataset=ds,case=c,a=a,b=b,pair=a+'__'+b,condition=condition,z=z,**freshmetric(v[a][0][j],v[b][ci][j],y[j],m[j])))
    df=pd.DataFrame(rows);compare('cross_arch_shared_disjoint.csv',pd.read_csv(P/'cross_arch_shared_disjoint.csv'),df,['dataset','case','pair','condition','z'],['observable','alignment','disagreement','reference_error','paired_error'],atol=1e-10,rtol=1e-10)
    ag=df.groupby(['dataset','case','pair','condition'])[['observable','alignment','disagreement','reference_error','paired_error']].mean();results=[]
    for ds,seed in [('fastmri',18001),('ixi',18002)]:
        g=ag.loc[ds];names=[x['pair'] for x in read(P/'pair_registry.json')];cases=sorted(g.index.get_level_values('case').unique());idx=np.random.default_rng(seed).integers(0,len(cases),(5000,len(cases)))
        def mat(ep,cond):return g[ep].unstack('condition')[cond].unstack('pair').loc[cases,names].to_numpy()
        for ep in ['observable','alignment','disagreement','fixed_reference_ranking','paired_error_ranking']:
            if ep.endswith('ranking'):
                x=mat('reference_error','shared') if ep.startswith('fixed') else mat('paired_error','shared');y=x if ep.startswith('fixed') else mat('paired_error','disjoint')
                s,d=mat('disagreement','shared'),mat('disagreement','disjoint');point=rho(d,y,0)-rho(s,x,0);boot=rho(d[idx],y[idx],1)-rho(s[idx],x[idx],1);name=ep
            else:
                delta=mat(ep,'disjoint')-mat(ep,'shared');point=delta.mean(0);boot=delta[idx].mean(1);name=ep+'_gap'
            iv=sim(point,boot)
            for j,pair in enumerate(names):results.append(dict(dataset=ds,pair=pair,endpoint=name,delta=point[j],simultaneous_low=iv[j,0],simultaneous_high=iv[j,1]))
    compare('cross_arch_shared_disjoint_intervals.csv',pd.read_csv(P/'cross_arch_shared_disjoint_intervals.csv'),pd.DataFrame(results),['dataset','pair','endpoint'],['delta','simultaneous_low','simultaneous_high'],atol=1e-10,rtol=1e-9)

def acquired():
    rows=[]
    for i,file in enumerate(sorted((BASEOUT/'acquired_responses').glob('*.npz'))):
        f,meta=array(file)
        with f:
            base=f['base'];rr=f['response'];m=f['mask'];y=np.load(P/'targets'/f'{meta["dataset"]}_{meta["case"]}_z{meta["z"]}.npy')
            for ei,eps in enumerate(f['epsilons']):
                ref=rr[ei,0].astype(float);refenergy=np.sum(ref**2)
                for ci,ctx in enumerate(CONTEXTS[1:],1):
                    other=rr[ei,ci].astype(float);numerator=sum(np.sum(ref[REF.index(off)]*other[ctx.index(off)]) for off in set(REF)&set(ctx))
                    inf=numerator/np.sqrt(refenergy*np.sum(other**2))
                    rows.append({k:meta[k] for k in ['dataset','model','case','z']}|dict(epsilon=eps,context=str(ctx),span=ctx[1]-ctx[0],asymmetry=abs(sum(ctx)),overlap_count=len(set(REF)&set(ctx)),influence=inf,**freshmetric(base[0],base[ci],y,m)))
        if i%100==0:print('Acquired raw reproduction',i,flush=True)
    df=pd.DataFrame(rows);compare('acquired_only_influence.csv',pd.read_csv(P/'acquired_only_influence.csv'),df,['dataset','model','case','z','epsilon','context'],['influence','observable','alignment','disagreement','reference_error','paired_error'],atol=1e-10,rtol=1e-9)
    results=[];st=[]
    for ds,seed in [('ixi',18003),('fastmri',18004)]:
        cases=sorted(df[df.dataset==ds].case.unique());idx=np.random.default_rng(seed).integers(0,len(cases),(5000,len(cases)));counts=np.stack([np.bincount(i,minlength=len(cases)) for i in idx])
        for endpoint in ['beyond_count','fixed_count']:
            points=[];boots=[]
            for model in ['hat','swinir']:
                q=df[(df.dataset==ds)&(df.model==model)&(df.epsilon==.01)].copy()
                if endpoint=='fixed_count':q=q[q.overlap_count==1]
                x=q.influence.to_numpy();y=q.alignment.to_numpy();c=q.overlap_count.to_numpy();geo=q[['span','asymmetry']].to_numpy();case=q.case.to_numpy();w=counts[:,pd.Categorical(q.case,categories=cases).codes]
                point=abs(float(rho(x,y)))-abs(float(rho(c,y))) if endpoint=='beyond_count' else partial(x,y,geo,case)
                bb=[]
                for start in range(0,5000,125):
                    ww=w[start:start+125];bb.extend(abs(weighted_rho(x,y,ww))-abs(weighted_rho(c,y,ww)) if endpoint=='beyond_count' else weighted_partial(x,y,geo,case,ww))
                points.append(point);boots.append(bb)
            iv=sim(np.array(points),np.array(boots).T)
            for j,model in enumerate(['hat','swinir']):results.append(dict(dataset=ds,model=model,endpoint=endpoint,estimate=points[j],simultaneous_low=iv[j,0],simultaneous_high=iv[j,1]))
        for model in ['hat','swinir']:
            q=df[(df.dataset==ds)&(df.model==model)&(df.overlap_count==1)].pivot(index=['case','z','context'],columns='epsilon',values='influence')
            for eps in [.005,.02,-.01]:st.append(dict(dataset=ds,model=model,epsilon=eps,rank_stability=float(rho(q[eps],q[.01]))))
    compare('acquired_only_summary.csv',pd.read_csv(BASEOUT/'acquired_only_summary.csv'),pd.DataFrame(results),['dataset','model','endpoint'],['estimate','simultaneous_low','simultaneous_high'],atol=1e-9,rtol=1e-8)
    compare('acquired_only_stability.csv',pd.read_csv(P/'acquired_only_stability.csv'),pd.DataFrame(st),['dataset','model','epsilon'],['rank_stability'],atol=1e-12,rtol=1e-10)

def proposition():
    rows=[]
    for file in sorted((BASEOUT/'proposition_arrays').glob('*.npz')):
        f,meta=array(file)
        with f:
            v=f['predictions'].astype(float);base=f['base'].astype(float)
            for ci,ctx in enumerate(CONTEXTS[1:5],1):
                off=next(iter(set(REF)&set(ctx)));a=v[:,0,REF.index(off)];b=v[:,ci,ctx.index(off)]
                oa=(a[0,:4]-a[0,4:])/2;ob=(b[0,:4]-b[0,4:])/2;k0=np.mean(oa*ob)
                for ei,eps in enumerate(f['epsilons']):
                    aa,bb=a[ei],b[ei];coupled=np.mean((aa-bb)**2);ind=np.mean(aa**2+bb**2)-2*np.mean(aa.mean(0)*bb.mean(0));delta=coupled-ind;pred=-2*k0*(eps/.0025)**2
                    rows.append(dict(model=meta['model'],case=meta['case'],context=str(ctx),epsilon=eps,observed_delta=delta,linear_prediction=pred,approx_relative_error=abs(delta-pred)/abs(pred)))
    df=pd.DataFrame(rows);compare('proposition1_neural_validation.csv',pd.read_csv(P/'proposition1_neural_validation.csv'),df,['model','case','context','epsilon'],['observed_delta','linear_prediction','approx_relative_error'],atol=1e-9,rtol=1e-8)
    names=read(P/'proposition_case_registry.json');cols=[(m,e) for m in ['hat','swinir'] for e in [.0025,.005,.01,.02]];mat=df.groupby(['case','model','epsilon']).observed_delta.mean().unstack(['model','epsilon']).loc[sorted(names),cols].to_numpy();idx=np.random.default_rng(18005).integers(0,len(names),(5000,len(names)));pt=mat.mean(0);iv=sim(pt,mat[idx].mean(1));res=[]
    for j,(model,eps) in enumerate(cols):
        q=df[(df.model==model)&(df.epsilon==eps)];res.append(dict(model=model,epsilon=eps,observed_delta_mean=pt[j],linear_prediction_mean=q.linear_prediction.mean(),median_relative_error=q.approx_relative_error.median(),simultaneous_low=iv[j,0],simultaneous_high=iv[j,1]))
    compare('proposition_summary.csv',pd.read_csv(BASEOUT/'proposition_summary.csv'),pd.DataFrame(res),['model','epsilon'],['observed_delta_mean','linear_prediction_mean','median_relative_error','simultaneous_low','simultaneous_high'],atol=1e-8,rtol=1e-8)

def main():
    guard();cross();acquired();proposition();pd.DataFrame(CHECKS).to_csv(OUT/'new_array_reproduction_checks.csv',index=False);write(OUT/'new_array_bindings.json',BINDINGS)
    assert all(r['status']=='PASS' for r in CHECKS),'Resolve numerical mismatches before writing'
if __name__=='__main__':main()
