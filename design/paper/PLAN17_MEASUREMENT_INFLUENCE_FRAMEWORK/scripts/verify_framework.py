from common import *
from mira import audit_pair,embedded_response_cosine
def main():
 # Observable estimator is linear interpolation of acquired anchors only.
 rng=np.random.default_rng(SEED);v=rng.uniform(0,1,(10,9,16));a={0:v[:,:,0],4:v[:,:,4]};b={0:v[:,:,0],6:v[:,:,6]}
 def f(c,z):
  ids=sorted(c);left,right=ids[0],ids[-1];u=(z-left)/(right-left)
  return (1-u)*c[left]+u*c[right]
 r=audit_pair(f,a,b,2,amplitude=.01,target=v[:,:,2]);s=audit_pair(f,a,b,2,amplitude=.01,target=np.full((10,9),100.))
 assert np.array_equal(r['prediction_a'],s['prediction_a']) and r['influence']==s['influence'] and r['disagreement_mae']==s['disagreement_mae']
 assert r['evaluation']['paired_mae']!=s['evaluation']['paired_mae']
 assert abs(r['evaluation']['observable_fraction']+r['evaluation']['shared_fraction']-1)<1e-12
 wa=np.array([.5,.5,0]);wb=np.array([2/3,0,1/3]);expected=float(wa@wb/np.sqrt((wa@wa)*(wb@wb)))
 assert abs(r['influence']-expected)<1e-12
 assert abs(audit_pair(f,a,b,2,amplitude=-.01)['influence']-expected)<1e-12
 assert not audit_pair(f,a,b,2,amplitude=.01,support_source='target')['target_free_score_contract']
 rejected=False
 try:audit_pair(f,a,{0:v[:,:,0]+1,6:v[:,:,6]},2,amplitude=.01)
 except ValueError:rejected=True
 assert rejected
 # Targets may vary arbitrarily while acquired-only range and masks stay fixed.
 v2=v.copy();v2[:,:,1::4]=999;v2[:,:,2::4]=-333;v2[:,:,3::4]=543
 assert features(v[:,:,::4])==features(v2[:,:,::4])
 assert np.array_equal(fg(v[:,:,0])|fg(v[:,:,4]),fg(v2[:,:,0])|fg(v2[:,:,4]))
 for name,keys in [('neural_pair_per_plane.csv',['dataset','case','pair','z']),('practical_proxy_per_plane.csv',['dataset','case','pair','condition','z'])]:
  df=pd.read_csv(OUT/name);assert not df.duplicated(keys).any();assert np.isfinite(df.select_dtypes('number')).all().all()
 split=json.loads((OUT/'development_freeze.json').read_text());assert not set(split['development'])&set(split['internal_evaluation'])
 result={'embedded_linear_coefficient_cosine':expected,'target_mutation_invariance':True,'shared_anchor_identity_mismatch_rejected':True,'energy_closure':True,'gt_support_flagged':True,'acquired_features_and_masks_target_invariant':True,'new_prediction_keys_unique_and_finite':True,'development_eval_disjoint':True}
 result['linear_influence_invariant_under_perturbation_sign_reversal']=True
 save('framework_verification.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
