"""Cross-check official release log subjects against fixed Git split and TCIA."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "literature/source_cache/vs_seg_task_model_sources_2026-10-02"
LOG_ROOT = ROOT / "literature/source_cache/vs_seg_t2_release_logs_2026-10-02"
OUT = LOG_ROOT / "split_verification.json"


def parse_log(path: Path) -> dict[str, list[str]]:
    result = {}
    for name in ("training", "validation", "test"):
        line = next(x for x in path.read_text().splitlines() if re.search(rf"\b{name} set\s*=\s*\[", x))
        records = ast.literal_eval(line.split("=", 1)[1].strip())
        ids = []
        for r in records:
            image_id = int(re.search(r"/vs_gk_(\d+)/", r["image"]).group(1))
            label_id = int(re.search(r"/vs_gk_(\d+)/", r["label"]).group(1))
            if image_id != label_id:
                raise ValueError("Logged image and label patient differ")
            ids.append(f"VS-SEG-{image_id:03d}")
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate logged subject")
        result[name] = ids
    return result


def main() -> None:
    split = {name: [] for name in ("training", "validation", "test")}
    with (SOURCE / "params/split_TCIA.csv").open(newline="") as stream:
        for subject, group in csv.reader(stream):
            split[group].append(f"VS-SEG-{int(subject.removeprefix('vs_gk_')):03d}")
    results = {}
    for name in ("training_log.txt", "test_log.txt"):
        log = LOG_ROOT / "UNet2d5_Att_Hard_T2_final/logs" / name
        logged = parse_log(log)
        results[name] = {"sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
                         "counts": {k: len(v) for k, v in logged.items()},
                         "all_subject_lists_equal_to_git_split": logged == split}
    cohort = json.loads((ROOT / "literature/source_cache/vs_seg_nonpixel_cohort_2026-10-01.json").read_text())
    listed = {x["patient"]: x for x in cohort["t2_series"]}
    mapped = {p.stem for p in (ROOT / "literature/source_cache/vs_seg_rtstruct_labels_2026-10-01").glob("VS-SEG-*.json")}
    bound = json.loads((ROOT / "experiments/vs_seg_target_bound_independent_2026-10-02.json").read_text())
    bound_by_id = {x["patient"]: x for x in bound["cases"]}
    previously_attempted = {p.stem for p in (ROOT / "experiments/vs_seg_thin3d_model_confirmation/cases").glob("*.json")}
    test = split["test"]
    result = {"logs": results, "split_counts": {k: len(v) for k, v in split.items()},
              "test_ids": test, "test_missing_from_mapped_242": sorted(set(test) - mapped),
              "test_missing_from_nbia_241": sorted(set(test) - set(listed)),
              "test_overlap_with_stopped_14_case_attempts": sorted(set(test) & previously_attempted),
              "test_possible_under_old_four_target_relaxation": sum(bound_by_id[x]["possible_ignoring_all_edges_pixels"] for x in test),
              "test_series_counts": {"CISS": sum("ci3d" in listed[x]["description"].lower() for x in test),
                                     "TSE": sum("tse3d" in listed[x]["description"].lower() for x in test)},
              "released_native_t2_mean_dice": 0.9066144033618595,
              "released_native_t2_dice_std": 0.03628977831172135,
              "these_are_release_log_values_not_our_task_results": True,
              "checkpoint_deserialized": False, "patient_pixels_read": False}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "test_ids"}, indent=2))
    if not all(x["all_subject_lists_equal_to_git_split"] for x in results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
