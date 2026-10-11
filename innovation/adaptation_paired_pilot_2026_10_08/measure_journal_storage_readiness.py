"""Actual lossless journal compression; full-budget forecasts explicitly remain forecasts."""
import gzip,zlib,json,sys,hashlib,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    resource_guard();out=HERE/'journal_storage_attempt01';out.mkdir(exist_ok=False)
    fit=json.loads((HERE/'attempt01/receipt.json').read_text());assert fit['complete'] and not fit['errors']
    rows=[]
    for a in fit['arms']:
        p=ROOT/a['history_path'];assert sha(p)==a['history_sha256'];data=p.read_bytes()
        start=time.perf_counter();compressed=gzip.compress(data,compresslevel=6,mtime=0);elapsed=time.perf_counter()-start
        assert gzip.decompress(compressed)==data and zlib.decompress(compressed,wbits=31)==data
        parsed=[json.loads(line) for line in gzip.decompress(compressed).decode('utf-8').splitlines()]
        assert len(parsed)==99 and [r['step'] for r in parsed]==list(range(1,100))
        saved=out/(p.name+'.gz')
        with saved.open('xb') as f:f.write(compressed)
        rows.append(dict(branch=a['name'],source_file=p.relative_to(ROOT).as_posix(),source_sha256=sha(p),
            gzip_file=saved.relative_to(ROOT).as_posix(),gzip_sha256=sha(saved),actual_raw_bytes=len(data),actual_gzip_bytes=len(compressed),
            actual_compression_seconds=elapsed,independent_gzip_and_zlib_replay_exact=True,steps=99))
    res=resource_guard();weights=sum((ROOT/a['checkpoint_path']).stat().st_size for a in fit['arms'])
    logs=sum(r['actual_gzip_bytes'] for r in rows);forecast_logs=logs*202
    margin=res['workspace_free_bytes']-8_000_000_000;maxweight=max((ROOT/a['checkpoint_path']).stat().st_size for a in fit['arms'])
    # Existing same-capacity optimizer checkpoint bytes, not an actually saved new optimizer.
    old=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07';maxresume=max((old/(k+'_resume.pt')).stat().st_size for k in ('native_reference','raw_pchip'))
    guarded_forecast=int(forecast_logs*1.25)+weights+2_000_000
    modes=[dict(name='weights_only_no_optimizer_resume',forecast_peak_bytes=guarded_forecast+maxweight),
        dict(name='one_rolling_optimizer_with_atomic_replacement',forecast_peak_bytes=guarded_forecast+2*maxresume),
        dict(name='four_optimizer_resumes_with_atomic_replacement',forecast_peak_bytes=guarded_forecast+5*maxresume)]
    for m in modes:m['forecast_fits_current_margin']=m['forecast_peak_bytes']<=margin
    r=dict(complete=True,errors=[],actual_compression_records=rows,actual_four_final_checkpoint_bytes=weights,
        full_budget_updates_per_branch=19998,full_budget_branches=4,full_budget_journal_byte_forecast=forecast_logs,
        forecast_basis='99step actual journals scaled202, additional25percent allowance; not full19998step storage measurement',
        disk_above_reserve_bytes=margin,storage_modes=modes,
        CPU_full_budget_step_time_forecast_seconds=19998*sum(a['median_step_seconds'] for a in fit['arms']),
        forecast_excludes_cache_IO_eval_independent_replay_and_resume_restart=True,
        formal_full_training_launched=False,full_training_budget_frozen=False,publication_claim_confirmed=False,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [Path(__file__),HERE/'attempt01/receipt.json']],resources=res)
    with (out/'receipt.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in r.items() if k not in ['actual_compression_records','source_bindings']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
