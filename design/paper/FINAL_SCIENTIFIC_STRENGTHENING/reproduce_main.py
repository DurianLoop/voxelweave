"""One-command CPU reproduction from the retained arrays; no new inference."""
from pathlib import Path
import subprocess,sys,json,datetime
P=Path(__file__).resolve().parent
steps=['reproduce_arrays.py','reproduce_new.py','reproduce_main.py','build_report_cards.py','final_figures.py','assert_final_headlines.py']
result=[]
for name in steps:
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    print('REPRODUCTION STEP',name,flush=True)
    with (P/'logs'/('replay_'+name+'.log')).open('w',encoding='utf-8') as log:
        run=subprocess.run([sys.executable,'-B',str(P/'scripts'/name)],cwd=P,stdout=log,stderr=subprocess.STDOUT)
    result.append({'script':name,'started_utc':start,'returncode':run.returncode})
    (P/'outputs/reproduction_run.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    if run.returncode:raise SystemExit('Reproduction failed: '+name+'; inspect its log. No manuscript is installed.')
print('Complete: arrays, historical/new statistics, report cards, figures and final LaTeX assertions.',flush=True)
