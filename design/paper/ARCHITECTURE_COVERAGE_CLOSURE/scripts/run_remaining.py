from pathlib import Path
import subprocess,sys,json,time
P=Path(__file__).resolve().parents[1]
def run(name):
 with (P/'logs'/f'{name}.log').open('wb') as f:
  r=subprocess.run([sys.executable,'-B',str(P/'scripts'/f'{name}.py')],stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode)
if __name__=='__main__':
 # Caller starts this only once core_acquired.py has completed successfully.
 run('analyze_core')
 run('expanded_phase')
