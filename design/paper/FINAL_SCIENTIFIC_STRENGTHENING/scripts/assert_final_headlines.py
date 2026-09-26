"""Assert the final LaTeX against freshly array-reproduced headline estimates."""
from common import *
from reproduce_new import sim
import re
CV=P/'revised_manuscript';R=OUT/'array_reproduced';checks=[]
def check(label,reported,value,tolerance,source,level='saved arrays -> independently reconstructed observations/statistics'):
    d=abs(float(reported)-float(value));checks.append(dict(headline=label,reported_value=float(reported),recomputed_value=float(value),absolute_difference=d,tolerance=tolerance,status='PASS' if d<=tolerance else 'FAIL',source_hash=sha(source),source_level=level))
def numbers(text):return [float(x) for x in re.findall(r'[-+]?\d*\.\d+',text)]
def ap(y,s,w):
    result=np.zeros(len(w));positives=w[:,y==1].sum(1)
    for cut in np.unique(s):
        select=s>=cut;mass=w[:,select].sum(1);tp=w[:,select&(y==1)].sum(1);new=w[:,(s==cut)&(y==1)].sum(1)
        result+=np.divide(new*tp,mass,out=np.zeros_like(mass,dtype=float),where=mass>0)
    return np.divide(result,positives,out=np.full(len(w),np.nan),where=positives>0)

def guard_negative():
    old=PAPER/'PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/outputs';df=pd.read_csv(old/'neural_pair_per_case.csv');split=read(old/'development_freeze.json');freeze=read(old/'score_formula_freeze.json');seed=20260911
    sourcecode=(PAPER/'PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/scripts/common.py').read_text(encoding='utf-8');seed=int(re.search(r'SEED\s*=\s*(\d+)',sourcecode).group(1))
    bs=['disagreement_norm','anchor_cv_norm','adjacent_mae_norm','adjacent_rmse_norm','acquired_range','spacing'];point=[];reps=[];rows=[]
    for ds in ['fastmri','ixi']:
        for pair,g in df[df.dataset==ds].groupby('pair'):
            if ds=='fastmri':g=g[g.case.isin(split['internal_evaluation'])]
            g=g.sort_values('case');par=freeze['parameters'][pair];y=((g.both_error_norm>=par['error_q75'])&(g.disagreement_norm<=par['disagreement_q25'])).to_numpy(int)
            check('Final guard positives '+ds+'/'+pair,0 if ds=='fastmri' else 2,y.sum(),0,old/'neural_pair_per_case.csv','lowest preserved per-examination score records and frozen formula; no new image inference')
            if ds!='ixi':continue
            d=np.searchsorted(np.sort(par['cdf_d']),g.disagreement_norm,side='right')/len(par['cdf_d']);a=np.searchsorted(np.sort(par['cdf_acv']),g.anchor_cv_norm,side='right')/len(par['cdf_acv']);s=np.maximum(d,a)
            n=len(g);idx=np.random.default_rng(seed).integers(0,n,(5000,n));w=np.vstack([np.ones(n),[np.bincount(i,minlength=n) for i in idx]]);baseap=ap(y,s,w)
            for name in bs:
                delta=baseap-ap(y,g[name].to_numpy(),w);point.append(delta[0]);reps.append(delta[1:])
    interval=sim(np.array(point),np.array(reps).T);check('Final guard positive simultaneous AP comparisons',0,int((interval[:,0]>0).sum()),0,old/'neural_pair_per_case.csv','fresh AP/bootstrap from lowest per-examination records; full image-level guard reproduction not claimed')
    check('Final guard all twelve AP intervals cross zero',12,int(((interval[:,0]<=0)&(interval[:,1]>=0)).sum()),0,old/'neural_pair_per_case.csv','fresh AP/bootstrap from lowest per-examination records')

def main():
    guard();text=(CV/'main.tex').read_text(encoding='utf-8');tab=(CV/'final_acquired_table.tex').read_text(encoding='utf-8');c=pd.read_csv(R/'cross_arch_shared_disjoint_intervals.csv');a=pd.read_csv(R/'acquired_only_summary.csv');st=pd.read_csv(R/'acquired_only_stability.csv');p=pd.read_csv(R/'proposition_summary.csv');pr=pd.read_csv(R/'proposition1_neural_validation.csv')
    current_control=(CV/'p17_control_table.tex').read_text(encoding='utf-8')
    regenerated_control=(P/'reproduced_tables/table1.tex').read_text(encoding='utf-8')
    for cohort in ['fastMRI','IXI','NingXia']:
        actual=next(line for line in current_control.splitlines() if line.startswith(cohort+' &'))
        regenerated=next(line for line in regenerated_control.splitlines() if line.startswith(cohort+' &'))
        assert numbers(actual)==numbers(regenerated),('Final Table1 LaTeX mismatch',cohort)
    for ds,pattern in [('fastmri',r'(\d+\.\d+)--(\d+\.\d+) percentage points on fastMRI'),('ixi',r'(\d+\.\d+)--(\d+\.\d+) on IXI')]:
        reported=list(map(float,re.search(pattern,text).groups()));g=c[(c.dataset==ds)&(c.endpoint=='observable_gap')]
        for name,r,v in zip(['minimum','maximum'],reported,[100*g.delta.min(),100*g.delta.max()]):check('Final cross '+ds+' '+name+' pp',r,v,.051,R/'cross_arch_shared_disjoint_intervals.csv')
        check('All ordered local intervals positive '+ds,20,(g.simultaneous_low>0).sum(),0,R/'cross_arch_shared_disjoint_intervals.csv')
        for ep,n in [('fixed_reference_ranking',16 if ds=='ixi' else 0),('paired_error_ranking',20 if ds=='ixi' else 0)]:
            g=c[(c.dataset==ds)&(c.endpoint==ep)];check('Final '+ds+' '+ep+' positive count',n,(g.simultaneous_low>0).sum(),0,R/'cross_arch_shared_disjoint_intervals.csv')
    for ds in ['ixi','fastmri']:
        for model in ['hat','swinir']:
            prefix=('IXI' if ds=='ixi' else 'fastMRI')+' & '+('HAT' if model=='hat' else 'SwinIR')+' & '
            line=next(x for x in tab.splitlines() if x.startswith(prefix));values=numbers(line);recomputed=[]
            for ep in ['beyond_count','fixed_count']:
                row=a[(a.dataset==ds)&(a.model==model)&(a.endpoint==ep)].iloc[0];recomputed += [row.estimate,row.simultaneous_low,row.simultaneous_high]
            recomputed.append(st[(st.dataset==ds)&(st.model==model)].rank_stability.min())
            for k,(reported,value) in enumerate(zip(values,recomputed)):check(f'Final Table2 {ds}/{model} field{k+1}',reported,value,.00051,R/'acquired_only_summary.csv')
    check('All twelve acquired stability checks pass',12,(st.rank_stability>=.85).sum(),0,R/'acquired_only_stability.csv')
    check('Minimum acquired stability',float(re.search(r'minimum (\.\d+)',text).group(1)),st.rank_stability.min(),.00051,R/'acquired_only_stability.csv')
    check('Eight neural mean intervals negative',8,(p.simultaneous_high<0).sum(),0,R/'proposition_summary.csv')
    lo,hi=map(float,re.search(r'errors range from (\d+\.\d+)\\% to (\d+\.\d+)\\%',text).groups())
    check('Minimum median approximation percent',lo,100*p.median_relative_error.min(),.051,R/'proposition_summary.csv');check('Maximum median approximation percent',hi,100*p.median_relative_error.max(),.051,R/'proposition_summary.csv')
    worst=float(re.search(r'worst individual error is (\d+\.\d+)\\%',text).group(1));check('Maximum individual approximation percent',worst,100*pr.approx_relative_error.max(),.051,R/'proposition1_neural_validation.csv')
    # Categories recomputed from actual epsilon0 predictions, not the label CSV.
    classes=[]
    for file in sorted((OUT/'proposition_arrays').glob('*.npz')):
        with np.load(file) as f:
            v=f['predictions'][0].astype(float)
            for ci,ctx in enumerate(CONTEXTS[1:5],1):
                off=next(iter(set(REF)&set(ctx)));a0=v[0,REF.index(off)];b0=v[ci,ctx.index(off)];oa=(a0[:4]-a0[4:])/2;ob=(b0[:4]-b0[4:])/2;co=np.mean(oa*ob)/np.sqrt(np.mean(oa**2)*np.mean(ob**2));classes.append('aligned' if co>=.1 else ('opposing' if co<=-.1 else 'near'))
    for key,n in [('aligned',86),('near',10),('opposing',0)]:check('Final neural reference sensitivity '+key,n,classes.count(key),0,OUT/'new_array_bindings.json')
    # Ensure that the corrected endpoint contract is actually present in both text and caption.
    assert 'disjoint-pair mean error on IXI' in text
    assert 'disjoint-pair mean MAE on IXI' in (CV/'p17_control_table.tex').read_text(encoding='utf-8')
    assert 'No new scalar score' in text and 'worst individual error is' in text
    guard_negative()
    pd.DataFrame(checks).to_csv(OUT/'final_headline_checks.csv',index=False)
    old=pd.read_csv(OUT/'reproduction_initial_checks.csv');allchecks=pd.concat([old,pd.DataFrame(checks)],ignore_index=True);arrays=pd.concat([pd.read_csv(OUT/'array_checks_all.csv'),pd.read_csv(OUT/'new_array_reproduction_checks.csv')],ignore_index=True)
    assert (allchecks.status=='PASS').all() and (arrays.status=='PASS').all()
    lines=['# Clean-room reproduction check','','All historical and new headline checks below PASS. No manuscript summary CSV is used as a numerical input. The three new experiments and the principal historical control/influence/architecture results are independently recomputed from saved target/prediction/response arrays. The old guard negative statement is independently recomputed from the lowest preserved per-examination score records and frozen CDF/threshold parameters; this is explicitly not a full image-level guard replay. Old supplemental benchmark results are retained, not mislabeled as newly array-reproduced.','','The array audit has '+str(len(arrays))+' per-table/column checks. Historical maximum numerical difference is '+f"{pd.read_csv(OUT/'array_checks_all.csv').maximum_abs_difference.max():.3g}"+'; new maximum is '+f"{pd.read_csv(OUT/'new_array_reproduction_checks.csv').maximum_abs_difference.max():.3g}"+'. Absolute and relative tolerances, observation counts and source bindings are in the CSV/JSON audit. A field-name adaptation (historical target_z to z) was needed by the independent reproducer; it changed no experiment. The original failed run and completed rerun remain in this iteration history.','','The exact original/current protocol hashes remain immutable. The SAINT coordinate amendment was made before inference; the IXI fixed-ranking endpoint label was corrected after source audit without changing its numbers.','','## Every headline assertion','','| Headline | Reported | Recomputed | Difference | Tolerance | Result | Source SHA-256 |','|---|---:|---:|---:|---:|---|---|']
    for r in allchecks.itertuples():lines.append(f'| {r.headline} | {r.reported_value:.9g} | {r.recomputed_value:.9g} | {r.absolute_difference:.3g} | {r.tolerance:g} | {r.status} | `{r.source_hash}` |')
    lines += ['','## Array comparison details','','| Table | Field | Observations | Max absolute difference | Failed observations | Result |','|---|---|---:|---:|---:|---|']
    for r in arrays.itertuples():lines.append(f'| {r.table} | {r.column} | {r.observations} | {r.maximum_abs_difference:.3g} | {r.failed_observations} | {r.status} |')
    (P/'REPRODUCTION_CHECK.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print('Final headline assertions',len(checks),'plus historical',len(old),'all PASS',flush=True)
if __name__=='__main__':main()
