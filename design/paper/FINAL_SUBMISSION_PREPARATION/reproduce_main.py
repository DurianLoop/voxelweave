"""Full array-to-paper reproduction, CPU only, no model inference."""
from pathlib import Path
import subprocess,sys,json,datetime
P=Path(__file__).resolve().parent
steps=['reproduce_arrays.py','reproduce_new.py','reproduce_main.py']
if '--complete' in sys.argv:steps+=['reproduce_sensitivity.py','paper_assets.py','assert_submission.py']
results=[]
for name in steps:
 print('START',name,flush=True);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (P/'logs'/('reproduce_'+name+'.log')).open('wb') as f:r=subprocess.run([sys.executable,'-B',str(P/'scripts'/name)],stdout=f,stderr=subprocess.STDOUT)
 results.append(dict(script=name,started=start,finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),returncode=r.returncode));(P/'outputs/reproduction_run.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 print('END',name,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
