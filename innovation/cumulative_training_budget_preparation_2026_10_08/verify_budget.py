"""Independent integer/sha replay; does not import budget_ledger or execute CPU markers."""
import sys,json,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'independent_attempt01'
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8');tick=time.perf_counter();resource_guard()
    OUT.mkdir(exist_ok=False);q=load(HERE/'attempt01/receipt.json')
    assert q['complete'] and not q['errors'] and q['actual_work_child_exits']==[0,0,0,17]
    for b in q['source_bindings']:
        p=ROOT/b['path'];assert bind(p)==b
    arms=['legacy_dense','direct','common_projected_dense'];normal=HERE/'attempt01/normal'
    head='GENESIS';paid=0;counts={a:0 for a in arms};actual_total=0;rows=[]
    for n,observation in enumerate(q['normal_transactions'],1):
        p=normal/f'invocation{n:04d}_receipt.json';r=load(p)
        assert r['invocation']==n and r['parent_sha256']==head and r['contract_sha256']==sha(HERE/'attempt01/contract.json')
        for b in r['sources']:
            source=HERE/b['name'];assert source.stat().st_size==b['bytes'] and sha(source)==b['sha256']
        journal=normal/r['journal']['name'];assert journal.stat().st_size==r['journal']['bytes'] and sha(journal)==r['journal']['sha256']
        events=[json.loads(s) for s in journal.read_text(encoding='utf-8').splitlines()];assert len(events)==3
        for e,arm in zip(events,arms):
            counts[arm]+=1;token=f'synthetic-common-step-{counts[arm]}'
            assert e['arm']==arm and e['step']==counts[arm] and e['shared_token']==token
            assert e['digest']==hashlib.sha256(token.encode('ascii')).hexdigest() and e['work_kind']=='sha256_cpu_marker'
        assert r['duration_ns']>0 and r['close_allowance_ns']==1_000_000_000 and r['charged_ns']==r['duration_ns']+1_000_000_000
        paid+=r['charged_ns'];assert paid==r['cumulative_paid_ns'] and counts==r['cumulative_units']
        close=load(normal/r['close_proof']);assert close['receipt_sha256']==sha(p)
        assert 0<=close['observed_close_prefix_ns']<=r['close_allowance_ns']
        actual=observation['actual_controller_ns_through_seal'];assert 0<actual<=r['charged_ns']
        actual_total+=actual;assert observation['actual_child_exit']==0 and observation['sealed']
        head=sha(p);rows.append(dict(invocation=n,paid_ns=paid,actual_ns=actual,counts=dict(counts)))
    assert paid==q['final_normal_state']['paid_ns'] and head==q['final_normal_state']['head']
    assert counts==dict.fromkeys(arms,3) and paid>actual_total and paid<=60_000_000_000
    assert paid+60_000_000_000>60_000_000_000 and q['budget_probe']['rejected']
    assert q['fresh_process_state_probe']['accepted'] and q['fresh_process_state_probe']['state']['paid_ns']==rows[0]['paid_ns']
    assert q['fresh_process_state_probe']['actual_process_exit']==0
    assert q['actual_validation_subprocesses_launched']==7 and q['actual_total_child_processes_launched']==11
    assert q['quota_probe']['rejected'] and all(f['rejected'] and f['new_CPU_work_units']==0 for f in q['faults'])
    crash=HERE/'attempt01/unsealed_failure';pending=load(crash/'pending.json')
    assert pending['prior_paid_ns']==rows[0]['paid_ns'] and pending['prior_units']==dict.fromkeys(arms,1)
    assert (crash/'invocation0002_journal.jsonl').is_file() and not (crash/'invocation0002_receipt.json').exists()
    events=[json.loads(s) for s in (crash/'invocation0002_journal.jsonl').read_text(encoding='utf-8').splitlines()]
    assert [e['arm'] for e in events]==arms and all(e['step']==2 for e in events)
    failed=load(crash/'failure_observation.json');assert failed['actual_child_exit']==17 and failed['actual_CPU_work_units']==3
    assert failed['known_failed_controller_elapsed_ns']>0 and q['unsealed_resume_probe']['rejected']
    assert q['actual_CPU_work_units']==sum(t['actual_CPU_work_units'] for t in q['normal_transactions'])+3==12
    assert 'budget_ledger' not in sys.modules and 'torch' not in sys.modules and 'numpy' not in sys.modules
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[bind(p) for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'attempt01/receipt.json')],
        independent_rows=rows,cumulative_paid_ns=paid,actual_recorded_normal_controller_ns=actual_total,
        cumulative_charge_conservative_bound_verified=True,normal_work_units_replayed=9,crash_work_units_replayed=3,
        markers_executed_by_verifier=0,child_processes_launched_by_verifier=0,new_core_imported=False,
        medical_arrays_loaded=0,checkpoint_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        formal_medical_budget_frozen=False,formal_medical_long_runner_qualified=False,
        publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-tick)
    with (OUT/'receipt.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,cumulative_paid_ns=paid,actual_recorded_normal_controller_ns=actual_total,
        independent_normal_markers_replayed=9,crash_markers_replayed=3,new_core_imported=False,
        markers_executed_by_verifier=0,elapsed_seconds=r['elapsed_seconds'])),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
