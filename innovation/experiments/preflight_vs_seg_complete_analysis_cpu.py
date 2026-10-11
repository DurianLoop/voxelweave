"""Known-answer statistical vectors, with no patient-effect reading."""
import json
from pathlib import Path
from verify_vs_seg_complete_analysis_cpu import mean, quantile, replay, same, sha, ROOT

def main():
    checks, errors = [], []
    for name, actual, expected in [
        ('manual_lower_quantile', quantile([3., 1., 0., 2.], .025), .075),
        ('manual_upper_quantile', quantile([3., 1., 0., 2.], .975), 2.925),
        ('single_patient_constant', replay([-2.]), dict(n=1, mean_difference=-2., ci95_percentile=[-2.,-2.], seed=20261012, draws=5000, negative_patients=1, zero_patients=0)),
        ('zero_cohort', replay([0.] * 45), dict(n=45, mean_difference=0., ci95_percentile=[0.,0.], seed=20261012, draws=5000, negative_patients=0, zero_patients=45)),
        ('balanced_three_patient_support', replay([-1.,0.,1.]), dict(n=3, mean_difference=0., ci95_percentile=[-1.,1.], seed=20261012, draws=5000, negative_patients=1, zero_patients=1)),
    ]:
        before=len(errors);same(actual,expected,name,errors);checks.append(dict(name=name,passed=len(errors)==before,actual=actual,expected=expected))
    deliberate=[];same(dict(dice=None),dict(dice=0.),'null_vs_zero',deliberate)
    checks.append(dict(name='null_not_zero',passed=bool(deliberate)))
    if not deliberate: errors.append('Comparator collapses null and zero')
    out=ROOT/'experiments/vs_seg_complete_analysis_preflight';out.mkdir(exist_ok=True);p=out/'attempt_01.json'
    result=dict(complete=not errors,synthetic_only=True,patient_effects_read=False,script_sha256=sha(__file__),verifier_sha256=sha(Path(__file__).with_name('verify_vs_seg_complete_analysis_cpu.py')),checks=checks,errors=errors)
    with p.open('x',encoding='utf-8') as f: json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
    if errors: raise SystemExit(1)

if __name__=='__main__': main()
