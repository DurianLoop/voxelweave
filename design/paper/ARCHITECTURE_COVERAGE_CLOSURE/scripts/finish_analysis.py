from pathlib import Path
import subprocess,sys,json,time,datetime
P=Path(__file__).resolve().parents[1]
def main():
 # A background queue keeps dependent analyses strictly after complete inference.
 while True:
  f=P/'logs/expanded_phase_v2.log'
  if f.exists() and 'EXPANDED COMPLETE' in f.read_text(encoding='utf-8',errors='replace'):break
  time.sleep(5)
 assert len(list((P/'outputs/expanded_phase_arrays').glob('*.npz')))==1112
 assert json.loads((P/'outputs/expanded_failures_v2.json').read_text())==[]
 runs=[]
 for name in ['analyze_expanded','eligibility','revise_paper','reproduce_closure','verify_expanded']:
  start=datetime.datetime.now(datetime.timezone.utc).isoformat()
  with (P/'logs'/f'{name}.log').open('wb') as f:r=subprocess.run([sys.executable,'-B',str(P/'scripts'/f'{name}.py')],stdout=f,stderr=subprocess.STDOUT)
  runs.append(dict(script=name,returncode=r.returncode,start_utc=start,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
  (P/'outputs/analysis_run.json').write_text(json.dumps(runs,indent=2),encoding='utf-8');print(name,r.returncode,flush=True)
  assert r.returncode==0,(name,r.returncode)
if __name__=='__main__':main()
