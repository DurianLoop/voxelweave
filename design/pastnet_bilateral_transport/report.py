import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np
import pastnet_v2.report as statistics
from pastnet_v2.common import PACKAGE,sha256,write_json
from pastnet_v2.run import RECIPE
from .run import code_hashes,repair_code_hashes


def native(x):
    if isinstance(x,dict):return {k:native(v) for k,v in x.items()}
    if isinstance(x,list):return [native(v) for v in x]
    return x.item() if isinstance(x,np.generic) else x


def load_run(path):
    path=Path(path);m=json.loads((path/'manifest.json').read_text(encoding='utf-8'));c=json.loads((path/'completion.json').read_text(encoding='utf-8'))
    if m['smoke'] or not c['completed'] or m['dataset']!='fastmri' or m['test_selected']:raise ValueError('Completed fastMRI validation full required')
    if m['variant'] not in ('repair','bilateral','stationary'):raise ValueError('Wrong experiment')
    expected=repair_code_hashes() if m['variant']=='repair' else code_hashes()
    if m['code_hashes']!=expected or m['recipe']!=RECIPE:raise ValueError('Code / recipe mismatch')
    if sha256(path/'best.pth')!=c['best_sha256'] or sha256(m['data_manifest'])!=m['data_sha256']:raise ValueError('Checkpoint / data changed')
    data=json.loads(Path(m['data_manifest']).read_text(encoding='utf-8'))
    ids={str(r['patient_id']) for r in data['records'] if r['split']=='val'}
    p=pd.read_csv(path/'validation/per_patient.csv',dtype={'patient_id':str}).set_index('patient_id').sort_index()
    if p.index.has_duplicates or set(p.index)!=ids or not np.isfinite(p.to_numpy()).all():raise ValueError('Invalid patient table')
    return m,p


def control(seed):return PACKAGE.parent/'pastnet_series_integrity/runs'/f'full_repair_seed{seed}_vram20'


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,nargs='+',required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--stationary-parent',type=Path,nargs='+');a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    statistics.load_run=load_run;seeds=[]
    for path in a.candidate:
        m,_=load_run(path)
        if m['variant']!='bilateral':raise ValueError('Expected bilateral')
        seeds.append(m['seed'])
    result=native(statistics.paired_report(a.candidate,a.stationary_parent or [control(s) for s in seeds],.03 if a.stationary_parent else .10))
    result['guards']['tail10']=result['metrics']['tail10_mse']['delta']<=0
    result['promoted']=bool(all(result['guards'].values()))
    result['stage']='transport_ablation' if a.stationary_parent else 'screen';result['final_candidate']=False
    if a.stationary_parent:
        for path in a.stationary_parent:
            if load_run(path)[0]['variant']!='stationary':raise ValueError('Transport ablation requires stationary parents')
    write_json(a.out,result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
