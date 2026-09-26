from common import *
import time,subprocess
while not (OUT/'proposition_summary.csv').exists():time.sleep(10)
with (P/'logs/regenerate_legacy_arrays.log').open('w',encoding='utf-8') as f:
 p=subprocess.run([sys.executable,'-B',str(P/'scripts/regenerate_legacy_arrays.py')],stdout=f,stderr=subprocess.STDOUT)
raise SystemExit(p.returncode)
