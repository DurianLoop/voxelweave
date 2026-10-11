"""One authorized CPU diagnostic after already-running native proof completes."""
import json,os,subprocess,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_anchor_qda_queue';NATIVE=ROOT/'experiments/mc_rc_native_competence_queue/attempt_01.json'
def now(): return datetime.now(timezone.utc).isoformat()
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);state=dict(started_utc=now(),complete=False,active_stage='waiting_existing_native16_queue',stages=[],automatic_retries=0)
 def save(): (OUT/'attempt_01.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 save();print(json.dumps(dict(active_stage=state['active_stage'],existing_native_session=80884)),flush=True)
 try:
  deadline=time.monotonic()+6*3600
  while True:
   native=json.loads(NATIVE.read_text(encoding='utf-8'))
   if native.get('active_stage')=='failed': raise ValueError('Existing native16 queue failed; new diagnostic stopped')
   if native['complete']: break
   if time.monotonic()>deadline: raise TimeoutError('Existing native16 not complete within six hours')
   time.sleep(15)
  for stage,script in [('native_complete_report','report_mc_rc_native_competence_cpu.py'),('anchor_qda_diagnostic','mc_rc_anchor_qda_cpu.py'),('independent_anchor_qda_replay','verify_mc_rc_anchor_qda_cpu.py')]:
   state['active_stage']=stage;save();log=OUT/(stage+'_attempt_01.log')
   with log.open('xb') as stream: done=subprocess.run([sys.executable,'-B',str(ROOT/'experiments'/script)],cwd=ROOT.parent,stdout=stream,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   row=dict(stage=stage,finished_utc=now(),returncode=done.returncode,log_file=log.relative_to(ROOT).as_posix());state['stages'].append(row);save();print(json.dumps(row),flush=True)
   if done.returncode: raise RuntimeError('Single stage failed: '+stage)
  state.update(complete=True,active_stage='complete',finished_utc=now());save()
 except Exception as exc: state.update(active_stage='failed',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc(),finished_utc=now());save();print(json.dumps(dict(error=state['error'])),flush=True);return 1
 return 0
if __name__=='__main__': raise SystemExit(main())
