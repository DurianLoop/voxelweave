from setup import P,ROOT,S,sha,write
import json,datetime
rows=json.loads((S/'ARRAY_FREEZE_MANIFEST.json').read_text());fail=[]
for i,r in enumerate(rows,1):
 f=ROOT/r['path']
 if not f.exists() or sha(f)!=r['sha256']:fail.append(r['path'])
 if i%500==0:print('verified',i,'/',len(rows),flush=True)
write(P/'outputs/frozen_array_verification.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':len(rows),'failures':fail,'status':'PASS' if not fail else 'FAIL'})
assert not fail,fail
print('FROZEN ARRAY PASS',len(rows),flush=True)
