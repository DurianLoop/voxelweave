from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from stat_utils import corr,partial,ci,gain,naurc
P14=Path(__file__).resolve().parents[1]; OUT=P14/'outputs'
p=pd.read_csv(OUT/'topcow_per_plane.csv',dtype={'case':str})
b=pd.read_csv(OUT/'topcow_benefit_per_plane.csv',dtype={'case':str})
assert p.case.nunique()==125 and b.case.nunique()==125
assert not p.duplicated(['case','z','pair','condition','mask']).any()
assert not b.duplicated(['case','z','model']).any()
assert p.z.mod(2).eq(1).all()
cols=['error','disagreement','observable','total_energy','linear_error','cubic_error','linear_vessel_error','cubic_vessel_error']
case=p.groupby(['case','pair','condition','mask','residue'])[cols].mean().groupby(['case','pair','condition','mask']).mean().reset_index()
case.to_csv(OUT/'topcow_per_case.csv',index=False)
bp=b.groupby(['case','model','residue'])[['mae_x4','mae_x2','vessel_mae_x4','vessel_mae_x2','anchor_cv','adjacent_mae','acquired_range']].mean().groupby(['case','model']).mean().reset_index()
bp['benefit']=bp.mae_x4-bp.mae_x2; bp['vessel_benefit']=bp.vessel_mae_x4-bp.vessel_mae_x2
bp.to_csv(OUT/'topcow_benefit_per_case.csv',index=False)
cases=sorted(p.case.unique()); idx=np.random.default_rng(20260909).integers(0,125,(10000,125))
effects=[]; ranks=[]; risks=[]; mask_sensitivity=[]
for mask in ['acquired','full','gt']:
    point=[]; reps=[]; cache={}
    for pair in ['LC','CL']:
        g=case[case['mask'].eq(mask)&case.pair.eq(pair)]
        a=g[g.condition.eq('shared')].set_index('case').loc[cases]
        d=g[g.condition.eq('disjoint')].set_index('case').loc[cases]
        delta=d.observable.to_numpy()-a.observable.to_numpy(); point.append(delta.mean()); reps.append(delta[idx].mean(1))
        cache[pair]=(a,d,delta)
    reps=np.stack(reps,axis=1); point=np.array(point); sd=reps.std(0,ddof=1)
    critical=np.quantile(np.max(abs((reps-point)/sd),axis=1),.95)
    for j,pair in enumerate(['LC','CL']):
        a,d,delta=cache[pair]
        effects.append({'mask':mask,'pair':pair,'cases':125,'gain':point[j],'ci_low':ci(reps[:,j])[0],'ci_high':ci(reps[:,j])[1],
                        'simultaneous_low':point[j]-critical*sd[j],'simultaneous_high':point[j]+critical*sd[j],
                        'positive_cases':int((delta>0).sum()),'loo_min':float(((delta.sum()-delta)/124).min()),'loo_max':float(((delta.sum()-delta)/124).max())})
        model='linear' if pair=='LC' else 'cubic'
        for endpoint in ['error','vessel_error']:
            y=a[model+'_'+endpoint].to_numpy(); sa=a.disagreement.to_numpy(); da=d.disagreement.to_numpy()
            assert np.isfinite(y).all()
            rd=corr(da[idx],y[idx])-corr(sa[idx],y[idx])
            ranks.append({'mask':mask,'pair':pair,'endpoint':endpoint,'shared_rho':float(corr(sa,y)),'disjoint_rho':float(corr(da,y)),
                          'delta_rho':float(corr(da,y)-corr(sa,y)),'delta_ci_low':ci(rd)[0],'delta_ci_high':ci(rd)[1]})
            if mask=='acquired':
                risk_reps=naurc(y[idx],da[idx])-naurc(y[idx],sa[idx])
                risks.append({'pair':pair,'endpoint':endpoint,'shared_naurc':float(naurc(y,sa)),'disjoint_naurc':float(naurc(y,da)),
                              'delta_naurc':float(naurc(y,da)-naurc(y,sa)),'ci_low':ci(risk_reps)[0],'ci_high':ci(risk_reps)[1]})
pd.DataFrame(effects).to_csv(OUT/'topcow_effects.csv',index=False)
pd.DataFrame(ranks).to_csv(OUT/'topcow_rankings.csv',index=False)
pd.DataFrame(risks).to_csv(OUT/'topcow_risk_coverage.csv',index=False)

correlations=[]; budgets=[]; means=[]
for model in ['linear','cubic']:
    g=bp[bp.model.eq(model)].set_index('case').loc[cases]
    means.append({'model':model,**{k:float(g[k].mean()) for k in ['mae_x4','mae_x2','benefit','vessel_mae_x4','vessel_mae_x2','vessel_benefit']},
                  'positive_benefit_cases':int((g.benefit>0).sum()),'positive_vessel_benefit_cases':int((g.vessel_benefit>0).sum())})
    for endpoint in ['benefit','vessel_benefit']:
        for endpoint_unit in ['raw','normalized']:
            scale=1 if endpoint_unit=='raw' else g.acquired_range.to_numpy()
            y=g[endpoint].to_numpy()/scale; z=g['mae_x4' if endpoint=='benefit' else 'vessel_mae_x4'].to_numpy()/scale
            for score in ['anchor_cv','adjacent_mae']:
                for score_unit in ['raw','normalized']:
                    x=g[score].to_numpy()/(1 if score_unit=='raw' else g.acquired_range.to_numpy())
                    raw=corr(x[idx],y[idx]); adj=partial(x[idx],y[idx],z[idx])
                    key={'model':model,'endpoint':endpoint,'endpoint_unit':endpoint_unit,'score':score,'score_unit':score_unit}
                    correlations.append({**key,'rho':float(corr(x,y)),'ci_low':ci(raw)[0],'ci_high':ci(raw)[1],
                                         'partial_rho_given_x4':float(partial(x,y,z)),'partial_ci_low':ci(adj)[0],'partial_ci_high':ci(adj)[1]})
                    for budget in [.2,.5]:
                        bs=gain(y[idx],x[idx],budget); oracle=float(gain(y,y,budget))
                        budgets.append({**key,'budget':budget,'gain_above_random':float(gain(y,x,budget)),'ci_low':ci(bs)[0],'ci_high':ci(bs)[1],
                                        'oracle_normalized_gain':float(gain(y,x,budget))/oracle})
pd.DataFrame(correlations).to_csv(OUT/'topcow_benefit_correlations.csv',index=False)
pd.DataFrame(budgets).to_csv(OUT/'topcow_benefit_budgets.csv',index=False)
pd.DataFrame(means).to_csv(OUT/'topcow_benefit_means.csv',index=False)
(OUT/'topcow_analysis_manifest.json').write_text(json.dumps({'status':'COMPLETE','bootstrap':10000,'seed':20260909,'cases':125,'unique_target_planes':len(p.drop_duplicates(['case','z'])),
        'rows_per_plane':len(p),'aggregation':'within-residue mean then equal residue mean then equal-case mean','benefit_means':means,
        'input_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in [OUT/'topcow_per_plane.csv',OUT/'topcow_benefit_per_plane.csv']},
        'inference':'simultaneous intervals cover the two estimator pairings within each mask for local gain only; all other intervals exploratory pointwise'},indent=2))
print(pd.DataFrame(effects).to_string(index=False)); print(pd.DataFrame(ranks).to_string(index=False));print(pd.DataFrame(means).to_string(index=False))
