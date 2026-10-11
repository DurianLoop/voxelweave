"""Plot the saved one-patient image/lesion trade-off, retaining oracle status."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent


def main():
    path = ROOT / "experiments/vs_seg_001_local_action_oracle/attempt_01.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    if not result["complete"] or result["independent_confirmation"]:
        raise ValueError("Expected completed development-only result")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.0), sharex=True, sharey=True)
    for ax, action in zip(axes, result["analysis"]["actions"]):
        strategies = action["strategies"]
        def point(key):
            metrics = strategies[key]["image_metrics"]
            return (1000*metrics["support"]["target_equal_nmse"], 1000*metrics["lesion"]["target_equal_nmse"])
        fixed = [point(f"fixed_{a:g}") for a in (0., .25, .5, .75, 1.)]
        ax.plot([v[0] for v in fixed], [v[1] for v in fixed], "o-", color="#295a86", lw=1.4, ms=4, label="Fixed mixtures")
        ax.annotate("PCHIP", fixed[0], xytext=(-8, 9), textcoords="offset points", ha="right", color="#295a86")
        ax.annotate("HAT", fixed[-1], xytext=(-3, 8), textcoords="offset points", ha="right", color="#295a86")
        for size in (16, 32, 64):
            xy = point(f"tile_{size}_oracle")
            ax.scatter(*xy, marker="*" if size == 32 else "^", s=110 if size == 32 else 38, color="#ad4931",
                       zorder=3, label="Local oracle (target used)" if size == 32 else None)
            offset, align = ((-12, 5), "right") if size == 64 else ((10, -12), "left")
            ax.annotate(f"{size} px", xy, xytext=offset, textcoords="offset points",
                        ha=align, fontsize=9, color="#9a3e28")
        ax.set_title("Raw PCHIP to HAT" if action["base"] == "raw_pchip" else "Pipeline PCHIP to HAT", fontsize=12)
        ax.set_xlabel("Support NMSE x 1000")
        ax.set_xlim(1.57, 2.36)
        ax.set_ylim(6.45, 8.17)
        ax.grid(alpha=.16)
    axes[0].set_ylabel("Lesion target-equal NMSE x 1000")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5, .925), frameon=False, ncol=2)
    fig.suptitle("VS-SEG-001: limited local action-space headroom", fontsize=14, y=.98)
    fig.text(.5, .075, "One reused development patient; oracle uses hidden targets. Lower is better on both axes.", ha="center", fontsize=9)
    fig.text(.5, .035, "32 px is the prewritten main size. No new task inference or independent confirmation.", ha="center", fontsize=9)
    fig.subplots_adjust(left=.09, right=.98, bottom=.23, top=.79, wspace=.12)
    files = []
    for suffix in ("png", "svg"):
        target = OUT / ("VS_SEG_001_LOCAL_ACTION_ORACLE_2026-10-02." + suffix)
        fig.savefig(target, dpi=170, facecolor="white")
        files.append({"path": target.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    plt.close(fig)
    (OUT / "VS_SEG_001_LOCAL_ACTION_ORACLE_FIGURE_2026-10-02.json").write_text(json.dumps({
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "files": files,
        "scientific_claim_confirmed": False}, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"files": files}))


if __name__ == "__main__":
    main()
