"""Real observed MRI interpolation probe under all frozen, already failed ROIs."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
from scipy import ndimage
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,read,sha,array_sha,resource_guard,observed_package,reconstruct,stats,lattice,physical_mr,tile_plan,PATCH,torch,np
OUT=ROOT/'experiments/mc_rc_observed_roi_real_input_probe_2026_10_07'
PREP=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json'
OBS=ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json'
GEOM=ROOT/'experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07/attempt01.json'
OLD=ROOT/'experiments/mc_rc_anchor_qda_cpu/attempt_01.json'
PROTOCOL=ROOT/'MC_RC_OBSERVED_ROI_REAL_INPUT_PROBE_PROTOCOL_2026-10-07.md'
METHODS=('joint_QDA','appearance_QDA','coordinates_QDA','joint_LDA')
def stamp():return datetime.now(timezone.utc).isoformat()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def cost(support,locations):
    ids=[i for i,s in enumerate(locations) if support[tuple(slice(a,a+p) for a,p in zip(s,PATCH))].any()]
    pairs=sorted({i//2 for i in ids});n=(len(locations)+1)//2;k=len(pairs)
    return dict(affected_tile_ids=ids,recomputed_batch_pair_ids=pairs,recomputed_batch_pairs=k,full_forward_calls=n,
        saved_forward_fraction=(n-k)/n,five_same_support_actions_with_initialization_count_ratio=(n+5*k)/(5*n))
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);started=time.perf_counter();dest=OUT/'attempt01.json'
    r=dict(created_utc=stamp(),complete=False,errors=[],series=[],source_bindings=[],source_snapshots=[],
        observed_MRI_packages_loaded=0,cached_prediction_arrays_loaded=0,new_GT_arrays_loaded=0,
        native_reference_MRI_arrays_loaded=0,model_forwards=0,GPU_forwards=0,training_updates=0,
        confirmation_patients_opened=False,validation_data_read=False,publication_claim_confirmed=False,
        task_benefit_measured=False,coverage_metrics_sourced_not_newly_scored=True,
        workspace_read_paths=[],prohibited_access_attempts=[],other_processes_modified=False)
    allowed=set()
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if not p.is_relative_to(ROOT.parent.resolve()) or p.is_relative_to(OUT.resolve()):return
        if p not in allowed:r['prohibited_access_attempts'].append(str(p));raise PermissionError('Unlisted workspace read: '+str(p))
        rel=p.relative_to(ROOT).as_posix()
        if rel not in r['workspace_read_paths']:r['workspace_read_paths'].append(rel)
    def save():dest.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-started<900;v=resource_guard();v['cpu_threads']=torch.get_num_threads()
        assert v['cpu_threads']==4 and torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
        assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<50_000_000;return v
    save()
    try:
        torch.set_num_threads(4);r['resources_before']=guard()
        initial=[Path(__file__),PROTOCOL,PREP,OBS,GEOM,OLD,
            ROOT/'experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07/independent_disk_rational_attempt01.json',
            ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
            ROOT/'experiments/mc_rc_observed_only_training_input.py']
        allowed.update(p.resolve() for p in initial);sys.addaudithook(audit)
        geom=read(GEOM);proof=read(initial[6]);prep=read(PREP);ob=read(OBS);old=read(OLD)
        assert all(x['complete'] and not x['errors'] for x in (geom,proof,prep,ob,old))
        assert proof['checked_series']==16 and proof['checked_method_supports']==64
        assert next(x for x in proof['source_bindings'] if x['path']==GEOM.relative_to(ROOT).as_posix())['sha256']==sha(GEOM)
        allowed.update((ROOT/v['path']).resolve() for v in geom['source_bindings'])
        for v in geom['source_bindings']:assert sha(ROOT/v['path'])==v['sha256']
        cases={c['uid']:c for c in prep['cases']};obs={c['uid']:c for c in ob['series']};previous={c['uid']:c for c in old['series']}
        assert len(cases)==len(obs)==19 and len(geom['series'])==16
        for s in geom['series']:
            assert s['uid'] in cases and s['uid'] in obs
            for p in (ROOT/obs[s['uid']]['observed_package'],ROOT/previous[s['uid']]['prediction_file']):
                allowed.add(p.resolve());initial.append(p)
        r['source_bindings']=[entry(p) for p in initial]
        for i,p in enumerate(initial[:10]):
            snap=OUT/(f'{i:02d}_'+p.name+'.source_snapshot');snap.write_bytes(p.read_bytes());assert sha(snap)==sha(p)
            r['source_snapshots'].append(dict(source_path=p.relative_to(ROOT).as_posix(),snapshot=entry(snap)))
        r['unavailable_old_predictor_series']=geom['current_developer_series_without_old_predictor']
        for index,s in enumerate(geom['series']):
            guard();c=cases[s['uid']];o=obs[s['uid']];before=sha(ROOT/o['observed_package']);tick=time.perf_counter()
            observed=observed_package(c,o);r['observed_MRI_packages_loaded']+=1
            statistics=stats(observed.pixels);assert statistics==o['observed_stats']
            raw_pchip=reconstruct(observed,'raw_pchip');raw_linear=reconstruct(observed,'raw_linear')
            for name,x in [('raw_pchip',raw_pchip),('raw_linear',raw_linear)]:assert array_sha(x)==o['inputs'][name+'_observed_shared']['raw_reconstruction_sha256']
            normalize=lambda x:((x.astype(np.float64)-statistics['mean'])/statistics['divisor']).astype(np.float32)
            baseline=normalize(raw_pchip);assert array_sha(baseline)==o['inputs']['raw_pchip_observed_shared']['normalized_rcz_sha256']
            grid=lattice(c);assert json.loads(json.dumps(grid))==s['physical_grid']
            physical_base=physical_mr(baseline,grid);locations,_=tile_plan(physical_base.shape)
            assert [list(x) for x in locations]==s['tile_locations_zrc']
            row=dict(patient=c['patient'],uid=c['uid'],observed_package=entry(ROOT/o['observed_package']),
                raw_pchip_sha256=array_sha(raw_pchip),raw_linear_sha256=array_sha(raw_linear),observed_statistics=statistics,
                baseline_normalized_sha256=array_sha(baseline),baseline_physical_sha256=array_sha(physical_base),
                full_forward_calls=(len(locations)+1)//2,full_input_generation_seconds=time.perf_counter()-tick,methods={})
            n=c['native_shape'][2];anchors=list(range(0,n,4));last=anchors[-1];tail=list(range(last+1,n))
            targets=[z for z in range(1,last) if z%4]
            predfile=ROOT/previous[c['uid']]['prediction_file']
            with np.load(predfile,allow_pickle=False) as pack:
                for method in METHODS:
                    guard();tick=time.perf_counter();pred=pack[method];r['cached_prediction_arrays_loaded']+=1
                    prior=s['methods'][method];assert array_sha(pred)==prior['anchor_prediction_array_sha256']
                    native=np.zeros(c['native_shape'],bool);cache={}
                    for z in targets:
                        j=z//4
                        if j not in cache:
                            union=pred[:,:,j]|pred[:,:,j+1]
                            cache[j]=ndimage.distance_transform_edt(~union,sampling=c['native_spacing_rcz_mm'][:2])<=2.+1e-12 if union.any() else np.zeros(union.shape,bool)
                        native[:,:,z]=cache[j]
                    assert array_sha(native)==prior['native_ROI_sha256']
                    raw_candidate=raw_pchip.copy();raw_candidate[native]=raw_linear[native]
                    assert not np.any((raw_candidate!=raw_pchip)&~native)
                    assert np.array_equal(raw_candidate[:,:,anchors],observed.pixels) and np.array_equal(raw_candidate[:,:,tail],raw_pchip[:,:,tail])
                    candidate=normalize(raw_candidate);native_changed=candidate!=baseline
                    assert not np.any(native_changed&~native)
                    assert np.array_equal(candidate[:,:,anchors],baseline[:,:,anchors]) and np.array_equal(candidate[:,:,tail],baseline[:,:,tail])
                    physical_candidate=physical_mr(candidate,grid);physical_changed=physical_candidate!=physical_base
                    geometric=physical_mr(native.astype(np.float32),grid)>0
                    assert array_sha(geometric)==prior['physical_support_sha256'] and not np.any(physical_changed&~geometric)
                    actual=cost(physical_changed,locations);geometric_cost=prior['cost'];assert set(actual['recomputed_batch_pair_ids'])<=set(geometric_cost['recomputed_batch_pair_ids'])
                    equality=[]
                    for tile,start in enumerate(locations):
                        sl=tuple(slice(a,a+p) for a,p in zip(start,PATCH))
                        equal=bool(np.array_equal(physical_base[sl],physical_candidate[sl]))
                        assert equal==(tile not in actual['affected_tile_ids'])
                        equality.append(equal)
                    path=OUT/f'{index:02d}_{method}_actual_changed_support.npz'
                    np.savez_compressed(path,native_changed=native_changed,physical_changed=physical_changed)
                    row['methods'][method]=dict(raw_candidate_sha256=array_sha(raw_candidate),normalized_candidate_sha256=array_sha(candidate),
                        physical_candidate_sha256=array_sha(physical_candidate),native_changed_voxels=int(native_changed.sum()),
                        physical_changed_voxels=int(physical_changed.sum()),native_changed_sha256=array_sha(native_changed),
                        physical_changed_sha256=array_sha(physical_changed),changed_support_package=entry(path),
                        empty_ROI=prior['empty_ROI_no_proposed_edit'],no_actual_input_change=not physical_changed.any(),
                        tile_input_equal_to_baseline=equality,actual_cost=actual,geometric_recomputed_batch_pairs=geometric_cost['recomputed_batch_pairs'],
                        sourced_original_roi_gate_passed=prior['sourced_original_roi_gate_passed'],
                        CPU_full_candidate_preparation_seconds=time.perf_counter()-tick)
            assert sha(ROOT/o['observed_package'])==before
            r['series'].append(row);save()
            print(json.dumps(dict(series_completed=len(r['series']),observed_packages_loaded=r['observed_MRI_packages_loaded'],model_forwards=0)),flush=True)
        summaries=[]
        for method in METHODS:
            pairs=[(s,s['methods'][method]) for s in r['series']];patients=sorted({s['patient'] for s,m in pairs});means={}
            for p in patients:
                a=[m for s,m in pairs if s['patient']==p];means[p]=sum(m['actual_cost']['saved_forward_fraction'] for m in a)/len(a)
            summaries.append(dict(method=method,series=16,patients=8,full_forward_calls_total=sum(s['full_forward_calls'] for s,m in pairs),
                actual_recomputed_batch_pairs_total=sum(m['actual_cost']['recomputed_batch_pairs'] for s,m in pairs),
                geometric_recomputed_batch_pairs_total=sum(m['geometric_recomputed_batch_pairs'] for s,m in pairs),
                empty_ROI_series=sum(m['empty_ROI'] for s,m in pairs),no_actual_input_change_series=sum(m['no_actual_input_change'] for s,m in pairs),
                series_actual_k_less_than_geometric_k=sum(m['actual_cost']['recomputed_batch_pairs']<m['geometric_recomputed_batch_pairs'] for s,m in pairs),
                patient_mean_actual_saved_forward_fraction=means,patient_first_mean_actual_saved_forward_fraction=sum(means.values())/len(means),
                nonempty_changed_series=sum(not m['no_actual_input_change'] for s,m in pairs),
                sourced_original_ROI_gates_passed=sum(m['sourced_original_roi_gate_passed'] for s,m in pairs)))
        r.update(summaries=summaries,all_anchor_and_tail_arrays_bitwise_unchanged=True,
            all_actual_changes_inside_geometric_support=True,all_literal_tile_equalities_verified=True,
            CUDA_initialized=torch.cuda.is_initialized(),resources_after=guard(),complete=True)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-started,finished_utc=stamp());save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','observed_MRI_packages_loaded','cached_prediction_arrays_loaded','summaries','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
