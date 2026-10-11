"""Matched annotation oracle, geometry only; no MRI, checkpoint or neural calls."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
from scipy import ndimage
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,read,sha,array_sha,lattice,physical_mr,tile_plan,PATCH,np,torch,resource_guard
from mc_rc_anchor_qda_cpu import observed_truth
from mc_rc_true_native_reference_v2_2026_10_07 import read_reference_label,DEVELOPERS
from mc_rc_native_competence_cpu import roi_summary
PREP=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json'
PRED=ROOT/'experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07/attempt01.json'
PROOF=PRED.parent/'independent_label_models_roi_attempt01.json'
PROTOCOL=ROOT/'MC_RC_MATCHED_ANCHOR_ORACLE_PROTOCOL_2026-10-08.md'
OUT=ROOT/'experiments/mc_rc_matched_anchor_oracle_2026_10_08'
METHODS=('joint_QDA_empirical_prior_19','joint_QDA_balanced_prior_19','joint_ExtraTrees_balanced_19')
def stamp():return datetime.now(timezone.utc).isoformat()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def save(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def geometry(native,c):
    grid=lattice(c);physical=physical_mr(native.astype(np.float32),grid)>0;loc,_=tile_plan(physical.shape)
    ids=[i for i,start in enumerate(loc) if physical[tuple(slice(s,s+p) for s,p in zip(start,PATCH))].any()]
    pairs=sorted({i//2 for i in ids});n=(len(loc)+1)//2;k=len(pairs);t=len(ids)
    return dict(native_ROI_voxels=int(native.sum()),native_ROI_sha256=array_sha(native),physical_support_voxels=int(physical.sum()),physical_support_sha256=array_sha(physical),
        physical_grid=json.loads(json.dumps(grid)),tile_locations_zrc=[list(x) for x in loc],affected_tile_ids=ids,recomputed_batch_pair_ids=pairs,full_forward_calls=n,recomputed_batch_pairs=k,
        saved_forward_fraction=(n-k)/n,empty_ROI=not native.any(),directly_affected_tiles=t,original_pair_recomputed_tiles=sum(min(2,len(loc)-2*b) for b in pairs),
        hypothetical_repacked_calls=(t+1)//2,repacking_execution_equivalence_verified=False)
def component_records(truth):
    coordinates=np.array(np.nonzero(truth));assert coordinates.shape[1]>0
    low=coordinates.min(1);high=coordinates.max(1)+1;crop=truth[tuple(slice(int(a),int(b)) for a,b in zip(low,high))]
    assert crop.size*4<=1_000_000_000;last=(truth.shape[2]-1)//4*4;result={};segmentations={}
    for connectivity in (1,3):
        labels,n=ndimage.label(crop,structure=ndimage.generate_binary_structure(3,connectivity),output=np.int32);rows=[]
        for index,slices in enumerate(ndimage.find_objects(labels),1):
            assert slices is not None;where=np.array(np.nonzero(labels[slices]==index))
            origin=low+np.array([sl.start for sl in slices]);where+=origin[:,None];z=where[2]
            anchors=int(np.count_nonzero(z%4==0));missing=int(np.count_nonzero((z%4!=0)&(z<last)));tail=int(np.count_nonzero(z>last))
            assert len(z)==anchors+missing+tail
            rows.append(dict(index=index,voxels=len(z),bbox_half_open_rcz=[[int(a),int(b)] for a,b in zip(where.min(1),where.max(1)+1)],observed_voxels=anchors,missing_voxels=missing,tail_voxels=tail,
                missing_component_without_observed_contact=missing>0 and anchors==0))
        result[str(6 if connectivity==1 else 26)]=dict(components=rows,count=n,total_foreground_voxels=sum(r['voxels'] for r in rows),
            components_with_missing=sum(r['missing_voxels']>0 for r in rows),missing_components_without_observed_contact=sum(r['missing_component_without_observed_contact'] for r in rows))
        segmentations[connectivity]=labels
    fine=segmentations[1];coarse=segmentations[3]
    for index in range(1,result['6']['count']+1):assert len(np.unique(coarse[fine==index]))==1
    return dict(foreground_crop_origin_rcz=low.tolist(),foreground_crop_shape_rcz=list(crop.shape),six_refines_twenty_six_verified=True,connectivity=result)
def summaries(series):
    people=sorted({s['patient'] for s in series});names=['ideal_observed_anchor_union_2mm_19',*METHODS];result=[]
    for name in names:
        values=[]
        for s in series:
            a=s['oracle'] if name==names[0] else s['frozen_predictions'][name]
            values.append((s,a))
        means={}
        for p in people:
            a=[v for s,v in values if s['patient']==p]
            means[p]={key:sum(v['roi']['metrics'][key] for v in a)/len(a) for key in ('foreground_recall','boundary_recall','roi_fraction')}
            means[p]['saved_forward_fraction']=sum(v['geometry_cost']['saved_forward_fraction'] for v in a)/len(a)
        result.append(dict(method=name,ROI_gates_passed=sum(v['roi']['gate_passed'] for s,v in values),
            coverage_boundary_ge099_and_any_saving=sum(v['roi']['metrics']['foreground_recall']>=.99 and v['roi']['metrics']['boundary_recall']>=.99 and v['geometry_cost']['saved_forward_fraction']>0 for s,v in values),
            N_total=sum(v['geometry_cost']['full_forward_calls'] for s,v in values),k_total=sum(v['geometry_cost']['recomputed_batch_pairs'] for s,v in values),
            patient_means=means,patient_first_means={key:sum(v[key] for v in means.values())/len(people) for key in next(iter(means.values()))}))
    return result
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);start=time.perf_counter();dest=OUT/'attempt01.json'
    r=dict(created_utc=stamp(),complete=False,errors=[],source_bindings=[],source_snapshots=[],anchor_receipts=[],series=[],observed_label_arrays_loaded=0,full_development_GT_arrays_loaded=0,
        new_MRI_pixel_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,confirmation_patients_opened=False,validation_data_read=False,
        oracle_geometry_only=True,actual_speed_or_action_benefit_measured=False,publication_claim_confirmed=False,workspace_read_paths=[],prohibited_access_attempts=[],other_processes_modified=False)
    allowed=set()
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if not p.is_relative_to(ROOT.parent.resolve()) or p.is_relative_to(OUT.resolve()):return
        if p not in allowed:r['prohibited_access_attempts'].append(str(p));raise PermissionError('Unlisted workspace access: '+str(p))
        path=p.relative_to(ROOT).as_posix()
        if path not in r['workspace_read_paths']:r['workspace_read_paths'].append(path)
    def persist():save(dest,r)
    def guard():
        assert time.perf_counter()-start<900;v=resource_guard()
        assert not torch.cuda.is_initialized() and torch.get_num_threads()==torch.get_num_interop_threads()==1
        assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<20_000_000;return v
    persist()
    try:
        r['resources_before']=guard()
        initial=[Path(__file__),PROTOCOL,PREP,PRED,PROOF,ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
            ROOT/'experiments/mc_rc_anchor_qda_cpu.py',ROOT/'experiments/mc_rc_true_native_reference_v2_2026_10_07.py',ROOT/'experiments/mc_rc_true_native_reference_2026_10_07.py',
            ROOT/'experiments/mc_rc_native_competence_cpu.py',ROOT/'experiments/mc_rc_observed_region_propagation.py',ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py']
        allowed.update(p.resolve() for p in initial);sys.addaudithook(audit)
        prep=read(PREP);pred=read(PRED);proof=read(PROOF);assert all(d['complete'] and not d['errors'] for d in (prep,pred,proof))
        assert proof['checked_series']==19 and proof['checked_candidate_supports']==57 and proof['forest_trees_compared']==704
        assert next(x for x in proof['source_bindings'] if x['path']==PRED.relative_to(ROOT).as_posix())['sha256']==sha(PRED)
        cases=prep['cases'];assert len(cases)==19 and len({c['uid'] for c in cases})==19 and {c['patient'] for c in cases}==DEVELOPERS
        old={s['uid']:s for s in pred['series']};assert set(old)=={c['uid'] for c in cases}
        for c in cases:initial.append(ROOT/c['label_file']);allowed.add((ROOT/c['label_file']).resolve())
        r['source_bindings']=[entry(p) for p in initial]
        for i,p in enumerate(initial[:13]):
            copy=OUT/(f'{i:02d}_'+p.name+'.source_snapshot');copy.write_bytes(p.read_bytes());r['source_snapshots'].append(dict(source_path=p.relative_to(ROOT).as_posix(),snapshot=entry(copy)))
        persist()
        for i,c in enumerate(cases):
            guard();assert sha(ROOT/c['label_file'])==c['label_sha256'];anchors,indices=observed_truth(c);r['observed_label_arrays_loaded']+=1
            file=OUT/f'{i:02d}_ideal_observed_anchors.npz';np.savez_compressed(file,ideal_anchor_mask=anchors)
            receipt=dict(patient=c['patient'],uid=c['uid'],file=entry(file),anchor_array_sha256=array_sha(anchors),foreground_voxels=int(anchors.sum()),label_decoded_planes=indices,
                full_GT_not_read_yet=True,annotation_oracle_not_deployment_input=True)
            r['anchor_receipts'].append(receipt);persist()
        assert len(r['anchor_receipts'])==19 and r['full_development_GT_arrays_loaded']==0;r['all19_anchor_masks_saved_before_full_GT_scoring']=True;persist()
        for c,receipt in zip(cases,r['anchor_receipts']):
            guard();truth=read_reference_label(c);r['full_development_GT_arrays_loaded']+=1;edge=truth&~ndimage.binary_erosion(truth,structure=ndimage.generate_binary_structure(3,1),border_value=0)
            assert sha(ROOT/receipt['file']['path'])==receipt['file']['sha256']
            with np.load(ROOT/receipt['file']['path'],allow_pickle=False) as pack:anchors=pack['ideal_anchor_mask'].copy()
            assert array_sha(anchors)==receipt['anchor_array_sha256'] and np.array_equal(anchors,truth[:,:,::4])
            last=(truth.shape[2]-1)//4*4;targets=[z for z in range(1,last) if z%4];full=np.zeros(truth.shape,bool);full[:,:,::4]=anchors
            roi=roi_summary(full,truth,edge,c,targets);native=np.zeros(truth.shape,bool);cache={}
            for z in targets:
                j=z//4
                if j not in cache:
                    union=anchors[:,:,j]|anchors[:,:,j+1];cache[j]=ndimage.distance_transform_edt(~union,sampling=c['native_spacing_rcz_mm'][:2])<=2.+1e-12 if union.any() else np.zeros(union.shape,bool)
                native[:,:,z]=cache[j]
            assert int(native.sum())==roi['metrics']['roi_voxels'];g=geometry(native,c);frozen={}
            for name in METHODS:
                a=old[c['uid']]['methods'][name];assert a['geometry_cost']['physical_grid']==g['physical_grid'] and a['geometry_cost']['tile_locations_zrc']==g['tile_locations_zrc']
                assert a['geometry_cost']['full_forward_calls']==g['full_forward_calls']
                frozen[name]=dict(roi=a['roi'],geometry_cost=a['geometry_cost'],endpoints_are_sourced_from_previously_verified_predictions=True)
            components=component_records(truth)
            r['series'].append(dict(patient=c['patient'],uid=c['uid'],label_array_sha256=array_sha(truth),missing_targets=targets,oracle=dict(roi=roi,geometry_cost=g),frozen_predictions=frozen,label_components=components))
            persist();print(json.dumps(dict(stage='matched_oracle_scored',series=len(r['series']))),flush=True)
        r.update(summaries=summaries(r['series']),resources_after=guard(),complete=True)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-start,finished_utc=stamp());persist()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','observed_label_arrays_loaded','full_development_GT_arrays_loaded','summaries','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
