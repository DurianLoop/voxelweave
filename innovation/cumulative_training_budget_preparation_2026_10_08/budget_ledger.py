"""Pure cumulative transaction accounting; it never authorizes medical work."""
import json,hashlib,os,time
from pathlib import Path
ARMS=('legacy_dense','direct','common_projected_dense')
CLOSE_ALLOWANCE_NS=1_000_000_000
class Rejected(ValueError):pass
def require(ok,message):
    if not ok:raise Rejected(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def new(path,obj):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def binding(path):return dict(name=Path(path).name,bytes=Path(path).stat().st_size,sha256=sha(path))
def contract(path):
    q=load(path)
    require(q['synthetic_accounting_only'] is True,'This entry only qualifies synthetic CPU accounting')
    require(q['arms']==list(ARMS) and type(q['units_per_arm']) is int and q['units_per_arm']==3,'Invalid quota')
    require(type(q['max_cumulative_controller_ns']) is int and q['max_cumulative_controller_ns']==60_000_000_000,'Invalid qualification limit')
    return q
def state(directory,contract_path,expected_head):
    directory=Path(directory);q=contract(contract_path)
    require(not (directory/'pending.json').exists(),'Unsealed invocation: no automatic tail rollback')
    files=sorted(directory.glob('invocation*_receipt.json'))
    require(expected_head==(sha(files[-1]) if files else 'GENESIS'),'External expected-head mismatch')
    head='GENESIS';paid=0;counts={a:0 for a in ARMS}
    for number,p in enumerate(files,1):
        r=load(p);require(r['invocation']==number and r['parent_sha256']==head,'Broken receipt chain')
        require(r['contract_sha256']==sha(contract_path),'Contract changed')
        require(r['sources']==[binding(Path(__file__)),binding(Path(__file__).with_name('cpu_child.py'))],'Source changed')
        require(r['journal']['name']==f"invocation{number:04d}_journal.jsonl" and r['close_proof']==f"invocation{number:04d}_close.json",'Artifact path mismatch')
        j=directory/r['journal']['name']
        require(binding(j)==r['journal'],'Journal SHA/size changed')
        events=[json.loads(line) for line in j.read_text(encoding='utf-8').splitlines()]
        require(len(events)==len(ARMS),'Incomplete transaction')
        for event,arm in zip(events,ARMS):
            require(event['arm']==arm and event['step']==counts[arm]+1,'Arm quota/sequence mismatch')
            require(event['shared_token']==f"synthetic-common-step-{event['step']}",'Shared stream mismatch')
            require(event['work_kind']=='sha256_cpu_marker','Not a qualified work kind')
            require(event['digest']==hashlib.sha256(event['shared_token'].encode('ascii')).hexdigest(),'CPU marker mismatch')
            counts[arm]+=1
            require(counts[arm]<=q['units_per_arm'],'Quota exceeded')
        require(type(r['duration_ns']) is int and r['duration_ns']>0,'Invalid paid duration')
        require(r['close_allowance_ns']==CLOSE_ALLOWANCE_NS,'Closing allowance changed')
        require(r['charged_ns']==r['duration_ns']+CLOSE_ALLOWANCE_NS,'Closing cost omitted')
        close=load(directory/r['close_proof'])
        require(close['receipt_sha256']==sha(p) and 0<=close['observed_close_prefix_ns']<=CLOSE_ALLOWANCE_NS,'Closing proof mismatch')
        paid+=r['charged_ns']
        require(r['cumulative_paid_ns']==paid and r['cumulative_units']==counts,'Cumulative account mismatch')
        require(paid<=q['max_cumulative_controller_ns'],'Cumulative budget exceeded')
        head=sha(p)
    return dict(head=head,paid_ns=paid,counts=counts,invocations=len(files),contract=q)
def admit(s,reserve_ns):
    require(type(reserve_ns) is int and reserve_ns>=0,'Invalid reserve')
    require(s['paid_ns']+reserve_ns<=s['contract']['max_cumulative_controller_ns'],'Insufficient cumulative budget')
    require(all(s['counts'][a]<s['contract']['units_per_arm'] for a in ARMS),'No remaining quota')
def begin(directory,contract_path,expected_head,reserve_ns):
    started_ns=time.perf_counter_ns();s=state(directory,contract_path,expected_head);admit(s,reserve_ns)
    pending=dict(invocation=s['invocations']+1,parent_sha256=s['head'],prior_paid_ns=s['paid_ns'],
       prior_units=s['counts'],contract_sha256=sha(contract_path),reserve_ns=reserve_ns,
       controller_start_monotonic_ns=started_ns)
    new(Path(directory)/'pending.json',pending);return s,pending
def seal(directory,contract_path,s,pending,journal):
    directory=Path(directory)
    events=[json.loads(line) for line in Path(journal).read_text(encoding='utf-8').splitlines()]
    require(len(events)==len(ARMS),'Incomplete transaction')
    for event,arm in zip(events,ARMS):
        require(event['arm']==arm and event['step']==s['counts'][arm]+1,'Transaction schedule mismatch')
        token=f"synthetic-common-step-{event['step']}"
        require(event['shared_token']==token and event['digest']==hashlib.sha256(token.encode('ascii')).hexdigest(),'Transaction work mismatch')
        require(event['work_kind']=='sha256_cpu_marker','Transaction work kind mismatch')
    elapsed=time.perf_counter_ns()-pending['controller_start_monotonic_ns']
    charge=elapsed+CLOSE_ALLOWANCE_NS
    require(elapsed>0 and s['paid_ns']+charge<=s['contract']['max_cumulative_controller_ns'],'Live cumulative budget exceeded')
    counts={a:n+1 for a,n in s['counts'].items()}
    receipt=dict(invocation=pending['invocation'],parent_sha256=s['head'],contract_sha256=sha(contract_path),
       duration_ns=elapsed,close_allowance_ns=CLOSE_ALLOWANCE_NS,charged_ns=charge,
       cumulative_paid_ns=s['paid_ns']+charge,cumulative_units=counts,journal=binding(journal),
       close_proof=f"invocation{pending['invocation']:04d}_close.json",
       sources=[binding(Path(__file__)),binding(Path(__file__).with_name('cpu_child.py'))],
       accounting_scope='observed prefix plus a conservatively charged 1-second closing allowance',
       synthetic_accounting_only=True,neural_updates=0)
    path=directory/f"invocation{pending['invocation']:04d}_receipt.json";new(path,receipt)
    close_ns=time.perf_counter_ns()-pending['controller_start_monotonic_ns']-elapsed
    require(0<=close_ns<=CLOSE_ALLOWANCE_NS,'Receipt closure exceeded its charged allowance')
    new(directory/receipt['close_proof'],dict(receipt_sha256=sha(path),observed_close_prefix_ns=close_ns))
    (directory/'pending.json').unlink()
    actual_total=time.perf_counter_ns()-pending['controller_start_monotonic_ns']
    if actual_total>charge:
        new(directory/'pending.json',dict(status='closing_overrun',actual_duration_ns=actual_total,charged_ns=charge))
        raise Rejected('Total closure exceeded its charged allowance')
    # Caller receives the new external head only after this bound is verified.
    return path,actual_total

