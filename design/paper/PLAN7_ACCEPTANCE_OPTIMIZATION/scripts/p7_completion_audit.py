"""Plan7 requirement-by-requirement completion audit."""
from pathlib import Path
import json,re,subprocess

HERE=Path(__file__).resolve(); P7=HERE.parents[1]; PAPER=P7.parent
TMI=PAPER/"TMI"/"TMI_MANUSCRIPT_SUBMISSION_FINAL"
CV=PAPER/"CVPR"/"CVPR_UPGRADE"/"PAPER_FINAL"

REQ_P7=["ACCEPTANCE_RISK_REGISTER.md","EXPERIMENT_QUEUE.md","NOVELTY_COLLISION_AUDIT.md",
 "TMI_REVIEW_SIMULATION.md","CVPR_REVIEW_SIMULATION.md","VENUE_CALIBRATION.md","CLAIM_EVIDENCE_MATRIX.md",
 "DECISION_LOG.md","RESEARCH_STATE.md","NEGATIVE_RESULTS.md","SUBMISSION_OVERLAP_AUDIT.md",
 "TMI_REBUTTAL_BANK.md","CVPR_REBUTTAL_BANK.md","CLAIM_COMPRESSION_AND_STRESS_TEST.md",
 "PDF_VISUAL_AUDIT.md","FINAL_ACCEPTANCE_OPTIMIZATION_REPORT.md"]
REQ_TMI=["main.tex","main.pdf","references.bib","CLAIM_TRACEABILITY.md","REVIEWER_RISK_AUDIT.md","COVER_LETTER_DRAFT.md"]
REQ_CV=["main.tex","main.pdf","supplement.tex","supplement.pdf","references.bib","CLAIM_TRACEABILITY.md","REVIEWER_RISK_AUDIT.md","REBUTTAL_BANK.md"]

def pdf_pages(path):
 out=subprocess.run(["pdfinfo",str(path)],capture_output=True,text=True,encoding="utf-8",errors="replace").stdout
 m=re.search(r"^Pages:\s+(\d+)",out,re.M); return int(m.group(1)) if m else None
def log_clean(path):
 if not path.exists(): return False
 t=path.read_text(encoding="utf-8",errors="replace")
 return not re.search(r"Undefined|Overfull|LaTeX Warning: Reference|Citation.*undefined",t,re.I)

checks={}
for n in REQ_P7: checks[f"p7/{n}"]=(P7/n).is_file() and (P7/n).stat().st_size>0
for n in REQ_TMI: checks[f"tmi/{n}"]=(TMI/n).is_file() and (TMI/n).stat().st_size>0
for n in REQ_CV: checks[f"cvpr/{n}"]=(CV/n).is_file() and (CV/n).stat().st_size>0
checks["experiment/P7-CV-E02_complete"]=(json.loads((P7/"outputs"/"p7_cvpr_neural_influence_stability.json").read_text())["status"]=="COMPLETE")
checks["experiment/P7-CV-E02_parameter_gate"]=(json.loads((P7/"outputs"/"p7_cvpr_neural_influence_stability.json").read_text())["perturbation_parameter_gate_passed"] is True)
checks["experiment/P7-CV-E02_plane_boundary_recorded"]=(json.loads((P7/"outputs"/"p7_cvpr_neural_influence_stability.json").read_text())["plane_selection_gate_passed"] is False)
for eid in ["P7-CV-E01","P7-CV-E02","P7-CV-E03","P7-CV-E04","P7-TMI-E01","P7-TMI-E02","P7-TMI-E03"]:
 checks[f"queue/{eid}_complete"]=bool(re.search(rf"\|\s*{re.escape(eid)}\s*\|.*?COMPLETE",(P7/"EXPERIMENT_QUEUE.md").read_text(encoding="utf-8"),re.I))
checks["pdf/tmi_pages_8"]=pdf_pages(TMI/"main.pdf")==8
checks["pdf/cvpr_pages_8"]=pdf_pages(CV/"main.pdf")==8
checks["pdf/cvpr_supp_pages_7"]=pdf_pages(CV/"supplement.pdf")==7
checks["log/tmi_clean"]=log_clean(TMI/"main.log")
checks["log/cvpr_clean"]=log_clean(CV/"main.log")
checks["log/cvpr_supp_clean"]=log_clean(CV/"supplement.log")
candidate_text="\n".join((d/n).read_text(encoding="utf-8",errors="replace") for d,n in [(TMI,"main.tex"),(CV,"main.tex"),(CV,"supplement.tex")])
checks["manuscripts/no_pending_markers"]=not re.search(r"PENDING|TODO|TBD|RUNNING|RESOURCE-WAIT",candidate_text,re.I)
overlap=json.loads((P7/"outputs"/"p7_submission_overlap.json").read_text())
checks["overlap/final_audit_complete"]=overlap["status"]=="COMPLETE" and overlap["tmi_paragraphs"]==63 and overlap["cvpr_paragraphs"]==47
checks["review/final_TMI_verdict"]= "READY AFTER HUMAN METADATA" in (P7/"FINAL_ACCEPTANCE_OPTIMIZATION_REPORT.md").read_text(encoding="utf-8")
checks["review/final_CVPR_verdict"]= "MERGE / CHANGE SUBMISSION SEQUENCE" in (P7/"FINAL_ACCEPTANCE_OPTIMIZATION_REPORT.md").read_text(encoding="utf-8")
failed=[k for k,v in checks.items() if not v]
payload={"audit":"PLAN7_COMPLETION","status":"PASS" if not failed else "FAIL","checks":len(checks),"failed":failed,"details":checks}
(P7/"outputs"/"p7_completion_audit.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
lines=["# Plan7 completion audit","",f"- Status: **{payload['status']}**",f"- Checks: {len(checks)}",f"- Failed: {len(failed)}","", "| Requirement | Result |","|---|---|"]
lines += [f"| `{k}` | {'PASS' if v else 'FAIL'} |" for k,v in checks.items()]
(P7/"PLAN7_COMPLETION_AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps(payload,indent=2)); raise SystemExit(1 if failed else 0)
