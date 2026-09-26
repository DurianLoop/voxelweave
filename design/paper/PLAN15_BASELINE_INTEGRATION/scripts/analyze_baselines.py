"""Verify native metrics and use every declared extended-budget experiment."""
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
P=Path(__file__).resolve().parents[1];ROOT=P.parent.parents[1];OUT=P/'outputs';MET=['psnr','ssim','mae','mse','ncc']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=pd.read_csv(OUT/'master_provenance_audit.csv');recovered=pd.read_csv(OUT/'saint_recovered_summary.csv')
for idx,row in a[a.status=='UNMATCHED'].iterrows():
    r=recovered[(recovered.dataset==row.dataset)&(recovered.model==row.model)&(recovered.scale==row.scale)].iloc[0]
    assert max(abs(row[m]-r[m]) for m in MET)<.000051
    a.loc[idx,'status']='RECOVERED_FROM_PREDICTIONS';a.loc[idx,'source_paths']='[]';a.loc[idx,'units']=24
    a.loc[idx,'max_rounding_difference']=max(abs(row[m]-r[m]) for m in MET)
    for m in MET:a.loc[idx,'source_'+m]=r[m]
assert len(a)==111 and not a.status.eq('UNMATCHED').any()
a.to_csv(OUT/'baseline_all_verified.csv',index=False)
case_rows=[];input_records=[];checks=[]
for row in a.itertuples():
    native=[]
    if row.status=='RECOVERED_FROM_PREDICTIONS':
        native=pd.read_csv(OUT/'saint_recovered_per_case.csv');native=native[native.scale==row.scale].copy();native['fold']=''
    else:
        for path in json.loads(row.source_paths):
            file=ROOT/Path(path).parent/'per_case_metrics.csv';assert file.exists(),file
            input_records.append({'path':str(file.relative_to(ROOT)),'sha256':sha(file)})
            g=pd.read_csv(file);g['method']=g.method.replace({'smamba':'smamba_unet','gan':'gan_2p5d','saint_residual':'saint'})
            g=g[g.method.eq(row.model)].copy();assert len(g)>0,(file,row.model)
            g['fold']=next((x for x in file.parts if x.startswith('fold_')),'')
            native.append(g)
        native=pd.concat(native,ignore_index=True)
    assert not native.duplicated(['fold','case']).any()
    values=native.groupby('fold')[MET].mean().mean() if row.dataset=='NingXia' else native[MET].mean()
    discrepancy=max(abs(values[m]-getattr(row,'source_'+m)) for m in MET)
    assert discrepancy<1e-8,(row.row_id,discrepancy)
    checks.append({'row_id':row.row_id,'series':len(native),'units':int(row.units),'max_summary_reproduction_error':discrepancy})
    for _,r in native.iterrows():
        case_rows.append(dict(row_id=row.row_id,dataset=row.dataset,model=row.model,scale=row.scale,budget=row.budget,case=r['case'],fold=r['fold'],generated_slices=int(r['generated_slices']),**{m:r[m] for m in MET}))
c=pd.DataFrame(case_rows);c.to_csv(OUT/'all_baseline_per_case.csv',index=False)
from scipy.stats import spearmanr
from itertools import combinations
correlations=[];breadth=[]
for ds,g in c[c.budget.eq('master')&c.scale.eq(4)].groupby('dataset'):
    unit='fold' if ds=='NingXia' else 'case'
    pivot=g.groupby([unit,'model']).mae.mean().unstack('model');assert pivot.shape[1]==13 and pivot.notna().all().all()
    for left,right in combinations(pivot.columns,2):correlations.append({'dataset':ds,'model_a':left,'model_b':right,'rho':float(spearmanr(pivot[left],pivot[right]).statistic),'units':len(pivot)})
    corr=[r['rho'] for r in correlations if r['dataset']==ds]
    breadth.append({'dataset':ds,'models':13,'pairs':len(corr),'median_case_error_rho':float(np.median(corr)),'min_case_error_rho':min(corr),'max_case_error_rho':max(corr)})
pd.DataFrame(correlations).to_csv(OUT/'all13_error_dependence_pairs.csv',index=False)
pd.DataFrame(breadth).to_csv(OUT/'all13_error_dependence_summary.csv',index=False)
# Target-count contracts: record when equal case IDs hide unequal generated support.
support=[]
for (ds,scale),g in c[c.budget.eq('master')].groupby(['dataset','scale']):
    pairs=g.groupby(['case','fold']).generated_slices.nunique()
    support.append({'dataset':ds,'scale':int(scale),'cases':len(pairs),'cases_with_unequal_model_target_counts':int(pairs.gt(1).sum()),'min_count':int(g.generated_slices.min()),'max_count':int(g.generated_slices.max())})
pd.DataFrame(support).to_csv(OUT/'target_support_audit.csv',index=False)
rng=np.random.default_rng(20260910);boot={8:rng.integers(0,8,(10000,8)),24:rng.integers(0,24,(10000,24))};result=[];mae_draws=[];points=[]
for row in a[~a.budget.eq('master')].itertuples():
    base=a[(a.dataset==row.dataset)&(a.model==row.model)&(a.scale==row.scale)&(a.budget=='master')].iloc[0]
    old=c[c.row_id.eq(base.row_id)].copy();new=c[c.row_id.eq(row.row_id)].copy()
    assert set(zip(old.fold,old['case']))==set(zip(new.fold,new['case']))
    old=old.set_index(['fold','case']).sort_index();new=new.set_index(['fold','case']).sort_index()
    assert np.array_equal(old.generated_slices,new.generated_slices)
    unit='fold' if row.dataset=='NingXia' else 'case'
    d=(new[MET]-old[MET]).groupby(level=unit).mean();idx=boot[len(d)];draw=d.to_numpy()[idx].mean(axis=1)
    rec={'row_id':row.row_id,'dataset':row.dataset,'model':row.model,'scale':row.scale,'budget':row.budget,'units':len(d)}
    for j,m in enumerate(MET):
        rec[m+'_delta']=float(d[m].mean());rec[m+'_ci_low'],rec[m+'_ci_high']=np.quantile(draw[:,j],[.025,.975])
        rec[m+'_standard']=float(old[m].groupby(level=unit).mean().mean());rec[m+'_extended']=float(new[m].groupby(level=unit).mean().mean())
    result.append(rec);mae_draws.append(-draw[:,2]);points.append(-rec['mae_delta'])
draw=np.stack(mae_draws,axis=1);points=np.array(points);sd=draw.std(0,ddof=1)
assert (sd>0).all();crit=np.quantile(np.max(abs((draw-points)/sd),axis=1),.95)
for j,r in enumerate(result):r['mae_gain']=float(points[j]);r['mae_gain_sim_low']=float(points[j]-crit*sd[j]);r['mae_gain_sim_high']=float(points[j]+crit*sd[j])
res=pd.DataFrame(result);assert len(res)==20;res.to_csv(OUT/'training_budget_paired.csv',index=False)
(OUT/'analysis_manifest.json').write_text(json.dumps({'status':'PASS','master_rows':len(a),'master_metric_cells':len(a)*5,'native_case_rows':len(c),'per_row_checks':checks,'per_case_source_files':input_records,'bootstrap':10000,'seed':20260910,'simultaneous_family':'all 20 extended-budget comparisons; primary MAE only','script_sha256':sha(Path(__file__)),'protocol_sha256':sha(P/'PROTOCOL.md')},indent=2))
print(pd.DataFrame(support).to_string(index=False));print(res[['dataset','model','scale','budget','mae_gain','mae_gain_sim_low','mae_gain_sim_high']].to_string(index=False))
