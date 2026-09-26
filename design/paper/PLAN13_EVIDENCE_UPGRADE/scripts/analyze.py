"""Exploratory, paired cluster reanalysis. Never mutates historical evidence."""
from pathlib import Path
import hashlib, json, sys, platform
import numpy as np
import pandas as pd
from scipy.stats import rankdata

P13=Path(__file__).resolve().parents[1]; PAPER=P13.parent
P9=PAPER/'ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/outputs'
P11=PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs'
OUT=P13/'outputs'; OUT.mkdir(exist_ok=True)
SEED=20260908; B=10000; MODELS=['hat','swinir','i3net','saint','cycleinr']
INPUTS=[]
def read(p):
    INPUTS.append({'path':p.relative_to(PAPER).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    return pd.read_csv(p)
def corr(x,y,axis=-1):
    x=rankdata(x,axis=axis); y=rankdata(y,axis=axis)
    x=x-x.mean(axis=axis,keepdims=True); y=y-y.mean(axis=axis,keepdims=True)
    den=np.sqrt((x*x).sum(axis=axis)*(y*y).sum(axis=axis))
    return np.divide((x*y).sum(axis=axis),den,out=np.full_like(den,np.nan,dtype=float),where=den>1e-15)
def partial(x,y,z,axis=-1):
    a=corr(x,y,axis); b=corr(x,z,axis); c=corr(y,z,axis)
    den=np.sqrt(np.maximum((1-b*b)*(1-c*c),0))
    return np.divide(a-b*c,den,out=np.full_like(den,np.nan,dtype=float),where=den>1e-12)
def ci(x): return np.nanquantile(x,[.025,.975]).tolist()
def simultaneous(point,reps):
    se=np.nanstd(reps,axis=0,ddof=1)
    q=np.nanquantile(np.nanmax(np.abs((reps-point)/se),axis=1),.95)
    return point-q*se,point+q*se

audit=[]; arch=[]; jack=[]; original=[]
fast=pd.concat([read(P9/'p9_disjoint_shared_per_plane.csv'),read(P9/'p9_disjoint_shared_per_plane_transformer_reference.csv')],ignore_index=True)
ixi=read(P11/'p11_ixi_clean_per_plane_full.csv')
for ds,df,n in [('fastmri',fast,24),('ixi',ixi,115)]:
    keys=['case','model','target_z','condition']
    assert not df.duplicated(keys).any()
    assert len(df)==n*5*5*2 and set(df.model)==set(MODELS)
    metrics=['observable_error_fraction','shared_error_fraction','paired_error_mae','prediction_disagreement_mae','error_cosine']
    assert np.isfinite(df[metrics]).all().all()
    assert df.groupby(['case','model','condition']).size().eq(5).all()
    closure=float(np.max(np.abs(df.observable_error_fraction+df.shared_error_fraction-1)))
    assert closure<1e-10
    audit.append({'dataset':ds,'rows':len(df),'cases':df.case.nunique(),'duplicate_keys':0,'max_fraction_closure_error':closure})
    for within in ['mean','median']:
        ag=df.groupby(['case','model','condition'])[metrics].agg(within)
        cases=sorted(df.case.unique())
        def matrix(metric,cond):
            return ag[metric].unstack('condition')[cond].unstack('model').loc[cases,MODELS].to_numpy()
        gain=matrix('observable_error_fraction','disjoint')-matrix('observable_error_fraction','shared')
        ed=matrix('paired_error_mae','disjoint'); es=matrix('paired_error_mae','shared')
        dd=matrix('prediction_disagreement_mae','disjoint'); sd=matrix('prediction_disagreement_mae','shared')
        common=(ed+es)/2
        idx=np.random.default_rng(SEED).integers(0,n,(B,n))
        rank_point=corr(dd,ed,0)-corr(sd,es,0)
        rank_reps=corr(dd[idx],ed[idx],1)-corr(sd[idx],es[idx],1)
        common_point=corr(dd,common,0)-corr(sd,common,0)
        common_reps=corr(dd[idx],common[idx],1)-corr(sd[idx],common[idx],1)
        rl,rh=simultaneous(rank_point,rank_reps); cl,ch=simultaneous(common_point,common_reps)
        for across in ['mean','median']:
            fn=getattr(np,across); point=fn(gain,axis=0); reps=fn(gain[idx],axis=1)
            lo,hi=simultaneous(point,reps)
            for j,m in enumerate(MODELS):
                arch.append({'dataset':ds,'model':m,'within_case':within,'across_cases':across,'cases':n,
                    'gain':point[j],'ci_low':ci(reps[:,j])[0],'ci_high':ci(reps[:,j])[1],
                    'simultaneous_low':lo[j],'simultaneous_high':hi[j],'positive_cases':int((gain[:,j]>0).sum()),
                    'ranking_delta':rank_point[j],'ranking_sim_low':rl[j],'ranking_sim_high':rh[j],
                    'common_endpoint_ranking_delta':common_point[j],'common_ranking_sim_low':cl[j],'common_ranking_sim_high':ch[j]})
                for k,case in enumerate(cases):
                    keep=np.arange(n)!=k
                    jack.append({'dataset':ds,'model':m,'within_case':within,'across_cases':across,'left_out':case,
                        'gain':fn(gain[keep,j]),'ranking_delta':corr(dd[keep,j],ed[keep,j])-corr(sd[keep,j],es[keep,j])})
        print(ds,within,'complete',flush=True)
    original_df=read(P9/'p9_architecture_forest.csv') if ds=='fastmri' else read(P11/'p11_ixi_clean_model_summary_full.csv')
    original.append({'dataset':ds,'columns':original_df.columns.tolist(),'rows':original_df.to_dict('records')})
pd.DataFrame(audit).to_csv(OUT/'integrity.csv',index=False)
pd.DataFrame(arch).to_csv(OUT/'architecture_sensitivity.csv',index=False)
pd.DataFrame(jack).to_csv(OUT/'architecture_leave_one_out.csv',index=False)

table=read(P11/'p11_same_model_benefit_per_case.csv')
assert len(table)==598 and table.eligible_benefit.all()
assert not table.duplicated(['dataset','fold','case','model','support']).any()
assert np.allclose(table.benefit,table.mae_x4-table.mae_x2,atol=1e-10)
assert table[['anchor_cv','adjacent_mae','mae_x4','mae_x2']].notna().all().all()
rows=[]; loo=[]; patient=[]
for (ds,model),g in table.groupby(['dataset','model'],sort=True):
    g=g.reset_index(drop=True); clusters=sorted(g.patient_cluster.unique())
    by=[np.flatnonzero(g.patient_cluster.eq(c)) for c in clusters]
    draws=np.random.default_rng(SEED).integers(0,len(by),(B,len(by)))
    # Group replicate indices by total row count: correct patient-cluster bootstrap,
    # with ranks recomputed on each resampled set including multiplicities.
    batches={}
    for draw in draws:
        idx=np.concatenate([by[k] for k in draw]); batches.setdefault(len(idx),[]).append(idx)
    batches=[np.stack(v) for v in batches.values()]
    for score in ['anchor_cv','adjacent_mae','bank_median_disagreement']:
        if g[score].isna().all():
            assert model in ['linear','cubic']; continue
        assert np.isfinite(g[score]).all()
        x=g[score].to_numpy(); y=g.benefit.to_numpy(); z=g.mae_x4.to_numpy()
        raw=np.concatenate([corr(x[i],y[i]) for i in batches])
        adjusted=np.concatenate([partial(x[i],y[i],z[i]) for i in batches])
        rec={'dataset':ds,'model':model,'score':score,'cases':len(g),'clusters':len(clusters),
             'raw_rho':float(corr(x,y)),'raw_ci_low':ci(raw)[0],'raw_ci_high':ci(raw)[1],
             'partial_rho_given_x4':float(partial(x,y,z)),'partial_ci_low':ci(adjusted)[0],'partial_ci_high':ci(adjusted)[1],
             'valid_bootstrap':int(np.isfinite(adjusted).sum()),'score_current_error_rho':float(corr(x,z))}
        rows.append(rec)
        for k,c in enumerate(clusters):
            keep=~g.patient_cluster.eq(c).to_numpy()
            loo.append({'dataset':ds,'model':model,'score':score,'left_out':str(c),'raw_rho':float(corr(x[keep],y[keep])),
                'partial_rho_given_x4':float(partial(x[keep],y[keep],z[keep]))})
        gp=g.groupby('patient_cluster')[[score,'benefit','mae_x4']].median()
        patient.append({'dataset':ds,'model':model,'score':score,'patients':len(gp),
            'rho_patient_equal':float(corr(gp[score],gp.benefit)),
            'partial_patient_equal':float(partial(gp[score],gp.benefit,gp.mae_x4))})
    print('benefit',ds,model,flush=True)
pd.DataFrame(rows).to_csv(OUT/'benefit_coupling.csv',index=False)
pd.DataFrame(loo).to_csv(OUT/'benefit_leave_one_cluster_out.csv',index=False)
pd.DataFrame(patient).to_csv(OUT/'benefit_patient_equal.csv',index=False)

# Actual stored statistic is MAE / sqrt(mean paired MSE), not RMSE / RMSE.
cov=read(PAPER/'TMI/archive/TMI_MANUSCRIPT_MASTER/experiments/p6_e02_consensus_per_plane.csv')
cov['l2_normalized']=2*np.sqrt(cov.observable_fraction.clip(lower=0))
cov['shape_ratio']=cov.disagreement_mae/(2*np.sqrt(cov.diversity_mse))
cov['reconstructed_mae_normalized']=cov.shape_ratio*cov.l2_normalized
res=np.abs(cov.reconstructed_mae_normalized-cov.disagreement_mae/np.sqrt(cov.mean_mse))
assert cov.shape_ratio.between(0,1+1e-6).all()
algebra={'rows':len(cov),'max_factorization_residual':float(res.max()),
    'shape_ratio_min':float(cov.shape_ratio.min()),'shape_ratio_max':float(cov.shape_ratio.max()),
    'formula':'MAE(a-b)/sqrt(T) = kappa * 2 sqrt(1-q); kappa=MAE(a-b)/RMSE(a-b), 0<=kappa<=1',
    'interpretation':'structural coupling, not independent validation or exact MAE identity without shape factor'}
cov.groupby(['dataset','model','condition']).shape_ratio.agg(['min','median','max']).to_csv(OUT/'algebra_shape_factor.csv')
(OUT/'algebra_audit.json').write_text(json.dumps(algebra,indent=2),encoding='utf-8')
(OUT/'run_manifest.json').write_text(json.dumps({'status':'COMPLETE EXPLORATORY REANALYSIS','seed':SEED,'bootstrap':B,
    'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,
    'protocol_sha256':hashlib.sha256((P13/'PROTOCOL.md').read_bytes()).hexdigest(),'inputs':INPUTS,
    'historical_model_summaries':original,'benefit_rows':len(table)},indent=2),encoding='utf-8')
print('ALL ANALYSES COMPLETE',flush=True)
