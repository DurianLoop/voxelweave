"""Aggregate locked IXI test-115 or NingXia eight held-out patient folds."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .common import write_json
from .run import SEEDS


def load_group(list_path):
    paths=[Path(x) for x in Path(list_path).read_text(encoding='utf-8-sig').splitlines() if x.strip()]
    frames=[]; records=[]
    for path in paths:
        m=json.loads((path/'evaluation_manifest.json').read_text(encoding='utf-8'))
        if m['split']!='test' or m['smoke'] or not m['lock_sha256'] or m['dataset']=='fastmri':
            raise ValueError('Only locked full external tests are accepted')
        df=pd.read_csv(path/'per_patient.csv')
        df['seed']=m['seed'];df['fold']=m['fold']
        frames.append(df);records.append(m)
    if len({m['dataset'] for m in records})!=1 or len({m['variant'] for m in records})!=1:
        raise ValueError('Mixed domains or variants')
    df=pd.concat(frames).set_index(['seed','patient_id']).sort_index()
    if df.index.has_duplicates or set(df.index.get_level_values('seed'))!=set(SEEDS):
        raise ValueError('Missing seeds or repeated test patient within seed')
    expected=8 if records[0]['dataset']=='ningxia' else 115
    for seed in SEEDS:
        if len(df.loc[seed])!=expected:
            raise ValueError(f'Expected {expected} test patients for each seed')
        if records[0]['dataset']=='ningxia' and set(df.loc[seed,'fold'])!=set(range(8)):
            raise ValueError('All eight held-out patient folds are required')
    return records,df


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--candidate-list',type=Path,required=True)
    p.add_argument('--parent-list',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    cm,c=load_group(a.candidate_list);bm,b=load_group(a.parent_list)
    if not c.index.equals(b.index) or not c.fold.equals(b.fold):
        raise ValueError('External patients/folds/seeds differ')
    if {x['lock_sha256'] for x in cm+bm}.__len__()!=1 or cm[0]['dataset']!=bm[0]['dataset']:
        raise ValueError('Lock or domain differs')
    if {(m['seed'],m['fold']):m['data_sha256'] for m in cm}!={(m['seed'],m['fold']):m['data_sha256'] for m in bm}:
        raise ValueError('External paired data manifests differ')
    if bm[0]['variant']!='control':
        raise ValueError('Matched control is required')
    n=len(c.loc[SEEDS[0]]);rng=np.random.default_rng(73019)
    sd=rng.integers(0,3,(10000,3));pd_=rng.integers(0,n,(10000,n))
    report={}
    for k in c.columns.drop('fold'):
        cv=np.stack([c.loc[s,k].to_numpy() for s in SEEDS])
        bv=np.stack([b.loc[s,k].to_numpy() for s in SEEDS]);d=cv-bv
        draws=d[sd[:,:,None],pd_[:,None,:]].mean((1,2))
        report[k]=dict(candidate_mean=float(cv.mean()),candidate_seed_std=float(cv.mean(1).std(ddof=1)),
                       parent_mean=float(bv.mean()),parent_seed_std=float(bv.mean(1).std(ddof=1)),
                       paired_delta=float(d.mean()),paired_ci95=np.quantile(draws,[.025,.975]).tolist(),
                       wins=int(((d.mean(0)<0) if k in ('mae','mse','hd95_proxy','tail10_mse') else (d.mean(0)>0)).sum()))
    write_json(a.out,dict(dataset=cm[0]['dataset'],seeds=list(SEEDS),patients=n,metrics=report,
        bootstrap='crossed seed/patient; 10000 resamples',
        no_post_test_tuning=True,anatomical_segmentation_metrics_available=False,
        statistical_limit='NingXia n=8; intervals ignore dependence from overlapping CV training sets'))


if __name__=='__main__':
    main()
