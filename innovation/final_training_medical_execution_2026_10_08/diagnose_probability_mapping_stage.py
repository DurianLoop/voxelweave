"""Full-FOV stage isolation on the first failed development case; old outputs stay fixed."""
import sys,json,time,gc,traceback,math
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'lossless_final_evaluation_entry_2026_10_08'))
import final_eval_lossless_v3 as g
import verify_final_lossless_v3 as replay
torch=g.torch;np=g.np
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(4);started=time.perf_counter()
    dest=HERE/'PROBABILITY_MAPPING_STAGE_DIAGNOSIS.json';assert not dest.exists()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        publication_claim_confirmed=False,goal_status='active',original_production_or_replay_files_modified=False,
        confirmation_patients_opened=False,lockedIXI_opened=False,new_training_updates=0,GPU_forwards=0)
    def check():
        assert time.perf_counter()-started<=600,'Diagnostic600s bound exceeded'
        return g.guard(started)
    try:
        check();models,sources=g.frozen_training();ep=g.OUT/'evaluation_attempt01.json';vp=g.OUT/'independent_all56_attempt01.json'
        q=g.read(ep);v=g.read(vp);assert q['complete'] and v['complete'] and not v['errors']
        caseby={c['uid']:(role,c,row) for role,c,row in g.roles()}
        fail=next(f for f in v['numerical_failures'] if caseby[f['uid']][0]=='development')
        role,c,row=caseby[fail['uid']];kind=fail['kind']
        checkpoint=next(m for m in models if m['kind']==kind)
        source=next(s for a in q['arms'] if a['kind']==kind for s in a['series'] if s['uid']==c['uid'])
        r.update(case_selection='first_recorded_development_numerical_failure',kind=kind,patient=c['patient'],uid=c['uid'],
            scope='one complete FOV diagnostic; not full56 acceptance',prior_failure=fail,
            source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=g.sha(p)) for p in sorted(set(sources+[ep,vp,Path(__file__)]))])
        cp=torch.load(ROOT/checkpoint['path'],map_location='cpu',weights_only=True)
        model=g.TaskUNet3D();model.load_state_dict(cp['state_dict']);model.eval()
        normalized,stats=g.source_image(c,row,kind);grid=g.lattice(c);image=g.physical_mr(normalized,grid);del normalized
        assert g.array_sha(image)==source['physical_input_sha256'] and stats==source['observed_statistics']
        captured={};tag={'value':'production'};original_interpolate=replay.F.interpolate
        def capture(input,*args,**kwargs):
            result=original_interpolate(input,*args,**kwargs)
            expected=(c['native_shape'][2],c['native_shape'][0],c['native_shape'][1])
            if kwargs.get('mode')=='trilinear' and tuple(kwargs.get('size',()))==expected:
                key=tag['value'];assert key not in captured
                captured[key]=input.detach().cpu().numpy()[0,0].copy()
            return result
        replay.F.interpolate=capture
        try:
            old,meta=g.infer_full_fov(g.GuardedModel(model,check),image,grid,c['native_shape'])
            assert g.array_sha(old)==source['probability_sha256'] and meta==source['inference']
            tag['value']='functional';ind,imeta=replay.functional_fov(cp['state_dict'],image,grid,c['native_shape'],check)
        finally:replay.F.interpolate=original_interpolate
        assert set(captured)=={'production','functional'} and captured['production'].dtype==np.float32
        pp=captured['production'];fp=np.ascontiguousarray(captured['functional'],dtype=np.float32)
        assert pp.shape==fp.shape
        physical_error=float(np.max(np.abs(pp.astype(np.float64)-fp.astype(np.float64))))
        same_field_numpy=replay.independent_native_resample(pp,c['native_shape'])
        check()
        with torch.inference_mode():
            mapped=original_interpolate(torch.from_numpy(pp.astype(np.float64))[None,None],
                size=(c['native_shape'][2],c['native_shape'][0],c['native_shape'][1]),mode='trilinear',align_corners=False)[0,0].numpy()
        prototype=np.ascontiguousarray(mapped.transpose(1,2,0),dtype=np.float32)
        def compare(a,b):return dict(max_probability_error=float(np.max(np.abs(a-b))),threshold_disagreements=int(np.count_nonzero((a>=.5)!=(b>=.5))))
        old_functional=compare(old,ind);old_numpy=compare(old,same_field_numpy)
        proto_numpy=compare(prototype,same_field_numpy);proto_functional=compare(prototype,ind)
        r.update(complete=True,resources_after=check(),old_production_probability_hash_replayed=True,
            physical_probability_shape=list(pp.shape),physical_probability_max_error=physical_error,
            physical_probability_fields_identical=g.array_sha(pp)==g.array_sha(fp),
            old_production_vs_functional=old_functional,old_production_vs_numpy64_same_physical_field=old_numpy,
            torch64_coordinate_prototype_vs_numpy64_same_physical_field=proto_numpy,
            torch64_coordinate_prototype_vs_functional=proto_functional,
            functional_float64_coordinate_check=imeta,
            mapping_precision_cause_supported_for_this_case=physical_error==0 and old_numpy==old_functional,
            prototype_case_strict_gate_passed=proto_functional['max_probability_error']<=3e-6 and proto_functional['threshold_disagreements']==0 and imeta['float64_coordinate_gate_passed'],
            deployment_or_full56_acceptance_established=False,medical_input_arrays_loaded=1,GT_arrays_loaded=0,
            full_fov_neural_passes=2,full_fov_tiles_each=meta['total_tiles'],cuda_initialized=torch.cuda.is_initialized())
        assert g.state_hash(model.state_dict())==checkpoint['state_hash'];del model,cp,image,old,ind,prototype,same_field_numpy;gc.collect()
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started
    g.dump_new(dest,r)
    print(json.dumps({k:r.get(k) for k in ['complete','errors','case_selection','patient','physical_probability_max_error',
        'physical_probability_fields_identical','old_production_vs_functional','old_production_vs_numpy64_same_physical_field',
        'torch64_coordinate_prototype_vs_functional','mapping_precision_cause_supported_for_this_case','prototype_case_strict_gate_passed','elapsed_seconds']},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
