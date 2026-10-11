"""Actual tool terminal evidence plus checkpoint/journal/source audit; no neural forwards."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import read,sha,state_hash,torch,resource_guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();tool=HERE/'ACTUAL_PILOT_TERMINAL_TOOL.json';obs=read(tool)
    assert obs['exit_code']==0 and 'session_id' not in obs
    path=HERE/'attempt01/receipt.json';r=read(path);assert r['complete'] and r['status']=='completed' and not r['errors']
    assert r['new_cpu_updates']+r['new_GPU_updates']==396 and len(r['arms'])==4
    assert r['paired_labels_geometry_and_strong_primitives_verified']
    frozen=HERE/'attempt01/frozen_config.json';assert sha(frozen)==r['frozen_config_sha256']
    sources=[tool,path,frozen,Path(__file__)];histories={};arms=[]
    for b in r['source_bindings']:
        assert sha(ROOT/b['path'])==b['sha256'];sources.append(ROOT/b['path'])
    for a in r['arms']:
        assert a['complete'] and a['updates_completed']==99
        p=ROOT/a['checkpoint_path'];assert sha(p)==a['checkpoint_sha256'];sources.append(p)
        cp=torch.load(p,map_location='cpu',weights_only=True);assert state_hash(cp['state_dict'])==cp['final_weights_sha256']==a['final_weights_sha256']
        assert cp['starting_weights_sha256']==a['starting_weights_sha256'] and cp['updates']==99
        h=ROOT/a['history_path'];assert sha(h)==a['history_sha256']==cp['history_sha256'];sources.append(h)
        rows=[json.loads(line) for line in h.read_text().splitlines()];assert len(rows)==99
        assert [s['step'] for s in rows]==list(range(1,100));histories[a['name']]=rows
        arms.append(dict(name=a['name'],updates=99,checkpoint_file=a['checkpoint_path'],checkpoint_sha256=sha(p),history_file=a['history_path'],history_sha256=sha(h),final_weights_sha256=a['final_weights_sha256']))
    fields=('step','patient','uid','label_sha256','geometry','strong_primitives','lr')
    baseline=histories['native_reference_basic']
    for name,rows in histories.items():
        assert all({k:a[k] for k in fields}=={k:b[k] for k in fields} for a,b in zip(baseline,rows))
    for kind in ('native_reference','raw_pchip'):
        basic=histories[kind+'_basic'];strong=histories[kind+'_strong']
        assert all(a['basic_input_sha256']==b['basic_input_sha256'] for a,b in zip(basic,strong))
        aa=[a for a in r['arms'] if a['kind']==kind];assert aa[0]['starting_weights_sha256']==aa[1]['starting_weights_sha256']
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],observed_tool_exit=0,
        observed_tool_session=80513,observed_tool_chunk=obs['chunk_id'],result_file=path.relative_to(ROOT).as_posix(),result_sha256=sha(path),
        checkpoint_and_journal_audits_passed=True,all396_history_rows_verified=True,all99_paired_steps_verified=True,arms=arms,
        new_cpu_updates=r['new_cpu_updates'],new_GPU_updates=r['new_GPU_updates'],actual_device=r['device'],
        medical_effects_scored=False,neural_forwards_this_audit=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(sources))])
    with (HERE/'ACTUAL_PILOT_EXIT.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['source_bindings','arms']}),flush=True)
if __name__=='__main__':main()
