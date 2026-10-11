"""Evaluate only terminal paired last19998 models; readiness-only never loads MRI."""
import argparse,gc,json,sys,time,traceback
from mc_rc_3d_19series_final_eval_2026_10_07 import *
def main():
    sys.stdout.reconfigure(encoding='utf-8');ap=argparse.ArgumentParser();ap.add_argument('--readiness-only',action='store_true');a=ap.parse_args()
    status=readiness()
    if a.readiness_only or not status['ready']:
        print(json.dumps(dict(status='ready' if status['ready'] else 'execution_deferred',**status),ensure_ascii=False));return 0 if status['ready'] else 3
    torch.set_num_threads(4);started=time.perf_counter();OUT.mkdir(exist_ok=False)
    path=OUT/'evaluation_attempt01.json';r=dict(created_utc=now(),complete=False,errors=[],status='preparing',arms=[],
        script_sha256=sha(__file__),actual_training_updates=0,actual_gpu_updates=0,confirmation_patients_opened=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    def save():atomic_json(path,r)
    dump_new(path,r)
    try:
        r['resources_before']=guard(started);checkpoints,sources=frozen_training();cases=roles()
        r['planned_series_per_arm']=28;r['planned_prediction_files']=56
        sourcefiles=[ROOT/'experiments/mc_rc_3d_19series_final_eval_2026_10_07.py',Path(__file__),
            ROOT/'experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py']
        sources.extend(sourcefiles)
        for role,c,row in cases:
            sources.extend(ROOT/c[k] for k in ('header_file','mr_zip_file','label_file'));sources.append(ROOT/row['observed_package'])
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(sources))]
        r['formal_training_completed_updates']=39996;r['both_last_checkpoints_frozen']=True;save()
        for checkpoint in checkpoints:
            guard(started);cp=torch.load(ROOT/checkpoint['path'],map_location='cpu',weights_only=True)
            model=TaskUNet3D();model.load_state_dict(cp['state_dict']);model.eval();wrapped=GuardedModel(model,lambda:guard(started))
            arm=dict(kind=checkpoint['kind'],checkpoint_file=checkpoint['path'],checkpoint_sha256=checkpoint['sha256'],
                weights_sha256=checkpoint['state_hash'],complete=False,series=[]);r['arms'].append(arm);save()
            for index,(role,c,row) in enumerate(cases):
                guard(started);tick=time.perf_counter();normalized,stats=source_image(c,row,checkpoint['kind']);grid=lattice(c)
                image=physical_mr(normalized,grid);image_hash=array_sha(image);load_seconds=time.perf_counter()-tick;del normalized
                tick=time.perf_counter();probability,meta=infer_full_fov(wrapped,image,grid,c['native_shape'])
                inference_seconds=time.perf_counter()-tick;assert probability.dtype==np.float32 and np.isfinite(probability).all()
                assert list(probability.shape)==c['native_shape'];prediction=probability>=.5
                # Gold standard is loaded only after the complete prediction, never supplied to inference.
                label=read_reference_label(c);scored=metrics(prediction,label);dest=OUT/(checkpoint['kind']+'_'+str(index).zfill(2)+'.npz')
                pack_prediction(dest,prediction)
                record=dict(role=role,patient=c['patient'],uid=c['uid'],native_shape=c['native_shape'],physical_input_sha256=image_hash,
                    observed_statistics=stats,label_sha256=array_sha(label),probability_sha256=array_sha(probability),
                    prediction_sha256=array_sha(prediction),prediction_file=dest.relative_to(ROOT).as_posix(),prediction_file_sha256=sha(dest),
                    load_and_input_hash_seconds=load_seconds,inference_seconds=inference_seconds,inference=meta,metrics=scored)
                arm['series'].append(record);save();guard(started)
                print(json.dumps(dict(kind=arm['kind'],role=role,series_completed=len(arm['series']),full_dice=scored['full']['dice'])),flush=True)
                del image,probability,prediction,label;gc.collect()
            assert state_hash(model.state_dict())==checkpoint['state_hash'] and sha(ROOT/checkpoint['path'])==checkpoint['sha256']
            arm['development_aggregate']=aggregate([s for s in arm['series'] if s['role']=='development'],DEVELOPERS)
            arm['validation_aggregate']=aggregate([s for s in arm['series'] if s['role']=='validation'],VALIDATORS)
            arm['validation_gates']=gates(arm['validation_aggregate']);arm['all_validation_gates_passed']=all(arm['validation_gates'].values())
            arm['complete']=len(arm['series'])==28;save();del cp,model,wrapped;gc.collect()
        r.update(complete=all(a['complete'] for a in r['arms']) and len(r['arms'])==2,status='completed',
            prediction_files_saved=56,all_arms_validation_gates_passed=all(a['all_validation_gates_passed'] for a in r['arms']),
            cuda_initialized=torch.cuda.is_initialized(),resources_after=guard(started),last_models_not_selected_by_effect=True)
    except Exception as e:r['status']='failed';r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=now();r['elapsed_seconds']=time.perf_counter()-started;r['stage_saved_bytes']=stage_bytes();save()
    print(json.dumps({k:r.get(k) for k in ('status','complete','errors','all_arms_validation_gates_passed','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
