"""Sequential GPU jobs after phase generation; checkpointed local execution."""
from common import *
import time,subprocess
guard()
while not (OUT/'phase_wrapper_verification.csv').exists():time.sleep(10)
for script in ['analyze_cross_arch.py','run_acquired_influence.py','analyze_acquired.py','run_proposition_validation.py']:
 log=P/'logs'/(Path(script).stem+'.log');print('START',script,flush=True)
 with log.open('w',encoding='utf-8') as f:
  proc=subprocess.run([sys.executable,'-B',str(P/'scripts'/script)],stdout=f,stderr=subprocess.STDOUT)
 if proc.returncode:raise SystemExit(f'{script} failed; inspect {log}')
 print('COMPLETE',script,flush=True)
