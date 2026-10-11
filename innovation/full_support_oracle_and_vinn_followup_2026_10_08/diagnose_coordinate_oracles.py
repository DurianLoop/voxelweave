"""Quantify old/new coordinate precision without any patient images or GT."""
import sys,itertools,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,dump,entry,resource_guard
import verify_full_geometry_support as old
import verify_full_geometry_support_v2 as new
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    p=ROOT/'resolution_and_lesion_followup_2026_10_08/development_geometry_attempt01/receipt.json'
    q=ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json';previous=read(q)
    series={s['uid']:s for s in previous['series']};records=[]
    for row in [r for r in read(p)['records'] if r['input']=='native_reference']:
        spacing=series[row['uid']]['realized_spacing_zrc_mm'];record=dict(uid=row['uid'],patch=row['patch'])
        for name,module in [('old',old),('v2',new)]:
            matrices=module.independently_physical_matrices(row['primitive'],row['pivot_zrc'],spacing);errors=[]
            for (a,b),prod in zip(matrices,[row['plan']['first_voxel_matrix'],row['plan']['second_voxel_matrix']]):
                t=np.array(prod)
                for corner in itertools.product([0,127],[0,127],[0,63]):errors.append(float(np.max(np.abs(a@corner+b-(t[:3,:3]@corner+t[:3,3])))))
            record[name+'_max_voxel_error']=max(errors);record[name+'_passes_3e12']=max(errors)<=3e-12
        records.append(record)
    r=dict(complete=True,errors=[],records=records,old_failed_patches=sum(not r['old_passes_3e12'] for r in records),
        v2_failed_patches=sum(not r['v2_passes_3e12'] for r in records),old_max_voxel_error=max(r['old_max_voxel_error'] for r in records),
        v2_max_voxel_error=max(r['v2_max_voxel_error'] for r in records),medical_arrays_loaded=0,GT_arrays_loaded=0,neural_forwards=0,
        source_bindings=[entry(x) for x in [Path(__file__),Path(old.__file__),Path(new.__file__),p,q]])
    dump(HERE/'COORDINATE_ORACLE_DIAGNOSTIC.json',r);assert r['old_failed_patches']>0 and r['v2_failed_patches']==0
    print(json.dumps({k:r[k] for k in ['complete','old_failed_patches','v2_failed_patches','old_max_voxel_error','v2_max_voxel_error']}),flush=True)
if __name__=='__main__':main()
