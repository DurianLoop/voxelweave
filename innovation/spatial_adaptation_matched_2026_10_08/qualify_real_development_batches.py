"""All19 development series, two legal input arms, paired spatial targets; no neural forwards."""
import json,sys,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'));sys.path.insert(0,str(ROOT/'adaptation_paired_pilot_2026_10_08'))
from mc_rc_3d_19series_common_init_2026_10_07 import (development_cases,source_image,lattice,physical_mr,physical_label,
    read_reference_label,sample_batch,batch_rng,read,sha,array_sha,torch,np,resource_guard,QPATH)
import augmentation as intensity
import spatial_transform as spatial

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);started=time.perf_counter()
    out=HERE/'real_batch_attempt01';out.mkdir(exist_ok=False);r=dict(complete=False,errors=[],series=[],MR_input_arrays_loaded=0,GT_arrays_loaded=0,
        model_arrays_loaded=0,neural_forwards=0,training_updates=0,validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False)
    def save():
        temp=out/'receipt.json.tmp'
        with temp.open('w',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
        temp.replace(out/'receipt.json')
    save()
    try:
        qualified=read(HERE/'synthetic_attempt01/receipt.json');assert qualified['complete'] and qualified['all10_full_patch_gates_passed']
        for b in qualified['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        cases=development_cases();old=read(QPATH);reference={a['kind']:{s['uid']:s for s in a['cache_records']} for a in old['arms']}
        sources={Path(__file__),HERE/'spatial_transform.py',HERE/'PROTOCOL.md',HERE/'synthetic_attempt01/receipt.json',Path(intensity.__file__),QPATH}
        for i,(c,row) in enumerate(cases,1):
            resource_guard();assert time.perf_counter()-started<600;grid=lattice(c);target=physical_label(read_reference_label(c),grid)
            target_sha=array_sha(target);r['GT_arrays_loaded']+=1;assert target_sha==reference['native_reference'][c['uid']]['label_sha256']
            pair=None;records=[]
            for kind in ['native_reference','raw_pchip']:
                normalized,stats=source_image(c,row,kind);image=physical_mr(normalized,grid);del normalized;r['MR_input_arrays_loaded']+=1
                assert array_sha(image)==reference[kind][c['uid']]['input_sha256']
                x,y,geometry=sample_batch(image,target,batch_rng(19998+i));pivots=spatial.pivots(geometry,x.shape[2:])
                assert y.numpy()[0,0][tuple(map(int,pivots[0]))]==1
                spatial_p=spatial.primitives(i);intensity_p=intensity.primitives(i)
                xx,yy,matrix=spatial.apply(x.numpy(),y.numpy(),spatial_p,pivots,grid['realized_spacing_zrc_mm'])
                spatial_image=intensity.apply(xx,intensity_p);control_image=intensity.apply(x.numpy(),intensity_p)
                assert yy[0,0][tuple(map(int,pivots[0]))]==1 and yy[0].sum()>0
                identity=dict(mother_label_sha256=array_sha(y.numpy()),transformed_label_sha256=array_sha(yy),geometry=geometry,
                    pivots_zrc=pivots,spatial_primitives=spatial_p,intensity_primitives=intensity_p,theta_normalized_xyz=matrix)
                if pair is None:pair=identity
                else:assert identity==pair
                records.append(dict(kind=kind,input_batch_sha256=array_sha(x.numpy()),control_intensity_input_sha256=array_sha(control_image),
                    spatial_intensity_input_sha256=array_sha(spatial_image),label_foreground_before=[int(z.sum()) for z in y.numpy()],
                    label_foreground_after=[int(z.sum()) for z in yy],**identity))
                del image,x,y,xx,yy,spatial_image,control_image
            sources.update(ROOT/c[k] for k in ['header_file','mr_zip_file','label_file']);sources.add(ROOT/row['observed_package'])
            r['series'].append(dict(patient=c['patient'],uid=c['uid'],physical_label_sha256=target_sha,arms=records));del target;save()
            print(json.dumps(dict(development_series_verified=len(r['series']),paired_targets_and_transforms=True)),flush=True)
        r.update(complete=True,all38_real_batches_verified=True,all19_mother_labels_and_geometry_paired=True,
            all19_transformed_labels_paired=True,all38_forced_foreground_voxels_preserved=True,CUDA_initialized=torch.cuda.is_initialized(),
            resources_after=resource_guard(),source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(sources)])
        assert not r['CUDA_initialized']
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ['complete','errors','all38_real_batches_verified','all38_forced_foreground_voxels_preserved','elapsed_seconds']}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
