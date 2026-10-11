"""Repair one mistaken reference path in a new source, retaining the failed generation."""
import ast,json,hashlib,difflib,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');old=HERE/'fetch_and_extract_direct_attempt02.py';source=old.read_text(encoding='utf-8')
    before="refsrc=ROOT/'pulse_sequence_and_forward_model_2026_10_09/primary_attempt02/jointsr.html'"
    after="refsrc=ROOT/'pulse_sequence_and_forward_model_2026_10_09/primary_attempt01/jointsr.html'"
    assert source.count(before)==1;new=source.replace(before,after);ast.parse(new)
    ref=HERE.parent/'pulse_sequence_and_forward_model_2026_10_09/primary_attempt01/jointsr.html'
    assert sha(ref)=='78b5fc22017dcc7a1f6d723037e0e5d5fded6ccf9443fe9f4556e7a2c0f14ad9'
    path=HERE/'fetch_and_extract_reference_recovered.py'
    with path.open('x',encoding='utf-8') as f:f.write(new)
    diff=''.join(difflib.unified_diff(source.splitlines(keepends=True),new.splitlines(keepends=True),fromfile=old.name,tofile=path.name))
    with (HERE/'REFERENCE_BINDING_RECOVERY.diff').open('x',encoding='utf-8') as f:f.write(diff)
    receipt=dict(complete=True,errors=[],old_failed_source_sha256=sha(old),new_source_sha256=sha(path),
        reference_source_sha256=sha(ref),exact_single_reference_path_fixed=True,medical_results_obtained=False,actual_papers_read=0,goal_status='active')
    with (HERE/'REFERENCE_BINDING_BUILD_RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
