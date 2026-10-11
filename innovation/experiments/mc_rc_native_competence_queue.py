"""Wait for the already-running proof, then perform each new stage once."""
import json,os,subprocess,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_native_competence_queue'
PROOF=ROOT/'experiments/mc_rc_frozen_predicted_region_cpu/independent_observed_input_roi_and_model_replay.json'
def now(): return datetime.now(timezone.utc).isoformat()
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
 status=dict(started_utc=now(),complete=False,active_stage='waiting_existing_fifteen_replay_proof',stages=[],automatic_stage_retries=0)
 def save(): (OUT/'attempt_01.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 save();print(json.dumps(dict(active_stage=status['active_stage'],waiting_on_existing_session=29338)),flush=True)
 try:
  deadline=time.monotonic()+6*3600
  while not PROOF.exists():
   if time.monotonic()>deadline: raise TimeoutError('Existing proof not produced in six hours; no process restarted')
   time.sleep(15)
  proof=json.loads(PROOF.read_text(encoding='utf-8'))
  if proof['errors']: raise ValueError('Prerequisite replay failed; native study not started')
  for stage,script in [('native_diagnostic','mc_rc_native_competence_cpu.py'),('independent_native_replay','verify_mc_rc_native_competence_cpu.py')]:
   status['active_stage']=stage;save();log=OUT/(stage+'_attempt_01.log')
   with log.open('xb') as f: done=subprocess.run([sys.executable,'-B',str(ROOT/'experiments'/script)],cwd=ROOT.parent,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   row=dict(stage=stage,finished_utc=now(),returncode=done.returncode,log_file=log.relative_to(ROOT).as_posix());status['stages'].append(row);save();print(json.dumps(row),flush=True)
   if done.returncode: raise RuntimeError('Single attempt failed: '+stage)
  status.update(complete=True,active_stage='complete',finished_utc=now());save()
 except Exception as exc:
  status.update(active_stage='failed',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc(),finished_utc=now());save();print(json.dumps(dict(error=status['error'])),flush=True);return 1
 return 0
if __name__=='__main__': raise SystemExit(main())
