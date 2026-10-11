"""V2 corrects observed-array binding to its authoritative input-preparation row.
Independent candidate construction and exact input/cost replay.

Shares specified SciPy PCHIP and torch trilinear operators, not production helpers.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import hashlib,itertools,json,math,sys,time,traceback
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
import numpy as np
import torch
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import binary_dilation
from mc_rc_reference_resources_2026_10_07 import resource_guard
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_observed_roi_real_input_probe_2026_10_07'
PATCH=(64,128,128)
METHODS=('joint_QDA','appearance_QDA','coordinates_QDA','joint_LDA')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def array_hash(a):
    a=np.ascontiguousarray(a);h=hashlib.sha256(json.dumps(dict(shape=list(a.shape),dtype=a.dtype.str),sort_keys=True).encode());h.update(memoryview(a).cast('B'));return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def compare(actual,expected):
    if isinstance(expected,float):assert math.isclose(actual,expected,rel_tol=0,abs_tol=1e-14),(actual,expected)
    elif isinstance(expected,dict):
        assert set(actual)==set(expected)
        for k,v in expected.items():compare(actual[k],v)
    else:assert actual==expected,(actual,expected)
def rebuild(observed,indices,n,pchip):
    result=np.empty((*observed.shape[:2],n),np.float32)
    for z in range(n):
        if z%4==0:result[:,:,z]=observed[:,:,z//4]
        elif z>indices[-1]:result[:,:,z]=observed[:,:,-1]
        else:
            j=z//4;t=(z-4*j)/4
            if pchip and j>0 and j+2<observed.shape[2]:
                q=np.asarray([j-1,j,j+1,j+2]);result[:,:,z]=PchipInterpolator(q*4,observed[:,:,q],axis=2)(z)
            else:result[:,:,z]=(1-t)*observed[:,:,j]+t*observed[:,:,j+1]
    return result
def resample(values,grid):
    tensor=torch.from_numpy(np.ascontiguousarray(values.transpose(2,0,1))).unsqueeze(0).unsqueeze(0)
    with torch.inference_mode():
        result=torch.nn.functional.interpolate(tensor,size=grid['unpadded_shape_zrc'],mode='trilinear',align_corners=False).squeeze(0).squeeze(0).numpy()
    return np.pad(result,grid['padding'],mode='constant',constant_values=0)
def main():
    sys.stdout.reconfigure(encoding='utf-8');dest=OUT/'independent_real_input_replay_attempt02.json';assert not dest.exists();started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],checked_series=0,checked_candidates=0,
        checked_literal_tile_equalities=0,observed_MRI_packages_loaded=0,cached_prediction_arrays_loaded=0,
        new_GT_arrays_loaded=0,native_reference_MRI_arrays_loaded=0,model_forwards=0,GPU_forwards=0,training_updates=0,
        confirmation_patients_opened=False,validation_data_read=False,publication_claim_confirmed=False,
        shared_operators=['scipy.interpolate.PchipInterpolator','torch.nn.functional.interpolate trilinear align_corners=False'],
        independent_components=['raw candidate construction np.where','physical disk binary_dilation','literal window replay','Fraction costs and patient means'],
        workspace_read_paths=[],prohibited_access_attempts=[])
    allowed={Path(__file__).resolve()}
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if not p.is_relative_to(ROOT.parent.resolve()) or p.is_relative_to(OUT.resolve()):return
        if p not in allowed:r['prohibited_access_attempts'].append(str(p));raise PermissionError('Unlisted workspace access: '+str(p))
        key=p.relative_to(ROOT).as_posix()
        if key not in r['workspace_read_paths']:r['workspace_read_paths'].append(key)
    def save():dest.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-started<900 and not torch.cuda.is_initialized();v=resource_guard();v['cpu_threads']=torch.get_num_threads()
        assert v['cpu_threads']==4 and torch.get_num_interop_threads()==1
        assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<50_000_000;return v
    save()
    try:
        torch.set_num_threads(4);torch.set_num_interop_threads(1);r['resources_before']=guard();sys.addaudithook(audit)
        prod=read(OUT/'attempt01.json');assert prod['complete'] and not prod['errors'] and not prod['prohibited_access_attempts']
        allowed.update((ROOT/x['path']).resolve() for x in prod['source_bindings'])
        for source in prod['source_bindings']:assert sha(ROOT/source['path'])==source['sha256']
        prep=read(ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json')
        observed_rows={v['uid']:v for v in read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json')['series']}
        old=read(ROOT/'experiments/mc_rc_anchor_qda_cpu/attempt_01.json')
        geom=read(ROOT/'experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07/attempt01.json')
        cases={x['uid']:x for x in prep['cases']};oldrows={x['uid']:x for x in old['series']};grids={x['uid']:x for x in geom['series']}
        assert len(prod['series'])==16 and {x['uid'] for x in prod['series']}==set(oldrows)==set(grids)
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in (Path(__file__),OUT/'attempt01.json')]
        (OUT/(Path(__file__).name+'.source_snapshot')).write_bytes(Path(__file__).read_bytes())
        replay_rows=[]
        for row in prod['series']:
            guard();c=cases[row['uid']];g=grids[c['uid']];grid=g['physical_grid'];oldrow=oldrows[c['uid']]
            with np.load(ROOT/row['observed_package']['path'],allow_pickle=False) as pack:
                observed=pack['observed_rcz'].copy();indices=tuple(map(int,pack['observed_indices']))
                assert np.array_equal(pack['affine_rcz_ras'],c['affine_rcz_ras']) and list(pack['native_shape'])==c['native_shape']
            r['observed_MRI_packages_loaded']+=1
            assert indices==tuple(range(0,c['native_shape'][2],4)) and array_hash(observed)==observed_rows[c['uid']]['observed_array_sha256']
            raw_base=rebuild(observed,indices,c['native_shape'][2],True);linear=rebuild(observed,indices,c['native_shape'][2],False)
            assert array_hash(raw_base)==row['raw_pchip_sha256'] and array_hash(linear)==row['raw_linear_sha256']
            mu=float(np.mean(observed,dtype=np.float64));std=float(np.std(observed,dtype=np.float64));divisor=std if std else 1.
            assert mu==row['observed_statistics']['mean'] and divisor==row['observed_statistics']['divisor']
            norm=lambda x:np.asarray((x.astype(np.float64)-mu)/divisor,dtype=np.float32)
            baseline=norm(raw_base);physical_base=resample(baseline,grid)
            assert array_hash(baseline)==row['baseline_normalized_sha256'] and array_hash(physical_base)==row['baseline_physical_sha256']
            starts=[sorted(set(range(0,n-p+1,p//2))|{n-p}) for n,p in zip(physical_base.shape,PATCH)]
            locations=list(itertools.product(*starts));assert [list(x) for x in locations]==g['tile_locations_zrc']
            n=(len(locations)+1)//2;assert n==row['full_forward_calls']
            sr,sc=c['native_spacing_rcz_mm'][:2];rr,cc=math.ceil((2.+1e-12)/sr),math.ceil((2.+1e-12)/sc)
            disk=np.hypot(np.arange(-rr,rr+1)[:,None]*sr,np.arange(-cc,cc+1)[None,:]*sc)<=2.+1e-12
            checked=dict(patient=row['patient'],uid=row['uid'],full=n,methods={})
            with np.load(ROOT/oldrow['prediction_file'],allow_pickle=False) as pack:
                for method in METHODS:
                    guard();prediction=pack[method];r['cached_prediction_arrays_loaded']+=1;m=row['methods'][method]
                    assert array_hash(prediction)==g['methods'][method]['anchor_prediction_array_sha256']
                    roi=np.zeros(c['native_shape'],bool);cache={}
                    for z in range(1,indices[-1]):
                        if not z%4:continue
                        j=z//4
                        if j not in cache:cache[j]=binary_dilation(prediction[:,:,j]|prediction[:,:,j+1],structure=disk,border_value=0)
                        roi[:,:,z]=cache[j]
                    assert array_hash(roi)==g['methods'][method]['native_ROI_sha256']
                    candidate_raw=np.where(roi,linear,raw_base)
                    assert array_hash(candidate_raw)==m['raw_candidate_sha256'] and np.array_equal(candidate_raw[:,:,indices],observed)
                    assert np.array_equal(candidate_raw[:,:,indices[-1]+1:],raw_base[:,:,indices[-1]+1:])
                    candidate=norm(candidate_raw);physical_candidate=resample(candidate,grid)
                    assert array_hash(candidate)==m['normalized_candidate_sha256'] and array_hash(physical_candidate)==m['physical_candidate_sha256']
                    native_change=candidate!=baseline;physical_change=physical_candidate!=physical_base
                    assert not np.any(native_change&~roi)
                    package=ROOT/m['changed_support_package']['path'];assert sha(package)==m['changed_support_package']['sha256']
                    with np.load(package,allow_pickle=False) as masks:
                        assert set(masks.files)=={'native_changed','physical_changed'}
                        assert np.array_equal(masks['native_changed'],native_change) and np.array_equal(masks['physical_changed'],physical_change)
                    assert array_hash(native_change)==m['native_changed_sha256'] and int(native_change.sum())==m['native_changed_voxels']
                    assert array_hash(physical_change)==m['physical_changed_sha256'] and int(physical_change.sum())==m['physical_changed_voxels']
                    ids=[];equalities=[]
                    for i,start in enumerate(locations):
                        sl=tuple(slice(s,s+p) for s,p in zip(start,PATCH));equal=bool(np.array_equal(physical_base[sl],physical_candidate[sl]));equalities.append(equal)
                        assert equal==bool(not physical_change[sl].any())
                        if not equal:ids.append(i)
                    assert equalities==m['tile_input_equal_to_baseline']
                    pairs=sorted({i//2 for i in ids});k=len(pairs)
                    expected=dict(affected_tile_ids=ids,recomputed_batch_pair_ids=pairs,recomputed_batch_pairs=k,full_forward_calls=n,
                        saved_forward_fraction=float(Fraction(n-k,n)),five_same_support_actions_with_initialization_count_ratio=float(Fraction(n+5*k,5*n)))
                    compare(m['actual_cost'],expected)
                    assert set(pairs)<=set(g['methods'][method]['cost']['recomputed_batch_pair_ids'])
                    assert bool(not physical_change.any())==m['no_actual_input_change'] and bool(not roi.any())==m['empty_ROI']
                    checked['methods'][method]=dict(k=k,geometric_k=m['geometric_recomputed_batch_pairs'],empty=m['empty_ROI'],nochange=m['no_actual_input_change'])
                    r['checked_candidates']+=1;r['checked_literal_tile_equalities']+=len(locations)
            replay_rows.append(checked);r['checked_series']+=1;save()
        exact=[]
        for summary in prod['summaries']:
            method=summary['method'];pairs=[(s,s['methods'][method]) for s in replay_rows];patients=sorted({s['patient'] for s,m in pairs});means={}
            for patient in patients:
                a=[(s,m) for s,m in pairs if s['patient']==patient]
                means[patient]=sum(Fraction(s['full']-m['k'],s['full']) for s,m in a)/len(a)
            expected=dict(method=method,series=16,patients=8,full_forward_calls_total=sum(s['full'] for s,m in pairs),
                actual_recomputed_batch_pairs_total=sum(m['k'] for s,m in pairs),geometric_recomputed_batch_pairs_total=sum(m['geometric_k'] for s,m in pairs),
                empty_ROI_series=sum(m['empty'] for s,m in pairs),no_actual_input_change_series=sum(m['nochange'] for s,m in pairs),
                series_actual_k_less_than_geometric_k=sum(m['k']<m['geometric_k'] for s,m in pairs),
                patient_mean_actual_saved_forward_fraction={p:float(x) for p,x in means.items()},
                patient_first_mean_actual_saved_forward_fraction=float(sum(means.values())/len(means)),
                nonempty_changed_series=sum(not m['nochange'] for s,m in pairs),
                sourced_original_ROI_gates_passed=sum(s['methods'][method]['sourced_original_roi_gate_passed'] for s in prod['series']))
            compare(summary,expected)
            exact.append(dict(method=method,patient_first_actual_saving_fraction=str(sum(means.values())/len(means))))
        assert r['observed_MRI_packages_loaded']==r['checked_series']==16 and r['checked_candidates']==64
        r.update(complete=True,exact_fraction_summaries=exact,CUDA_initialized=torch.cuda.is_initialized(),resources_after=guard())
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-started,finished_utc=datetime.now(timezone.utc).isoformat());save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','checked_series','checked_candidates','checked_literal_tile_equalities','exact_fraction_summaries','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
