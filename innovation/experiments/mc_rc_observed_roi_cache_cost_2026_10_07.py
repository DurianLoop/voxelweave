"""Frozen observed predictions only: old coverage joined with new tiling costs."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import json,math,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
from scipy import ndimage
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,read,sha,array_sha,resource_guard,lattice,physical_mr,tile_plan,PATCH,torch,np
OUT=ROOT/'experiments/mc_rc_observed_roi_cache_cost_2026_10_07'
OLD=ROOT/'experiments/mc_rc_anchor_qda_cpu'
PREP=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json'
PROTOCOL=ROOT/'MC_RC_OBSERVED_ROI_CACHE_COST_PROTOCOL_2026-10-07.md'
METHODS=('joint_QDA','appearance_QDA','coordinates_QDA','joint_LDA')
def stamp():return datetime.now(timezone.utc).isoformat()
def entry(p):p=Path(p);return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def save(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def costs(physical,locations):
    ids=[i for i,s in enumerate(locations) if physical[tuple(slice(a,a+p) for a,p in zip(s,PATCH))].any()]
    pairs=sorted({i//2 for i in ids});n=(len(locations)+1)//2;k=len(pairs)
    return dict(affected_tile_ids=ids,recomputed_batch_pair_ids=pairs,affected_tiles=len(ids),
        recomputed_tiles=sum(min(2,len(locations)-2*b) for b in pairs),recomputed_batch_pairs=k,
        saved_forward_calls=n-k,saved_forward_fraction=(n-k)/n,
        five_same_support_actions_with_initialization_count_ratio=(n+5*k)/(5*n),
        minimum_same_support_actions_for_strict_count_saving=n//(n-k)+1 if k<n else None)
def summaries(rows):
    allrows=[];patients=sorted({s['patient'] for s in rows})
    for method in METHODS:
        pairs=[(s,s['methods'][method]) for s in rows];means={}
        for p in patients:
            a=[(s,m) for s,m in pairs if s['patient']==p]
            means[p]=dict(saved_forward_fraction=sum(m['cost']['saved_forward_fraction'] for s,m in a)/len(a),
                sourced_foreground_recall=sum(m['sourced_original_roi_metrics']['foreground_recall'] for s,m in a)/len(a),
                sourced_boundary_recall=sum(m['sourced_original_roi_metrics']['boundary_recall'] for s,m in a)/len(a))
        n=sum(s['full_forward_calls'] for s,m in pairs);k=sum(m['cost']['recomputed_batch_pairs'] for s,m in pairs)
        allrows.append(dict(method=method,series=len(rows),patients=len(patients),full_forward_calls_total=n,recomputed_batch_pairs_total=k,
            empty_ROI_series=sum(m['native_ROI_voxels']==0 for s,m in pairs),nonempty_series_with_any_forward_saving=sum(m['native_ROI_voxels']>0 and m['cost']['saved_forward_calls']>0 for s,m in pairs),
            nonempty_series_with_all_batches_affected=[s['uid'] for s,m in pairs if m['native_ROI_voxels']>0 and not m['cost']['saved_forward_calls']],
            all_series_with_five_count_ratio_strictly_below1=sum(m['cost']['five_same_support_actions_with_initialization_count_ratio']<1 for s,m in pairs),
            series_with_coverage_boundary_ge099_and_forward_saving=sum(m['sourced_original_roi_metrics']['foreground_recall']>=.99 and m['sourced_original_roi_metrics']['boundary_recall']>=.99 and m['cost']['saved_forward_calls']>0 for s,m in pairs),
            sourced_original_ROI_gates_passed=sum(m['sourced_original_roi_gate_passed'] for s,m in pairs),
            patient_means=means,patient_first_mean_saved_forward_fraction=sum(m['saved_forward_fraction'] for m in means.values())/len(means),
            patient_first_mean_sourced_foreground_recall=sum(m['sourced_foreground_recall'] for m in means.values())/len(means),
            patient_first_mean_sourced_boundary_recall=sum(m['sourced_boundary_recall'] for m in means.values())/len(means),
            five_same_support_actions_with_initialization_total_count_ratio=(n+5*k)/(5*n)))
    return allrows
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);started=time.perf_counter();dest=OUT/'attempt01.json'
    r=dict(created_utc=stamp(),complete=False,errors=[],source_bindings=[],series=[],cached_prediction_arrays_loaded=0,new_MRI_pixel_arrays_loaded=0,
        new_GT_arrays_loaded=0,model_or_classification_calls=0,GPU_forwards=0,training_updates=0,confirmation_patients_opened=False,
        validation_data_read=False,publication_claim_confirmed=False,clinical_benefit_measured=False,coverage_metrics_sourced_not_newly_scored=True,
        previous_goal_turn_classification='progress',other_processes_modified=False,workspace_read_paths=[],prohibited_access_attempts=[])
    allowed=set()
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if not p.is_relative_to(ROOT.parent.resolve()):return
        if p.is_relative_to(OUT.resolve()):return
        if p not in allowed:
            r['prohibited_access_attempts'].append(str(p));raise PermissionError('Unlisted workspace read prohibited: '+str(p))
        rel=p.relative_to(ROOT).as_posix()
        if rel not in r['workspace_read_paths']:r['workspace_read_paths'].append(rel)
    def guard():
        assert time.perf_counter()-started<900;v=resource_guard();assert not torch.cuda.is_initialized()
        assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1
        assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<5_000_000;return v
    save(dest,r)
    try:
        torch.set_num_threads(4);r['resources_before']=guard()
        initial=[Path(__file__),PROTOCOL,PREP,OLD/'run_contract.json',OLD/'attempt_01.json',OLD/'independent_anchor_qda_replay.json',
            ROOT/'experiments/mc_rc_real_support_cache_diagnostic_2026_10_07/attempt01.json',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py']
        allowed.update(p.resolve() for p in initial);sys.addaudithook(audit)
        old=read(OLD/'attempt_01.json');contract=read(OLD/'run_contract.json');proof=read(OLD/'independent_anchor_qda_replay.json');prep=read(PREP)
        assert old['complete'] and not old['errors'] and not proof['errors'] and prep['complete'] and not prep['errors']
        assert sha(OLD/'attempt_01.json')==proof['result_sha256'] and sha(OLD/'run_contract.json')==proof['run_contract_sha256']==old['run_contract_sha256']
        assert proof['counts']['series']==len(contract['cases'])==len(old['series'])==16 and proof['counts']['patients']==8
        cases={c['uid']:c for c in contract['cases']};current={c['uid']:c for c in prep['cases']};assert len(current)==19 and set(cases)<=set(current)
        allowed.update((ROOT/s['prediction_file']).resolve() for s in old['series']);initial += [ROOT/s['prediction_file'] for s in old['series']]
        for fold in old['folds']:
            p=ROOT/fold['model_file'];allowed.add(p.resolve());initial.append(p);models=read(p);assert sha(p)==fold['model_sha256']
            assert fold['patient'] not in fold['training_patients'] and len(fold['training_patients'])==7
            for model in models.values():assert all(x['patient']!=fold['patient'] for x in model['training_membership'])
        r['source_bindings']=[entry(p) for p in initial]
        for p in initial[:9]:(OUT/(p.name+'.source_snapshot')).write_bytes(p.read_bytes())
        r['current_developer_series_without_old_predictor']=[dict(patient=c['patient'],uid=c['uid'],status='not_available_not_zero') for c in prep['cases'] if c['uid'] not in cases]
        assert len(r['current_developer_series_without_old_predictor'])==3
        oracle=read(ROOT/'experiments/mc_rc_real_support_cache_diagnostic_2026_10_07/attempt01.json');previous={s['uid']:s for s in oracle['series']};assert oracle['complete'] and not oracle['errors']
        for oldrow in old['series']:
            guard();c=cases[oldrow['uid']];now=current[c['uid']];p=ROOT/oldrow['prediction_file'];assert oldrow['complete'] and oldrow['predictions_saved_before_full_label_scoring'] and sha(p)==oldrow['prediction_sha256']
            for key in ('patient','uid','native_shape','native_spacing_rcz_mm','affine_rcz_ras','label_sha256','dicom_rcz_from_label_xyz'):assert c[key]==now[key]
            grid=lattice(c);shape=tuple(n+sum(pad) for n,pad in zip(grid['unpadded_shape_zrc'],grid['padding']));locations,axes=tile_plan(shape)
            assert grid==previous[c['uid']]['physical_grid'] and [list(v) for v in locations]==previous[c['uid']]['tile_locations_zrc']
            n=c['native_shape'][2];targets=list(range(1,(n-1)//4*4));targets=[z for z in targets if z%4]
            assert len(targets)==oldrow['missing_targets'];record=dict(patient=c['patient'],uid=c['uid'],native_shape_rcz=c['native_shape'],physical_grid=grid,
                physical_shape_zrc=list(shape),tile_locations_zrc=[list(v) for v in locations],full_forward_calls=(len(locations)+1)//2,methods={})
            with np.load(p,allow_pickle=False) as pack:
                assert set(pack.files)==set(METHODS)
                for method in METHODS:
                    pred=pack[method];assert pred.dtype==np.bool_ and pred.shape==(*c['native_shape'][:2],len(range(0,n,4)))
                    assert array_sha(pred)==oldrow['prediction_array_sha256'][method];r['cached_prediction_arrays_loaded']+=1
                    native=np.zeros(c['native_shape'],bool);cache={};plane_records=[]
                    sourced=oldrow['methods'][method]['roi'];by={x['z']:x for x in sourced['target_records']};assert set(by)==set(targets)
                    for z in targets:
                        j=z//4
                        if j not in cache:
                            union=pred[:,:,j]|pred[:,:,j+1]
                            cache[j]=(ndimage.distance_transform_edt(~union,sampling=c['native_spacing_rcz_mm'][:2])<=2.+1e-12) if union.any() else np.zeros(union.shape,bool)
                        mask=cache[j];native[:,:,z]=mask;count=int(mask.sum());assert count==by[z]['counts']['roi_voxels']
                        plane_records.append(dict(z=z,roi_voxels=count,roi_array_sha256=array_sha(mask)))
                    assert int(native.sum())==sourced['metrics']['roi_voxels'];physical=physical_mr(native.astype(np.float32),grid)>0
                    record['methods'][method]=dict(anchor_prediction_array_sha256=array_sha(pred),anchor_prediction_foreground=int(pred.sum()),
                        native_ROI_voxels=int(native.sum()),native_ROI_sha256=array_sha(native),physical_support_voxels=int(physical.sum()),physical_support_sha256=array_sha(physical),
                        empty_ROI_no_proposed_edit=not native.any(),plane_records=plane_records,cost=costs(physical,locations),
                        sourced_original_roi_metrics=sourced['metrics'],sourced_original_roi_gate_passed=sourced['gate_passed'])
            r['series'].append(record);save(dest,r)
        r.update(development_patients=8,development_series=16,methods=4,summaries=summaries(r['series']),resources_after=guard(),cuda_initialized=torch.cuda.is_initialized(),complete=True)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-started,finished_utc=stamp());save(dest,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','development_series','cached_prediction_arrays_loaded','summaries','prohibited_access_attempts','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
