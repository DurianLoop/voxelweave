"""Developer annotation-only geometric costs, with no MRI/model access."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import json, math, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
from scipy import ndimage
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,sha,read,array_sha,resource_guard,lattice,physical_mr,tile_plan,PATCH,torch,F,np
from mc_rc_observed_only_training_input import DEVELOPERS,read_supervised_label
OUT=ROOT/'experiments/mc_rc_real_support_cache_diagnostic_2026_10_07'
PREP=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json'
PROTOCOL=ROOT/'MC_RC_REAL_SUPPORT_CACHE_DIAGNOSTIC_PROTOCOL_2026-10-07.md'
def save(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def entry(p):p=Path(p);return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def cost(ids,locations):
    batches=sorted({i//2 for i in ids});n=(len(locations)+1)//2;k=len(batches)
    return dict(affected_tile_ids=ids,recomputed_batch_pair_ids=batches,directly_affected_tiles=len(ids),
        recomputed_tiles=sum(min(2,len(locations)-2*b) for b in batches),recomputed_batch_pairs=k,
        saved_forward_calls=n-k,saved_forward_fraction=(n-k)/n,
        five_same_support_actions_with_initialization_count_ratio=(n+5*k)/(5*n),
        minimum_same_support_actions_for_strict_count_saving=math.floor(n/(n-k))+1 if k<n else None)
def depth_dependencies(n,m):
    # Exact positive-contributor relation, used only for per-plane decomposition.
    numer=(2*np.arange(m,dtype=np.int64)+1)*n-m;den=2*m
    lo=np.clip(numer//den,0,n-1);hi=np.clip((numer+den-1)//den,0,n-1)
    return lo,hi
def summarize(rows):
    result=[]
    for variant in ('missing_foreground','missing_foreground_rc_radius2'):
        pairs=[(s,next(x for x in s['supports'] if x['variant']==variant)) for s in rows]
        patient={p:[] for p in sorted(DEVELOPERS)}
        for s,a in pairs:patient[s['patient']].append(a['joint']['saved_forward_fraction'])
        n=sum(s['full_forward_calls'] for s,a in pairs);k=sum(a['joint']['recomputed_batch_pairs'] for s,a in pairs)
        means={p:sum(v)/len(v) for p,v in patient.items()}
        result.append(dict(variant=variant,series_with_any_joint_forward_saving=sum(a['joint']['saved_forward_calls']>0 for s,a in pairs),
            series_with_zero_joint_forward_saving=[s['uid'] for s,a in pairs if not a['joint']['saved_forward_calls']],
            full_forward_calls_total=n,joint_recomputed_batch_pairs_total=k,
            patient_first_mean_joint_saved_forward_fraction=sum(means.values())/len(means),patient_mean_joint_saved_forward_fraction=means,
            five_same_support_actions_with_initialization_total_count_ratio=(n+5*k)/(5*n),
            all_nonempty_single_plane_actions=len([p for s,a in pairs for p in a['single_plane_actions']]),
            single_plane_actions_with_any_saving=sum(p['saved_forward_calls']>0 for s,a in pairs for p in a['single_plane_actions']),
            patient_first_mean_single_plane_saved_forward_fraction=sum(sum(sum(p['saved_forward_fraction'] for p in a['single_plane_actions'])/len(a['single_plane_actions']) for s,a in pairs if s['patient']==patient_id)/len([s for s,a in pairs if s['patient']==patient_id]) for patient_id in DEVELOPERS)/len(DEVELOPERS)))
    return result
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);started=time.perf_counter();path=OUT/'attempt01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],source_bindings=[],
        new_MRI_pixel_arrays_loaded=0,developer_label_arrays_loaded=0,validation_arrays_loaded=0,confirmation_patients_opened=False,
        model_forwards=0,GPU_forwards=0,training_updates=0,oracle_geometry_only=True,actual_speed_or_action_benefit_measured=False,
        publication_claim_confirmed=False,scientific_confirmation_patients=0,other_processes_modified=False)
    def guard():
        assert time.perf_counter()-started<=900;v=resource_guard();assert not torch.cuda.is_initialized()
        assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1
        assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<5_000_000;return v
    save(path,r)
    try:
        torch.set_num_threads(4);r['resources_before']=guard();prep=read(PREP);assert prep['complete'] and not prep['errors'];cases=prep['cases']
        assert len(cases)==19 and {x['patient'] for x in cases}==DEVELOPERS and len({x['uid'] for x in cases})==19
        sources=[Path(__file__),PROTOCOL,PREP,ROOT/'experiments/mc_rc_observed_only_training_input.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py']
        r['source_bindings']=[entry(p) for p in sources]
        for p in sources:(OUT/(p.name+'.source_snapshot')).write_bytes(p.read_bytes())
        save(path,r)
        for case in sorted(cases,key=lambda x:(x['patient'],x['uid'])):
            guard();label=read_supervised_label(case);r['developer_label_arrays_loaded']+=1
            z=np.arange(label.shape[2]);missing=(z%4!=0)&(z<(label.shape[2]-1)//4*4)
            grid=lattice(case);shape=tuple(n+sum(p) for n,p in zip(grid['unpadded_shape_zrc'],grid['padding']))
            locations,axes=tile_plan(shape);n=(len(locations)+1)//2
            record=dict(patient=case['patient'],uid=case['uid'],label_source=entry(ROOT/case['label_file']),native_shape_rcz=list(label.shape),
                label_array_sha256=array_sha(label),foreground_voxels=int(label.sum()),physical_grid=grid,
                physical_shape_zrc=list(shape),tile_locations_zrc=[list(v) for v in locations],full_forward_calls=n,supports=[])
            lo,hi=depth_dependencies(label.shape[2],grid['unpadded_shape_zrc'][0]);padz=grid['padding'][0][0]
            for variant,radius in [('missing_foreground',0),('missing_foreground_rc_radius2',2)]:
                native=label&missing[None,None,:]
                if radius:native=ndimage.binary_dilation(native,structure=np.ones((5,5,1),bool))
                assert not native[:,:,~missing].any();physical=physical_mr(native.astype(np.float32),grid)>0
                ids=[i for i,start in enumerate(locations) if physical[tuple(slice(s,s+p) for s,p in zip(start,PATCH))].any()]
                joint=cost(ids,locations);planes=[]
                for zi in np.flatnonzero(native.any(axis=(0,1))):
                    plane=native[:,:,zi];x=torch.from_numpy(plane.astype(np.float32))[None,None]
                    with torch.inference_mode():scaled=F.interpolate(x,size=grid['unpadded_shape_zrc'][1:],mode='bilinear',align_corners=False)[0,0].numpy()>0
                    scaled=np.pad(scaled,grid['padding'][1:],constant_values=False)
                    dz=np.flatnonzero((lo==zi)|(hi==zi))+padz;hits=[]
                    for i,(zz,rr,cc) in enumerate(locations):
                        if np.any((dz>=zz)&(dz<zz+PATCH[0])) and scaled[rr:rr+PATCH[1],cc:cc+PATCH[2]].any():hits.append(i)
                    planes.append(dict(z=int(zi),native_support_voxels=int(plane.sum()),**cost(hits,locations)))
                assert planes and sorted({i for p in planes for i in p['affected_tile_ids']})==ids
                record['supports'].append(dict(variant=variant,native_support_voxels=int(native.sum()),native_support_sha256=array_sha(native),
                    physical_support_voxels=int(physical.sum()),physical_support_sha256=array_sha(physical),joint=joint,single_plane_actions=planes,
                    sum_individual_plane_recomputed_batch_pairs=sum(p['recomputed_batch_pairs'] for p in planes),
                    one_joint_recomputed_batch_pairs=joint['recomputed_batch_pairs'],
                    count_ratio_all_single_plane_actions_with_initialization=(n+sum(p['recomputed_batch_pairs'] for p in planes))/(len(planes)*n)))
            r['series'].append(record);save(path,r)
        r.update(development_patients=len(DEVELOPERS),development_series=len(cases),total_tiles=sum(len(s['tile_locations_zrc']) for s in r['series']),
            summaries=summarize(r['series']),resources_after=guard(),cuda_initialized=torch.cuda.is_initialized(),complete=True)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-started,finished_utc=datetime.now(timezone.utc).isoformat());save(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','development_series','developer_label_arrays_loaded','summaries','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
