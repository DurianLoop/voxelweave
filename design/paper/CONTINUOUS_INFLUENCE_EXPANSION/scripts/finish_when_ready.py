from pathlib import Path
import json,subprocess,sys,time,datetime
P=Path(__file__).resolve().parents[1]
def status(name,**kwargs):
    (P/'DELIVERY_STATUS.json').write_text(json.dumps(dict(status=name,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),canonical_updated=False,**kwargs),indent=2),encoding='utf-8')
def call(script):
    with (P/f'logs/final_{script}.log').open('w',encoding='utf-8') as f:
        p=subprocess.run([sys.executable,'-B',str(P/f'scripts/{script}.py')],stdout=f,stderr=subprocess.STDOUT)
    return p.returncode
def main():
    while not (P/'outputs/analysis_complete.json').exists():
        call('status')
        failures=list((P/'logs').glob('failure_*.txt'))
        if failures:
            status('EXECUTION_NEEDS_ATTENTION',failure_logs=[x.name for x in failures],new_table_complete=False,latex_rebuilt=False,visual_review_complete=False)
            print('Inference failure recorded; preserve outputs and resume after review',flush=True);return
        time.sleep(30)
    # Run the final analysis source after the watcher has completed, including all
    # explicit positive/negative/undefined effect-status fields.
    for script in ['analyze','publish']:
        rc=call(script)
        if rc:status('POSTPROCESS_NEEDS_ATTENTION',script=script,returncode=rc,new_table_complete=script=='publish',latex_rebuilt=False,visual_review_complete=False);return
    rc=call('build')
    status('CANDIDATE_READY_FOR_VISUAL_REVIEW' if rc==0 else 'BUILD_NEEDS_ATTENTION',new_table_complete=True,latex_rebuilt=rc==0,visual_review_complete=False,build_returncode=rc)
    call('status')
    print('Scientific tables generated; review build and layout before canonical installation',flush=True)
if __name__=='__main__':main()
