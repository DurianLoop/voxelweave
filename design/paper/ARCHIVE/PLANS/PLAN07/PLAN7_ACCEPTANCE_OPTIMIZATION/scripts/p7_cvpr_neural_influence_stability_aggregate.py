"""Aggregate resumable P7-CV-E02 dataset shards and evaluate the frozen gate."""
from pathlib import Path
import importlib.util, json
import pandas as pd

HERE=Path(__file__).resolve(); P7=HERE.parents[1]; OUT=P7/"outputs"
spec=importlib.util.spec_from_file_location("e02",HERE.with_name("p7_cvpr_neural_influence_stability.py"))
e02=importlib.util.module_from_spec(spec); spec.loader.exec_module(e02)

def main():
 shards=[]; missing=[]
 for ds,expected in (("fastmri",48),("ixi",230),("ningxia",44)):
  p=OUT/f"p7_cvpr_neural_influence_stability_per_case_context_{ds}.csv"
  if not p.exists(): missing.append(ds); continue
  q=pd.read_csv(p); complete=q[["dataset","model","case"]].drop_duplicates().shape[0]
  if complete!=expected: missing.append(f"{ds}:{complete}/{expected}")
  shards.append(q)
 if missing: raise SystemExit("Incomplete shards: "+", ".join(missing))
 x=pd.concat(shards,ignore_index=True)
 x.to_csv(OUT/"p7_cvpr_neural_influence_stability_per_case_context.csv",index=False)
 summary=[]
 for (ds,model),g in x.groupby(["dataset","model"]):
  keys=["case","context"]
  base=g[g.condition.eq(e02.BASELINE)][keys+["neural_influence"]].rename(columns={"neural_influence":"base"})
  for condition,q in g.groupby("condition"):
   z=q.merge(base,on=keys)
   summary.append({"dataset":ds,"model":model,"condition":condition,"cases":q.case.nunique(),
    "rank_stability_vs_baseline":e02.rho(z.neural_influence,z.base),
    "rho_error_cosine":e02.rho(q.neural_influence,q.error_cosine),
    "rho_shared_fraction":e02.rho(q.neural_influence,q.shared_fraction),
    "rho_observable_fraction":e02.rho(q.neural_influence,q.observable_fraction)})
 s=pd.DataFrame(summary); s.to_csv(OUT/"p7_cvpr_neural_influence_stability_summary.csv",index=False)
 non=s[s.condition.ne(e02.BASELINE)]
 gates={c:{"strata":int(len(q)),"at_least_085":int((q.rank_stability_vs_baseline>=.85).sum()),
   "minimum":float(q.rank_stability_vs_baseline.min()),
   "passed":bool(len(q)==6 and (q.rank_stability_vs_baseline>=.85).sum()>=5 and (q.rank_stability_vs_baseline>=.70).all())}
   for c,q in non.groupby("condition")}
 # Plane choice is a separate prespecified condition family. Compare ranks of
 # the same case/context observations across the three frozen physical planes.
 raw=pd.read_csv(P7.parent/"CVPR"/"CVPR_UPGRADE"/"outputs"/"plan6_neural_shared_influence_confirm3_per_case_config.csv")
 raw=raw[raw.context.isin([str(q) for q in e02.CONTEXTS[1:]])].copy()
 raw["plane_order"]=raw.groupby(["dataset","model","case"])["z"].rank(method="dense").astype(int)
 plane_rows=[]
 for (ds,model),q in raw.groupby(["dataset","model"]):
  wide=q.pivot_table(index=["case","context"],columns="plane_order",values="neural_influence_cosine")
  for a,b in ((1,2),(1,3),(2,3)):
   z=wide[[a,b]].dropna()
   plane_rows.append({"dataset":ds,"model":model,"plane_pair":f"{a}-{b}","observations":len(z),
                      "rank_stability":e02.rho(z[a],z[b])})
 plane=pd.DataFrame(plane_rows); plane.to_csv(OUT/"p7_cvpr_neural_influence_plane_rank_stability.csv",index=False)
 plane_gates={pair:{"strata":int(len(q)),"at_least_085":int((q.rank_stability>=.85).sum()),
   "minimum":float(q.rank_stability.min()),
   "passed":bool(len(q)==6 and (q.rank_stability>=.85).sum()>=5 and (q.rank_stability>=.70).all())}
   for pair,q in plane.groupby("plane_pair")}
 perturbation_passed=bool(all(v["passed"] for v in gates.values()))
 plane_passed=bool(all(v["passed"] for v in plane_gates.values()))
 payload={"experiment":"P7-CV-E02","status":"COMPLETE","baseline":e02.BASELINE,
  "prespecified_primary_gate":"rank stability >=0.85 in at least 5/6 strata per condition and no stratum <0.70",
  "perturbation_parameter_gate_passed":perturbation_passed,"gate_by_perturbation_condition":gates,
  "plane_selection_gate_passed":plane_passed,"gate_by_plane_pair":plane_gates,
  "overall_stability_hypothesis_passed":bool(perturbation_passed and plane_passed),
  "decision":"PARTIALLY_SUPPORTED_PERTURBATIONS_STABLE_BUT_PLANE_GATE_FAILED" if perturbation_passed and not plane_passed else ("SUPPORTED" if perturbation_passed and plane_passed else "FALSIFIED"),
  "strata":6,"cases_by_dataset":{"fastmri":24,"ixi":115,"ningxia_series":22,"ningxia_patient_clusters":8},
  "scope":"full central-plane amplitude/sign/field/direction grid plus frozen three-plane association audit"}
 (OUT/"p7_cvpr_neural_influence_stability.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
 print(json.dumps(payload,indent=2)); print(s.to_string(index=False)); print(plane.to_string(index=False))

if __name__=="__main__": main()
