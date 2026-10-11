"""Require a real managed-tool exit, then audit all last2992 states and 11968 journal rows."""
import gzip,json,math,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import read,sha,state_hash,torch,np,resource_guard,array_sha
from datetime import datetime,timezone
STEPS=2992;NAMES=['native_reference_intensity','native_reference_spatial','raw_pchip_intensity','raw_pchip_spatial']

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    terminal=HERE/'ACTUAL_TRAINING_TERMINAL_TOOL.json';obs=read(terminal)
    assert obs['exit_code']==0 and 'session_id' not in obs
    assert obs['observed_unified_exec_session']==29823
    assert not (HERE/'ACTUAL_TRAINING_EXIT.json').exists()
    path=HERE/'training_attempt01/receipt.json';r=read(path)
    assert r['complete'] and r['status']=='completed' and not r['errors']
    assert r['new_cpu_updates']+r['new_GPU_updates']==11968 and [a['name'] for a in r['arms']]==NAMES
    assert r['mother_labels_geometry_and_augmentation_primitives_paired'] and r['cross_input_spatial_labels_paired']
    frozen=HERE/'training_attempt01/frozen_config.json';q=read(frozen);assert sha(frozen)==r['frozen_config_sha256']
    assert q['steps_per_branch']==STEPS and q['branches']==NAMES
    sources={terminal,path,frozen,Path(__file__)}
    for b in r['source_bindings']:assert sha(ROOT/b['path'])==b['sha256'];sources.add(ROOT/b['path'])
    original=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
    config=read(original/'frozen_config.json');schedule=np.load(original/config['schedule_file'],allow_pickle=False)[:STEPS]
    assert array_sha(schedule)==q['schedule_prefix_sha256']
    assert all(int(np.count_nonzero(schedule[:,0]==i))==272 for i in range(11))
    histories={};arms=[]
    for a in r['arms']:
        resource_guard();assert time.perf_counter()-started<180
        assert a['complete'] and a['updates_completed']==STEPS and a['starting_original_updates']==19998 and a['optimizer_reset']
        cpfile=ROOT/a['checkpoint_path'];log=ROOT/a['history_path'];sources.update([cpfile,log])
        assert sha(cpfile)==a['checkpoint_sha256'] and sha(log)==a['history_sha256'] and log.stat().st_size==a['history_bytes']
        cp=torch.load(cpfile,map_location='cpu',weights_only=True)
        assert state_hash(cp['state_dict'])==cp['final_weights_sha256']==a['final_weights_sha256']
        assert cp['kind']==a['kind'] and cp['augmentation']==a['augmentation'] and cp['updates']==STEPS
        assert cp['starting_original_updates']==19998 and cp['starting_weights_sha256']==a['starting_weights_sha256']
        assert cp['history_sha256']==sha(log) and cp['frozen_config_sha256']==sha(frozen) and cp['protocol_sha256']==sha(HERE/'PROTOCOL.md')
        assert cp['final_weights_sha256']!=cp['starting_weights_sha256'] and all(torch.isfinite(v).all() for v in cp['state_dict'].values())
        with gzip.open(log,'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
        assert len(rows)==STEPS and [h['step'] for h in rows]==list(range(1,STEPS+1))
        exposures={p:0 for p in config['patient_ids']}
        for step,h in enumerate(rows,1):
            pi,ci=map(int,schedule[step-1]);assert h['patient']==config['patient_ids'][pi] and h['uid']==config['series'][ci]['uid']
            assert h['lr']==1e-4 and math.isfinite(h['loss']) and h['total_step_seconds']>0;exposures[h['patient']]+=1
            if a['augmentation']=='intensity':
                assert h['theta_normalized_xyz'] is None and h['training_label_sha256']==h['mother_label_sha256']
            else:assert h['theta_normalized_xyz'] is not None
        assert set(exposures.values())=={272};histories[a['name']]=rows
        arms.append(dict(name=a['name'],kind=a['kind'],augmentation=a['augmentation'],updates=STEPS,patient_exposures=exposures,
            checkpoint_path=a['checkpoint_path'],checkpoint_sha256=sha(cpfile),history_path=a['history_path'],history_sha256=sha(log),
            starting_weights_sha256=a['starting_weights_sha256'],final_weights_sha256=a['final_weights_sha256']))
        del cp
    fields=('step','patient','uid','mother_label_sha256','geometry','spatial_primitives','intensity_primitives','pivots_zrc','lr')
    reference=histories[NAMES[0]]
    for rows in histories.values():assert all({k:a[k] for k in fields}=={k:b[k] for k in fields} for a,b in zip(reference,rows))
    for kind in ['native_reference','raw_pchip']:
        ia=histories[kind+'_intensity'];sa=histories[kind+'_spatial']
        assert all(a['base_input_sha256']==b['base_input_sha256'] for a,b in zip(ia,sa))
        aa=[a for a in arms if a['kind']==kind];assert aa[0]['starting_weights_sha256']==aa[1]['starting_weights_sha256']
    assert all(a['training_label_sha256']==b['training_label_sha256'] and a['theta_normalized_xyz']==b['theta_normalized_xyz']
        for a,b in zip(histories['native_reference_spatial'],histories['raw_pchip_spatial']))
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],observed_tool_exit=0,
        observed_tool_session=29823,observed_tool_chunk=obs['chunk_id'],result_file=path.relative_to(ROOT).as_posix(),result_sha256=sha(path),
        checkpoint_and_journal_audits_passed=True,all11968_history_rows_verified=True,all2992_paired_steps_verified=True,
        arms=arms,new_cpu_updates=r['new_cpu_updates'],new_GPU_updates=r['new_GPU_updates'],actual_device=r['device'],
        medical_effects_scored=False,neural_forwards_this_audit=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(sources)])
    with (HERE/'ACTUAL_TRAINING_EXIT.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['arms','source_bindings']}),flush=True)
if __name__=='__main__':main()
