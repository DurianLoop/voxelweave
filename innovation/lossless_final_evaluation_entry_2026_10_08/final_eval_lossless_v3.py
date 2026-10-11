"""Final-evaluation contract, safe packing and patient-first endpoints; no effects at import."""
import gc,json,math,os,time
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'experiments'))
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,lattice,physical_mr,
    read_reference_label,TaskUNet3D,infer_full_fov,torch,np,PATCH,SEED,tile_plan)
from mc_rc_true_native_reference_v2_2026_10_07 import DEVELOPERS,VALIDATORS
from mc_rc_3d_independent_replay_2026_10_07 import logical_counts
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
from datetime import datetime,timezone
TRAIN=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
HERE=Path(__file__).resolve().parent
OUT=HERE/'medical_attempt03'
PROTOCOL=HERE/'PROTOCOL.md'
FINAL_EXIT=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json'
EVAL_EXIT=HERE/'OBSERVED_EVALUATION_EXIT_V3.json'
KINDS=('native_reference','raw_pchip')
DOMAINS=('full','anchors','missing','tail')
FIELDS=('dice','precision','recall','signed_relative_volume_error','absolute_relative_volume_error')
def now():return datetime.now(timezone.utc).isoformat()
def dump_new(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def atomic_json(p,d):
    t=p.with_name(p.name+'.tmp')
    with t.open('w',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(t,p)
def stage_bytes():return sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()) if OUT.exists() else 0
def guard(started):
    assert time.perf_counter()-started<=3600,'Frozen 3600s evaluation/replay wall-clock bound exceeded'
    r=resource_guard();r['cpu_threads']=torch.get_num_threads()
    assert r['cpu_threads']==4 and torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
    assert stage_bytes()<=250000000,'Shared final postprocessing stage storage bound exceeded'
    r['stage_saved_bytes']=stage_bytes();return r
def roles():
    cases=sorted(fixed_cases(),key=lambda item:(item[0],item[1]['patient'],item[1]['uid']))
    assert len(cases)==28 and len({c['uid'] for role,c,row in cases})==28
    assert {c['patient'] for role,c,row in cases if role=='development'}==DEVELOPERS
    assert {c['patient'] for role,c,row in cases if role=='validation'}==VALIDATORS
    assert sum(role=='development' for role,c,row in cases)==19 and sum(role=='validation' for role,c,row in cases)==9
    return cases
def readiness():
    reasons=[];p=TRAIN/'invocation02.json'
    if not (HERE/'compression_qualification_v3/receipt.json').exists():reasons.append('Lossless packing qualification receipt absent')
    if not FINAL_EXIT.exists():reasons.append('Final actual-tool-exit receipt absent')
    if not p.exists():reasons.append('Final training result absent')
    else:
        q=read(p)
        if not q.get('complete') or q.get('status')!='completed_segment' or q.get('errors'):
            reasons.append('Full training is not a successful terminal result')
        if not q.get('formal_final_budget_completed') or not q.get('all_last_weights_frozen'):
            reasons.append('Both last19998 weights are not frozen')
    for kind in KINDS:
        if not (TRAIN/(kind+'_last19998.pt')).exists():reasons.append(kind+' final checkpoint absent')
    return dict(ready=not reasons,reasons=reasons,MR_or_GT_arrays_loaded=0,CUDA_initialized=torch.cuda.is_initialized())
def frozen_training():
    qualification=read(HERE/'compression_qualification_v3/receipt.json')
    assert qualification['complete'] and not qualification['errors'] and qualification['all_lossless_interoperability_checks_passed']
    for b in qualification['production_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    status=readiness();assert status['ready'],json.dumps(status)
    qpath=TRAIN/'invocation02.json';q=read(qpath);ex=read(FINAL_EXIT);old=read(TRAIN/'invocation01.json');config=read(TRAIN/'frozen_config.json')
    assert ex['training_observed_tool_exit']==0 and ex['training_result_file']==qpath.relative_to(ROOT).as_posix()
    assert ex['training_result_sha256']==sha(qpath) and ex['formal_training_updates']==39996
    assert q['new_cpu_backbone_updates']==39798 and old['new_cpu_backbone_updates']==198
    assert q['total_formal_updates_so_far']==39996 and q['stop_after']==19998 and q['paired_GT_and_augmentation_identical']
    assert q['both_last_checkpoints_frozen_utc'] and not q['task_effects_scored'] and not q['cuda_initialized']
    assert q['frozen_config_sha256']==sha(TRAIN/'frozen_config.json')
    assert config['planned_updates_per_arm']==19998 and sha(ROOT/config['protocol_file'])==config['protocol_sha256']
    for b in config['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    assert sha(TRAIN/config['schedule_file'])==config['schedule_file_sha256']
    draws=np.load(TRAIN/config['schedule_file'],allow_pickle=False);assert array_sha(draws)==config['schedule_array_sha256']
    histories=[];checkpoints=[];sources=[qpath,TRAIN/'invocation01.json',TRAIN/'frozen_config.json',TRAIN/config['schedule_file'],FINAL_EXIT,PROTOCOL]
    for kind in KINDS:
        a=next(a for a in q['arms'] if a['kind']==kind);cpfile=ROOT/a['final_checkpoint_file']
        assert a['updates_completed']==19998 and a['complete'] and sha(cpfile)==a['final_checkpoint_sha256']
        cp=torch.load(cpfile,map_location='cpu',weights_only=True)
        assert cp['kind']==kind and cp['updates_completed']==19998 and cp['initial_weights_sha256']==config['initial_weights_sha256']
        assert cp['frozen_config_sha256']==sha(TRAIN/'frozen_config.json') and state_hash(cp['state_dict'])==cp['final_weights_sha256']==a['final_weights_sha256']
        histfile=TRAIN/(kind+'_history.jsonl');assert sha(histfile)==cp['history_sha256']
        with histfile.open(encoding='utf-8') as f:history=[json.loads(line) for line in f if line.strip()]
        assert len(history)==19998
        for step,h in enumerate(history,1):
            pi,ci=map(int,draws[step-1]);assert h['update']==step and h['patient']==config['patient_ids'][pi] and h['uid']==config['series'][ci]['uid']
            assert h['lr']==.0001 and math.isfinite(h['loss']) and h['total_update_seconds']>0
        resume=TRAIN/(kind+'_resume.pt');rc=torch.load(resume,map_location='cpu',weights_only=True)
        assert rc['updates_completed']==19998 and rc['history_sha256']==sha(histfile) and rc['final_weights_sha256']==cp['final_weights_sha256']
        assert state_hash(rc['state_dict'])==cp['final_weights_sha256'] and all(torch.isfinite(v).all() for v in cp['state_dict'].values())
        assert len(rc['optimizer_state_dict']['state'])==len(rc['state_dict'])
        assert all(float(v['step'])==19998 and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all()
            and (v['exp_avg_sq']>=0).all() for v in rc['optimizer_state_dict']['state'].values())
        assert all(g['lr']==.0001 and g['weight_decay']==.0001 for g in rc['optimizer_state_dict']['param_groups'])
        histories.append(history);checkpoints.append(dict(kind=kind,path=cpfile.relative_to(ROOT).as_posix(),sha256=sha(cpfile),
            state_hash=cp['final_weights_sha256']));sources.extend((cpfile,histfile,resume));del cp,rc;gc.collect()
    keys=('update','patient','uid','label_sha256','label_foreground','augmentation_primitive')
    assert all({k:a[k] for k in keys}=={k:b[k] for k in keys} for a,b in zip(*histories))
    sources.extend(ROOT/b['path'] for b in config['source_bindings']);sources.extend([HERE/'compression_qualification_v3/receipt.json',
        HERE/'final_eval_lossless_v3.py',HERE/'evaluate_final_lossless_v3.py',HERE/'verify_final_lossless_v3.py',HERE/'REPAIR_V3.md',
        ROOT/'experiments/mc_rc_3d_19series_final_eval_2026_10_07.py',
        ROOT/'experiments/evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py',
        ROOT/'experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py']);return checkpoints,sources
def domain_masks(shape):
    z=np.arange(shape[2]);anchors=z%4==0;last=int(z[anchors][-1]);missing=(z<last)&~anchors;tail=z>last
    assert np.all(anchors.astype(int)+missing.astype(int)+tail.astype(int)==1)
    return dict(full=np.ones(len(z),bool),anchors=anchors,missing=missing,tail=tail)
def metrics(prediction,gt):
    assert prediction.dtype==gt.dtype==bool and prediction.shape==gt.shape
    result={}
    for name,m in domain_masks(gt.shape).items():
        c=logical_counts(prediction[:,:,m],gt[:,:,m]);c.update(voxels=int(gt[:,:,m].size),
            signed_relative_volume_error=(c['pred_foreground']-c['gt_foreground'])/c['gt_foreground'] if c['gt_foreground'] else None,
            absolute_relative_volume_error=c['absRVE']);result[name]=c
        assert c['tp']+c['fp']+c['fn']+c['tn']==c['voxels']
    for k in ('tp','fp','fn','tn','voxels','gt_foreground','pred_foreground'):
        assert result['full'][k]==sum(result[d][k] for d in ('anchors','missing','tail'))
    return result
def pack_prediction(path,prediction):
    p=np.packbits(prediction.reshape(-1),bitorder='little');assert p.nbytes==(prediction.size+7)//8
    np.savez_compressed(path,packed_prediction=p,shape=np.asarray(prediction.shape,dtype=np.int64),bitorder=np.asarray('little'),
        prediction_sha256=np.asarray(array_sha(prediction)))
    assert np.array_equal(unpack_prediction(path),prediction)
def unpack_prediction(path):
    with np.load(path,allow_pickle=False) as d:
        shape=tuple(map(int,d['shape']));assert len(shape)==3 and min(shape)>0 and str(d['bitorder'])=='little'
        p=d['packed_prediction'];assert p.dtype==np.uint8 and p.shape==((math.prod(shape)+7)//8,)
        result=np.unpackbits(p,count=math.prod(shape),bitorder='little').reshape(shape).astype(bool)
        assert array_sha(result)==str(d['prediction_sha256'])
    return result
def aggregate(rows,patients):
    assert {r['patient'] for r in rows}==set(patients);groups={}
    for patient in sorted(patients):
        rr=[r for r in rows if r['patient']==patient];vals={}
        for d in DOMAINS:
            vals[d]={}
            for f in FIELDS:
                v=[r['metrics'][d][f] for r in rr];vals[d][f]=sum(v)/len(v) if all(x is not None for x in v) else None
                vals[d][f+'_defined_series']=sum(x is not None for x in v)
        groups[patient]=dict(series=len(rr),metrics=vals)
    means={}
    for d in DOMAINS:
        means[d]={}
        for f in FIELDS:
            v=[groups[p]['metrics'][d][f] for p in sorted(patients)]
            means[d][f]=sum(v)/len(v) if all(x is not None for x in v) else None
            means[d][f+'_defined_patients']=sum(x is not None for x in v)
    return dict(patients=groups,patient_first_means=means,
        complete_miss_series=[r['uid'] for r in rows if r['metrics']['full']['tp']==0],
        empty_prediction_series=[r['uid'] for r in rows if r['metrics']['full']['empty_prediction']])
def gates(a):
    f=a['patient_first_means']['full'];m=a['patient_first_means']['missing']
    return dict(mean_full_dice_ge_070=f['dice'] is not None and f['dice']>=.70,
        mean_missing_dice_ge_065=m['dice'] is not None and m['dice']>=.65,
        mean_full_recall_ge_070=f['recall'] is not None and f['recall']>=.70,
        mean_full_absRVE_le_050=f['absolute_relative_volume_error'] is not None and f['absolute_relative_volume_error']<=.50,
        all_four_patient_full_missing_dice_positive=all(p['metrics'][d]['dice'] is not None and p['metrics'][d]['dice']>0
            for p in a['patients'].values() for d in ('full','missing')),
        no_series_complete_miss=not a['complete_miss_series'])
class GuardedModel(torch.nn.Module):
    def __init__(self,model,check):super().__init__();self.model=model;self.check=check
    def forward(self,x):self.check();return self.model(x)
