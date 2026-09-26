"""P7-TMI-E03: explicit reliability / compute / storage / information trade-off.

Never substitute timing from one strategy for another and never imply that a
score-only latency includes generating its prerequisite reconstructions.
"""
from pathlib import Path
import json
import pandas as pd

HERE=Path(__file__).resolve(); P7=HERE.parents[1]; PAPER=P7.parent; OUT=P7/"outputs"
RISK=PAPER/"TMI"/"TMI_MANUSCRIPT_MASTER"/"experiments"/"p6_e12_risk_summary.csv"
COST=PAPER/"CVPR"/"CVPR_UPGRADE"/"outputs"/"plan6_efficiency.csv"
CV_RISK=PAPER/"CVPR"/"CVPR_UPGRADE"/"outputs"/"plan6_frozen_risk_coverage_summary.csv"

ASSUMPTION={
 "Adjacent-anchor MAE":"already acquired sparse anchors; no reconstruction",
 "Anchor-CV":"withhold one acquired interior anchor and interpolate it from adjacent acquired anchors",
 "Output PC":"two reconstruction volumes must already exist or must be generated",
 "Committee":"frozen HAT and SwinIR outputs from the same sparse input",
 "Flip TTA":"one model evaluated on original and horizontally flipped views",
 "Measurement-disjoint":"two complementary physical phase grids / acquired-anchor subsets",
}
REGIME={
 "Adjacent-anchor MAE":"zero-call default screen; strongest NingXia nAURC in the common-endpoint audit",
 "Anchor-CV":"zero-call acquired-only alternative when an interior anchor can be withheld; not more accurate than adjacent difference",
 "Output PC":"use when two outputs already exist; generation cost cannot be ignored",
 "Committee":"use only when both architecture outputs already exist for another reason",
 "Flip TTA":"cost comparator only: definition-matched three-cohort reliability output is unavailable",
 "Measurement-disjoint":"worth considering on fastMRI/IXI when complementary reconstructions already exist; not universal",
}

def main():
 OUT.mkdir(parents=True,exist_ok=True); risk=pd.read_csv(RISK); cost=pd.read_csv(COST); cv=pd.read_csv(CV_RISK)
 rows=[]
 for ds in sorted(risk.dataset.unique()):
  rc=risk[risk.dataset.eq(ds)].set_index("method")
  cc=cost[cost.dataset.eq(ds)]
  cvd=cv[cv.dataset.eq(ds)]
  specs=[
   ("Adjacent-anchor MAE","score_only_cpu","Adjacent difference","common TMI endpoint",0),
   ("Anchor-CV","score_only_cpu","Anchor-CV","model-specific CVPR endpoints",0),
   ("Output PC","score_only_cpu","Output PC score","model-specific CVPR endpoints",2),
   ("Committee","strategy_total","Committee (HAT+SwinIR)","common TMI endpoint",2),
   ("Flip TTA","strategy_total","HAT flip TTA pair","not evaluated on a definition-matched three-cohort endpoint",2),
   ("Measurement-disjoint","strategy_total","HAT disjoint phase pair","common TMI endpoint",2),
  ]
  for method,stage,cost_name,source,calls in specs:
   q=cc[(cc.stage.eq(stage))&cc.method.eq(cost_name)]
   rec={"dataset":ds,"method":method,"reliability_source":source,"required_neural_calls":calls,
        "median_ms":float(q.median_ms.iloc[0]),"peak_allocated_mib":float(q.peak_allocated_mib.iloc[0]),
        "stored_output_mib":float(q.stored_output_mib.iloc[0]),"information_assumption":ASSUMPTION[method],
        "operating_regime":REGIME[method],"spearman":None,"nAURC":None,"nAURC_model_min":None,"nAURC_model_max":None}
   if method in rc.index:
    rec["spearman"]=float(rc.loc[method,"spearman"]); rec["nAURC"]=float(rc.loc[method,"nAURC"])
   elif method=="Anchor-CV":
    z=cvd[cvd.method.eq("Anchor-CV")].nAURC; rec["nAURC_model_min"]=float(z.min()); rec["nAURC_model_max"]=float(z.max())
   elif method=="Output PC":
    z=cvd[cvd.method.eq("Output PC")].nAURC; rec["nAURC_model_min"]=float(z.min()); rec["nAURC_model_max"]=float(z.max())
   rows.append(rec)
 table=pd.DataFrame(rows); table.to_csv(OUT/"p7_tmi_reliability_compute_tradeoff.csv",index=False)
 payload={"experiment":"P7-TMI-E03","status":"COMPLETE",
  "measurement_scope":"representative measured cost joined to full-cohort reliability; endpoint-source differences remain explicit",
  "missing_evidence":"flip-TTA reliability is N/A because a definition-matched IXI output was unavailable",
  "decision":"adjacent is the zero-call default; disjoint is conditional on already available complementary outputs and cohort evidence",
  "output":"p7_tmi_reliability_compute_tradeoff.csv"}
 (OUT/"p7_tmi_operating_regimes.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
 print(table.to_string(index=False)); print(json.dumps(payload,indent=2))

if __name__=="__main__": main()
