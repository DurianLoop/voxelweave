"""Independent D4 numbered-plane geometry and original-sampler all4000 replay."""
import sys,json,hashlib,traceback
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT,SEED,read,sha,array_sha,load_authenticated_observed,sparse_image,physical_shape,
    resize_image,resize_training_label,training_example,context_plane,np,torch,F)
from mc_rc_task_metrics_cpu import independent_label
OUT=ROOT/'experiments/mc_rc_coverage_augmentation_draw_cpu'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(example):
    h=hashlib.sha256()
    for value in example[:4]:h.update(array_sha(value.numpy()).encode())
    h.update(json.dumps(dict(locations=example[4],shape=example[5],record=example[6]),sort_keys=True).encode());return h.hexdigest()
def spatial(value,record):
    if record['flip_rows']:value=np.flip(value,-2)
    if record['flip_cols']:value=np.flip(value,-1)
    return np.rot90(value,record['rot90'],axes=(-2,-1))
def reference_example(item,record,arm):
    plane=context_plane(item['image_zrc'],record['z'],item['zspacing']);target=item['label_zrc'][record['z']]
    if arm.endswith('_aug'):
        plane=spatial(plane,record)*record['scale']+record['shift'];target=spatial(target,record)
    plane=np.ascontiguousarray(plane,dtype=np.float32);target=np.ascontiguousarray(target,dtype=np.float32)
    locations=[tuple(v) for v in record[('coverage' if arm.startswith('coverage') else 'legacy')+('_augmented_locations' if arm.endswith('_aug') else '_native_locations')]]
    x=torch.from_numpy(np.stack([plane[:,r:r+128,c:c+128] for r,c in locations]))
    y=torch.from_numpy(np.stack([target[r:r+128,c:c+128][None] for r,c in locations]))
    gv=F.interpolate(torch.from_numpy(plane)[None],size=(256,256),mode='bilinear',align_corners=False)
    gt=F.interpolate(torch.from_numpy(target)[None,None],size=(256,256),mode='area')
    return gv,x,y,gt,locations,target.shape,dict(z=record['z'],foreground_plane=record['foreground_plane'])
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();source=OUT/'attempt_01.json';r=read(source)
    assert r['complete'] and not r['errors'];path=OUT/'independent_all4000_geometry_and_inputs_attempt_01.json';assert not path.exists()
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),result_sha256=sha(source),
        legacy_original_sampler_matches=0,all_arm_real_input_sha_checks=0,full_patch_geometry_checks=0,
        per_z_coverage_tile_exposure={},per_z_updates={},sampler_reference='Original frozen training_example; not new production primitive generator.',
        geometry_reference='Numbered whole plane flipped/rotated, all16384 patch source pixels; no rectangle matrix used to construct reference.',
        network_forward_calls=0,training_updates=0,native_hidden_MR_pixels_decoded=False,
        confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,q)
    try:
        assert r['draws_completed']==4000 and r['legacy_exact_matches']==4000 and len(r['rows'])==4000 and r['legacy_baseline_exact_reuse_eligible']
        for binding in r['source_bindings']:assert sha(ROOT/binding['path'])==binding['sha256']
        assert sha(ROOT/r['protocol_file'])==r['protocol_sha256']
        assert sha(ROOT/'experiments/prepare_mc_rc_coverage_augmentation_draw_cpu.py')==r['script_sha256']
        assert sha(ROOT/'experiments/mc_rc_coverage_augmentation_draw_cpu_support.py')==r['draw_support_sha256']
        old=read(ROOT/r['source_bindings'][0]['path']);case=r['case_binding'];assert case['patient']=='VS-MC-RC-012'
        row=next(v for v in read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json')['series'] if v['uid']==case['uid'])
        obs=load_authenticated_observed(case,row);native,_=sparse_image(obs,'raw_pchip',row);label=independent_label(case)
        shape,spacing=physical_shape(case);image=resize_image(native,shape);target=resize_training_label(label,shape)
        item=dict(image_zrc=image,label_zrc=target,native_foreground=np.argwhere(label),zspacing=spacing)
        assert array_sha(native)==r['input_binding']['native_input_sha256'] and array_sha(image)==r['input_binding']['physical_input_sha256']
        assert array_sha(label)==r['input_binding']['native_label_sha256'] and array_sha(target)==r['input_binding']['physical_label_sha256']
        axes=[sorted(set(range(0,n-127,96))|{n-128}) for n in shape];tiles=[(rr,cc) for rr in axes[0] for cc in axes[1]]
        numbered=np.arange(shape[0]*shape[1],dtype=np.int32).reshape(shape);cache={}
        for fr in (False,True):
            for fc in (False,True):
                for k in range(4):
                    desc=dict(flip_rows=fr,flip_cols=fc,rot90=k);grid=spatial(numbered,desc)
                    positions=[np.argwhere(grid==v)[0] for v in (0,shape[1],1)]
                    p0,pr,pc=positions;matrix=np.array([[pr[0]-p0[0],pc[0]-p0[0],p0[0]],[pr[1]-p0[1],pc[1]-p0[1],p0[1]],[0,0,1]],np.int64)
                    cache[(fr,fc,k)]=(grid,matrix)
        rng=np.random.default_rng(SEED);stream=hashlib.sha256()
        for step,record in enumerate(r['rows']):
            if step%100==0:resource_gate()
            assert record['step']==step
            rng.integers(1);rng.integers(1);oldexample=training_example(item,rng)
            assert digest(oldexample)==old['arms'][0]['draw_sha256'][step]==record['example_sha256_by_arm']['legacy_aug'];q['legacy_original_sampler_matches']+=1
            assert oldexample[4]==[tuple(v) for v in record['legacy_augmented_locations']]
            grid,matrix=cache[(record['flip_rows'],record['flip_cols'],record['rot90'])]
            assert np.array_equal(matrix,record['augmentation_matrix_rc'])
            for prefix in ('legacy','coverage'):
                for a,b in zip(record[prefix+'_native_locations'],record[prefix+'_augmented_locations']):
                    nr,nc=a;ar,ac=b
                    plain=numbered[nr:nr+128,nc:nc+128];aug=grid[ar:ar+128,ac:ac+128]
                    assert plain.shape==aug.shape==(128,128) and np.array_equal(spatial(plain,record),aug)
                    q['full_patch_geometry_checks']+=1
            z=str(record['z']);oldcount=q['per_z_updates'].get(z,0);expected_ids=[(2*oldcount+j)%len(tiles) for j in range(2)]
            assert expected_ids==record['coverage_tile_ids']
            assert record['coverage_native_locations']==[list(tiles[i]) for i in expected_ids]
            q['per_z_updates'][z]=oldcount+1;exposure=q['per_z_coverage_tile_exposure'].setdefault(z,{})
            for i in expected_ids:exposure[str(i)]=exposure.get(str(i),0)+1
            if record['foreground_z_selected']:assert int(item['native_foreground'][record['foreground_voxel_index'],2])==record['z']
            for arm in r['arms']:
                example=reference_example(item,record,arm)
                assert digest(example)==record['example_sha256_by_arm'][arm]
                assert float(example[2].sum())==r['foreground_mass_by_arm'][arm][step];q['all_arm_real_input_sha_checks']+=1
            stream.update(hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest().encode())
            if (step+1)%500==0:write(path,q);print(json.dumps(dict(draws_verified=step+1,full_patch_geometry_checks=q['full_patch_geometry_checks'])),flush=True)
        assert stream.hexdigest()==r['record_stream_sha256'] and q['per_z_updates']==r['per_z_updates'] and q['per_z_coverage_tile_exposure']==r['per_z_coverage_tile_exposure']
        assert sha(ROOT/r['legacy_baseline_checkpoint_file'])==r['legacy_baseline_checkpoint_sha256']
        q['legacy_baseline_exact_reuse_verified']=True;q['gpu_initialized']=torch.cuda.is_initialized();assert not q['gpu_initialized']
        q['complete']=q['legacy_original_sampler_matches']==4000 and q['all_arm_real_input_sha_checks']==16000 and q['full_patch_geometry_checks']==16000
    except Exception as error:q['errors'].append(type(error).__name__+': '+str(error));q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,q)
    print(json.dumps({k:q.get(k) for k in ('complete','errors','legacy_original_sampler_matches','all_arm_real_input_sha_checks','full_patch_geometry_checks','gpu_initialized')}),flush=True)
    return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
