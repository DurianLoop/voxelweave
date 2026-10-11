"""Post-result algebraic description of the frozen UPENN paired errors."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


OUT = Path(__file__).resolve().parent / "upenn_gbm_processed_t2_context"
SOURCE = OUT / "per_target.csv"
MAIN = OUT / "summary.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observable(cosine: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return .5 - cosine * np.sqrt(a * b) / (a + b)


def main() -> None:
    destination = OUT / "posthoc_decomposition.json"
    if destination.exists():
        raise FileExistsError(destination)
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    main = json.loads(MAIN.read_text(encoding="utf-8"))
    if len(rows) != 1496 or main["patients_scored"] != 374:
        raise ValueError("Frozen cohort mismatch")
    cols = lambda name: np.asarray([float(row[name]) for row in rows], dtype=float)
    a, bs, bd = (cols(name) for name in ("shared_a_mse", "shared_b_mse", "disjoint_b_mse"))
    os, od, delta = (cols(name) for name in ("shared_observable", "disjoint_observable", "delta_o"))
    if not np.isfinite(np.column_stack([a, bs, bd, os, od, delta])).all() or min(a.min(), bs.min(), bd.min()) <= 0:
        raise ValueError("Invalid metric input")
    if not np.allclose(a, cols("disjoint_a_mse"), rtol=0, atol=1e-8):
        raise ValueError("Fixed HAT reference changed")
    rs = (.5 - os) * (a + bs) / np.sqrt(a * bs)
    rd = (.5 - od) * (a + bd) / np.sqrt(a * bd)
    if max(np.max(np.abs(rs)), np.max(np.abs(rd))) > 1 + 1e-8:
        raise ValueError("Invalid error cosine")
    fss, fsd = observable(rs, a, bs), observable(rs, a, bd)
    fds, fdd = observable(rd, a, bs), observable(rd, a, bd)
    quality = .5 * ((fsd - fss) + (fdd - fds))
    alignment = .5 * ((fds - fss) + (fdd - fsd))
    closure = float(np.max(np.abs(quality + alignment - delta)))
    if closure > 1e-10:
        raise ValueError("Decomposition failed")
    fixed_shared_denominator = ((cols("disjoint_disagreement_mse") -
                                 cols("shared_disagreement_mse")) /
                                (4 * cols("shared_paired_mse")))
    measures = {"delta_o": delta, "quality_imbalance": quality,
                "error_alignment": alignment, "shared_error_cosine": rs,
                "disjoint_error_cosine": rd,
                "fixed_shared_denominator_delta_o": fixed_shared_denominator}
    per_patient = defaultdict(lambda: defaultdict(list))
    for index, row in enumerate(rows):
        for name, array in measures.items():
            per_patient[row["patient"]][name].append(float(array[index]))
    if len(per_patient) != 374 or any(len(values["delta_o"]) != 4 for values in per_patient.values()):
        raise ValueError("Incomplete patient")
    points = {name: float(np.mean([np.mean(values[name]) for values in per_patient.values()]))
              for name in measures}
    if abs(points["delta_o"] - main["mean_delta_o"]) > 1e-10:
        raise ValueError("Primary result mismatch")
    report = {"status": "post-result algebraic description; not independent or causal evidence",
              "source_sha256": sha(SOURCE), "main_summary_sha256": sha(MAIN),
              "script_sha256": sha(Path(__file__)), "patients": len(per_patient),
              "targets": len(rows), "points": points,
              "positive_targets": int((delta > 0).sum()),
              "negative_targets": int((delta < 0).sum()),
              "max_abs_component_identity_error": closure}
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
