"""Four prespecified, nonmedical algebra/gradient diagnostics; downloaded code never executed."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,numpy as np,torch
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);torch.set_num_interop_threads(1);started=time.perf_counter();before=resource_guard()
    assert before['workspace_free_bytes']-11_800_000>=8_000_000_000
    out=HERE/'source_diagnostics_attempt02';out.mkdir(exist_ok=False)
    sources=[Path(__file__),HERE/'CPU_SOURCE_DIAGNOSTIC_PROTOCOL.md',HERE/'amdu_blobs_attempt01/file1.txt.gz',HERE/'amdu_blobs_attempt01/file0.txt.gz',
        HERE/'primary_xml_attempt01/dgtta.xml.gz',HERE/'primary_xml_attempt01/missing.xml.gz',HERE/'primary_xml_attempt01/peil.xml.gz']
    dump(out/'frozen_config.json',dict(source_bindings=[entry(p) for p in sources],medical_data=False,author_repository_executed=False,diagnostics=4))
    rows=[]
    def kl(logits):
        probabilities=torch.softmax(logits,dim=1)+1e-8;target=torch.full_like(probabilities,1/logits.shape[1])
        return torch.nn.functional.kl_div(probabilities.log(),target,reduction='batchmean')
    logits=torch.tensor([[2.,-1.,.5]],dtype=torch.float64,requires_grad=True);initial=kl(logits);gradient=torch.autograd.grad(initial,logits)[0]
    after_logits=(logits-.1*gradient).detach();after=kl(after_logits);assert after<initial
    uniform=kl(torch.zeros_like(logits));assert uniform<initial
    encoder=torch.nn.Linear(2,2,bias=False,dtype=torch.float64);head=torch.nn.Linear(2,3,bias=False,dtype=torch.float64)
    with torch.no_grad():encoder.weight.copy_(torch.eye(2,dtype=torch.float64));head.weight.copy_(torch.tensor([[2.,0.],[-1.,0.],[.5,0.]],dtype=torch.float64))
    x=torch.tensor([[1.,.2]],dtype=torch.float64);pred=head(encoder(x).detach());torch.nn.functional.cross_entropy(pred,torch.tensor([0])).backward()
    assert encoder.weight.grad is None and head.weight.grad is not None
    head.zero_grad();encoder.zero_grad();loss=kl(head(encoder(x)));loss.backward();assert encoder.weight.grad is not None
    head_before=head.weight.detach().clone();step=torch.optim.SGD(encoder.parameters(),lr=.01);step.step()
    assert torch.equal(head.weight,head_before)
    rows.append(dict(key='positive_uniform_KL_and_detach_paths',initial=float(initial.detach()),after_one_step=float(after),uniform_loss=float(uniform),
        classifier_step_encoder_gradient_absent=True,confusion_step_encoder_gradient_present=True,head_weights_unchanged_with_encoder_only_optimizer=True,
        epsilon_uniform_loss_can_be_slightly_negative=True,complete=True))
    variance=torch.linspace(0,4,9,dtype=torch.float64);gates={str(alpha):torch.sigmoid(-(alpha*variance)).numpy().tolist() for alpha in [1.,0.,-1.]}
    assert np.all(np.diff(gates['1.0'])<0) and np.all(np.diff(gates['-1.0'])>0) and np.all(np.diff(gates['0.0'])==0)
    rows.append(dict(key='UAA_unconstrained_alpha_monotonicity',variance=variance.numpy().tolist(),gates=gates,positive_alpha_decreases=True,zero_alpha_constant=True,negative_alpha_increases=True,author_negative_alpha_observed=False,complete=True))
    field=np.tile(np.array([.75,.25],np.float64),(100,1));target=np.zeros(100,int);target[:10]=1
    eps=1e-7
    def consistent(d):return float(np.mean(1-(2*np.sum(field*field,axis=0)+eps)/(np.sum(field**d+field**d,axis=0)+eps)))
    d2=consistent(2);d1=consistent(1);assert d2==0 and d1>0
    prediction=field.argmax(axis=1);FN=int(np.count_nonzero((prediction==0)&(target==1)));assert FN==10
    rows.append(dict(key='d2_consistency_not_lesion_correctness',d2_consistency_loss=d2,d1_consistency_loss=d1,lesion_voxels=10,FN=FN,lesion_recall=0.,author_patient_failure_claimed=False,complete=True))
    image=np.array([1+2j,3-1j,.5+.8j],np.complex128);sens=np.array([[1+.1j,.7-.2j,.5+.2j],[.3-.4j,.8+.1j,1.1-.2j]],np.complex128)
    factor=2*np.exp(.7j);observations=sens*image;changed_sens=sens*factor;changed_image=image/factor
    error=float(np.max(np.abs(changed_sens*changed_image-observations)));assert error<3e-12
    rows.append(dict(key='MRI_scale_phase_gauge',max_observation_error=error,sensitivity_parameter_change_L2=float(np.linalg.norm(changed_sens-sens)),
        image_magnitude_ratio=.5,physical_sensitivity_identified_by_consistency_alone=False,PEIL_CG_or_regularizer_reproduced=False,complete=True))
    assert len(rows)==4 and time.perf_counter()-started<120 and not torch.cuda.is_initialized()
    result=dict(complete=True,errors=[],diagnostics_completed=4,diagnostics=rows,source_bindings=[entry(p) for p in sources]+[entry(out/'frozen_config.json')],
        resources_before=before,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started,patient_arrays_loaded=0,GT_arrays_loaded=0,
        model_checkpoints_loaded=0,author_repository_executed=False,medical_training_updates=0,new_medical_effects=0,publication_claim_confirmed=False,goal_status='active')
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    dump(out/'receipt.json',result);print(json.dumps({k:v for k,v in result.items() if k!='source_bindings'},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
