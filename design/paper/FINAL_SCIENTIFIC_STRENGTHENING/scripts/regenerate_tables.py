"""Regenerate main-table LaTeX as review artifacts from array-derived statistics."""
from common import *
def main():
    dest=P/'reproduced_tables';dest.mkdir(exist_ok=True);raw=OUT/'array_reproduced'
    c=pd.read_csv(OUT/'reproduced_original_control.csv');clean=pd.concat([pd.read_csv(raw/'clean_max_overlap_per_plane.csv'),pd.read_csv(raw/'clean_max_overlap_ixi_per_plane.csv')])
    z=pd.concat([pd.read_csv(raw/'overlap_covariance_per_plane.csv'),pd.read_csv(raw/'overlap_covariance_ixi_per_plane.csv')]);q=z[['dataset','case_id','model','z','mae','disagreement_mae']].merge(clean,on=['dataset','case_id','model','z'],validate='one_to_one')
    rows=[]
    for ds in ['fastmri','ixi','ningxia']:
        r=c[c.dataset==ds].iloc[0];flags=[]
        for _,g in q[q.dataset==ds].groupby('model'):
            e=g.mae.quantile(.75);d=g.disagreement_mae.quantile(.25);flags.extend(((g.error>=e)&(g.score<=d)).astype(int)-((g.mae>=e)&(g.disagreement_mae<=d)).astype(int))
        name={'fastmri':'fastMRI','ixi':'IXI','ningxia':'NingXia'}[ds];units={'fastmri':'24 examinations','ixi':'115 examinations','ningxia':'8 patients (22 series)'}[ds]
        rows.append(f'{name} & {units} & {r.rho_disjoint:.3f} & {r.rho_shared:.3f} & {r.delta:.3f} [{r.low:.3f},{r.high:.3f}] & {r.observable_percent:.2f}\\% / {100*np.mean(flags):+.1f} pp \\\\')
    t=r'''\begin{table*}[t]\centering
\caption{Original clean comparison. Pooled-plane ranking uses fixed phase-0 MAE for fastMRI/NingXia and disjoint-pair mean MAE for IXI; intervals resample examinations/patients. Stable-wrong thresholds are test-relative.}
\label{tab:controlled}\setlength{\tabcolsep}{4pt}
\begin{tabular}{lrrrrr}\toprule
Cohort & Independent units & $\rho_{\rm disjoint}$ & $\rho_{\rm shared}$ & $\Delta\rho$ [95\% CI] & Observable error / stable-wrong $\Delta$\\\midrule
'''+ '\n'.join(rows)+r'\bottomrule\end{tabular}\end{table*}'
    (dest/'table1.tex').write_text(t,encoding='utf-8')
    a=pd.read_csv(raw/'acquired_only_summary.csv').set_index(['dataset','model','endpoint']);s=pd.read_csv(raw/'acquired_only_stability.csv');rows=[]
    for ds in ['ixi','fastmri']:
        for model in ['hat','swinir']:
            b=a.loc[(ds,model,'beyond_count')];f=a.loc[(ds,model,'fixed_count')];v=s[(s.dataset==ds)&(s.model==model)].rank_stability.min();rows.append(f'{ds} & {model} & {b.estimate:.3f} [{b.simultaneous_low:.3f},{b.simultaneous_high:.3f}] & {f.estimate:.3f} [{f.simultaneous_low:.3f},{f.simultaneous_high:.3f}] & {v:.3f} / '+('PASS' if v>=.85 else 'FAIL')+r' \\')
    t=r'''\begin{table*}[t]\centering\small\caption{Acquired-only influence; simultaneous two-model intervals within each cohort/endpoint. Stability threshold .85.}\label{tab:neural}
\begin{tabular}{llrrr}\toprule Cohort & Model & Beyond-count [CI] & Fixed-count partial [CI] & Minimum stability / status\\\midrule
'''+ '\n'.join(rows)+r'\bottomrule\end{tabular}\end{table*}'
    (dest/'table2.tex').write_text(t,encoding='utf-8');print('Both main tables regenerated from array-derived observations/statistics',flush=True)
if __name__=='__main__':main()
