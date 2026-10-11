"""Independent, exact toy checks for metric, uncertainty, and augmentation assumptions."""
import json,math,sys,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from inventory_frozen_text_storage import ROOT,HERE,entry,dump,guard

def ratio(v):return dict(exact=str(v),float=float(v))
def exact_linear_quantile(values,q):
    values=sorted(values);pos=(len(values)-1)*q;lo=pos.numerator//pos.denominator;w=pos-lo
    return values[lo] if lo==len(values)-1 else values[lo]*(1-w)+values[lo+1]*w
def bernstein(t,c1,c2):return 3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3
def polynomial(t,c1,c2):return 3*c1*t+(-6*c1+3*c2)*t*t+(3*c1-3*c2+1)*t**3

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=guard(started)
    source=HERE/'primary_xml_attempt01';pub=json.loads((source/'receipt.json').read_text(encoding='utf-8'))
    assert pub['complete'] and len(pub['records'])==3
    result=dict(complete=False,errors=[],synthetic_only=True,diagnostics=[],medical_arrays_loaded=0,
        patient_GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        new_training_launched=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        publication_claim_confirmed=False,goal_status='active')
    # Counterexample: matched total volume with large balanced FP/FN.
    gt=np.zeros(200,dtype=bool);gt[:100]=True
    predicted=np.zeros(200,dtype=bool);predicted[:50]=True;predicted[100:150]=True
    tp=int(np.count_nonzero(gt&predicted));fp=int(np.count_nonzero(~gt&predicted));fn=int(np.count_nonzero(gt&~predicted))
    rve=F(abs(int(predicted.sum())-int(gt.sum())),int(gt.sum()));dice=F(2*tp,2*tp+fp+fn)
    assert (tp,fp,fn)==(50,50,50) and rve==0 and dice==F(1,2)
    result['diagnostics'].append(dict(name='low_absRVE_does_not_bound_FP_or_FN',TP=tp,FP=fp,FN=fn,
        reference_voxels=100,predicted_voxels=100,absRVE=ratio(rve),Dice=ratio(dice),recall=ratio(F(tp,tp+fn)),
        FN_plus_FP_per_reference_volume=ratio(F(fp+fn,100)),claim_supported=True,
        limitation='Toy logical counterexample; does not estimate any author or MRI patient false positives'))
    # Same one-voxel marginals, distinct joint predictive volume distributions.
    datasets={'anticorrelated':[[F(1,10),F(9,10)],[F(9,10),F(1,10)]],
              'comonotonic':[[F(1,10),F(1,10)],[F(9,10),F(9,10)]]}
    uncertainty=[]
    for name,rows in datasets.items():
        samples=np.array([[float(v) for v in row] for row in rows]);volumes=[sum(row) for row in rows]
        qrows=[]
        for q in [F(0),F(1,4),F(1,2),F(3,4),F(1)]:
            marginal=sum(exact_linear_quantile([row[j] for row in rows],q) for j in range(2))
            joint=exact_linear_quantile(volumes,q)
            assert abs(float(marginal)-float(np.quantile(samples,float(q),axis=0,method='linear').sum()))<1e-12
            assert abs(float(joint)-float(np.quantile(samples.sum(axis=1),float(q),method='linear')))<1e-12
            qrows.append(dict(q=ratio(q),sum_voxel_marginal_quantiles=ratio(marginal),quantile_of_sample_volume=ratio(joint)))
        mean=sum(volumes)/len(volumes);variance=sum((v-mean)**2 for v in volumes)/len(volumes)
        assert abs(float(variance)-float(samples.sum(axis=1).var()))<1e-12
        uncertainty.append(dict(name=name,samples=[[ratio(v) for v in row] for row in rows],
                                sample_volumes=[ratio(v) for v in volumes],empirical_volume_variance=ratio(variance),quantiles=qrows))
    assert uncertainty[0]['empirical_volume_variance']['float']==0
    assert uncertainty[0]['quantiles'][1]['sum_voxel_marginal_quantiles']['exact']=='3/5'
    assert uncertainty[0]['quantiles'][1]['quantile_of_sample_volume']['exact']=='1'
    result['diagnostics'].append(dict(name='marginal_quantile_sum_is_not_joint_volume_quantile',cases=uncertainty,
        claim_supported=True,limitation='Separate estimands; no assertion that separately calibrated intervals cannot cover truth'))
    # Label-aware region curves can encode an artificial boundary even in a featureless fixture.
    foreground=(F(7,10),F(9,10));background=(F(1,10),F(3,10))
    t=F(1,2);fg=bernstein(t,*foreground);bg=bernstein(t,*background)
    for controls in [foreground,background]:
        assert F(0)<=controls[0]<=controls[1]<=F(1)
        assert abs(controls[0]-F(1,3))<=F(1,2) and abs(controls[1]-F(2,3))<=F(1,2)
        for x in [F(k,100) for k in range(101)]:assert bernstein(x,*controls)==polynomial(x,*controls)
    assert fg==F(29,40) and bg==F(11,40)
    mask=np.zeros((16,16,16),dtype=bool);mask[4:12,4:12,4:12]=True
    image=np.full(mask.shape,float(t));changed=np.where(mask,float(fg),float(bg))
    independent=mask.astype(float)*polynomial(image,*[float(v) for v in foreground])+(1-mask.astype(float))*polynomial(image,*[float(v) for v in background])
    max_error=float(np.max(np.abs(changed-independent)));assert max_error<1e-12
    assert np.array_equal(changed>0.5,mask)
    global_control=polynomial(image,*[float(v) for v in foreground]);assert np.ptp(global_control)==0
    result['diagnostics'].append(dict(name='regionwise_curve_can_create_mask_correlated_boundary_signal',
        fixture_shape=list(mask.shape),constant_input=ratio(t),foreground_output=ratio(fg),background_output=ratio(bg),
        artificial_boundary_jump=ratio(fg-bg),monotonic_curves=True,identity_deviation_bound=0.5,
        exact_mask_recovery_by_fixed_threshold_in_fixture=True,global_same_curve_has_no_boundary=True,
        independent_Bernstein_polynomial_max_error=max_error,mother_label_unchanged=True,
        author_optional_seam_smoothing_reproduced=False,author_sampler_or_training_reproduced=False,
        limitation='Training GT is legitimate; this toy does not prove leakage or exploitation on real patients'))
    # Verify source sign in the original MathML rather than a flattened-only string.
    formulas=json.loads((source/'acquisition_formulas.json').read_text(encoding='utf-8'))
    literal=next(v for v in formulas if v['id']=='FD1');assert '<ns0:mo>−</ns0:mo>' in literal['xml']
    identical=F(0);separated=-((F(0)-F(1))**2)
    assert separated<identical
    result['diagnostics'].append(dict(name='literal_negative_pair_L2_under_plain_minimization',
        source_formula_id='FD1',source_literal=literal['text'],identical_loss=ratio(identical),separated_loss=ratio(separated),
        conflicts_with_pull_features_together_if_minimized_directly=True,
        author_code_gradient_path_or_final_PDF_verified=False))
    formulas=json.loads((source/'unlearning_formulas.json').read_text(encoding='utf-8'))
    literal=next(v for v in formulas if v['id']=='EQ4');assert '<ns0:mo>-</ns0:mo>' in literal['xml']
    def negative_kl(p):return -sum(v*math.log(v/0.5) for v in p)
    uniform=negative_kl([.5,.5]);biased=negative_kl([.75,.25]);confident=negative_kl([.999,.001])
    assert confident<biased<uniform==0
    result['diagnostics'].append(dict(name='literal_negative_KL_under_plain_minimization',
        source_formula_id='EQ4',source_literal=literal['text'],uniform_loss=uniform,biased_loss=biased,confident_loss=confident,
        uniform_is_not_plain_minimizer=True,gradient_reversal_mentioned_in_paper=True,
        author_code_gradient_path_or_final_PDF_verified=False))
    result.update(complete=True,diagnostics_completed=5,source_bindings=[entry(Path(__file__)),entry(HERE/'CPU_DIAGNOSTIC_PROTOCOL.md'),entry(source/'receipt.json')]
        +[entry(source/(key+'_'+name+'.json')) for key in ['acquisition','unlearning','bezier'] for name in ['blocks','tables','formulas']],
        resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
    out=HERE/'cpu_diagnostics_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='source_bindings'},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
