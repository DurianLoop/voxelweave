"""Real current19 sparse packages and label-independent input invariants, no network."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import json,sys,traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from vs_seg_task_cpu_support import resource_gate
from mc_rc_observed_only_training_input import ROOT,read,sha,array_sha,read_observed,reconstruct,normalize,stats,to_ras,support_domains,read_supervised_label,from_dense_observations_only
OUT=ROOT/'experiments/mc_rc_development_training_input_cpu';DATA=ROOT/'data/mc_rc_development_observed_only'
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();prepfile=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json';prep=read(prepfile)
    assert prep['complete'] and not prep['errors'] and len(prep['cases'])==19;OUT.mkdir(exist_ok=False);DATA.mkdir(exist_ok=False)
    oldpath=ROOT/'experiments/mc_rc_native_competence_cpu/attempt_01.json';old=read(oldpath);oldby={x['uid']:x for x in old['series']};assert old['complete']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),resources=resources,script_sha256=sha(__file__),loader_sha256=sha(ROOT/'experiments/mc_rc_observed_only_training_input.py'),preparation_sha256=sha(prepfile),prior_native_result_sha256=sha(oldpath),complete=False,errors=[],series=[],
        developer_patients=11,expected_series=19,phase=0,stride=4,label_input_separated=True,non_observed_MR_pixels_decoded=False,torch_imported=False,new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False,max_total_saved_observed_bytes=500000000,saved_observed_bytes=0)
    path=OUT/'attempt_01.json';write(path,r)
    try:
        for case in prep['cases']:
            resource_gate();observed=read_observed(case);a=observed.pixels;domains=support_domains(observed);uid=case['uid'];row=dict(patient=case['patient'],uid=uid,native_shape=case['native_shape'],observed_shape=list(a.shape),observed_array_sha256=array_sha(a),decoded_sop_uids=list(observed.sop_uids),decoded_zip_members=list(observed.decoded_members),observed_indices=list(observed.indices),domain_planes={k:int(v.sum()) for k,v in domains.items()},observed_stats=stats(a),inputs={},complete=False)
            if uid in oldby:assert row['observed_array_sha256']==oldby[uid]['observed_array_sha256'] and row['decoded_sop_uids']==oldby[uid]['observed_sop_uids']
            dest=DATA/(case['patient']+'_'+uid+'_observed_only.npz');np.savez_compressed(dest,observed_rcz=a,observed_indices=np.asarray(observed.indices),native_shape=np.asarray(case['native_shape']),affine_rcz_ras=np.asarray(observed.affine_rcz_ras));r['saved_observed_bytes']+=dest.stat().st_size;assert r['saved_observed_bytes']<=r['max_total_saved_observed_bytes']
            row.update(observed_package=dest.relative_to(ROOT).as_posix(),observed_package_sha256=sha(dest))
            for method in ('raw_linear','raw_pchip'):
                generated=reconstruct(observed,method);rawhash=array_sha(generated)
                if method=='raw_pchip' and uid in oldby:assert rawhash==oldby[uid]['raw_pchip_display_array_sha256']
                for policy in ('observed_shared','full_own'):
                    normalized,st=normalize(generated,observed,policy);ras,affine,orientation=to_ras(normalized,observed)
                    row['inputs'][method+'_'+policy]=dict(raw_reconstruction_sha256=rawhash,normalized_rcz_sha256=array_sha(normalized),normalized_ras_sha256=array_sha(ras),statistics=st,ras_shape=list(ras.shape),ras_affine=affine.tolist(),orientation=orientation.tolist())
                    del normalized,ras
                del generated
            # Counterfactual dense container has identical acquired planes but arbitrary hidden values.
            if case==prep['cases'][0]:
                toy=np.zeros((7,9,17),dtype=np.float32);toy[:,:,::4]=np.arange(5,dtype=np.float32)
                left=from_dense_observations_only(toy,np.eye(4));toy[:,:,np.arange(17)%4!=0]=np.nan;right=from_dense_observations_only(toy,np.eye(4))
                assert np.array_equal(left.pixels,right.pixels)
                for method in ('raw_linear','raw_pchip'):assert np.array_equal(reconstruct(left,method),reconstruct(right,method))
                r['counterfactual_nonfinite_hidden_reference_invariance_passed']=True
            # Only now open developer labels; no supervised label is accepted by sparse interfaces.
            label=read_supervised_label(case);labelras,laff,lorient=to_ras(label,observed)
            row.update(label_array_sha256=array_sha(label),label_ras_sha256=array_sha(labelras),label_foreground=int(label.sum()),label_ras_shape=list(labelras.shape),label_ras_affine=laff.tolist(),label_read_after_all_inputs_recorded=True,complete=True)
            assert all(x['ras_shape']==list(labelras.shape) and np.array_equal(x['ras_affine'],laff) for x in row['inputs'].values())
            r['series'].append(row);write(path,r);print(json.dumps(dict(patient=case['patient'],uid=uid,complete=True,observed_planes=len(observed.indices),decoded_missing_MR_planes=0,matched_prior_input=uid in oldby)),flush=True);del observed,a,label,labelras
        r['torch_imported']='torch' in sys.modules;assert not r['torch_imported'];r['complete']=len(r['series'])==19
    except Exception as exc:r['errors'].append(type(exc).__name__+': '+str(exc));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r);print(json.dumps({k:r.get(k) for k in ('complete','errors','saved_observed_bytes','counterfactual_nonfinite_hidden_reference_invariance_passed','torch_imported','new_neural_forwards')}),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
