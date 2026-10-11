"""Check how reported QC metrics relate to rejection prevalence; no assumptions about class labels."""
import hashlib,json,re,sys
from pathlib import Path
from fractions import Fraction
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();out=HERE/'robust_qc_metric_audit_attempt01';out.mkdir(exist_ok=False)
    blocksfile=HERE/'robust_qc_extraction_attempt01/blocks.json';tablesfile=HERE/'robust_qc_extraction_attempt01/tables.json'
    blocks=json.loads(blocksfile.read_text(encoding='utf-8'));tables=json.loads(tablesfile.read_text(encoding='utf-8'))
    m=re.search(r'rejection rate of ([\d.]+)%',blocks[53]['text']);assert m
    rejected=Fraction(m.group(1))/100;accepted=1-rejected
    candidates=[t for t in tables if t['rows'] and [c['text'] for c in t['rows'][0]]==['Method','Sensitivity','Specificity','Accuracy','AUC']]
    assert len(candidates)==1;rows=[]
    for row in candidates[0]['rows'][1:]:
        c=[v['text'] for v in row];assert len(c)==5;sens,spec,acc,auc=map(Fraction,c[1:])
        acc_fail=rejected*sens+accepted*spec;acc_pass=accepted*sens+rejected*spec
        rows.append(dict(method=c[0],primary_cells=c,
            accuracy_if_failure_positive=float(acc_fail),accuracy_if_pass_positive=float(acc_pass),
            reported_accuracy=float(acc),absolute_discrepancy_failure_positive=float(abs(acc-acc_fail)),
            absolute_discrepancy_pass_positive=float(abs(acc-acc_pass))))
    r=dict(complete=True,errors=[],reported_rejection_fraction=float(rejected),rows=rows,
        conclusion='Reported accuracies are much closer to pass-positive than failure-positive orientation. This arithmetic does not prove the article class convention or reproduce a confusion matrix; rounded aggregate statistics do not resolve it.',
        prohibited_inference='Do not describe the 0.999 sensitivity cell as 99.9% detection of failed segmentations without resolving positive-class definition.',
        supplementary_material_read=False,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        publication_claim_confirmed=False,resources=resource_guard(),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [Path(__file__),blocksfile,tablesfile]])
    with (out/'receipt.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r),flush=True)
if __name__=='__main__':main()
