"""Independent transpose/flip labels and rational Boolean interpolation geometry."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import hashlib,itertools,json,math,sys,time,traceback
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
import nibabel as nib
import numpy as np
from scipy.ndimage import maximum_filter
from mc_rc_true_native_reference_v2_2026_10_07 import resource_guard
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_real_support_cache_diagnostic_2026_10_07'
PATCH=(64,128,128)
PATIENTS={'VS-MC-RC-'+x for x in ('001','002','004','005','006','007','009','010','011','012','013')}
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for x in iter(lambda:f.read(1048576),b''):h.update(x)
    return h.hexdigest()
def array_hash(a):
    a=np.ascontiguousarray(a);h=hashlib.sha256(json.dumps({'shape':list(a.shape),'dtype':a.dtype.str},sort_keys=True).encode());h.update(memoryview(a).cast('B'));return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def neighbors(n,m):
    lower=[];upper=[]
    for i in range(m):
        q=Fraction((2*i+1)*n-m,2*m);q=max(Fraction(0),min(q,Fraction(n-1)))
        lower.append(q.numerator//q.denominator);upper.append(-((-q.numerator)//q.denominator))
    return np.asarray(lower),np.asarray(upper)
def positive_support(native,dims,padding):
    x=np.transpose(native,(2,0,1)).copy()
    for axis,(n,m) in enumerate(zip(x.shape,dims)):
        a,b=neighbors(n,m);x=np.take(x,a,axis=axis)|np.take(x,b,axis=axis)
    return np.pad(x,padding,mode='constant',constant_values=False)
def costs(ids,locations):
    ids=sorted(ids);pairs=sorted({v//2 for v in ids});full=(len(locations)+1)//2;k=len(pairs)
    return dict(affected_tile_ids=ids,recomputed_batch_pair_ids=pairs,directly_affected_tiles=len(ids),
        recomputed_tiles=len([i for i in range(len(locations)) if i//2 in pairs]),recomputed_batch_pairs=k,
        saved_forward_calls=full-k,saved_forward_fraction=float(Fraction(full-k,full)),
        five_same_support_actions_with_initialization_count_ratio=float(Fraction(full+5*k,5*full)),
        minimum_same_support_actions_for_strict_count_saving=full//(full-k)+1 if k<full else None)
def compare(actual,expected):
    if isinstance(expected,float):assert math.isclose(actual,expected,rel_tol=0,abs_tol=1e-14),(actual,expected)
    elif isinstance(expected,dict):
        assert set(actual)==set(expected),(set(actual),set(expected))
        for k,v in expected.items():compare(actual[k],v)
    else:assert actual==expected,(actual,expected)
def main():
    sys.stdout.reconfigure(encoding='utf-8');dest=OUT/'independent_rational_support_attempt01.json';assert not dest.exists()
    started=time.perf_counter();r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],source_bindings=[],
        checked_series=0,developer_label_arrays_loaded=0,checked_supports=0,checked_single_plane_actions=0,new_MRI_pixel_arrays_loaded=0,
        model_forwards=0,GPU_forwards=0,training_updates=0,validation_arrays_loaded=0,confirmation_patients_opened=False,
        implementation_independence='transpose/flip; Fraction center neighbors and Boolean OR; maximum_filter envelope; independent tile and cost formulas',
        clinical_independent_confirmation=False,publication_claim_confirmed=False)
    def save():dest.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():assert time.perf_counter()-started<900;return resource_guard()
    save()
    try:
        r['resources_before']=guard();prodfile=OUT/'attempt01.json';prod=read(prodfile);assert prod['complete'] and not prod['errors']
        prepfile=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json';cases=read(prepfile)['cases'];assert len(cases)==19
        by={(c['patient'],c['uid']):c for c in cases};assert len(by)==19 and {x[0] for x in by}==PATIENTS
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (Path(__file__),prodfile,prepfile)]
        (OUT/(Path(__file__).name+'.source_snapshot')).write_bytes(Path(__file__).read_bytes())
        for source in prod['source_bindings']:assert sha(ROOT/source['path'])==source['sha256']
        assert {(s['patient'],s['uid']) for s in prod['series']}==set(by)
        for s in prod['series']:
            guard();c=by[s['patient'],s['uid']];label_path=ROOT/c['label_file'];assert sha(label_path)==c['label_sha256']==s['label_source']['sha256']
            img=nib.load(label_path);raw=np.empty(img.shape,bool)
            for zz in range(0,img.shape[2],4):
                slab=np.asanyarray(img.dataobj[:,:,zz:zz+4]);assert slab.nbytes<=32_000_000 and np.isfinite(slab).all() and np.isin(slab,[0,1]).all()
                raw[:,:,zz:zz+4]=slab
            matrix=np.asarray(c['dicom_rcz_from_label_xyz']);assert np.array_equal(matrix,np.rint(matrix));matrix=matrix.astype(int)
            assert np.array_equal(np.abs(matrix[:3,:3]).sum(axis=0),[1,1,1]) and np.array_equal(np.abs(matrix[:3,:3]).sum(axis=1),[1,1,1])
            axes=np.argmax(np.abs(matrix[:3,:3]),axis=1);label=np.transpose(raw,axes)
            for axis,j in enumerate(axes):
                assert matrix[axis,3]==(label.shape[axis]-1 if matrix[axis,j]<0 else 0)
                if matrix[axis,j]<0:label=np.flip(label,axis)
            label=np.ascontiguousarray(label);r['developer_label_arrays_loaded']+=1
            assert list(label.shape)==c['native_shape']==s['native_shape_rcz']
            assert int(label.sum())==c['expected_label_foreground_voxels']==s['foreground_voxels'] and array_hash(label)==s['label_array_sha256']
            af=np.asarray(c['affine_rcz_ras'],float);spacing=np.sqrt((af[:3,:3]**2).sum(axis=0));old=np.asarray(c['native_shape'])[[2,0,1]]
            dims=np.maximum(1,np.rint(old*spacing[[2,0,1]]/0.5).astype(int)).tolist()
            padding=[((max(0,p-n))//2,(max(0,p-n)+1)//2) for p,n in zip(PATCH,dims)]
            assert dims==s['physical_grid']['unpadded_shape_zrc'] and [list(p) for p in padding]==s['physical_grid']['padding']
            shape=[n+sum(p) for n,p in zip(dims,padding)];assert shape==s['physical_shape_zrc']
            starts=[]
            for n,p in zip(shape,PATCH):starts.append(sorted({i for i in range(n-p+1) if i%(p//2)==0}|{n-p}))
            locations=list(itertools.product(*starts));assert [list(x) for x in locations]==s['tile_locations_zrc'] and (len(locations)+1)//2==s['full_forward_calls']
            axis_native=[]
            for oldn,newn,pad in zip(old,dims,padding):
                low,high=neighbors(int(oldn),newn);axis_native.append((low,high,pad[0]))
            tile_native=[]
            for loc in locations:
                target=[]
                for j,st in enumerate(loc):
                    low,high,padlo=axis_native[j];a=max(0,st-padlo);b=min(dims[j],st+PATCH[j]-padlo)
                    target.append(np.unique(np.r_[low[a:b],high[a:b]]))
                tile_native.append(target)
            missing=np.asarray([zz%4!=0 and zz<(label.shape[2]-1)//4*4 for zz in range(label.shape[2])])
            for a in s['supports']:
                native=label&missing[None,None,:]
                if a['variant']=='missing_foreground_rc_radius2':native=maximum_filter(native,size=(5,5,1),mode='constant',cval=0)>0
                else:assert a['variant']=='missing_foreground'
                assert int(native.sum())==a['native_support_voxels'] and array_hash(native)==a['native_support_sha256']
                physical=positive_support(native,dims,padding)
                assert int(physical.sum())==a['physical_support_voxels'] and array_hash(physical)==a['physical_support_sha256']
                ids=[i for i,loc in enumerate(locations) if np.any(physical[tuple(slice(st,st+p) for st,p in zip(loc,PATCH))])]
                compare(a['joint'],costs(ids,locations));pl=[]
                for zz in np.flatnonzero(native.any(axis=(0,1))):
                    hits=[i for i,(zs,rs,cs) in enumerate(tile_native) if zz in zs and len(rs) and len(cs) and native[:,:,zz][np.ix_(rs,cs)].any()]
                    pl.append(dict(z=int(zz),native_support_voxels=int(native[:,:,zz].sum()),**costs(hits,locations)))
                assert len(pl)==len(a['single_plane_actions'])
                for actual,expected in zip(a['single_plane_actions'],pl):compare(actual,expected)
                assert sorted({i for p in pl for i in p['affected_tile_ids']})==ids
                ksum=sum(p['recomputed_batch_pairs'] for p in pl);n=s['full_forward_calls']
                assert ksum==a['sum_individual_plane_recomputed_batch_pairs'] and len(a['joint']['recomputed_batch_pair_ids'])==a['one_joint_recomputed_batch_pairs']
                compare(a['count_ratio_all_single_plane_actions_with_initialization'],float(Fraction(n+ksum,len(pl)*n)))
                r['checked_supports']+=1;r['checked_single_plane_actions']+=len(pl)
            r['checked_series']+=1;save()
        exact=[]
        for summary in prod['summaries']:
            pairs=[(s,next(a for a in s['supports'] if a['variant']==summary['variant'])) for s in prod['series']]
            total=sum(s['full_forward_calls'] for s,a in pairs);k=sum(a['joint']['recomputed_batch_pairs'] for s,a in pairs)
            means={};plane_means={}
            for p in sorted(PATIENTS):
                pp=[(s,a) for s,a in pairs if s['patient']==p]
                means[p]=sum(Fraction(s['full_forward_calls']-a['joint']['recomputed_batch_pairs'],s['full_forward_calls']) for s,a in pp)/len(pp)
                plane_means[p]=sum(sum(Fraction(s['full_forward_calls']-b['recomputed_batch_pairs'],s['full_forward_calls']) for b in a['single_plane_actions'])/len(a['single_plane_actions']) for s,a in pp)/len(pp)
            assert total==summary['full_forward_calls_total'] and k==summary['joint_recomputed_batch_pairs_total']
            assert sum(a['joint']['saved_forward_calls']>0 for s,a in pairs)==summary['series_with_any_joint_forward_saving']
            assert [s['uid'] for s,a in pairs if not a['joint']['saved_forward_calls']]==summary['series_with_zero_joint_forward_saving']
            compare(summary['patient_mean_joint_saved_forward_fraction'],{p:float(v) for p,v in means.items()})
            compare(summary['patient_first_mean_joint_saved_forward_fraction'],float(sum(means.values())/len(means)))
            compare(summary['patient_first_mean_single_plane_saved_forward_fraction'],float(sum(plane_means.values())/len(plane_means)))
            compare(summary['five_same_support_actions_with_initialization_total_count_ratio'],float(Fraction(total+5*k,5*total)))
            assert sum(len(a['single_plane_actions']) for s,a in pairs)==summary['all_nonempty_single_plane_actions']
            assert sum(b['saved_forward_calls']>0 for s,a in pairs for b in a['single_plane_actions'])==summary['single_plane_actions_with_any_saving']
            exact.append(dict(variant=summary['variant'],patient_first_joint_saving_fraction=str(sum(means.values())/len(means)),patient_first_single_plane_saving_fraction=str(sum(plane_means.values())/len(plane_means))))
        assert prod['development_patients']==11 and prod['development_series']==r['checked_series']==19
        assert prod['total_tiles']==sum(len(s['tile_locations_zrc']) for s in prod['series'])==1139
        r.update(exact_fraction_summaries=exact,resources_after=guard(),complete=True)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-started,finished_utc=datetime.now(timezone.utc).isoformat());save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','checked_series','checked_supports','checked_single_plane_actions','exact_fraction_summaries','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
