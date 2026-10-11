"""Anonymous patient-level comparison of SwinIR and linear partner contrasts."""
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
OUT = ROOT / "figures"
SOURCES = [
    ("MSValid RRMS", 84, "#147d74", "msvalid_ixi_weights_secondary", "msvalid"),
    ("ReMIND preoperative T2", 62, "#c04b37", "remind_native_t2_ixi_pair", "remind"),
]


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    result = {row["patient"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"duplicate patient in {path}")
    return result


def main() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.1), sharex=True, sharey=True)
    manifest = {}
    for ax, (title, expected, color, main_folder, control_folder) in zip(axes, SOURCES):
        main_path = ROOT / "experiments" / main_folder / "per_patient.csv"
        control_path = (ROOT / "experiments/public_linear_partner_control" /
                        control_folder / "per_patient.csv")
        main, control = read(main_path), read(control_path)
        if set(main) != set(control) or len(main) != expected:
            raise ValueError(f"patient set mismatch: {title}")
        ids = sorted(main)
        x = np.array([float(control[pid]["delta_o"]) * 100 for pid in ids])
        y = np.array([float(main[pid]["delta_o"]) * 100 for pid in ids])
        if not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError(f"nonfinite patient contrast: {title}")
        ax.plot([0, 40], [0, 40], color="#a7b3b5", linewidth=1, linestyle="--", zorder=1)
        ax.scatter(x, y, s=22, color=color, alpha=.72, edgecolors="none", zorder=2)
        ax.scatter([x.mean()], [y.mean()], marker="D", s=72, facecolor="white",
                   edgecolor="#18292c", linewidth=1.35, zorder=3)
        ax.set_title(f"{title}\n{expected} paired patients", loc="left",
                     fontsize=10.5, fontweight="bold", pad=10)
        ax.set_xlim(15, 36)
        ax.set_ylim(15, 36)
        ax.set_xticks([15, 20, 25, 30, 35])
        ax.set_yticks([15, 20, 25, 30, 35])
        ax.set_aspect("equal", adjustable="box")
        ax.grid(color="#dce3e4", linewidth=.6)
        ax.set_axisbelow(True)
        ax.text(.04, .96, f"Mean: linear +{x.mean():.2f} pp\n"
                f"SwinIR +{y.mean():.2f} pp", transform=ax.transAxes,
                va="top", ha="left", fontsize=8.4, color="#253235",
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": .88, "pad": 2})
        manifest[title] = {"main_patient_sha256": sha(main_path),
                           "linear_patient_sha256": sha(control_path),
                           "patients": expected, "linear_mean_pp": float(x.mean()),
                           "swinir_mean_pp": float(y.mean())}
    axes[0].set_ylabel("SwinIR partner Delta O (percentage points)")
    fig.supxlabel("Native-linear partner Delta O (percentage points)", y=.04)
    fig.subplots_adjust(left=.105, right=.985, top=.85, bottom=.18, wspace=.13)
    fig.savefig(OUT / "public_linear_control_patient_comparison.pdf", facecolor="white")
    fig.savefig(OUT / "public_linear_control_patient_comparison.png",
                dpi=220, facecolor="white")
    plt.close(fig)
    (OUT / "public_linear_control_patient_comparison_sources.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
