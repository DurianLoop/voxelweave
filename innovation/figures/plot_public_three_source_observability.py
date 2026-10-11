"""Render anonymized patient-level observability for three public T2 sources."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
SOURCES = (
    ("MSValid", "same-patient follow-up", "#087f72",
     "msvalid_ixi_weights_secondary", 84, 479),
    ("ReMIND", "later frozen source", "#b84b35",
     "remind_native_t2_ixi_pair", 62, 248),
    ("UPENN-GBM", "later informed, processed", "#4870a5",
     "upenn_gbm_processed_t2_context", 374, 1496),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.spines.top": False, "axes.spines.right": False,
    })
    figure, axes = plt.subplots(1, 3, figsize=(11.4, 4.1), sharey=True)
    provenance = {}
    for axis, (name, history, color, folder, expected_n, expected_t) in zip(axes, SOURCES):
        csv_path = ROOT / "experiments" / folder / "per_patient.csv"
        summary_path = ROOT / "experiments" / folder / "summary.json"
        with csv_path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        if (len(rows), summary["patients_scored"], summary["targets_scored"]) != (
                expected_n, expected_n, expected_t):
            raise ValueError(f"{name}: frozen count mismatch")
        shared = np.array([float(row["shared_observable"]) for row in rows]) * 100
        disjoint = np.array([float(row["disjoint_observable"]) for row in rows]) * 100
        delta = disjoint - shared
        if not np.isclose(delta.mean(), summary["mean_delta_o"] * 100, atol=1e-8):
            raise ValueError(f"{name}: frozen mean mismatch")
        if np.any(delta <= 0):
            raise ValueError(f"{name}: nonpositive patient difference needs review")
        jitter = np.random.default_rng(20261001 + expected_n).uniform(-.09, .09, expected_n)
        alpha = .28 if expected_n > 100 else .48
        for offset, left, right in zip(jitter, shared, disjoint):
            axis.plot([offset, 1 + offset], [left, right], color="#8b989a",
                      linewidth=.55, alpha=alpha, zorder=1)
        axis.scatter(jitter, shared, s=8, color="#46575a", alpha=.5,
                     linewidths=0, zorder=2)
        axis.scatter(1 + jitter, disjoint, s=8, color=color, alpha=.55,
                     linewidths=0, zorder=2)
        axis.scatter([0, 1], [shared.mean(), disjoint.mean()], marker="D", s=55,
                     facecolor="white", edgecolor="#17282b", linewidth=1.2, zorder=3)
        lower, upper = np.asarray(summary["ci95_delta_o"]) * 100
        axis.text(.5, .96,
                  f"Delta O +{delta.mean():.2f} pp\n95% CI +{lower:.2f} to +{upper:.2f}",
                  transform=axis.transAxes, ha="center", va="top", fontsize=8.8,
                  linespacing=1.3, color="#243537")
        axis.set_title(f"{name}\n{expected_n} patients | {expected_t} targets",
                       loc="left", fontsize=10.2, fontweight="bold", pad=11)
        axis.set_xticks([0, 1], ["Shared", "Disjoint"])
        axis.set_xlim(-.28, 1.28)
        axis.set_ylim(-1, 40)
        axis.set_yticks([0, 10, 20, 30, 40])
        axis.grid(axis="y", color="#dce3e4", linewidth=.6)
        axis.set_axisbelow(True)
        axis.text(.5, -.2, history, transform=axis.transAxes,
                  ha="center", va="top", fontsize=8.2, color="#536367")
        provenance[name] = {
            "per_patient_sha256": sha256(csv_path),
            "summary_sha256": sha256(summary_path),
            "patients": expected_n, "targets": expected_t,
            "mean_delta_o_points": float(delta.mean()),
        }
    axes[0].set_ylabel("Patient-level observable paired error (%)")
    figure.subplots_adjust(left=.075, right=.985, top=.805, bottom=.23, wspace=.16)
    image_path = OUT / "public_three_source_observability.png"
    figure.savefig(image_path, dpi=220, facecolor="white")
    plt.close(figure)
    provenance["figure_sha256"] = sha256(image_path)
    (OUT / "public_three_source_observability_sources.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({name: provenance[name] for name in ("MSValid", "ReMIND", "UPENN-GBM")},
                     indent=2))


if __name__ == "__main__":
    main()
