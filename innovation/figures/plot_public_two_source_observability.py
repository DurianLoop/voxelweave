"""Publication-draft paired observability figure from public-source patient tables."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "figures"
SOURCES = [
    ("MSValid RRMS", "same-patient IXI-weight follow-up", "#147d74",
     BASE / "experiments/msvalid_ixi_weights_secondary/per_patient.csv",
     BASE / "experiments/msvalid_ixi_weights_secondary/summary.json"),
    ("ReMIND preoperative T2", "later frozen source test", "#c04b37",
     BASE / "experiments/remind_native_t2_ixi_pair/per_patient.csv",
     BASE / "experiments/remind_native_t2_ixi_pair/summary.json"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.9), sharey=True)
    hashes = {}
    for ax, (title, status, color, table, summary_path) in zip(axes, SOURCES):
        with table.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert len(rows) == summary["patients_scored"]
        shared = np.array([float(r["shared_observable"]) for r in rows]) * 100
        disjoint = np.array([float(r["disjoint_observable"]) for r in rows]) * 100
        assert np.isclose(np.mean(disjoint - shared), summary["mean_delta_o"] * 100)
        rng = np.random.default_rng(20261001)
        offset = rng.uniform(-.075, .075, len(rows))
        for x, a, b in zip(offset, shared, disjoint):
            ax.plot([x, 1 + x], [a, b], color="#a8b2b4", linewidth=.65,
                    alpha=.42, zorder=1)
        ax.scatter(offset, shared, s=10, color="#49585a", alpha=.75,
                   linewidths=0, zorder=2)
        ax.scatter(1 + offset, disjoint, s=10, color=color, alpha=.8,
                   linewidths=0, zorder=2)
        ax.scatter([0, 1], [shared.mean(), disjoint.mean()], marker="D", s=48,
                   facecolor="white", edgecolor="#162427", linewidth=1.2, zorder=4)
        lo, hi = np.array(summary["ci95_delta_o"]) * 100
        ax.text(.5, .97, f"Delta O  +{summary['mean_delta_o']*100:.2f} pp\n"
                f"95% CI  +{lo:.2f} to +{hi:.2f} pp",
                transform=ax.transAxes, va="top", ha="center", fontsize=9,
                color="#182528", linespacing=1.35)
        ax.set_title(f"{title}\n{len(rows)} patients  |  {summary['targets_scored']} targets",
                     loc="left", fontsize=10.5, fontweight="bold", pad=12)
        ax.set_xticks([0, 1], ["Shared", "Disjoint"])
        ax.set_xlim(-.3, 1.3)
        ax.set_ylim(-1, 39)
        ax.set_yticks([0, 10, 20, 30])
        ax.grid(axis="y", color="#dbe2e3", linewidth=.6)
        ax.set_axisbelow(True)
        ax.text(.5, -.2, status, transform=ax.transAxes, ha="center", va="top",
                fontsize=8.5, color="#536165")
        hashes[title] = {"per_patient_sha256": sha(table),
                         "summary_sha256": sha(summary_path),
                         "patients": len(rows), "targets": summary["targets_scored"]}
    axes[0].set_ylabel("Patient-level observable error (%)")
    fig.subplots_adjust(left=.095, right=.985, top=.81, bottom=.235, wspace=.22)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "public_two_source_observability.pdf", facecolor="white")
    fig.savefig(OUT / "public_two_source_observability.png", dpi=220, facecolor="white")
    plt.close(fig)
    (OUT / "public_two_source_observability_sources.json").write_text(
        json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(hashes, indent=2))


if __name__ == "__main__":
    main()
