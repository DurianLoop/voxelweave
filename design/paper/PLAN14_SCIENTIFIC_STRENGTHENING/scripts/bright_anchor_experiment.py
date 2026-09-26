"""One post-E02, fixed-threshold acquired-bright-support hypothesis. No tuning."""
from pathlib import Path
import json,time,hashlib
import numpy as np
import pandas as pd
import nibabel as nib
from topcow_experiment import interpolate,fg
from stat_utils import corr,ci,naurc
P14=Path(__file__).resolve().parents[1]; ROOT=P14.parents[2]; OUT=P14/'outputs'
def bright_mask(anchor):
    absolute=abs(anchor); fore=fg(anchor)
    threshold=float(np.quantile(absolute[fore],.95))
    return fore&(absolute>=threshold)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    q=pd.read_csv(OUT/'external_data_qualification.csv',dtype={'case':str});q=q[q.dataset.eq('topcow_mr')]
    oldp=pd.read_csv(OUT/'topcow_per_plane.csv',dtype={'case':str}); per=P14/'bright_records';per.mkdir(exist_ok=True)
    start=time.perf_counter()
    for i,r in enumerate(q.itertuples(),1):
        dst=per/(r.case+'.csv')
        if dst.exists(): continue
        v=nib.load(ROOT/r.path).get_fdata(dtype=np.float32);lab=np.asarray(nib.load(ROOT/r.label_path).dataobj)
        masks={z:bright_mask(v[:,:,z]) for z in range(0,v.shape[2],4)}
        zs=sorted(oldp.loc[oldp.case.eq(r.case),'z'].unique());rows=[]
        for z in zs:
            left=(z//4)*4;mask=masks[left]|masks[left+4]; assert mask.any()
            l0=interpolate(v,z,4,0,'linear');c0=interpolate(v,z,4,0,'cubic')
            l2=interpolate(v,z,4,2,'linear');c2=interpolate(v,z,4,2,'cubic')
            vessel=lab[:,:,z]>0
            for tag,a,b in [('LC_shared',l0,c0),('LC_disjoint',l0,c2),('CL_shared',c0,l0),('CL_disjoint',c0,l2)]:
                pair,condition=tag.split('_');rows.append({'case':r.case,'z':z,'residue':z%4,'pair':pair,'condition':condition,
                    'bright_disagreement':float(np.mean(abs(a-b)[mask],dtype=np.float64)),'mask_pixels':int(mask.sum()),'vessel_pixels':int(vessel.sum()),'vessel_pixels_covered':int((mask&vessel).sum())})
        pd.DataFrame(rows).to_csv(dst,index=False)
        print(f'Bright support {i}/125 {r.case} elapsed={time.perf_counter()-start:.1f}s',flush=True)
    p=pd.concat([pd.read_csv(per/(str(c)+'.csv'),dtype={'case':str}) for c in q.case],ignore_index=True)
    p.to_csv(OUT/'bright_anchor_per_plane.csv',index=False)
    g=p.groupby(['case','pair','condition','residue']).bright_disagreement.mean().groupby(['case','pair','condition']).mean().reset_index()
    old=pd.read_csv(OUT/'topcow_per_case.csv',dtype={'case':str}); old=old[old['mask'].eq('acquired')]
    g=g.merge(old,on=['case','pair','condition'],validate='one_to_one');g.to_csv(OUT/'bright_anchor_per_case.csv',index=False)
    cases=sorted(g.case.unique());idx=np.random.default_rng(20260909).integers(0,125,(10000,125));rows=[]
    for context in ['shared','disjoint']:
        points=[];reps=[];vesselrows=[]
        for pair,model in [('LC','linear'),('CL','cubic')]:
            a=g[g.pair.eq(pair)&g.condition.eq(context)].set_index('case').loc[cases]
            x=a.bright_disagreement.to_numpy();baseline=a.disagreement.to_numpy()
            for endpoint in ['error','vessel_error']:
                y=a[model+'_'+endpoint].to_numpy();raw=corr(x[idx],y[idx]);rd=raw-corr(baseline[idx],y[idx]);risk=naurc(y[idx],x[idx])-naurc(y[idx],baseline[idx])
                row={'pair':pair,'condition':context,'endpoint':endpoint,'baseline_rho':float(corr(baseline,y)),'bright_rho':float(corr(x,y)),
                     'bright_ci_low':ci(raw)[0],'bright_ci_high':ci(raw)[1],'delta_rho':float(corr(x,y)-corr(baseline,y)),'delta_ci_low':ci(rd)[0],'delta_ci_high':ci(rd)[1],
                     'baseline_naurc':float(naurc(y,baseline)),'bright_naurc':float(naurc(y,x)),'delta_naurc':float(naurc(y,x)-naurc(y,baseline)),'risk_delta_ci_low':ci(risk)[0],'risk_delta_ci_high':ci(risk)[1]}
                rows.append(row)
                if endpoint=='vessel_error':points.append(row['delta_rho']);reps.append(rd);vesselrows.append(len(rows)-1)
        points=np.array(points);reps=np.stack(reps,axis=1);sd=reps.std(0,ddof=1);critical=np.quantile(np.max(abs((reps-points)/sd),axis=1),.95)
        for j,k in enumerate(vesselrows):rows[k].update(simultaneous_low=float(points[j]-critical*sd[j]),simultaneous_high=float(points[j]+critical*sd[j]))
    pd.DataFrame(rows).to_csv(OUT/'bright_anchor_rankings.csv',index=False)
    cov=p[p.pair.eq('LC')&p.condition.eq('shared')].groupby('case')[['vessel_pixels','vessel_pixels_covered','mask_pixels']].sum()
    cov['vessel_coverage']=cov.vessel_pixels_covered/cov.vessel_pixels;cov.to_csv(OUT/'bright_anchor_coverage.csv')
    (OUT/'bright_anchor_manifest.json').write_text(json.dumps({'status':'COMPLETE POST-E02 EXPLORATORY','cases':125,'threshold_percentile':95,'threshold_searched':False,'bootstrap':10000,'seed':20260909,
        'protocol_sha256':sha(P14/'PROTOCOL.md'),'script_sha256':sha(Path(__file__)),'vessel_coverage_median':float(cov.vessel_coverage.median()),'outcome_origin':'hypothesis motivated after E02 on same cases; not independent confirmation'},indent=2))
    print(pd.DataFrame(rows).to_string(index=False));print('BRIGHT COMPLETE',flush=True)
if __name__=='__main__':main()
