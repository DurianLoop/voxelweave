"""Qualified nineteen development series only; no task model or patient effect scoring."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,sys,time,traceback,gc
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'));sys.path.insert(0,str(ROOT/'adaptation_paired_pilot_2026_10_08'))
from mc_rc_3d_19series_common_init_2026_10_07 import (development_cases,source_image,lattice,physical_mr,physical_label,
    read_reference_label,sample_batch,batch_rng,read,sha,array_sha,torch,np,resource_guard,QPATH)
import augmentation as intensity
sys.path.insert(0,str(HERE))
from label_preserving_roundtrip import apply_roundtrip
from spatial_transform import pivots
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);started=time.perf_counter();out=HERE/'real_development_entry_attempt01';out.mkdir(exist_ok=False)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],MR_input_arrays_loaded=0,GT_arrays_loaded=0,
        model_arrays_loaded=0,neural_forwards=0,training_updates=0,validation_pixels_loaded=False,confirmation_patients_opened=False,
        lockedIXI_opened=False,new_patient_medical_effects=0,author_code_executed=False,publication_claim_confirmed=False,goal_status='active')
    def save():
        temp=out/'receipt.json.tmp'
        with temp.open('w',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
        temp.replace(out/'receipt.json')
    def guard():
        res=resource_guard();assert time.perf_counter()-started<600 and not torch.cuda.is_initialized()
        assert torch.get_num_threads()==torch.get_num_interop_threads()==1
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
        return res
    save()
    try:
        for rel in ['roundtrip_synthetic_attempt01/receipt.json','roundtrip_texture_attempt01/receipt.json']:
            q=read(HERE/rel);assert q['complete'] and not q['errors']
            for b in q['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        old=read(QPATH);assert old['complete'] and not old['errors'];reference={a['kind']:{s['uid']:s for s in a['cache_records']} for a in old['arms']}
        cases=development_cases();assert len(cases)==19 and len({c['patient'] for c,row in cases})==11
        sources={Path(__file__),HERE/'REAL_DEVELOPMENT_ROUNDTRIP_ENTRY_PROTOCOL.md',HERE/'label_preserving_roundtrip.py',
            HERE/'roundtrip_synthetic_attempt01/receipt.json',HERE/'roundtrip_texture_attempt01/receipt.json',QPATH,Path(intensity.__file__),
            ROOT/'spatial_adaptation_matched_2026_10_08/spatial_transform.py'}
        stress=[dict(enabled=True,degrees_xyz=[15,-11,8],scale=.85),dict(enabled=True,degrees_xyz=[-12,9,-7],scale=1.15)]
        for i,(c,row) in enumerate(cases,1):
            guard();begin=time.perf_counter();grid=lattice(c);target=physical_label(read_reference_label(c),grid);r['GT_arrays_loaded']+=1
            target_sha=array_sha(target);assert target_sha==reference['native_reference'][c['uid']]['label_sha256']
            pair=None;arms=[]
            for kind in ['native_reference','raw_pchip']:
                guard();normalized,stats=source_image(c,row,kind);image=physical_mr(normalized,grid);del normalized;r['MR_input_arrays_loaded']+=1
                assert array_sha(image)==reference[kind][c['uid']]['input_sha256']
                x,y,geometry=sample_batch(image,target,batch_rng(19998+i));xn=x.numpy();yn=y.numpy();p=pivots(geometry,xn.shape[2:])
                source_sha=array_sha(xn);mother=array_sha(yn);assert yn[0,0][tuple(map(int,p[0]))]==1
                xx,yy,meta=apply_roundtrip(xn,yn,stress,p,grid['realized_spacing_zrc_mm'])
                ip=intensity.primitives(i);final=intensity.apply(xx,ip)
                assert array_sha(xn)==source_sha and array_sha(yy)==mother and np.array_equal(yy,yn)
                assert final.dtype==np.float32 and final.shape==xn.shape and np.isfinite(final).all()
                assert yy[0,0][tuple(map(int,p[0]))]==1 and yy[0].sum()>0
                identity=dict(mother_label_sha256=mother,roundtrip_label_sha256=array_sha(yy),geometry=geometry,pivots_zrc=p,
                    stress_primitives=stress,intensity_primitives=ip,roundtrip_metadata=meta)
                if pair is None:pair=identity
                else:assert identity==pair
                arms.append(dict(kind=kind,base_input_sha256=source_sha,roundtrip_intensity_input_sha256=array_sha(final),
                    changed_roundtrip_voxels=int(np.count_nonzero(xx-xn)),GT_foreground_per_patch=[int(a.sum()) for a in yy],
                    all_original_GT_kept=True,**identity))
                del image,x,y,xn,yn,xx,yy,final;gc.collect();guard()
            sources.update(ROOT/c[k] for k in ['header_file','mr_zip_file','label_file']);sources.add(ROOT/row['observed_package'])
            r['series'].append(dict(patient=c['patient'],uid=c['uid'],physical_label_sha256=target_sha,realized_spacing_zrc_mm=grid['realized_spacing_zrc_mm'],
                arms=arms,elapsed_seconds=time.perf_counter()-begin));del target;save()
            print(json.dumps(dict(development_series_verified=len(r['series']),paired_inputs_and_original_GT=True)),flush=True)
        r.update(complete=True,all38_real_batches_verified=True,all19_mother_labels_geometry_and_transforms_paired=True,
            all38_original_GT_kept_exactly=True,all38_forced_FG_voxels_kept=True,CUDA_initialized=torch.cuda.is_initialized(),resources_after=guard(),
            source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(sources)])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ['complete','errors','all38_real_batches_verified','all38_original_GT_kept_exactly','elapsed_seconds']}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
