"""Bounded decoded source reading, with literal numbered lines or paper block indices."""
import sys,gzip,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
mode=sys.argv[1];name=sys.argv[2];start=int(sys.argv[3]);stop=int(sys.argv[4])
p=(HERE/name).resolve();assert p.is_relative_to(HERE) and start>=0 and stop>=start
data=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
if mode=='lines':
    rows=data.decode('utf-8').splitlines();assert stop<=len(rows)
    for i in range(start,stop):print(str(i+1)+': '+rows[i])
elif mode=='blocks':
    rows=json.loads(data);assert stop<=len(rows)
    for b in rows[start:stop]:print(json.dumps(b,ensure_ascii=False))
else:raise ValueError(mode)
