"""Actual own-child CPU transactions and failure fixtures; no medical or neural work."""
import sys,json,time,subprocess,shutil,os
from pathlib import Path
from datetime import datetime,timezone
import budget_ledger as core
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'attempt01'
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def guard(start):
    q=resource_guard();assert q['workspace_free_bytes']>=8_002_000_000
    assert time.perf_counter()-start<600
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    assert 'torch' not in sys.modules and 'numpy' not in sys.modules
    return q
def reject(fn):
    try:fn()
    except core.Rejected as e:return dict(rejected=True,reason=str(e),new_CPU_work_units=0,neural_imported=False)
    raise AssertionError('Fault accepted')
def fresh_probe(label,directory,cp,head,reserve=None):
    cmd=[sys.executable,'-X','utf8','-B',str(HERE/'probe_state.py'),'--directory',str(directory),
         '--contract',str(cp),'--expected-head',head]
    if reserve is not None:cmd+=['--reserve-ns',str(reserve)]
    proc=subprocess.run(cmd,capture_output=True,timeout=20,creationflags=0x08004000)
    (OUT/(label+'_stdout.txt')).write_bytes(proc.stdout);(OUT/(label+'_stderr.txt')).write_bytes(proc.stderr)
    result=json.loads(proc.stdout.decode('utf-8'));result['actual_process_exit']=proc.returncode
    result['new_CPU_work_units']=result['actual_CPU_work_units']
    assert proc.returncode==(3 if result['rejected'] else 0) and result['actual_CPU_work_units']==0
    assert not result['torch_imported'] and not result['numpy_imported']
    return result
def run_child(directory,cp,head,crash,outer_start):
    guard(outer_start)
    s,p=core.begin(directory,cp,head,1_000_000_000)
    journal=directory/f"invocation{p['invocation']:04d}_journal.jsonl"
    step=s['counts'][core.ARMS[0]]+1
    before=time.perf_counter_ns()
    proc=subprocess.run([sys.executable,'-X','utf8','-B',str(HERE/'cpu_child.py'),
        '--journal',str(journal),'--step',str(step)]+(['--crash-after-journal'] if crash else []),
        capture_output=True,timeout=20,creationflags=0x08004000)
    subprocess_ns=time.perf_counter_ns()-before
    name=f"invocation{p['invocation']:04d}"
    (directory/(name+'_stdout.txt')).write_bytes(proc.stdout)
    (directory/(name+'_stderr.txt')).write_bytes(proc.stderr)
    child=json.loads(proc.stdout.decode('utf-8'))
    assert child['actual_CPU_work_units']==3 and child['neural_updates']==0 and child['MRI_arrays_loaded']==0
    assert not child['torch_imported'] and not child['numpy_imported']
    row=dict(invocation=p['invocation'],actual_child_exit=proc.returncode,child_observation=child,
        actual_CPU_work_units=3,subprocess_ns=subprocess_ns)
    if crash:
        assert proc.returncode==17
        row.update(sealed=False,known_failed_controller_elapsed_ns=time.perf_counter_ns()-p['controller_start_monotonic_ns'],
            unsealed_pending_retained=True)
        core.new(directory/'failure_observation.json',row)
        return head,row
    assert proc.returncode==0
    receipt,actual_total=core.seal(directory,cp,s,p,journal)
    newhead=core.sha(receipt);v=core.state(directory,cp,newhead)
    row.update(sealed=True,receipt=core.binding(receipt),actual_controller_ns_through_seal=actual_total,
        cumulative_paid_ns=v['paid_ns'],cumulative_units=v['counts'])
    assert actual_total<=core.load(receipt)['charged_ns']
    return newhead,row
def copy_first(source,dest):
    dest.mkdir(exist_ok=False)
    for name in ('invocation0001_receipt.json','invocation0001_close.json','invocation0001_journal.jsonl'):
        shutil.copyfile(source/name,dest/name)
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resources=guard(started)
    OUT.mkdir(exist_ok=False);cp=OUT/'contract.json'
    frozen_sources=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=core.sha(p))
        for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'budget_ledger.py',HERE/'cpu_child.py',HERE/'probe_state.py',HERE/'verify_budget.py')]
    core.new(OUT/'PRE_EXECUTION_SOURCE_BINDINGS.json',frozen_sources)
    core.new(cp,dict(synthetic_accounting_only=True,arms=list(core.ARMS),units_per_arm=3,
        max_cumulative_controller_ns=60_000_000_000,protocol_sha256=core.sha(HERE/'PROTOCOL.md')))
    normal=OUT/'normal';normal.mkdir();head='GENESIS';rows=[]
    head,row=run_child(normal,cp,head,False,started);rows.append(row)
    first_state=core.state(normal,cp,head)
    fresh_state_probe=fresh_probe('valid_fresh_state',normal,cp,head)
    assert fresh_state_probe['accepted'] and fresh_state_probe['state']['paid_ns']==first_state['paid_ns']
    budget_probe=fresh_probe('budget_rejection',normal,cp,head,60_000_000_000)
    assert budget_probe['reason']=='Insufficient cumulative budget' and not (normal/'pending.json').exists()
    for _ in range(2):
        head,row=run_child(normal,cp,head,False,started);rows.append(row)
    final=core.state(normal,cp,head);quota_probe=fresh_probe('quota_rejection',normal,cp,head,0)
    assert quota_probe['reason']=='No remaining quota'
    crashdir=OUT/'unsealed_failure';copy_first(normal,crashdir)
    crash_head=core.sha(crashdir/'invocation0001_receipt.json')
    _,crash_row=run_child(crashdir,cp,crash_head,True,started)
    crash_probe=fresh_probe('unsealed_rejection',crashdir,cp,crash_head)
    assert 'Unsealed invocation' in crash_probe['reason']
    faults=[]
    for key in ('cumulative_duration','joint_step'):
        d=OUT/key;copy_first(normal,d)
        receipt=d/'invocation0001_receipt.json';r=core.load(receipt)
        if key=='cumulative_duration':r['cumulative_paid_ns']+=1
        else:
            j=d/'invocation0001_journal.jsonl';events=[json.loads(v) for v in j.read_text(encoding='utf-8').splitlines()]
            events[0]['step']=99
            j.write_text(''.join(json.dumps(e,separators=(',',':'))+'\n' for e in events),encoding='utf-8')
            r['journal']=core.binding(j)
        receipt.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        close=d/'invocation0001_close.json';cl=core.load(close);cl['receipt_sha256']=core.sha(receipt)
        close.write_text(json.dumps(cl,indent=2)+'\n',encoding='utf-8')
        faults.append(dict(kind=key,fixture=str(d.relative_to(HERE)),**fresh_probe(key+'_rejection',d,cp,core.sha(receipt))))
    faults.append(dict(kind='expected_head',**fresh_probe('expected_head_rejection',normal,cp,'0'*64)))
    for b in frozen_sources:
        p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and core.sha(p)==b['sha256']
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=core.sha(p))
        for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'budget_ledger.py',HERE/'cpu_child.py',HERE/'probe_state.py',
            HERE/'verify_budget.py',cp,OUT/'PRE_EXECUTION_SOURCE_BINDINGS.json')],
        normal_transactions=rows,final_normal_state={k:final[k] for k in ('head','paid_ns','counts','invocations')},
        fresh_process_state_probe=fresh_state_probe,budget_probe=budget_probe,quota_probe=quota_probe,crash_transaction=crash_row,unsealed_resume_probe=crash_probe,
        faults=faults,actual_CPU_work_units=12,actual_work_child_processes_launched=4,
        actual_validation_subprocesses_launched=7,actual_total_child_processes_launched=11,
        actual_work_child_exits=[0,0,0,17],known_failed_elapsed_charged_as_sealed_success=False,
        unsealed_failed_cost_cannot_be_silently_ignored=True,cumulative_charge_is_conservative_not_exact_actual_wall=True,
        medical_arrays_loaded=0,checkpoint_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,medical_training_updates=0,
        new_primary_papers_read=0,formal_medical_budget_frozen=False,formal_medical_long_runner_qualified=False,
        actual_new_MRI_task_benefit_measured=False,publication_claim_confirmed=False,goal_status='active',
        resources_before=resources,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
    core.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=True,normal_invocations=3,normal_paid_ns=final['paid_ns'],
        actual_CPU_work_units=12,actual_work_child_exits=[0,0,0,17],budget_probe=budget_probe,quota_probe=quota_probe,
        unsealed_resume_probe=crash_probe,faults=faults,elapsed_seconds=result['elapsed_seconds'])),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
