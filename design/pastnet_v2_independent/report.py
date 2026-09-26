"""Compare independent pilot with immutable existing budget-matched control."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pastnet_v2.report as statistics
from pastnet_v2.common import write_json,sha256
from pastnet_v2.run import RECIPE
from .run import code_hashes,original_code_hashes


def load_run(path):
    path=Path(path)
    m=json.loads((path/'manifest.json').read_text(encoding='utf-8'))
    c=json.loads((path/'completion.json').read_text(encoding='utf-8'))
    if m['smoke'] or not c['completed'] or m['dataset']!='fastmri':
        raise ValueError('Only full fastMRI validation can select this pilot')
    expected=original_code_hashes() if m['variant']=='control' else code_hashes()
    if m['variant'] not in ('control','correspondence_only') or m['code_hashes']!=expected or m['recipe']!=RECIPE:
        raise ValueError('Wrong variant, source lineage or recipe')
    if sha256(path/'best.pth')!=c['best_sha256']:
        raise ValueError('Checkpoint differs from completed run')
    frame=pd.read_csv(path/'validation/per_patient.csv').set_index('patient_id').sort_index()
    if frame.index.has_duplicates or not np.isfinite(frame.to_numpy()).all():
        raise ValueError('Duplicate patient or nonfinite metric')
    return m,frame


def native(x):
    if isinstance(x,dict):return {k:native(v) for k,v in x.items()}
    if isinstance(x,list):return [native(v) for v in x]
    return x.item() if isinstance(x,np.generic) else x


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    cm,_=load_run(a.candidate);bm,_=load_run(a.parent)
    if cm['variant']!='correspondence_only' or bm['variant']!='control':
        raise ValueError('Expected correspondence_only vs control')
    statistics.load_run=load_run
    result=native(statistics.paired_report([a.candidate],[a.parent],.10))
    result['stage']='independent_correspondence_pilot'
    result['not_cumulative_geometry_promotion']=True
    write_json(a.out,result)
    print(json.dumps(dict(promoted=result['promoted'],guards=result['guards'],psnr=result['metrics']['psnr']),indent=2))


if __name__=='__main__':
    main()
