"""Inverse labels, disk morphology, Fraction physical supports and component counts."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import hashlib,itertools,json,math,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
from fractions import Fraction
from scipy import ndimage
from mc_rc_matched_anchor_oracle_independent_helpers_2026_10_08 import ROOT,np,observed_labels,full_truth,boundary,physical_support,roi_metrics,compare
from mc_rc_reference_resources_2026_10_07 import resource_guard
OUT=ROOT/'experiments/mc_rc_matched_anchor_oracle_2026_10_08'
PATCH=(64,128,128)
METHODS=('joint_QDA_empirical_prior_19','joint_QDA_balanced_prior_19','joint_ExtraTrees_balanced_19')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def array_hash(a):
    a=np.ascontiguousarray(a);h=hashlib.sha256(json.dumps(dict(shape=list(a.shape),dtype=a.dtype.str),sort_keys=True).encode());h.update(memoryview(a).cast('B'));return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def components_independent(truth):
    positions=np.nonzero(truth);low=np.array([x.min() for x in positions]);high=np.array([x.max()+1 for x in positions]);crop=truth[tuple(slice(int(a),int(b)) for a,b in zip(low,high))]
    assert crop.size*4<=1_000_000_000;last=(truth.shape[2]-1)//4*4;zglobal=np.arange(crop.shape[2])+low[2];out={};maps={}
    for conn in (1,3):
        values,n=ndimage.label(crop,structure=ndimage.generate_binary_structure(3,conn),output=np.int32);counts=np.bincount(values.ravel(),minlength=n+1)
        group={name:np.zeros(n+1,dtype=np.int64) for name in ('observed','missing','tail')}
        for j,z in enumerate(zglobal):
            key='observed' if z%4==0 else ('missing' if z<last else 'tail');group[key]+=np.bincount(values[:,:,j].ravel(),minlength=n+1)
        boxes=ndimage.find_objects(values);rows=[]
        for index,box in enumerate(boxes,1):
            anchors,missing,tail=[int(group[key][index]) for key in ('observed','missing','tail')];assert int(counts[index])==anchors+missing+tail
            rows.append(dict(index=index,voxels=int(counts[index]),bbox_half_open_rcz=[[int(low[axis]+sl.start),int(low[axis]+sl.stop)] for axis,sl in enumerate(box)],observed_voxels=anchors,missing_voxels=missing,tail_voxels=tail,
                missing_component_without_observed_contact=missing>0 and anchors==0))
        out[str(6 if conn==1 else 26)]=dict(components=rows,count=n,total_foreground_voxels=int(counts[1:].sum()),components_with_missing=int(np.count_nonzero(group['missing'][1:])),missing_components_without_observed_contact=int(np.count_nonzero((group['missing'][1:]>0)&(group['observed'][1:]==0))))
        maps[conn]=values
    pairs=np.unique(np.stack([maps[1][crop],maps[3][crop]],axis=1),axis=0);assert len(pairs)==out['6']['count']
    return dict(foreground_crop_origin_rcz=low.tolist(),foreground_crop_shape_rcz=list(crop.shape),six_refines_twenty_six_verified=True,connectivity=out)
def main():
    sys.stdout.reconfigure(encoding='utf-8');start=time.perf_counter();dest=OUT/'independent_labels_disk_fraction_attempt01.json';assert not dest.exists()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],source_bindings=[],checked_series=0,checked_supports=0,checked_missing_plane_records=0,
        observed_label_arrays_loaded=0,full_development_GT_arrays_loaded=0,new_MRI_pixel_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,confirmation_patients_opened=False,validation_data_read=False,
        publication_claim_confirmed=False,workspace_read_paths=[],prohibited_access_attempts=[],shared_components=['SciPy ndimage.label and find_objects only for component partition; independent aggregation','previous independently verified label/metrics/Fraction helpers; no production geometry import'])
    allowed=set()
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if not p.is_relative_to(ROOT.parent.resolve()) or p.is_relative_to(OUT.resolve()):return
        if p not in allowed:r['prohibited_access_attempts'].append(str(p));raise PermissionError('Unlisted workspace access: '+str(p))
        path=p.relative_to(ROOT).as_posix()
        if path not in r['workspace_read_paths']:r['workspace_read_paths'].append(path)
    def save():dest.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():assert time.perf_counter()-start<900;return resource_guard()
    save()
    try:
        r['resources_before']=guard();prodfile=OUT/'attempt01.json';prod=read(prodfile);assert prod['complete'] and not prod['errors'] and not prod['prohibited_access_attempts']
        initial=[Path(__file__),ROOT/'experiments/mc_rc_matched_anchor_oracle_independent_helpers_2026_10_08.py',ROOT/'experiments/matched_anchor_oracle_independent_helper_origin_2026_10_08.json',prodfile]
        allowed.update(p.resolve() for p in initial);allowed.update((ROOT/b['path']).resolve() for b in prod['source_bindings']);sys.addaudithook(audit)
        for b in prod['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in initial]
        for p in initial[:3]:(OUT/(p.name+'.source_snapshot')).write_bytes(p.read_bytes())
        cases=read(ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json')['cases'];rows={s['uid']:s for s in prod['series']};receipts={s['uid']:s for s in prod['anchor_receipts']}
        frozen=read(ROOT/'experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07/attempt01.json');old={s['uid']:s for s in frozen['series']}
        assert len(cases)==len(rows)==len(receipts)==19 and len({c['patient'] for c in cases})==11 and prod['all19_anchor_masks_saved_before_full_GT_scoring']
        for c in cases:
            guard();s=rows[c['uid']];rec=receipts[c['uid']];anchors,indices=observed_labels(c);r['observed_label_arrays_loaded']+=1
            assert sha(ROOT/rec['file']['path'])==rec['file']['sha256'] and array_hash(anchors)==rec['anchor_array_sha256'] and indices==rec['label_decoded_planes']
            with np.load(ROOT/rec['file']['path'],allow_pickle=False) as pack:assert np.array_equal(pack['ideal_anchor_mask'],anchors)
            truth=full_truth(c);r['full_development_GT_arrays_loaded']+=1;assert array_hash(truth)==s['label_array_sha256'] and int(truth.sum())==c['expected_label_foreground_voxels']
            assert np.array_equal(anchors,truth[:,:,::4]);edge=boundary(truth);last=(truth.shape[2]-1)//4*4;targets=[z for z in range(1,last) if z%4];assert targets==s['missing_targets']
            sr,sc=c['native_spacing_rcz_mm'][:2];nr,nc=math.ceil(2/sr),math.ceil(2/sc)
            disk=np.hypot(np.arange(-nr,nr+1)[:,None]*sr,np.arange(-nc,nc+1)[None,:]*sc)<=2.+1e-12;native=np.zeros(truth.shape,bool);cache={}
            for z in targets:
                j=z//4
                if j not in cache:cache[j]=ndimage.binary_dilation(anchors[:,:,j]|anchors[:,:,j+1],structure=disk,border_value=0)
                native[:,:,z]=cache[j]
            compare(s['oracle']['roi'],roi_metrics(native,truth,edge,targets));g=s['oracle']['geometry_cost']
            assert int(native.sum())==g['native_ROI_voxels'] and array_hash(native)==g['native_ROI_sha256']
            spacing=np.sqrt((np.asarray(c['affine_rcz_ras'])[:3,:3]**2).sum(axis=0));dims=np.maximum(1,np.rint(np.array(c['native_shape'])[[2,0,1]]*spacing[[2,0,1]]/.5).astype(int))
            padding=[[(max(0,p-int(n)))//2,(max(0,p-int(n))+1)//2] for p,n in zip(PATCH,dims)]
            assert dims.tolist()==g['physical_grid']['unpadded_shape_zrc'] and padding==g['physical_grid']['padding']
            physical=physical_support(native,g['physical_grid']);assert int(physical.sum())==g['physical_support_voxels'] and array_hash(physical)==g['physical_support_sha256']
            starts=[sorted(set(range(0,n-p+1,p//2))|{n-p}) for n,p in zip(physical.shape,PATCH)];loc=list(itertools.product(*starts));assert [list(x) for x in loc]==g['tile_locations_zrc']
            ids=[i for i,start0 in enumerate(loc) if physical[tuple(slice(a,a+p) for a,p in zip(start0,PATCH))].any()];pairs=sorted({i//2 for i in ids});n=(len(loc)+1)//2;k=len(pairs)
            assert ids==g['affected_tile_ids'] and pairs==g['recomputed_batch_pair_ids'] and n==g['full_forward_calls'] and k==g['recomputed_batch_pairs']
            assert bool(not native.any())==g['empty_ROI'] and len(ids)==g['directly_affected_tiles'] and (len(ids)+1)//2==g['hypothetical_repacked_calls']
            assert sum(i//2 in pairs for i in range(len(loc)))==g['original_pair_recomputed_tiles'] and not g['repacking_execution_equivalence_verified']
            compare(g['saved_forward_fraction'],float(Fraction(n-k,n)));compare(s['label_components'],components_independent(truth))
            for name in METHODS:
                a=s['frozen_predictions'][name];assert a['roi']==old[c['uid']]['methods'][name]['roi'] and a['geometry_cost']==old[c['uid']]['methods'][name]['geometry_cost']
                assert a['geometry_cost']['physical_grid']==g['physical_grid'] and a['geometry_cost']['tile_locations_zrc']==g['tile_locations_zrc']
            r['checked_series']+=1;r['checked_supports']+=1;r['checked_missing_plane_records']+=len(targets);save()
        for summary in prod['summaries']:
            name=summary['method'];items=[(s,s['oracle'] if name=='ideal_observed_anchor_union_2mm_19' else s['frozen_predictions'][name]) for s in prod['series']];people=sorted({s['patient'] for s,a in items});means={}
            for p in people:
                values=[a for s,a in items if s['patient']==p];means[p]={key:sum(v['roi']['metrics'][key] for v in values)/len(values) for key in ('foreground_recall','boundary_recall','roi_fraction')}
                means[p]['saved_forward_fraction']=float(sum(Fraction(v['geometry_cost']['full_forward_calls']-v['geometry_cost']['recomputed_batch_pairs'],v['geometry_cost']['full_forward_calls']) for v in values)/len(values))
            compare(summary['patient_means'],means);compare(summary['patient_first_means'],{key:sum(v[key] for v in means.values())/11 for key in next(iter(means.values()))})
            assert summary['N_total']==sum(a['geometry_cost']['full_forward_calls'] for s,a in items) and summary['k_total']==sum(a['geometry_cost']['recomputed_batch_pairs'] for s,a in items)
            assert summary['ROI_gates_passed']==sum(a['roi']['gate_passed'] for s,a in items)
            assert summary['coverage_boundary_ge099_and_any_saving']==sum(a['roi']['metrics']['foreground_recall']>=.99 and a['roi']['metrics']['boundary_recall']>=.99 and a['geometry_cost']['saved_forward_fraction']>0 for s,a in items)
        assert r['checked_series']==19 and r['checked_supports']==19;r.update(complete=True,resources_after=guard())
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-start,finished_utc=datetime.now(timezone.utc).isoformat());save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','checked_series','checked_supports','checked_missing_plane_records','observed_label_arrays_loaded','full_development_GT_arrays_loaded','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
