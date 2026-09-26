"""Strict paired pilot reports; no external lock or test entry."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import pastnet_v2.report as statistics
from pastnet_v2.common import sha256,write_json,PACKAGE
from pastnet_v2.run import RECIPE
from .run import code_hashes,original_code_hashes


def native(x):
    if isinstance(x,dict):return {k:native(v) for k,v in x.items()}
    if isinstance(x,list):return [native(v) for v in x]
    return x.item() if isinstance(x,np.generic) else x


def load_run(path):
    path=Path(path)
    m=json.loads((path/'manifest.json').read_text(encoding='utf-8'))
    c=json.loads((path/'completion.json').read_text(encoding='utf-8'))
    if m['smoke'] or not c['completed'] or m['dataset']!='fastmri' or m['test_selected']:
        raise ValueError('Completed fastMRI validation full only')
    expected=original_code_hashes() if m['variant']=='control' else code_hashes()
    if m['variant'] not in ('control','trajectory_local','trajectory_extended') or m['code_hashes']!=expected or m['recipe']!=RECIPE:
        raise ValueError('Source / variant / recipe mismatch')
    if sha256(m['data_manifest'])!=m['data_sha256'] or sha256(path/'best.pth')!=c['best_sha256']:
        raise ValueError('Data or checkpoint changed')
    data=json.loads(Path(m['data_manifest']).read_text(encoding='utf-8'))
    expected_patients={str(r['patient_id']) for r in data['records'] if r['split']=='val'}
    frame=pd.read_csv(path/'validation/per_patient.csv',dtype={'patient_id':str}).set_index('patient_id').sort_index()
    if frame.index.has_duplicates or set(frame.index)!=expected_patients or not np.isfinite(frame.to_numpy()).all():
        raise ValueError('Invalid or incomplete validation patients')
    return m,frame


def control_path(seed):return PACKAGE/'runs'/f'full_control_seed{seed}_vram20'


def local_health(path):
    m,frame=load_run(path)
    if m['variant']!='trajectory_local':raise ValueError('Expected local control')
    base=control_path(m['seed']);bm,bf=load_run(base)
    if m['data_sha256']!=bm['data_sha256'] or m['init_sha256']!=bm['init_sha256']:
        raise ValueError('Control data / initialization mismatch')
    ef=json.loads((Path(path)/'efficiency.json').read_text());eb=json.loads((base/'efficiency.json').read_text())
    if ef['contract']!=eb['contract'] or ef['device']!=eb['device']:
        raise ValueError('Efficiency protocol / device mismatch')
    delta=float((frame.psnr-bf.psnr).mean())
    ratio=ef['latency_ms_slice_median']/eb['latency_ms_slice_median']
    mem=ef['peak_forward_gib']/eb['peak_forward_gib']
    return dict(eligible=delta>=-.02 and ratio<=1.5 and mem<=1.5,psnr_delta=delta,
                time_ratio=ratio,memory_ratio=mem,capacity_control_only=True,
                local_best_sha256=sha256(Path(path)/'best.pth'))


def main():
    p=argparse.ArgumentParser();p.add_argument('--local',type=Path,nargs='+',required=True)
    p.add_argument('--extended',type=Path,nargs='+');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    if len(a.local) not in (1,3):raise ValueError('One pilot or three paired seeds required')
    health=[local_health(path) for path in a.local];result={'local_health':health,'promoted':False}
    if a.extended:
        if len(a.extended)!=len(a.local):raise ValueError('Unmatched number of seeds')
        seeds=[]
        for ep,lp in zip(a.extended,a.local):
            em,_=load_run(ep);lm,_=load_run(lp)
            if em['variant']!='trajectory_extended' or em['seed']!=lm['seed']:raise ValueError('Wrong paired arms')
            seeds.append(em['seed'])
        statistics.load_run=load_run
        result['information_gate']=native(statistics.paired_report(a.extended,a.local,.10))
        result['total_gate']=native(statistics.paired_report(a.extended,[control_path(seed) for seed in seeds],.15))
        result['promoted']=all(h['eligible'] for h in health) and result['information_gate']['promoted'] and result['total_gate']['promoted']
        # Predefined boundary/centre and phase diagnostics, never a substitute for the overall gate.
        e=pd.concat([pd.read_csv(path/'validation/per_slice.csv',dtype={'patient_id':str,'case_id':str}).assign(seed=seed) for path,seed in zip(a.extended,seeds)])
        l=pd.concat([pd.read_csv(path/'validation/per_slice.csv',dtype={'patient_id':str,'case_id':str}).assign(seed=seed) for path,seed in zip(a.local,seeds)])
        paired=e.merge(l,on=['seed','patient_id','case_id','z','phase'],suffixes=('_e','_l'),validate='one_to_one')
        if len(paired)!=len(e) or len(paired)!=len(l):raise ValueError('Slice pairing mismatch')
        paired['delta']=paired.psnr_e-paired.psnr_l
        paired['region']=np.where(paired.z.between(5,7),'centre','boundary')
        grouped=paired.groupby(['seed','patient_id','region','phase']).delta.mean().reset_index()
        result['strata']=grouped.groupby(['region','phase']).delta.mean().reset_index().to_dict('records')
    write_json(a.out,native(result));print(json.dumps(native(result),indent=2))


if __name__=='__main__':main()
