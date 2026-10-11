"""Only follow an existing original queue; never start or repeat inference."""
import hashlib,json,os,subprocess,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/vs_seg_selection_after_complete_queue';ORIGINAL=ROOT/'experiments/vs_seg_full_volume_queue/attempt_01.json'
def now(): return datetime.now(timezone.utc).isoformat()
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);scripts=['vs_seg_selection_sensitivity.py','verify_vs_seg_selection_real_cpu.py'];files=[ROOT/'experiments'/s for s in scripts]+[Path(__file__),ROOT/'VS_SEG_SELECTION_REAL_REPLAY_PLAN_2026-10-03.md'];status=dict(started_utc=now(),complete=False,active_stage='waiting_existing_original_queue',original_session=83910,automatic_retries=0,stages=[],files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files])
 def save(): (OUT/'attempt_01.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 save();print(json.dumps(dict(active_stage=status['active_stage'],original_session=83910)),flush=True)
 try:
  deadline=time.monotonic()+6*3600
  while True:
   state=json.loads(ORIGINAL.read_text(encoding='utf-8'))
   if state.get('active_stage')=='failed' or state.get('error'): raise ValueError('Original queue failed; downstream stops without restarting it')
   if state.get('complete') and state.get('active_stage')=='complete': break
   if time.monotonic()>deadline: raise TimeoutError('Existing original queue not complete within six hours')
   time.sleep(15)
  for item in status['files']:
   if hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()!=item['sha256']: raise ValueError('Frozen followup mutated')
  for script in scripts:
   stage=Path(script).stem;status['active_stage']=stage;save();log=OUT/(stage+'_attempt_01.log')
   with log.open('xb') as stream: run=subprocess.run([sys.executable,'-B',str(ROOT/'experiments'/script)],cwd=ROOT.parent,stdout=stream,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   status['stages'].append(dict(stage=stage,returncode=run.returncode,log_file=log.relative_to(ROOT).as_posix(),finished_utc=now()));save();print(json.dumps(status['stages'][-1]),flush=True)
   if run.returncode: raise RuntimeError('Single followup stage failed: '+stage)
  status.update(complete=True,active_stage='complete',finished_utc=now());save()
 except Exception as exc: status.update(active_stage='failed',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc(),finished_utc=now());save();print(json.dumps(dict(error=status['error'])),flush=True);return 1
 return 0
if __name__=='__main__': raise SystemExit(main())
