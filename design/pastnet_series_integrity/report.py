import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from pastnet_v2.common import PACKAGE,sha256,write_json
from pastnet_v2.run import RECIPE
from .run import ROOT,code_hashes,original_code_hashes
from .prepare import MANIFEST,validation_hash
from .audit import SOURCE
from . import statistics

def native(x):
    if isinstance(x,dict):return {k:native(v) for k,v in x.items()}
    if isinstance(x,list):return [native(v) for v in x]
    return x.item() if isinstance(x,np.generic) else x
def load_run(path):
    path=Path(path);m=json.loads((path/'manifest.json').read_text());c=json.loads((path/'completion.json').read_text())
    if m['smoke'] or not c['completed'] or m['dataset']!='fastmri' or m['test_selected']:raise ValueError('Completed validation full required')
    if m['variant'] not in ('control','repair'):raise ValueError('Wrong variant')
    expected=original_code_hashes() if m['variant']=='control' else code_hashes()
    if m['code_hashes']!=expected or m['recipe']!=RECIPE:raise ValueError('Source/recipe mismatch')
    if sha256(path/'best.pth')!=c['best_sha256'] or sha256(m['data_manifest'])!=m['data_sha256']:raise ValueError('Weights/data changed')
    data=json.loads(Path(m['data_manifest']).read_text(encoding='utf-8'))
    reference=json.loads(SOURCE.read_text(encoding='utf-8'))
    # Pair by identical validation records only; preserve actual, different train hashes.
    m['validation_sha256']=validation_hash(data)
    if m['validation_sha256']!=validation_hash(reference):raise ValueError('Validation data changed')
    if m['variant']=='repair' and m['data_sha256']!=sha256(MANIFEST):raise ValueError('Unregistered training repair')
    ids={str(r['patient_id']) for r in data['records'] if r['split']=='val'}
    p=pd.read_csv(path/'validation/per_patient.csv',dtype={'patient_id':str}).set_index('patient_id').sort_index()
    if p.index.has_duplicates or set(p.index)!=ids or not np.isfinite(p.to_numpy()).all():raise ValueError('Invalid patient data')
    return m,p
def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,nargs='+',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    seeds=[];contracts=[]
    for path in a.candidate:
        m,_=load_run(path)
        if m['variant']!='repair':raise ValueError('Expected repair')
        seeds.append(m['seed']);contracts.append(dict(run=str(path),training_manifest_sha256=m['data_sha256'],validation_sha256=m['validation_sha256'],train_intervals=m['train_intervals']))
    parents=[PACKAGE/'runs'/f'full_control_seed{s}_vram20' for s in seeds]
    for path in parents:
        m,_=load_run(path);contracts.append(dict(run=str(path),training_manifest_sha256=m['data_sha256'],validation_sha256=m['validation_sha256'],train_intervals=m['train_intervals']))
    statistics.load_run=load_run
    result=native(statistics.paired_report(a.candidate,parents,.10))
    result['guards']['tail10']=result['metrics']['tail10_mse']['delta']<=0
    result['promoted']=bool(all(result['guards'].values()));result['final_candidate']=False
    result.update(data_contracts=contracts,comparison='Training-series repair; identical validation, seed, G086 initialization and recipe; training manifests/counts differ; NOT architecture ablation',
        repair_validity_is_independent_of_score=True)
    write_json(a.out,result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
