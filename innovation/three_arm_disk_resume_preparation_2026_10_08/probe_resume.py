"""Read actual disk bindings with no neural imports; expected fault rejects exit 3."""
import argparse,sys,time
import disk_resume_core as core

def main():
    sys.stdout.reconfigure(encoding='utf-8'); ap=argparse.ArgumentParser()
    for key in ('metadata','metadata-sha','arm','plan','output'): ap.add_argument('--'+key,required=True)
    a=ap.parse_args(); start=time.perf_counter()
    r=dict(created_utc=core.now(),complete=True,accepted=False,errors=[],neural_modules_imported=False,
           CUDA_initialized=False,medical_arrays_loaded=0,checkpoint_arrays_loaded=0,neural_forwards=0)
    try:
        core.guard(start,60); core.verify_resume(a.metadata,a.metadata_sha,a.arm,a.plan); r['accepted']=True
    except (AssertionError,OSError,ValueError,KeyError) as e: r['rejection_reason']=f'{type(e).__name__}: {e}'
    r.update(torch_in_sys_modules='torch' in sys.modules,numpy_in_sys_modules='numpy' in sys.modules)
    assert not r['torch_in_sys_modules'] and not r['numpy_in_sys_modules']
    core.new_json(a.output,r); print(core.json.dumps(r),flush=True)
    return 0 if r['accepted'] else 3
if __name__=='__main__': raise SystemExit(main())
