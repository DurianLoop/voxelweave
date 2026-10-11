"""New diagnostic version preserves the original any-null denominator convention."""
import ast,json,hashlib,difflib,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');old=HERE/'audit_medical_failure_decomposition.py';source=old.read_text(encoding='utf-8')
    before="    values=[v for v in values if v is not None];return sum(values,F(0))/len(values) if values else None"
    after="    return sum(values,F(0))/len(values) if values and all(v is not None for v in values) else None"
    assert source.count(before)==1
    new=source.replace(before,after).replace("HERE/'medical_failure_decomposition_attempt01'","HERE/'medical_failure_decomposition_attempt02'")
    new=new.replace("HERE/'MEDICAL_FAILURE_DECOMPOSITION_PROTOCOL.md',","HERE/'MEDICAL_FAILURE_DECOMPOSITION_PROTOCOL.md',HERE/'NULL_AGGREGATION_RECOVERY_PROTOCOL.md',HERE/'audit_medical_failure_decomposition.py',HERE/'build_decomposition_null_recovery.py',")
    ast.parse(new);dest=HERE/'audit_medical_failure_decomposition_attempt02.py'
    with dest.open('x',encoding='utf-8') as f:f.write(new)
    diff=''.join(difflib.unified_diff(source.splitlines(keepends=True),new.splitlines(keepends=True),fromfile=old.name,tofile=dest.name))
    with (HERE/'DECOMPOSITION_NULL_RECOVERY.diff').open('x',encoding='utf-8') as f:f.write(diff)
    result=dict(complete=True,errors=[],old_source_sha256=sha(old),new_source_sha256=sha(dest),original_patient_denominator_preserved=True,
        original_medical_source_unchanged=True,diagnostic_result_obtained=False,goal_status='active')
    with (HERE/'DECOMPOSITION_NULL_BUILD_RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
