"""Verify one-case fit with independent counts/physical surfaces and direct plane replay."""
import sys,json,traceback
from pathlib import Path
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_sparse_task_cpu_pilot_support import ROOT,SEED,PilotUNet,weight_hash,read,sha,array_sha,load_package,image_input,np,torch
from verify_mc_rc_sparse_task_training_cpu_pilot import independent_label,independent_counts,independent_surface,independent_plane
OUT=ROOT/'experiments/mc_rc_single_developer_fit_diagnostic_cpu'
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();path=OUT/'independent_metrics_and_checkpoint_attempt_01.json';assert not path.exists();source=OUT/'attempt_01.json';r=read(source);assert r['complete'] and not r['errors']
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),shared_verifier_sha256=sha(ROOT/'experiments/verify_mc_rc_sparse_task_training_cpu_pilot.py'),result_sha256=sha(source),scientific_confirmation_patients=0,publication_claim_confirmed=False)
    try:
        assert r['updates_completed']==4000 and r['training_patient_ids']==['VS-MC-RC-012'] and r['training_series_uids']==[r['uid']];e=r['evaluations'][0];case=next(x for x in read(ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json')['cases'] if x['uid']==r['uid'])
        row=next(x for x in read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json')['series'] if x['uid']==r['uid']);label=independent_label(case);assert array_sha(label)==e['label_array_sha256'];pp=ROOT/e['prediction_file'];assert sha(pp)==e['prediction_file_sha256']
        with np.load(pp,allow_pickle=False) as d:pred=d['prediction_rcz'].copy()
        assert pred.dtype==bool and pred.shape==label.shape and array_sha(pred)==e['prediction_array_sha256'];n=pred.shape[2];last=((n-1)//4)*4;domains={'full':np.arange(n),'anchors':np.arange(0,n,4),'missing':np.asarray([z for z in range(last) if z%4]),'tail':np.arange(last+1,n)};q['counts']={}
        for name,zs in domains.items():
            c=independent_counts(pred[:,:,zs],label[:,:,zs]);assert all(c[k]==e['metrics'][name][k] for k in c);q['counts'][name]=c
        q['independent_kdtree_surface']=independent_surface(pred,label,case['affine_rcz_ras'])
        assert all(abs(v-e['metrics']['full_surface'][k])<.0001 for k,v in q['independent_kdtree_surface'].items())
        torch.manual_seed(SEED);model=PilotUNet();assert weight_hash(model)==r['initial_weights_sha256'];cp=ROOT/r['checkpoint_file'];assert sha(cp)==r['checkpoint_sha256'];c=torch.load(cp,map_location='cpu',weights_only=True);assert c['training_patient_ids']==r['training_patient_ids'];model.load_state_dict(c['state_dict']);model.eval();assert weight_hash(model)==r['final_weights_sha256']
        o=load_package(case,row);image,st=image_input(o,'raw_pchip',row);assert array_sha(image)==r['input_sha256'];q['checkpoint_replayed_planes']=[]
        for z in (0,n//2,n-1):
            p,cov,rs,cs=independent_plane(model,image,z);assert np.array_equal(p,pred[:,:,z]) and array_sha(cov.astype(np.uint16))==e['coverage']['coverage_sha256'];q['checkpoint_replayed_planes'].append(z)
        q['neural_forward_calls']=model.forward_calls;q['gpu_initialized']=torch.cuda.is_initialized();assert not q['gpu_initialized'];q['fit_gate_passed_verified']=r['fit_gate_passed'];q['complete']=True
    except Exception as e:q['errors'].append(type(e).__name__+': '+str(e));q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(q,ensure_ascii=False));return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
