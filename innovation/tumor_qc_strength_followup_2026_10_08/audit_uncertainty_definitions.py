"""Scientific toy probability exploration; no patient outputs or author runtime."""
import sys,json,math,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
def entropy(p):
    return -sum(q*math.log2(q) for q in [p,1-p] if q>0)
def measures(draws):
    p=sum(draws)/len(draws);he=sum(entropy(x) for x in draws)/len(draws)
    return dict(draws=draws,mean_foreground_probability=p,predictive_entropy_bits=entropy(p),
        expected_entropy_bits=he,population_variance=sum((x-p)**2 for x in draws)/len(draws),mutual_information_bits=entropy(p)-he)
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();res=client.resource_guard()
    grid=[measures([i/10,j/10]) for i in range(11) for j in range(11)]
    tol=1e-12
    assert all(-tol<=x['mutual_information_bits']<=1+tol and 0<=x['population_variance']<=.25+tol for x in grid)
    complements=[measures([1-p for p in x['draws']]) for x in grid]
    entropy_error=max(abs(x['predictive_entropy_bits']-y['predictive_entropy_bits']) for x,y in zip(grid,complements))
    assert entropy_error<tol
    examples=[measures(v) for v in [[0,0],[1,1],[.1,.1],[.9,.9],[.5,.5],[.1,.9],[0,1]]]
    stable=examples[4];dispersed=examples[5]
    assert stable['mean_foreground_probability']==dispersed['mean_foreground_probability']==.5
    assert stable['predictive_entropy_bits']==dispersed['predictive_entropy_bits']==1
    assert stable['population_variance']==0 and dispersed['population_variance']>.15
    assert stable['mutual_information_bits']==0 and dispersed['mutual_information_bits']>.53
    out=HERE/'uncertainty_definition_attempt01';out.mkdir(exist_ok=False)
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],enumerated_two_draw_probability_pairs=len(grid),
        examples=examples,predictive_entropy_complement_symmetry_max_error=entropy_error,
        mean_probability_is_foreground_score_not_label_symmetric_uncertainty=True,
        same_mean_does_not_determine_MC_variance_or_mutual_information=True,
        authors_runtime_formula_verified=False,scope='Mathematical toy probabilities; no author reproduction or medical effects',
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        publication_claim_confirmed=False,goal_status='active',resources=res,elapsed_seconds=time.perf_counter()-started,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'UNCERTAINTY_DEFINITION_AUDIT_PROTOCOL.md',HERE/'jungo_extraction_attempt01/blocks.json',HERE/'extraction_attempt01/blocks.json']])
    client.dump(out/'probability_grid.json',grid);client.dump(out/'receipt.json',receipt)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=True,pairs=len(grid),examples=examples,elapsed_seconds=receipt['elapsed_seconds'])),flush=True)
if __name__=='__main__':main()
