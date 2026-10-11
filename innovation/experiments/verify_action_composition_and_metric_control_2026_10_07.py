"""Independent hash/coverage audit and an exact Dice counterexample; no MRI, GT, or model reads."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import hashlib,itertools,json,sys,time
from pathlib import Path
from fractions import Fraction
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'experiments/mc_rc_3d_action_composition_2026_10_07/attempt01.json'
OUT=SOURCE.parent/'independent_tile_and_metric_control_attempt01.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def counts(gt,pred):
    gt=np.asarray(gt,bool);pred=np.asarray(pred,bool);assert gt.shape==pred.shape
    return dict(TP=int(np.count_nonzero(gt&pred)),FP=int(np.count_nonzero(~gt&pred)),FN=int(np.count_nonzero(gt&~pred)))
def exact_dice(c):
    den=2*c['TP']+c['FP']+c['FN']
    return Fraction(2*c['TP'],den) if den else None
def dice_pair_decomposition(c0,ca,cb,cab):
    """Separate the Dice fraction's coupling from nonadditive confusion counts.

    This accepts frozen full-FOV confusion counts, not deployable GT feedback.
    The residual includes binary prediction overlap/threshold effects and does
    not identify a neural mechanism. Undefined and invalid surrogates stay null.
    """
    states=(c0,ca,cb,cab);gt_sizes={c['TP']+c['FN'] for c in states};assert len(gt_sizes)==1
    assert all(all(isinstance(v,int) and v>=0 for v in c.values()) for c in states)
    oracle={k:ca[k]+cb[k]-c0[k] for k in ('TP','FP','FN')}
    valid=min(oracle.values())>=0 and oracle['TP']+oracle['FN']==next(iter(gt_sizes))
    ds=[exact_dice(c) for c in states];do=exact_dice(oracle) if valid else None
    defined=all(d is not None for d in ds) and do is not None
    result=dict(states=list(states),additive_count_oracle=oracle,oracle_valid=valid,all_Dice_defined=defined)
    if defined:
        actual=ds[3]-ds[1]-ds[2]+ds[0];metric=do-ds[1]-ds[2]+ds[0];residual=ds[3]-do
        assert actual==metric+residual
        result.update(Dice=[float(d) for d in ds],Dice_exact=[str(d) for d in ds],
            actual_interaction=float(actual),actual_interaction_exact=str(actual),
            Dice_fraction_only_coupling=float(metric),Dice_fraction_only_coupling_exact=str(metric),
            nonadditive_counts_residual=float(residual),nonadditive_counts_residual_exact=str(residual))
    else:result.update(actual_interaction=None,Dice_fraction_only_coupling=None,nonadditive_counts_residual=None)
    return result
def tile_hashes(row):
    answer={}
    for batch in row['batch_records_full']:
        for i,h in zip(batch['tile_ids'],batch['tile_probability_sha256']):assert i not in answer;answer[i]=h
    assert len(answer)==16
    return answer
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not OUT.exists();started=time.perf_counter();r=read(SOURCE)
    receipt=ROOT/'SESSION_OBSERVED_EXITS_ACTION_COMPOSITION_2026-10-07.json';assert read(receipt)['probe_observed_tool_exit']==0
    assert r['complete'] and not r['errors'] and r['qualification_passed']
    for binding in r['source_bindings']:assert sha(ROOT/binding['file'])==binding['sha256']
    rows={x['mask']:x for x in r['subsets']};assert set(rows)==set(range(8));h={mask:tile_hashes(row) for mask,row in rows.items()}
    pairs=[]
    for a,b in itertools.combinations((1,2,4),2):
        affected_a=set(rows[a]['affected_tile_ids']);affected_b=set(rows[b]['affected_tile_ids']);common=affected_a&affected_b
        audits=[]
        for i in range(16):
            sources=[x for x in (a,b) if i in set(rows[x]['affected_tile_ids'])]
            if len(sources)<=1:
                donor=sources[0] if sources else 0
                audits.append(dict(tile=i,donor_mask=donor,joint_hash_equal_to_unique_singleton_or_baseline=h[a|b][i]==h[donor][i]))
        assert all(x['joint_hash_equal_to_unique_singleton_or_baseline'] for x in audits)
        pairs.append(dict(masks=[a,b],coaffected_tile_ids=sorted(common),checked_noncoaffected_tiles=audits,
            disjoint_tile_support=len(common)==0,all_tile_probabilities_explained_by_unique_singleton=len(common)==0 and len(audits)==16,
            native_nonzero_residual_does_not_by_itself_establish_neural_interaction=True))
    costs={0:0,**{mask:rows[mask]['cached_incremental_forward_count'] for mask in range(1,8)}}
    footprint={0:set(),**{mask:set(rows[mask]['recomputed_batch_starts']) for mask in range(1,8)}}
    assert all(footprint[s]==set().union(*(footprint[a] for a in (1,2,4) if s&a)) for s in range(8))
    inequalities=[]
    for a in range(8):
        for b in range(8):
            if a&b!=a:continue
            for e in (1,2,4):
                if b&e:continue
                lhs=costs[a|e]-costs[a];rhs=costs[b|e]-costs[b]
                assert lhs>=rhs>=0
                inequalities.append(dict(smaller=a,larger=b,add=e,small_marginal=lhs,large_marginal=rhs))
    expected_calls=8+r['baseline_repeat']['forwards']+sum(rows[s]['full_forward_count']+rows[s]['cached_incremental_forward_count'] for s in range(1,8))+r['production_joint_reference']['forwards']
    assert expected_calls==r['actual_model_forwards']==116 and r['actual_tiles']==2*expected_calls
    gt=np.array([1,1,0,0],bool);p0=np.array([1,1,1,1],bool);pa=np.array([1,1,0,1],bool);pb=np.array([1,1,1,0],bool);pab=np.array([1,1,0,0],bool)
    mix=pab.astype(int)-pa.astype(int)-pb.astype(int)+p0.astype(int)
    assert not mix.any() and not np.any((pa!=p0)&(pb!=p0))
    control=dice_pair_decomposition(*(counts(gt,p) for p in (p0,pa,pb,pab)))
    assert control['actual_interaction_exact']=='1/15' and control['nonadditive_counts_residual_exact']=='0'
    controls=0
    for tp,fn,fp in itertools.product(range(1,5),range(4),range(2,9)):
        for q1 in range(1,fp):
            for q2 in range(1,fp-q1+1):
                cs=[dict(TP=tp,FP=fp-q,FN=fn) for q in (0,q1,q2,q1+q2)]
                decomposition=dice_pair_decomposition(*cs)
                assert Fraction(decomposition['actual_interaction_exact'])>0
                assert decomposition['nonadditive_counts_residual_exact']=='0';controls+=1
    # Empty-both and incompatible-count cases must remain explicit.
    empty=dice_pair_decomposition(*([dict(TP=0,FP=0,FN=0)]*4));assert not empty['all_Dice_defined'] and empty['actual_interaction'] is None
    invalid=dice_pair_decomposition(dict(TP=1,FP=0,FN=1),dict(TP=0,FP=0,FN=2),dict(TP=0,FP=0,FN=2),dict(TP=0,FP=0,FN=2));assert not invalid['oracle_valid']
    result=dict(complete=True,errors=[],script_sha256=sha(__file__),source_sha256=sha(SOURCE),exit_receipt_sha256=sha(receipt),
        original_bindings_unchanged=True,MRI_arrays_loaded=0,GT_arrays_loaded=0,model_forwards=0,
        real_clinical_utility_measured=False,synthetic_metric_counterexample=True,
        pairs=pairs,joint_batch_costs=costs,all27_cost_diminishing_return_inequalities=inequalities,
        actual_total_forward_count_verified=expected_calls,sequential_execution_cost_is_not_support_union_increment=True,
        exact_Dice_control=control,synthetic_binary_mixed_response_zero=True,synthetic_changed_support_disjoint=True,
        additional_valid_confusion_count_cases=controls,empty_endpoint_preserved=empty,invalid_oracle_preserved=invalid,
        conclusions=['This finite measured batch-union cost obeys submodularity; it does not establish task-utility submodularity.',
                     'Positive Dice interaction is possible with exactly separable disjoint binary predictions; do not attribute it to neural spatial coupling.',
                     'AC and BC tile outputs come entirely from unique singleton or baseline outputs; tiny native mixed residual is not evidence of within-tile neural interaction.'],
        elapsed_seconds=time.perf_counter()-started)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('complete','joint_batch_costs','actual_total_forward_count_verified','exact_Dice_control','additional_valid_confusion_count_cases','elapsed_seconds')},ensure_ascii=False))
    return 0
if __name__=='__main__':raise SystemExit(main())
