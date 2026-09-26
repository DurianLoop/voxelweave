from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from stat_utils import corr,partial,ci,gain
P14=Path(__file__).resolve().parents[1]; OUT=P14/'outputs'
source=P14.parent/'PLAN13_EVIDENCE_UPGRADE/outputs/ixi_i3net_benefit_per_case.csv'
g=pd.read_csv(source); assert len(g)==115 and g.acquired_range.gt(0).all()
idx=np.random.default_rng(20260909).integers(0,115,(10000,115)); rows=[]; budgets=[]
for endpoint in ['raw','normalized']:
    s=np.ones(len(g)) if endpoint=='raw' else g.acquired_range.to_numpy()
    y=g.benefit.to_numpy()/s; z=g.mae_x4.to_numpy()/s
    for score in ['anchor_cv','adjacent_mae']:
        for score_unit in ['raw','normalized']:
            x=g[score].to_numpy()/(1 if score_unit=='raw' else g.acquired_range.to_numpy())
            raw=corr(x[idx],y[idx]); adj=partial(x[idx],y[idx],z[idx])
            rows.append({'score':score,'score_unit':score_unit,'endpoint_unit':endpoint,'rho':float(corr(x,y)),'ci_low':ci(raw)[0],'ci_high':ci(raw)[1],
                         'partial_rho_given_x4':float(partial(x,y,z)),'partial_ci_low':ci(adj)[0],'partial_ci_high':ci(adj)[1]})
            for budget in [.2,.5]:
                bs=gain(y[idx],x[idx],budget); denom=float(gain(y,y,budget))
                budgets.append({'score':score,'score_unit':score_unit,'endpoint_unit':endpoint,'budget':budget,'gain_above_random':float(gain(y,x,budget)),
                                'ci_low':ci(bs)[0],'ci_high':ci(bs)[1],'oracle_normalized_gain':float(gain(y,x,budget))/denom})
pd.DataFrame(rows).to_csv(OUT/'ixi_scale_contract_correlations.csv',index=False)
pd.DataFrame(budgets).to_csv(OUT/'ixi_scale_contract_budgets.csv',index=False)
(OUT/'ixi_scale_contract_manifest.json').write_text(json.dumps({'cases':len(g),'bootstrap':10000,'seed':20260909,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((P14/'PROTOCOL.md').read_bytes()).hexdigest(),'status':'COMPLETE EXPLORATORY'},indent=2))
print(pd.DataFrame(rows).to_string(index=False))
