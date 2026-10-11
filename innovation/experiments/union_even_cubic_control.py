"""CPU-only four-neighbor cubic baselines on fixed public-source targets."""
from __future__ import annotations

import csv
import json
import math
import zipfile
from collections import defaultdict
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy.interpolate import PchipInterpolator

import union_even_linear_control as prior


ROOT = prior.ROOT
PLAN = ROOT / "UNION_EVEN_CUBIC_CONTROL_PLAN_2026-10-01.md"
OUT = ROOT / "experiments/union_even_cubic_control"
PRIOR = ROOT / "experiments/union_even_linear_control/per_target.csv"
PRIOR_HASH = "7b0c2fd2df320b9d2bc85071d20cfe43fe1fb69b2ca79b239c0d2f2e59903611"
OFFSETS = np.array([-3., -1., 1., 3.])


def score(source: str, recorded: dict, planes: dict[int, np.ndarray]) -> dict:
    z = int(recorded["z"])
    left = (z // 4) * 4
    needed = {z - 3, z - 1, z, z + 1, z + 3, left, left + 4}
    if not needed <= planes.keys():
        raise ValueError(f"Four-plane contract unavailable: {source}, {recorded['patient']}, {z}")
    anchors = [planes[z + offset].astype(np.float64) for offset in (-3, -1, 1, 3)]
    p0left, p0right = planes[left], planes[left + 4]
    mask = ((np.abs(p0left) > .01 * max(float(np.max(np.abs(p0left))), 1e-6)) |
            (np.abs(p0right) > .01 * max(float(np.max(np.abs(p0right))), 1e-6)))
    if int(mask.sum()) != int(recorded["support_pixels"]):
        raise ValueError(f"Support changed: {source}, {recorded['patient']}, {z}")
    target = planes[z][mask].astype(np.float64)
    linear = (anchors[1] + anchors[2]) / 2
    linear_mse = float(np.mean((linear[mask] - target) ** 2))
    if not math.isclose(linear_mse, float(recorded["union_linear_mse"]), abs_tol=1e-5):
        raise ValueError(f"Prior linear endpoint changed: {source}, {recorded['patient']}, {z}")
    catmull = (-anchors[0] + 9 * anchors[1] + 9 * anchors[2] - anchors[3]) / 16
    pchip = PchipInterpolator(OFFSETS, np.stack(anchors), axis=0)(0)
    cat_mse = float(np.mean((catmull[mask] - target) ** 2))
    pchip_mse = float(np.mean((pchip[mask] - target) ** 2))
    model = float(recorded["disjoint_ensemble_mse"])
    return {"source": source, "patient": recorded["patient"], "z": z,
            "residue": int(recorded["residue"]), "stratum": recorded["stratum"],
            "support_pixels": int(mask.sum()), "linear_mse": linear_mse,
            "catmull_mse": cat_mse, "pchip_mse": pchip_mse,
            "disjoint_ensemble_mse": model,
            "catmull_relative_ensemble_gain": (cat_mse - model) / cat_mse,
            "pchip_relative_ensemble_gain": (pchip_mse - model) / pchip_mse}


def summarize(targets: list[dict]) -> tuple[dict, list[dict]]:
    patients = []
    for source in ("msvalid", "remind"):
        by_patient = defaultdict(list)
        for row in targets:
            if row["source"] == source:
                by_patient[row["patient"]].append(row)
        for patient, rows in sorted(by_patient.items()):
            residue = {r: [row for row in rows if row["residue"] == r] for r in (1, 3)}
            if not all(residue.values()):
                raise ValueError(f"Missing residue: {source}, {patient}")
            agg = lambda key: float(np.mean([np.mean([row[key] for row in residue[r]]) for r in (1, 3)]))
            cat, pchip, model = agg("catmull_mse"), agg("pchip_mse"), agg("disjoint_ensemble_mse")
            patients.append({"source": source, "patient": patient, "stratum": rows[0]["stratum"],
                             "targets": len(rows), "catmull_mse": cat, "pchip_mse": pchip,
                             "disjoint_ensemble_mse": model,
                             "catmull_relative_ensemble_gain": (cat - model) / cat,
                             "pchip_relative_ensemble_gain": (pchip - model) / pchip})
    summary = {}
    for source, seed in (("msvalid", 20261001), ("remind", 20261002)):
        group_patients = [row for row in patients if row["source"] == source]
        group_targets = [row for row in targets if row["source"] == source]
        rng = np.random.default_rng(seed)
        methods = {}
        for method in ("catmull", "pchip"):
            key = f"{method}_relative_ensemble_gain"
            values = np.array([row[key] for row in group_patients])
            if source == "msvalid":
                draws = values[rng.integers(0, len(values), size=(5000, len(values)))].mean(axis=1)
            else:
                draws = np.zeros(5000)
                for label, expected in (("2D_AX_T2", 35), ("2D_AX_T2_BLADE", 27)):
                    group = np.array([row[key] for row in group_patients if row["stratum"] == label])
                    if len(group) != expected:
                        raise ValueError(f"Wrong ReMIND stratum: {label}")
                    draws += (expected / len(values) *
                              group[rng.integers(0, expected, size=(5000, expected))].mean(axis=1))
            methods[method] = {"mean_patient_relative_ensemble_gain": float(values.mean()),
                               "ci95": np.percentile(draws, [2.5, 97.5]).tolist(),
                               "ensemble_better_patients": int((values > 0).sum()),
                               "cubic_better_patients": int((values < 0).sum()),
                               "ensemble_better_targets": sum(row[key] > 0 for row in group_targets),
                               "cubic_better_targets": sum(row[key] < 0 for row in group_targets)}
        summary[source] = {"patients": len(group_patients), "targets": len(group_targets),
                           "methods": methods}
    return summary, patients


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    recorded = defaultdict(list)
    for row in prior.csv_rows(PRIOR, PRIOR_HASH):
        recorded[(row["source"], row["patient"])].append(row)
    if len(recorded) != 146:
        raise ValueError("Prior patient set changed")
    if prior.sha256(prior.MS_MANIFEST) != prior.MS_MANIFEST_HASH:
        raise ValueError("MSValid source manifest changed")
    manifest = {row["patient"]: row for row in json.loads(prior.MS_MANIFEST.read_text(encoding="utf-8"))["records"]}
    geometry = {row["patient"]: row for row in json.loads(prior.MS_GEOMETRY.read_text(encoding="utf-8"))["patients"]}
    results = []
    for index, patient in enumerate(sorted(geometry), 1):
        record = manifest[patient]
        path = ROOT / record["path"]
        if prior.sha256(path) != record["sha256"]:
            raise ValueError(f"MSValid image hash changed: {patient}")
        volume = nib.load(str(path)).get_fdata(dtype=np.float32)
        if tuple(volume.shape) != tuple(geometry[patient]["shape"]):
            raise ValueError(f"MSValid geometry changed: {patient}")
        rows = recorded[("msvalid", patient)]
        expected = {z for r in (1, 3) for z in geometry[patient]["eligible_targets"][f"residue_{r}"]}
        if {int(row["z"]) for row in rows} != expected:
            raise ValueError(f"MSValid target list changed: {patient}")
        needed = {q for z in expected for q in (z - 3, z - 1, z, z + 1, z + 3, (z // 4) * 4, (z // 4 + 1) * 4)}
        if min(needed) < 0 or max(needed) >= volume.shape[2]:
            raise ValueError(f"MSValid four-plane bounds failed: {patient}")
        planes = {z: volume[:, :, z] for z in needed}
        for row in rows:
            results.append(score("msvalid", row, planes))
        if index % 10 == 0:
            print(f"MSValid {index}/84", flush=True)
    if prior.sha256(prior.REMIND_QUALIFIED) != prior.REMIND_QUALIFIED_HASH:
        raise ValueError("ReMIND qualification changed")
    qualified = json.loads(prior.REMIND_QUALIFIED.read_text(encoding="utf-8"))["records"]
    eligible = [row for row in qualified if row["eligible"]]
    if len(qualified) != 63 or len(eligible) != 62:
        raise ValueError("ReMIND patient set changed")
    for index, record in enumerate(eligible, 1):
        patient = record["patient"]
        path = ROOT / record["path"]
        if prior.sha256(path) != record["zip_sha256"]:
            raise ValueError(f"ReMIND ZIP hash changed: {patient}")
        rows = recorded[("remind", patient)]
        expected = {z for r in ("1", "3") for z in record["targets"][r]}
        if {int(row["z"]) for row in rows} != expected:
            raise ValueError(f"ReMIND target list changed: {patient}")
        needed = {q for z in expected for q in (z - 3, z - 1, z, z + 1, z + 3, (z // 4) * 4, (z // 4 + 1) * 4)}
        if min(needed) < 0 or max(needed) >= record["depth"]:
            raise ValueError(f"ReMIND four-plane bounds failed: {patient}")
        with zipfile.ZipFile(path) as archive:
            planes = {z: prior.read_dicom_plane(archive, record["ordered_files"][z]) for z in needed}
        for row in rows:
            results.append(score("remind", row, planes))
        if index % 10 == 0:
            print(f"ReMIND {index}/62", flush=True)
    if len(results) != 727:
        raise ValueError("Not all targets scored")
    summary, patients = summarize(results)
    OUT.mkdir(parents=True)
    for name, rows in (("per_target.csv", results), ("per_patient.csv", patients)):
        with (OUT / name).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    output = {"plan_sha256": prior.sha256(PLAN), "script_sha256": prior.sha256(Path(__file__)),
              "prior_linear_source_sha256": PRIOR_HASH, "sources": summary,
              "model_inference_run": False, "gpu_used": False, "status": "post_result_exploratory"}
    (OUT / "summary.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
