"""Independent arithmetic, ROI-dot-product and scalar aggregation replay, no networks."""
import json, math, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import residual_addback_cpu as study
from vs_seg_full_volume_runtime import array_sha, sha
ROOT,OUT=study.ROOT,study.OUT

def entries():
    rows=[]
    for folder,helper in [('mc_rc_three_development_action_oracle',study.three),('mc_rc_001_002_raw_action_oracle',study.two)]:
        base=ROOT/'experiments'/folder;prior=study.read(base/'attempt_01.json');by={r['patient']:r for r in prior['patients']}
        for case in study.read(base/'run_contract.json')['cases']: rows.append(dict(kind='mc_rc',patient=case['patient'],case=case,prior=by[case['patient']],helper=helper))
    rows.sort(key=lambda r:r['patient']);prior,paths,mask,_=study.seen.freeze_inputs();rows.append(dict(kind='seen_ciss',patient='VS-SEG-001',prior=prior,paths=paths,mask=mask));return rows

def main():
    sys.stdout.reconfigure(encoding='utf-8');study.resource_gate();result=study.read(OUT/'attempt_01.json');contract=study.read(OUT/'run_contract.json');errors=[];checked=[]
    if not result['complete'] or result['errors']: raise ValueError('Complete candidate run required')
    if result['run_contract_sha256']!=sha(OUT/'run_contract.json'): raise ValueError('Contract binding differs')
    for f in contract['files']:
        if sha(ROOT.parent/f['path'])!=f['sha256']: raise ValueError('Frozen input changed '+f['path'])
    old={r['patient']:r for r in result['series']}
    for entry in entries():
        study.resource_gate();native,label,raw,pipe,hat,obs,targets,span,_=study.load(entry)
        candidate=(hat.astype(float)+(raw.astype(float)-pipe.astype(float))).astype(np.float32)
        saved=old[entry['patient']]
        if array_sha(candidate)!=saved['candidate_array_sha256']: errors.append(entry['patient']+': independent formula/float32 hash differs')
        true_targets=[z for z in range(1,(native.shape[2]-1)//4*4) if z%4]
        if targets!=true_targets or obs!=list(range(0,native.shape[2],4)): errors.append(entry['patient']+': targets/observations differ')
        for name,pred in [('raw_pchip',raw),('pipeline_pchip',pipe),('hat',hat),('transfer',candidate)]:
            region_data={'support':[],'lesion':[]}
            for z in true_targets:
                left,right=native[:,:,4*(z//4)],native[:,:,4*(z//4+1)]
                support=np.logical_or(abs(left)>.01*max(float(np.max(abs(left))),1e-6),abs(right)>.01*max(float(np.max(abs(right))),1e-6))
                prior_row=next(x for x in saved['per_plane'][name] if x['z']==z)
                for region,mask in [('support',support),('lesion',np.logical_and(support,label[:,:,z]))]:
                    difference=np.subtract(pred[:,:,z][mask].astype(np.float64),native[:,:,z][mask].astype(np.float64))/span
                    count=len(difference);sse=float(np.dot(difference,difference));before=prior_row[region]
                    if before['pixels']!=count or not math.isclose(before['sse'],sse,rel_tol=1e-10,abs_tol=1e-12): errors.append(entry['patient']+'/'+name+'/'+str(z)+'/'+region+': ROI differs')
                    if count: region_data[region].append((count,sse))
            for region,values in region_data.items():
                pixels=sum(v[0] for v in values);actual=dict(nonempty_targets=len(values),pixels=pixels,target_equal_nmse=math.fsum(s/n for n,s in values)/len(values) if values else None,pixel_weighted_nmse=math.fsum(s for n,s in values)/pixels if pixels else None)
                for key,value in actual.items():
                    expected=saved['metrics'][name][region][key]
                    if value is None or expected is None:
                        if value!=expected: errors.append('Null differs')
                    elif not math.isclose(value,expected,rel_tol=1e-10,abs_tol=1e-12): errors.append(entry['patient']+'/'+name+'/'+region+'/'+key+': summary differs')
        m=saved['metrics'];gain=10*math.log10(min(m[k]['support']['target_equal_nmse'] for k in ('raw_pchip','hat'))/m['transfer']['support']['target_equal_nmse']);guard={k:m['transfer']['lesion'][k]<=m['raw_pchip']['lesion'][k]+1e-12 for k in ('target_equal_nmse','pixel_weighted_nmse')}
        if guard!=saved['lesion_guard'] or (gain>=.1 and all(guard.values())) != saved['development_gate_passed']: errors.append(entry['patient']+': gate differs')
        if not math.isclose(gain,saved['gain_db_vs_better_raw_or_hat'],abs_tol=1e-12): errors.append('Gain differs')
        checked.append(dict(patient=entry['patient'],targets=len(true_targets),conditions=4,development_gate_passed=saved['development_gate_passed']));print(json.dumps(checked[-1]),flush=True)
        del native,label,raw,pipe,hat,candidate
    if len(checked)!=6 or sum(r['targets'] for r in checked)!=297: errors.append('All-six/297 target denominator differs')
    expected_all=all(r['development_gate_passed'] for r in checked)
    if expected_all!=result['all_six_development_gate_passed'] or result['fixed_candidate_stopped']==expected_all: errors.append('All-patient gate differs')
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=not errors,script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),run_contract_sha256=sha(OUT/'run_contract.json'),checked=checked,errors=errors,gpu_used=False,new_neural_inferences=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,independence='Shared old-cache native decoder/grid and analytic constructors; alternative exact addback expression and float32 full-array SHA, independently sliced ROI dot products, scalar aggregation and gate; no task inference')
    with (OUT/'independent_algebra_and_roi_replay.json').open('x',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(complete=not errors,targets=297,errors=errors)))
    if errors: raise SystemExit(1)

if __name__=='__main__': main()
