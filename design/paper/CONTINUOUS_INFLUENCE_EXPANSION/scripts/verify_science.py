from adapters import *
from audit_statistics import simultaneous
import pandas as pd,datetime,argparse
def sources():
    count=0
    for r in read(P/'SOURCE_MANIFEST.json'):
        f=ROOT/r['path'];assert f.exists() and sha(f)==r['sha256'],f;count+=1
    for name,h in read(P/'OLD_OBSERVATION_MANIFEST.json').items():assert sha(ROOT/name)==h;count+=1
    # Full previous closure delivery, including its original raw-response arrays.
    previous=read(C/'DELIVERY_MANIFEST.json')
    for i,r in enumerate(previous['files']):
        f=C/r['path'];assert f.exists() and sha(f)==r['sha256'],f;count+=1
        if i%500==0:print('PREVIOUS DELIVERY PROTECTION',i,flush=True)
    f=read(P/'freeze.json');assert sha(P/'PROTOCOL.md')==f['protocol_sha256']
    assert sha(P/'model_registry.json')==f['registry_sha256']
    for name,h in f['inference_code'].items():assert sha(P/'scripts'/name)==h
    out=dict(status='PASS',files=count,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    write(P/'outputs/source_protection.json',out);print(out,flush=True)
def tables():
    assert read(P/'outputs/batch_repair_complete.json')['status']=='PASS'
    d=pd.read_csv(P/'CONTINUOUS_INFLUENCE_BIG_TABLE.csv');models=['linear','acvtt','resunet','smamba_unet','arssr','hat','swinir','saint']
    assert len(d)==26 and len(d[d.technical_status=='ELIGIBLE'])==16
    arrays=0;maxdiff=0.;bchecks=0
    for ds,n in [('fastmri',72),('ixi',345)]:
        for m in models:
            s=read(P/f'outputs/summary_{ds}_{m}.json');r=d[(d.model==m)&(d.dataset==ds)].iloc[0]
            assert s['threshold']==(.85 if m in ['hat','swinir'] else .90)
            assert s['stability_status']==r.stability
            for b in s['bootstrap_crosschecks']:assert b['error']<1e-10;bchecks+=1
            for ep in ['beyond_count','fixed_count']:
                q=next(x for x in s['endpoints'] if x['endpoint']==ep);assert np.isclose(q['estimate'],r[ep],atol=1e-14,equal_nan=True)
            if m in MODELS:
                paths=sorted((P/'outputs/responses').glob(f'{ds}_{m}_*.npz'));assert len(paths)==n
                assert s['checks']['arrays']==n and s['checks']['rows']==n*32
                maxdiff=max(maxdiff,s['checks']['maximum_influence_difference'])
                for path in paths:
                    meta=read(path.with_suffix('.json'));assert sha(path)==meta['sha256'];arrays+=1
            print('VERIFIED',ds,m,flush=True)
        for ep in ['beyond_count','fixed_count']:
            points=[d[(d.model==m)&(d.dataset==ds)][ep].iloc[0] for m in models]
            reps=np.column_stack([np.load(P/f'outputs/bootstrap_{ds}_{m}.npz')[ep] for m in models])
            ci,valid=simultaneous(points,reps);assert valid==5000
            for j,m in enumerate(models):
                r=d[(d.model==m)&(d.dataset==ds)].iloc[0]
                assert r[ep+'_family_n']==8 and r[ep+'_valid_draws']==5000
                assert np.allclose(ci[j],[r[ep+'_low'],r[ep+'_high']],atol=1e-12)
    assert arrays==2085
    # Previously observed scientific failures cannot be overwritten by the batch repair.
    old=pd.read_csv(P/'batch_repair_snapshot/CONTINUOUS_INFLUENCE_BIG_TABLE.csv')
    for _,r in old[old.technical_status=='ELIGIBLE'].iterrows():
        q=d[(d.model==r.model)&(d.dataset==r.dataset)].iloc[0]
        assert q.stability==r.stability
        for k in ['beyond_count','fixed_count','stability_half','stability_double','stability_negative']:assert abs(q[k]-r[k])<1e-14
    for ds,m in [('ixi','acvtt'),('fastmri','resunet'),('ixi','resunet')]:
        assert read(P/f'outputs/validation_{ds}_{m}.json')['status']=='FAIL'
        checks=read(P/f'outputs/validation_batch1_{ds}_{m}.json');assert checks['status']=='PASS'
        assert all(x['native_max_difference']<=1e-5 and x['repeat_batch_max_difference']<=1e-6 for x in checks['checks'])
    sec=pd.read_csv(P/'ALL_SECONDARY_SIGNS.csv');assert len(sec)==8*2*4*6
    out=dict(status='PASS',raw_response_files=arrays,observation_rows=arrays*32,table_rows=26,measured_strata=16,new_models=5,total_tested_models=8,secondary_rows=len(sec),independent_embedding_max_difference=maxdiff,explicit_cluster_bootstrap_checks=bchecks,joint_family_size=8,all_joint_valid_draws=5000,original_measured_strata_unchanged=13,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    write(P/'outputs/final_science_verification.json',out);print(out,flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--sources',action='store_true');args=ap.parse_args()
    sources() if args.sources else tables()
