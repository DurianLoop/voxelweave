"""Independent read-only arithmetic and source-hash check of the thin-3D pilot."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "experiments/ds007045_thin3d_model_pilot"
QUAL = ROOT / "experiments/ds007045_cohort_label_qualification/cases"
SIDECARS = ROOT / "literature/source_cache/ds007045_raw_t2_sidecars_2026-10-01/summary.json"
OUT = PILOT / "independent_full_verification.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def require_close(a: float, b: float, where: str) -> None:
    if not math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-12):
        raise AssertionError(f"Arithmetic mismatch at {where}: {a} != {b}")


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    ids = sorted(json.loads(SIDECARS.read_text(encoding="utf-8"))["thin_3d_<=1_5mm"])
    summary = json.loads((PILOT / "summary.json").read_text(encoding="utf-8"))
    if len(ids) != 34 or summary["attempted"] != 34 or not summary["complete_cohort"]:
        raise AssertionError("Frozen 34-case denominator not completed")
    checked = []
    for case in ids:
        item = json.loads((PILOT / "cases" / f"{case}.json").read_text(encoding="utf-8"))
        if not item["complete"]:
            checked.append({"case": case, "complete": False})
            continue
        qualifier = json.loads((QUAL / f"{case}.json").read_text(encoding="utf-8"))
        if item["targets"] != qualifier["targets"] or len(item["rows"]) != 4:
            raise AssertionError(f"Target list differs: {case}")
        t2_path = ROOT / item["source"]["t2_local_path"]
        mask_path = ROOT / qualifier["mask_local_path"]
        if (digest(t2_path) != item["source"]["t2_sha256"] or
                digest(mask_path) != item["source"]["mask_sha256"] or
                digest(mask_path) != qualifier["mask_sha256"]):
            raise AssertionError(f"Source file hash differs: {case}")
        with t2_path.open("rb") as stream:
            prefix_hash = hashlib.sha256(stream.read(65_536)).hexdigest()
        if prefix_hash != qualifier["t2_prefix_65536_sha256"]:
            raise AssertionError(f"T2 qualification prefix differs: {case}")
        span2 = item["observed_span"] ** 2
        if span2 <= 0:
            raise AssertionError(f"Invalid observed span: {case}")
        patient = item["patient"]
        if patient["case"] != case:
            raise AssertionError(f"Patient ID differs: {case}")
        for row in item["rows"]:
            if row["tumor_pixels"] < 64 or row["full_pixels"] < row["tumor_pixels"]:
                raise AssertionError(f"Invalid ROI size: {case} z{row['z']}")
            for roi in ("tumor", "full"):
                for method in ("pipeline_linear", "raw_linear", "hat", "swinir"):
                    prefix = f"{roi}_{method}"
                    require_close(row[f"{prefix}_normalized_mse"],
                                  row[f"{prefix}_mse"] / span2,
                                  f"{case} z{row['z']} {prefix}")
        for roi in ("tumor", "full"):
            for method in ("pipeline_linear", "raw_linear", "hat", "swinir"):
                for metric in ("normalized_mse", "mse", "mae"):
                    field = f"{roi}_{method}_{metric}"
                    require_close(patient[field], sum(row[field] for row in item["rows"]) / 4,
                                  f"{case} {field}")
            for model in ("swinir", "hat"):
                for baseline in ("pipeline_linear", "raw_linear"):
                    field = f"{roi}_{model}_minus_{baseline}_normalized_mse"
                    require_close(patient[field],
                                  patient[f"{roi}_{model}_normalized_mse"] -
                                  patient[f"{roi}_{baseline}_normalized_mse"],
                                  f"{case} {field}")
        sign = (patient["tumor_swinir_minus_pipeline_linear_normalized_mse"] > 0 and
                patient["full_swinir_minus_pipeline_linear_normalized_mse"] < 0)
        if patient["swinir_pipeline_sign_discordance"] != sign:
            raise AssertionError(f"Sign discordance differs: {case}")
        checked.append({"case": case, "complete": True, "site": patient["site"],
                        "tumor": patient["tumor_swinir_minus_pipeline_linear_normalized_mse"],
                        "full": patient["full_swinir_minus_pipeline_linear_normalized_mse"],
                        "sign": sign, "patient": patient})
    good = [row for row in checked if row["complete"]]
    if len(good) != summary["completed"] or len(checked) - len(good) != len(summary["failures"]):
        raise AssertionError("Completion denominator differs")
    rng = np.random.default_rng(20261004)
    draws = rng.integers(0, len(good), (5000, len(good)))
    for name, reported in summary["differences"].items():
        values = np.array([row["patient"][name] for row in good], dtype=np.float64)
        require_close(float(values.mean()), reported["mean"], name + " mean")
        ci = np.percentile(values[draws].mean(axis=1), [2.5, 97.5])
        for index in (0, 1):
            require_close(float(ci[index]), reported["ci95"][index], name + f" ci{index}")
        if int((values > 0).sum()) != reported["positive_patients"] or int((values < 0).sum()) != reported["negative_patients"]:
            raise AssertionError(f"Sign count differs: {name}")
    signs = sum(row["sign"] for row in good)
    if signs != summary["discordance"]["patients"] or dict(Counter(r["site"] for r in good)) != summary["sites"]:
        raise AssertionError("Discordance or site count differs")
    z = 1.959963984540054
    p = signs / len(good)
    wilson = (p + z * z / (2 * len(good)) -
              z * math.sqrt((p * (1 - p) + z * z / (4 * len(good))) / len(good))) / (1 + z * z / len(good))
    require_close(wilson, summary["discordance"]["wilson_95_lower"], "Wilson lower")
    for site, reported in summary["site_sensitivity"].items():
        site_rows = [row for row in good if row["site"] == site]
        if len(site_rows) != reported["patients"] or sum(row["sign"] for row in site_rows) != reported["discordant"]:
            raise AssertionError(f"Site count differs: {site}")
        for region in ("tumor", "full"):
            value = np.mean([row[region] for row in site_rows])
            require_close(float(value), reported[f"mean_{region}_difference"], site + region)
    result = {"attempted": len(checked), "completed": len(good),
              "source_hashes_checked": len(good) * 2,
              "targets_arithmetically_checked": len(good) * 4,
              "difference_intervals_checked": len(summary["differences"]),
              "sites_checked": len(summary["site_sensitivity"]),
              "discordant_patients": signs,
              "independent_arithmetic_and_hash_check": "pass"}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
