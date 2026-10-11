"""All28 completed cases, legal metadata and stored GT counts; no images, labels or models."""
import sys,time,json,collections,math
from pathlib import Path
from fetch_arxiv_maintext import guard,entry,dump
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'lossless_final_evaluation_entry_2026_10_08'))
import final_eval_lossless_v3 as g
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();guard();g.torch.set_num_threads(1)
 devp=ROOT/'development_capacity_after_matched_2026_10_09/evaluation_attempt01/receipt.json';medp=ROOT/'spatial_adaptation_matched_2026_10_08/evaluation_attempt01/receipt.json';dev=g.read(devp);med=g.read(medp)
 auditp=ROOT/'development_capacity_after_matched_2026_10_09/ACTUAL_DEVELOPMENT_EVALUATION_EXIT.json';audit=g.read(auditp);assert audit['observed_tool_exit']==0 and audit['all76_complete_FOVs_and_exact_case_sets_verified'] and audit['result_sha256']==g.sha(devp)
 assert dev['complete'] and med['complete'] and len(dev['arms'])==len(med['arms'])==4
 maps={role:[{v['uid']:v for v in a['series']} for a in r['arms']] for role,r in [('development',dev),('validation',med)]}
 rows=[];by_patient=collections.defaultdict(list)
 for role,c,_ in g.roles():
  shape=list(map(int,c['native_shape']));a=g.np.asarray(c['affine_rcz_ras'],dtype=float);spacing=g.np.linalg.norm(a[:3,:3],axis=0);vv=float(abs(g.np.linalg.det(a[:3,:3])));assert vv>0
  counts=[arm[c['uid']]['metrics']['full']['gt_foreground'] for arm in maps[role]];assert len(set(counts))==1 and counts[0]>0
  m=dict(row_spacing_mm=float(spacing[0]),column_spacing_mm=float(spacing[1]),slice_spacing_mm=float(spacing[2]),slice_count=shape[2],voxel_volume_mm3=vv,GT_lesion_volume_mm3=int(counts[0])*vv,GT_foreground_fraction=int(counts[0])/math.prod(shape))
  row=dict(role=role,patient=c['patient'],uid=c['uid'],native_shape_rcz=shape,GT_foreground_voxels=int(counts[0]),metrics=m);rows.append(row);by_patient[(role,c['patient'])].append(m)
 assert len(rows)==28 and len(by_patient)==15 and sum(v['role']=='development' for v in rows)==19
 patients=[]
 for (role,p),vs in sorted(by_patient.items()):patients.append(dict(role=role,patient=p,series=len(vs),means={k:sum(v[k] for v in vs)/len(vs) for k in vs[0]}))
 groups={}
 for role,n in [('development',11),('validation',4)]:
  ps=[v for v in patients if v['role']==role];ss=[v for v in rows if v['role']==role];assert len(ps)==n
  groups[role]=dict(patients=len(ps),series=len(ss),patient_first_means={k:sum(p['means'][k] for p in ps)/len(ps) for k in ps[0]['means']},series_ranges={k:dict(min=min(p['metrics'][k] for p in ss),max=max(p['metrics'][k] for p in ss)) for k in ps[0]['means']})
 r=dict(complete=True,errors=[],all28_series15_patients_retained=True,all_four_arm_GT_counts_identical_per_case=True,groups=groups,patients=patients,series=rows,GT_derived_features_used_for_analysis_only=True,deployment_gain_features_not_generated=True,causal_or_significance_claimed=False,MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,CUDA_initialized=g.torch.cuda.is_initialized(),confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',source_bindings=[entry(p) for p in [Path(__file__),HERE/'COHORT_METADATA_PROTOCOL.md',devp,medp,auditp,Path(g.__file__)]],elapsed_seconds=time.perf_counter()-started)
 assert not r['CUDA_initialized'];guard();out=HERE/'cohort_metadata_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',r);assert (out/'receipt.json').stat().st_size<30000 and time.perf_counter()-started<60
 print(json.dumps(dict(complete=True,groups=groups,patients=patients,elapsed_seconds=time.perf_counter()-started),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
