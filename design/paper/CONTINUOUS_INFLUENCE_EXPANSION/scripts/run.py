from adapters import *
import argparse,datetime,time,gc,traceback,shutil
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--models',nargs='+',choices=MODELS,required=True);args=ap.parse_args()
    freeze=read(P/'freeze.json');assert sha(P/'PROTOCOL.md')==freeze['protocol_sha256']
    for name,h in freeze['inference_code'].items():assert sha(P/'scripts'/name)==h,name
    torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    cases=read(B/'case_registry.json');dest=P/'outputs/responses';start=time.perf_counter()
    for m in args.models:
        for ds in ['fastmri','ixi']:
            net=load(ds,m);subset=[r for r in cases if r['dataset']==ds]
            validation=P/'outputs'/f'validation_{ds}_{m}.json'
            if validation.exists():assert read(validation)['status']=='PASS'
            else:
                r=subset[0];z=r['influence_targets'][0];checks=validate(net,m,B/'inputs'/f'{ds}_{r["case"]}_z{z}.npz',z)
                good=all(x['pass_check'] for x in checks);write(validation,dict(status='PASS' if good else 'FAIL',checks=checks,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
                if not good:print('INTERFACE FAIL',ds,m,flush=True);del net;continue
            for i,r in enumerate(subset,1):
                for z in r['influence_targets']:
                    out=dest/f'{ds}_{m}_{r["case"]}_z{z}.npz'
                    if out.exists() and out.with_suffix('.json').exists():
                        assert sha(out)==read(out.with_suffix('.json'))['sha256'];continue
                    assert shutil.disk_usage(P).free>15*1024**3,'RESOURCE STOP: preserve 15 GiB free disk'
                    inp=B/'inputs'/f'{ds}_{r["case"]}_z{z}.npz';d=compute(net,m,inp,z)
                    assert np.isfinite(d['base']).all() and np.isfinite(d['response']).all()
                    np.savez_compressed(out,**d)
                    write(out.with_suffix('.json'),dict(dataset=ds,model=m,case=r['case'],z=z,depth=r['depth'],sha256=sha(out),input_sha256=sha(inp),utc_before_target_access=datetime.datetime.now(datetime.timezone.utc).isoformat(),protocol_sha256=freeze['protocol_sha256'],adapter_sha256=freeze['inference_code']['adapters.py'],information_contract='acquired-only',threshold=.90))
                    print('TARGET',ds,m,i,z,'seconds',round(time.perf_counter()-start),flush=True)
                print('CASE',ds,m,i,'/',len(subset),flush=True)
            del net;gc.collect()
            if torch.cuda.is_available():torch.cuda.empty_cache()
    print('FINISHED',args.models,flush=True)
if __name__=='__main__':
    try:main()
    except Exception:
        f=P/'logs'/('failure_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.txt');f.write_text(traceback.format_exc(),encoding='utf-8');raise
