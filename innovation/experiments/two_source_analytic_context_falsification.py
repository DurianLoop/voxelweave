"""CPU-only PCHIP/linear context control on frozen public-source targets."""

from __future__ import annotations

import csv
import json
import zipfile
from collections import defaultdict
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy.interpolate import PchipInterpolator

import union_even_linear_control as prior


ROOT = prior.ROOT
PLAN = ROOT / "TWO_SOURCE_ANALYTIC_CONTEXT_FALSIFICATION_PROTOCOL_2026-10-01.md"
OUT = ROOT / "experiments/two_source_analytic_context_falsification"


def metric(a: np.ndarray, b: np.ndarray, y: np.ndarray) -> dict:
    ea, eb = a - y, b - y
    a_mse = float(np.mean(ea * ea))
    b_mse = float(np.mean(eb * eb))
    disagreement = float(np.mean((a - b) ** 2))
    denominator = 2 * (a_mse + b_mse)
    if not np.isfinite([a_mse, b_mse, disagreement, denominator]).all() or denominator <= 0:
        raise ValueError("Invalid paired-error metric")
    return {"a_mse": a_mse, "b_mse": b_mse,
            "paired_mse": (a_mse + b_mse) / 2,
            "disagreement_mse": disagreement, "observable": disagreement / denominator}


def score(source: str, original: dict, planes: dict[int, np.ndarray]) -> dict:
    z = int(original["z"])
    left = 4 * (z // 4)
    left2 = 2 + 4 * ((z - 2) // 4)
    anchors = [left - 4, left, left + 4, left + 8]
    needed = set(anchors + [left2, left2 + 4, z])
    if not needed <= planes.keys():
        raise ValueError(f"Missing analytic anchors: {source} z{z}")
    p0, p1 = planes[left], planes[left + 4]
    support = ((np.abs(p0) > .01 * max(float(np.max(np.abs(p0))), 1e-6)) |
               (np.abs(p1) > .01 * max(float(np.max(np.abs(p1))), 1e-6)))
    if int(support.sum()) != int(original["support_pixels"]):
        raise ValueError(f"Original support changed: {source} z{z}")
    values = np.stack([planes[q][support].astype(np.float64) for q in anchors])
    a = PchipInterpolator(np.asarray(anchors, dtype=np.float64), values, axis=0)(z)
    y = planes[z][support].astype(np.float64)
    b0 = ((1 - (z - left) / 4) * p0[support].astype(np.float64) +
          ((z - left) / 4) * p1[support].astype(np.float64))
    b2 = ((1 - (z - left2) / 4) * planes[left2][support].astype(np.float64) +
          ((z - left2) / 4) * planes[left2 + 4][support].astype(np.float64))
    if not np.isfinite([a, y, b0, b2]).all():
        raise ValueError(f"Nonfinite analytic arrays: {source} z{z}")
    shared, disjoint = metric(a, b0, y), metric(a, b2, y)
    return {"source": source, "patient": original["patient"], "z": z,
            "residue": int(original["residue"]),
            "stratum": original.get("series_description", "MSValid"),
            "support_pixels": int(support.sum()),
            "shared_o": shared["observable"], "disjoint_o": disjoint["observable"],
            "delta_o": disjoint["observable"] - shared["observable"],
            "neural_delta_o": float(original["delta_o"]),
            "analytic_minus_neural": disjoint["observable"] - shared["observable"] - float(original["delta_o"]),
            "a_mse": shared["a_mse"], "shared_b_mse": shared["b_mse"],
            "disjoint_b_mse": disjoint["b_mse"],
            "shared_paired_mse": shared["paired_mse"],
            "disjoint_paired_mse": disjoint["paired_mse"],
            "shared_disagreement_mse": shared["disagreement_mse"],
            "disjoint_disagreement_mse": disjoint["disagreement_mse"],
            "fixed_denominator_delta_o":
                (disjoint["disagreement_mse"] - shared["disagreement_mse"]) /
                (4 * shared["paired_mse"])}


def aggregate(targets: list[dict]) -> tuple[list[dict], dict]:
    patients = []
    keys = ("shared_o", "disjoint_o", "delta_o", "neural_delta_o",
            "analytic_minus_neural", "a_mse", "shared_b_mse", "disjoint_b_mse",
            "shared_paired_mse", "disjoint_paired_mse", "shared_disagreement_mse",
            "disjoint_disagreement_mse", "fixed_denominator_delta_o")
    groups = defaultdict(list)
    for row in targets:
        groups[(row["source"], row["patient"])].append(row)
    for (source, patient), rows in sorted(groups.items()):
        residues = {r: [row for row in rows if row["residue"] == r] for r in (1, 3)}
        if not all(residues.values()):
            raise ValueError(f"Missing target residue: {source} {patient}")
        values = {key: float(np.mean([np.mean([row[key] for row in residues[r]])
                                      for r in (1, 3)])) for key in keys}
        patients.append({"source": source, "patient": patient,
                         "stratum": rows[0]["stratum"], "targets": len(rows), **values})
    summary = {}
    for source, seed in (("msvalid", 20261007), ("remind", 20261008)):
        group = [row for row in patients if row["source"] == source]
        n = len(group)
        if n != (84 if source == "msvalid" else 62):
            raise ValueError(f"Wrong complete-patient count: {source}")
        rng = np.random.default_rng(seed)
        draws = np.zeros((5000, 2), dtype=np.float64)
        if source == "msvalid":
            matrix = np.array([[row["delta_o"], row["analytic_minus_neural"]] for row in group])
            indices = rng.integers(0, n, size=(5000, n))
            draws = matrix[indices].mean(axis=1)
        else:
            for label, count in (("2D_AX_T2", 35), ("2D_AX_T2_BLADE", 27)):
                matrix = np.array([[row["delta_o"], row["analytic_minus_neural"]]
                                   for row in group if row["stratum"] == label])
                if len(matrix) != count:
                    raise ValueError(f"Wrong ReMIND stratum: {label}")
                indices = rng.integers(0, count, size=(5000, count))
                draws += matrix[indices].mean(axis=1) * count / n
        fields = {key: float(np.mean([row[key] for row in group])) for key in keys}
        summary[source] = {
            "patients": n, "targets": sum(row["targets"] for row in group),
            **fields,
            "delta_o_ci95": np.percentile(draws[:, 0], [2.5, 97.5]).tolist(),
            "analytic_minus_neural_ci95": np.percentile(draws[:, 1], [2.5, 97.5]).tolist(),
            "positive_delta_patients": sum(row["delta_o"] > 0 for row in group),
            "positive_analytic_minus_neural_patients": sum(row["analytic_minus_neural"] > 0 for row in group),
        }
    return patients, summary


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    original = {}
    for source, (path, digest) in prior.ORIGINAL.items():
        rows = prior.csv_rows(path, digest)
        if len(rows) != (479 if source == "msvalid" else 248):
            raise ValueError(f"Original target count changed: {source}")
        original[source] = defaultdict(list)
        for row in rows:
            original[source][row["patient"]].append(row)
    if prior.sha256(prior.MS_MANIFEST) != prior.MS_MANIFEST_HASH:
        raise ValueError("MSValid source manifest changed")
    manifest = {row["patient"]: row for row in json.loads(prior.MS_MANIFEST.read_text(encoding="utf-8"))["records"]}
    geometry = {row["patient"]: row for row in json.loads(prior.MS_GEOMETRY.read_text(encoding="utf-8"))["patients"]}
    if set(original["msvalid"]) != set(manifest) or set(manifest) != set(geometry) or len(geometry) != 84:
        raise ValueError("MSValid patient source set changed")
    targets = []
    for index, patient in enumerate(sorted(geometry), 1):
        record = manifest[patient]
        path = ROOT / record["path"]
        if prior.sha256(path) != record["sha256"]:
            raise ValueError(f"MSValid image hash changed: {patient}")
        volume = nib.load(str(path)).get_fdata(dtype=np.float32)
        if tuple(volume.shape) != tuple(geometry[patient]["shape"]):
            raise ValueError(f"MSValid shape changed: {patient}")
        rows = original["msvalid"][patient]
        expected = {z for r in (1, 3) for z in geometry[patient]["eligible_targets"][f"residue_{r}"]}
        if {int(row["z"]) for row in rows} != expected:
            raise ValueError(f"MSValid target IDs changed: {patient}")
        needed = {q for z in expected for q in (z, 4 * (z // 4) - 4, 4 * (z // 4),
                                                4 * (z // 4) + 4, 4 * (z // 4) + 8,
                                                2 + 4 * ((z - 2) // 4), 6 + 4 * ((z - 2) // 4))}
        if min(needed) < 0 or max(needed) >= volume.shape[2]:
            raise ValueError(f"MSValid analytic bounds failed: {patient}")
        planes = {z: volume[:, :, z] for z in needed}
        targets.extend(score("msvalid", row, planes) for row in rows)
        if index % 10 == 0 or index == 84:
            print(f"MSValid {index}/84", flush=True)
    if prior.sha256(prior.REMIND_QUALIFIED) != prior.REMIND_QUALIFIED_HASH:
        raise ValueError("ReMIND qualification changed")
    records = json.loads(prior.REMIND_QUALIFIED.read_text(encoding="utf-8"))["records"]
    eligible = [record for record in records if record["eligible"]]
    if len(records) != 63 or len(eligible) != 62 or set(original["remind"]) != {row["patient"] for row in eligible}:
        raise ValueError("ReMIND patient set changed")
    for index, record in enumerate(eligible, 1):
        patient = record["patient"]
        path = ROOT / record["path"]
        if prior.sha256(path) != record["zip_sha256"]:
            raise ValueError(f"ReMIND source ZIP changed: {patient}")
        rows = original["remind"][patient]
        expected = {z for r in ("1", "3") for z in record["targets"][r]}
        if {int(row["z"]) for row in rows} != expected:
            raise ValueError(f"ReMIND target IDs changed: {patient}")
        needed = {q for z in expected for q in (z, 4 * (z // 4) - 4, 4 * (z // 4),
                                                4 * (z // 4) + 4, 4 * (z // 4) + 8,
                                                2 + 4 * ((z - 2) // 4), 6 + 4 * ((z - 2) // 4))}
        if min(needed) < 0 or max(needed) >= record["depth"]:
            raise ValueError(f"ReMIND analytic bounds failed: {patient}")
        with zipfile.ZipFile(path) as archive:
            planes = {z: prior.read_dicom_plane(archive, record["ordered_files"][z]) for z in needed}
        targets.extend(score("remind", row, planes) for row in rows)
        if index % 10 == 0 or index == 62:
            print(f"ReMIND {index}/62", flush=True)
    if len(targets) != 727:
        raise ValueError("Incomplete target set")
    patients, source_summary = aggregate(targets)
    output = {"classification": "post-result analytic falsification",
              "protocol_sha256": prior.sha256(PLAN), "script_sha256": prior.sha256(Path(__file__)),
              "msvalid_original_sha256": prior.ORIGINAL["msvalid"][1],
              "remind_original_sha256": prior.ORIGINAL["remind"][1],
              "msvalid_manifest_sha256": prior.MS_MANIFEST_HASH,
              "remind_qualification_sha256": prior.REMIND_QUALIFIED_HASH,
              "sources": source_summary, "gpu_used": False, "model_inference_run": False}
    OUT.mkdir(parents=True)
    write_csv(OUT / "per_target.csv", targets)
    write_csv(OUT / "per_patient.csv", patients)
    (OUT / "summary.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2), flush=True)


if __name__ == "__main__":
    main()
