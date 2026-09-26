from adapters import *
import adapters,datetime,time,gc,shutil
UNITS=[('ixi','acvtt'),('fastmri','resunet'),('ixi','resunet')]
original_normalized=adapters.normalized
def single(net,m,conds,ctx):return np.concatenate([original_normalized(net,m,[c],ctx) for c in conds],axis=0)
def main():
    binding=P/'batch_repair_freeze.json'
    if not binding.exists():
        for ds,m in UNITS:
            assert not list((P/'outputs/responses').glob(f'{ds}_{m}_*.npz'))
            assert read(P/f'outputs/validation_{ds}_{m}.json')['status']=='FAIL'
        snap=P/'batch_repair_snapshot';snap.mkdir(exist_ok=True)
        for f in [*P.glob('*.csv'),*P.glob('*.md'),P/'outputs/analysis_complete.json',P/'build_logs/build_audit.json']:
            if f.is_file():shutil.copy2(f,snap/f.name)
        write(binding,dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),addendum_sha256=sha(P/'BATCH_EXECUTION_ADDENDUM.md'),adapter_sha256=sha(P/'scripts/adapters.py'),units=UNITS))
    freeze=read(binding);assert freeze['script_sha256']==sha(Path(__file__)) and freeze['addendum_sha256']==sha(P/'BATCH_EXECUTION_ADDENDUM.md') and freeze['adapter_sha256']==sha(P/'scripts/adapters.py')
    adapters.normalized=single
    torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    cases=read(B/'case_registry.json');start=time.perf_counter()
    for ds,m in UNITS:
        net=load(ds,m);subset=[r for r in cases if r['dataset']==ds];r=subset[0];z=r['influence_targets'][0]
        checks=validate(net,m,B/'inputs'/f'{ds}_{r["case"]}_z{z}.npz',z);good=all(x['pass_check'] for x in checks)
        write(P/f'outputs/validation_batch1_{ds}_{m}.json',dict(status='PASS' if good else 'FAIL',checks=checks,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_batch4_failure_preserved=True))
        assert good,checks
        print('SINGLE-SAMPLE VALIDATED',ds,m,flush=True)
        for i,r in enumerate(subset,1):
            for z in r['influence_targets']:
                out=P/'outputs/responses'/f'{ds}_{m}_{r["case"]}_z{z}.npz'
                if out.exists() and out.with_suffix('.json').exists():assert sha(out)==read(out.with_suffix('.json'))['sha256'];continue
                assert shutil.disk_usage(P).free>15*1024**3
                inp=B/'inputs'/f'{ds}_{r["case"]}_z{z}.npz';d=compute(net,m,inp,z)
                assert np.isfinite(d['base']).all() and np.isfinite(d['response']).all()
                np.savez_compressed(out,**d)
                write(out.with_suffix('.json'),dict(dataset=ds,model=m,case=r['case'],z=z,depth=r['depth'],sha256=sha(out),input_sha256=sha(inp),utc_before_target_access=datetime.datetime.now(datetime.timezone.utc).isoformat(),protocol_sha256=sha(P/'PROTOCOL.md'),adapter_sha256=freeze['adapter_sha256'],repair_script_sha256=freeze['script_sha256'],information_contract='acquired-only',threshold=.90,batch_size=1))
            print('BATCH1',ds,m,i,'/',len(subset),'seconds',round(time.perf_counter()-start),flush=True)
        del net;gc.collect();torch.cuda.empty_cache()
        from analyze import process
        process(ds,m)
    from analyze import aggregate
    aggregate();write(P/'outputs/batch_repair_complete.json',dict(status='PASS',units=UNITS,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
if __name__=='__main__':main()
