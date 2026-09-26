import json
from pathlib import Path
import numpy as np
from pastnet_v2.common import sha256
from pastnet_v2.run import SEEDS
LOWER_BETTER={'mae','mse','hd95_proxy','tail10_mse'}

def paired_report(candidates,parents,threshold):
    if len(candidates)!=len(parents) or len(candidates) not in (1,3):
        raise ValueError('Require one or three paired seeds')
    manifests=[]; parent_manifests=[]; values=[]; baselines=[]; efficiency=[]
    patient_ids=None
    for cp,bp in zip(candidates,parents):
        cm,c=load_run(cp); bm,b=load_run(bp)
        if cm['seed']!=bm['seed'] or cm['validation_sha256']!=bm['validation_sha256'] or cm['init_sha256']!=bm['init_sha256']:
            raise ValueError('Unmatched seed/data/initialization')
        if not c.index.equals(b.index) or (patient_ids is not None and list(c.index)!=patient_ids):
            raise ValueError('Patient sets differ; never silently inner-join')
        patient_ids=list(c.index); manifests.append(cm); parent_manifests.append(bm)
        values.append(c-b); baselines.append(b)
        ce=json.loads((Path(cp)/'efficiency.json').read_text(encoding='utf-8'))
        be=json.loads((Path(bp)/'efficiency.json').read_text(encoding='utf-8'))
        if ce['contract']!=be['contract'] or ce['device']!=be['device']:
            raise ValueError('Efficiency protocols differ')
        efficiency.append(dict(latency_ratio=ce['latency_ms_interval_median']/be['latency_ms_interval_median'],
                               memory_ratio=ce['peak_forward_gib']/be['peak_forward_gib']))
    seeds=[m['seed'] for m in manifests]
    if len({m['variant'] for m in manifests})!=1 or len({m['variant'] for m in parent_manifests})!=1:
        raise ValueError('Mixed variants across seeds')
    if len(set(seeds))!=len(seeds):
        raise ValueError('Repeated seed is not a replicate')
    if len(seeds)==3 and set(seeds)!=set(SEEDS):
        raise ValueError('Final seeds differ from preregistration')
    rng=np.random.default_rng(73019)
    n=len(patient_ids); s=len(values)
    seed_draw=rng.integers(0,s,(10000,s))
    patient_draw=rng.integers(0,n,(10000,n))
    metrics={}
    for column in values[0].columns:
        matrix=np.stack([v[column].to_numpy() for v in values])
        draws=matrix[seed_draw[:,:,None],patient_draw[:,None,:]].mean((1,2))
        means=matrix.mean(1)
        metrics[column]=dict(delta=float(matrix.mean()),ci95=np.quantile(draws,[.025,.975]).tolist(),
            seed_delta_means=means.tolist(),seed_delta_std=float(means.std(ddof=1)) if s>1 else None,
            patient_wins=int(((matrix.mean(0)<0) if column in LOWER_BETTER else (matrix.mean(0)>0)).sum()),
            candidate_seed_means=[float((b[column]+v[column]).mean()) for b,v in zip(baselines,values)],
            parent_seed_means=[float(b[column].mean()) for b in baselines])
    base_psnr=np.stack([b.psnr.to_numpy() for b in baselines]).mean(0)
    hard=np.argsort(base_psnr)[:max(1,int(np.ceil(n*.25)))]
    hard_delta=float(np.stack([v.psnr.to_numpy() for v in values]).mean(0)[hard].mean())
    guards={
        'effect':metrics['psnr']['delta']>=threshold,
        'paired_ci':metrics['psnr']['ci95'][0]>0,
        'wins':metrics['psnr']['patient_wins']>=np.ceil(.6*n),
        'hard_quartile':hard_delta>=0,
        'quality':all(metrics[k]['delta']<=1e-8 if k in LOWER_BETTER else metrics[k]['delta']>=-1e-8
                      for k in ('ssim','mae','mse','ncc','dice_proxy','hd95_proxy')),
        'latency':max(e['latency_ratio'] for e in efficiency)<=1.5,
        'memory':max(e['memory_ratio'] for e in efficiency)<=1.5,
    }
    return dict(variant=manifests[0]['variant'],seeds=seeds,patients=n,threshold_db=threshold,
        bootstrap='10000 crossed seed and patient resamples; common patient resample across seeds',
        metrics=metrics,hard_quartile_psnr_delta=hard_delta,efficiency=efficiency,
        guards=guards,promoted=all(guards.values()),
        failed_patients=[patient_ids[i] for i,x in enumerate(np.stack([v.psnr.to_numpy() for v in values]).mean(0)) if x<=0],
        candidate_runs={str(Path(p).resolve()):sha256(Path(p)/'best.pth') for p in candidates},
        parent_runs={str(Path(p).resolve()):sha256(Path(p)/'best.pth') for p in parents})

