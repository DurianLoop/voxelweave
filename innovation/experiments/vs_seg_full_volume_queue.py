"""Resume the frozen queue, verify only new outputs, then write a reviewable result."""
from __future__ import annotations
import datetime
import argparse
import json
import subprocess
import sys
import time
import traceback
from pathlib import Path

from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_cohort import CONTRACT, OUT, cases_from_sources, successful_conditions, verify_contract, write_json
from vs_seg_full_volume_runtime import CONDITIONS, sha

QUEUE = ROOT / "experiments/vs_seg_full_volume_queue"


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def verification_current(patient, records, contract_sha):
    path = OUT / f"verification_{patient}.json"
    if not path.exists():
        return False
    proof = json.loads(path.read_text())
    expected = {(patient, name, record["prediction_sha256"]) for name, record in records.items()}
    found = {(r["patient"], r["condition"], r["prediction_sha256"]) for r in proof["checked_conditions"]}
    return not proof["errors"] and proof["contract_sha256"] == contract_sha and proof["script_sha256"] == sha(ROOT / "experiments/verify_vs_seg_full_volume_cohort.py") and proof["reconstruction_pixels_independently_regenerated"] and expected == found and len(records) == 7


def write_completed_report(contract, contract_sha):
    import numpy as np
    records = {p: successful_conditions(p, contract_sha) for p in contract["main_roster"]}
    state = json.loads((OUT / "status.json").read_text())
    if not state["main_complete"] or any(len(r) != 7 for r in records.values()):
        raise ValueError("Cannot report an incomplete fixed main cohort")
    summaries = []
    for name in CONDITIONS:
        for ref in ("original_json", "rtstruct"):
            metrics = [records[p][name]["task_metrics"][ref]["full"] for p in records]
            boundaries = [m["boundary"] for m in metrics]
            summaries.append({"condition": name, "reference": ref, "patients": len(metrics),
                              "mean_dice": float(np.mean([m["dice"] for m in metrics])),
                              "median_dice": float(np.median([m["dice"] for m in metrics])),
                              "mean_absolute_relative_volume_error": float(np.mean([m["absolute_relative_volume_error"] for m in metrics])),
                              "empty_predictions": sum(m["prediction_voxels"] == 0 for m in metrics),
                              "boundary_infinite_or_undefined_patients": sum(m["status"] != "finite" for m in boundaries),
                              "mean_support_nmse": float(np.mean([records[p][name]["image_metrics"]["support"]["target_equal_nmse"] for p in records]))})
    details = {"contract_sha256": contract_sha, "main_patients": 45, "independent_saved_outputs_verified": True,
               "publication_claim_confirmed": False, "primary_analysis": state["analysis"],
               "fixed_joint_direction_supported": state["fixed_primary_joint_direction_supported"], "condition_summaries": summaries}
    write_json(QUEUE / "completed_analysis.json", details)
    image = state["analysis"]["primary_image_difference"]
    task = state["analysis"]["primary_task_difference"]
    lines = ["# 固定完整体积队列：全部推断及输出复查结果", "",
             "这是固定 45 CISS 主名单全部完成后的自动结果记录，1 TSE 保留为次要病例。全部患者保存输出已复查，重建再生成哈希已核对。仍需要人工核读固定敏感性、反证及文献边界；自动程序不确认可发表主张。", "",
             f"合同 SHA256：{contract_sha}", "",
             f"主要 HAT − pipeline PCHIP 支持域 NMSE 均值差：{image['mean_difference']:.10g}，95% 患者 bootstrap 区间 {image['ci95_percentile']}。", "",
             f"主要原 JSON 完整体积 Dice 均值差：{task['mean_difference']:.10g}，95% 区间 {task['ci95_percentile']}。", "",
             f"预定双终点方向判据：{'支持' if state['fixed_primary_joint_direction_supported'] else '未支持'}。这不是统计通过即发表的判定。", "",
             "| 条件 | 原 JSON Dice 均值 | RT Dice 均值 | 支持域 NMSE 均值 | 原 JSON 空预测数 |", "| --- | ---: | ---: | ---: | ---: |"]
    for name in CONDITIONS:
        original = next(r for r in summaries if r["condition"] == name and r["reference"] == "original_json")
        rt = next(r for r in summaries if r["condition"] == name and r["reference"] == "rtstruct")
        lines.append(f"| {name} | {original['mean_dice']:.8f} | {rt['mean_dice']:.8f} | {original['mean_support_nmse']:.8g} | {original['empty_predictions']} |")
    lines.extend(["", "所有固定次要比较和标签/范围/边界敏感性保存在 [完整 JSON](experiments/vs_seg_full_volume_cohort/status.json)；次要区间为描述性，未作 familywise 调整。", "",
                  "原四层规则的来源覆盖仍以 [独立覆盖核验](experiments/vs_seg_full_volume_coverage/independent_verification.json)为准，不能用本结果修改主要名单。原 JSON 与历史 NIfTI 精确等价未证实、单中心/单分割器、体素中心边界约定及模拟抽层的限制保留。", ""])
    (ROOT / "VS_SEG_FULL_VOLUME_COHORT_COMPLETE_RESULT_2026-10-02.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    resource_gate()
    contract = verify_contract()
    contract_sha = sha(CONTRACT)
    QUEUE.mkdir(parents=True, exist_ok=True)
    if args.check_only:
        cases = cases_from_sources()
        records = {r["patient"]: successful_conditions(r["patient"], contract_sha) for r in cases}
        checked = {"script_sha256": sha(Path(__file__)), "contract_sha256": contract_sha,
                   "planned_main_patients": len(contract["main_roster"]), "planned_secondary_patients": len(contract["secondary_roster"]),
                   "completed_conditions": sum(len(r) for r in records.values()),
                   "current_verified_patients": [p for p, r in records.items() if verification_current(p, r, contract_sha)],
                   "ready_to_resume": True, "child_process_started": False}
        write_json(QUEUE / "prelaunch_check.json", checked)
        print(json.dumps(checked))
        return
    attempt = len(list(QUEUE.glob("attempt_*.json"))) + 1
    path = QUEUE / f"attempt_{attempt:02d}.json"
    report = {"attempt": attempt, "started_utc": utc(), "script_sha256": sha(Path(__file__)), "contract_sha256": contract_sha,
              "complete": False, "active_stage": "inference", "cuda_devices_hidden": True, "stages": []}
    start = time.perf_counter()
    write_json(path, report)

    def command(stage, arguments):
        resource_gate()
        log = QUEUE / f"{stage}_attempt_{attempt:02d}.log"
        report["active_stage"] = stage
        write_json(path, report)
        stage_start = time.perf_counter()
        with log.open("wb") as stream:
            completed = subprocess.run([sys.executable, "-B", *arguments], cwd=str(ROOT.parent), stdout=stream, stderr=subprocess.STDOUT,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        record = {"stage": stage, "arguments": arguments, "returncode": completed.returncode,
                  "log_file": log.relative_to(ROOT).as_posix(), "log_sha256": sha(log), "seconds": time.perf_counter() - stage_start}
        report["stages"].append(record)
        write_json(path, report)
        print(json.dumps(record), flush=True)
        if completed.returncode:
            raise RuntimeError(stage + " returned nonzero; frozen patient denominator retained")

    try:
        print(json.dumps({"queue_started": True, "attempt": attempt, "contract_sha256": contract_sha, "cpu_only": True}), flush=True)
        command("inference", [str(ROOT / "experiments/vs_seg_full_volume_cohort.py")])
        state = json.loads((OUT / "status.json").read_text())
        if not state["main_complete"] or not state["secondary_complete"]:
            raise ValueError("Inference returned but fixed cohort is incomplete")
        for case in cases_from_sources():
            records = successful_conditions(case["patient"], contract_sha)
            if verification_current(case["patient"], records, contract_sha):
                report.setdefault("verification_reused", []).append(case["patient"])
                continue
            command("verify_" + case["patient"], [str(ROOT / "experiments/verify_vs_seg_full_volume_cohort.py"), "--patient", case["patient"], "--regenerate"])
        write_completed_report(contract, contract_sha)
        report["complete"] = True
        report["active_stage"] = "complete"
    except Exception as exc:
        report.update({"active_stage": "failed", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    finally:
        report.update({"finished_utc": utc(), "elapsed_seconds": time.perf_counter() - start})
        write_json(path, report)
    print(json.dumps({"complete": report["complete"], "active_stage": report["active_stage"], "error": report.get("error")}), flush=True)
    if not report["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
