from pathlib import Path
import os,sys,json,hashlib,datetime,importlib.util
os.environ.setdefault('OMP_NUM_THREADS','2');os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import numpy as np,pandas as pd
PATCH=Path(__file__).resolve().parents[1];P=PATCH.parent/'FINAL_SCIENTIFIC_STRENGTHENING';PAPER=P.parent;ROOT=PAPER.parents[1];BASEOUT=P/'outputs';OUT=PATCH/'outputs'
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'pre'),str(ROOT/'design'),str(ROOT)]
MODELS=['hat','swinir','i3net','saint','cycleinr'];REF=(-2,2);CONTEXTS=[REF,(-2,1),(-2,3),(-1,2),(-3,2),(-1,1),(-1,3),(-3,1),(-3,3)];SEEDS=(6101,6102,6103,6104)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def guard():
 d=read(P/'execution_freeze.json');assert d['protocol_sha256']==sha(P/'FINAL_ITERATION_PROTOCOL.md')
 for n,h in read(P/'freeze.json')['artifacts'].items():
  if n=='FINAL_ITERATION_PROTOCOL.md':assert sha(P/'FINAL_ITERATION_PROTOCOL_V1.md')==h
  else:assert sha(P/n)==h,n
def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def wrappers():
 p9=load_module('p18_legacy_p9',PAPER/'ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/scripts/p9_disjoint_shared.py')
 p11=load_module('p18_legacy_p11',PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/scripts/p11_ixi_five_arch_clean.py')
 for m in [p9,p11]:m.ROOT=ROOT
 for r in read(P/'model_registry.json'):
  m=p9 if r['dataset']=='fastmri' else p11
  m.MODEL_SPECS[r['model']]['checkpoint']=ROOT/r['checkpoint'];m.MODEL_SPECS[r['model']]['stored']=ROOT/r['stored_predictions']
 return p9,p11
def load_net(ds,name):
 p9,p11=wrappers();return (p9 if ds=='fastmri' else p11).load_interpolator(name,'cuda')
def metrics(a,b,y,mask):
 ea=np.asarray(a,float)[mask]-np.asarray(y,float)[mask];eb=np.asarray(b,float)[mask]-np.asarray(y,float)[mask];dd=ea-eb
 na=ea@ea;nb=eb@eb;T=.5*(na+nb)
 return {'observable':float(.25*(dd@dd)/T) if T>0 else np.nan,'alignment':float(ea@eb/np.sqrt(na*nb)) if na*nb>0 else np.nan,'disagreement':float(abs(dd).mean()),'reference_error':float(abs(ea).mean()),'companion_error':float(abs(eb).mean()),'paired_error':float(.5*(abs(ea).mean()+abs(eb).mean()))}
def log_event(name,payload):
 with (P/'logs/events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':name,**payload},ensure_ascii=False)+'\n')
