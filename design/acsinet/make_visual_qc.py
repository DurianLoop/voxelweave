from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "acsinet" / "runs" / "full_test115"
OUT_DIR = ROOT / "docx" / "experiment_notes" / "acsinet_3d_consistency" / "visual_qc"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _load(path: Path) -> np.ndarray:
    arr = np.asarray(nib.load(str(path)).get_fdata(dtype=np.float32), dtype=np.float32)
    return np.nan_to_num(arr)


def _scale_from_gt(gt: np.ndarray) -> tuple[float, float]:
    mask = gt > np.percentile(gt, 5)
    values = gt[mask] if np.any(mask) else gt.reshape(-1)
    lo, hi = np.percentile(values, [1, 99.5])
    if hi <= lo:
        lo, hi = float(np.min(gt)), float(np.max(gt))
    if hi <= lo:
        hi = lo + 1.0
    return float(lo), float(hi)


def _display_slice(volume: np.ndarray, plane: str, index: int) -> np.ndarray:
    if plane == "sagittal":
        image = volume[index, :, :]
    elif plane == "coronal":
        image = volume[:, index, :]
    else:
        raise ValueError(f"Unknown plane: {plane}")
    return np.rot90(image)


def _center_indices(gt: np.ndarray) -> tuple[int, int]:
    threshold = np.percentile(gt, 25)
    coords = np.argwhere(gt > threshold)
    if coords.size == 0:
        return gt.shape[0] // 2, gt.shape[1] // 2
    return int(np.median(coords[:, 0])), int(np.median(coords[:, 1]))


def _select_cases() -> list[tuple[str, str, float]]:
    rows = _read_csv(RUN_DIR / "metrics" / "per_case_3d_consistency.csv")
    by_case: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        by_case.setdefault(row["case"], {})[row["method"]] = row

    scored = []
    for case, methods in by_case.items():
        acsi = methods.get("acsinet")
        linear = methods.get("linear")
        if not acsi or not linear:
            continue
        gain = float(linear["zge"]) - float(acsi["zge"])
        scored.append((case, gain))
    scored.sort(key=lambda item: item[1])
    if not scored:
        return []

    picks = [
        ("worst_gain", scored[0]),
        ("median_gain", scored[len(scored) // 2]),
        ("best_gain", scored[-1]),
    ]
    return [(label, case, gain) for label, (case, gain) in picks]


def _paths_for_case(case: str) -> dict[str, Path]:
    return {
        "GT": RUN_DIR / "eval_inputs" / "gt" / case,
        "Linear": RUN_DIR / "baseline_outputs" / "linear" / f"linear_{case}",
        "I3Net": ROOT / "ixi_i3net" / "runs" / "full_test115_stable" / "model_outputs" / f"diff_{case}",
        "ACSI-Net": RUN_DIR / "model_outputs" / f"diff_{case}",
    }


def _plot_case(label: str, case: str, gain: float) -> list[Path]:
    paths = _paths_for_case(case)
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"{case}: missing {', '.join(missing)}")

    volumes = {name: _load(path) for name, path in paths.items()}
    gt = volumes["GT"]
    lo, hi = _scale_from_gt(gt)
    sx, cy = _center_indices(gt)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for plane, index in [("sagittal", sx), ("coronal", cy)]:
        fig, axes = plt.subplots(2, 4, figsize=(12, 6), constrained_layout=True)
        for col, name in enumerate(["GT", "Linear", "I3Net", "ACSI-Net"]):
            axes[0, col].imshow(_display_slice(volumes[name], plane, index), cmap="gray", vmin=lo, vmax=hi)
            axes[0, col].set_title(name)
            axes[0, col].axis("off")

            if name == "GT":
                axes[1, col].imshow(np.zeros_like(_display_slice(gt, plane, index)), cmap="magma", vmin=0, vmax=max(hi - lo, 1.0))
                axes[1, col].set_title("reference")
            else:
                err = np.abs(volumes[name] - gt)
                axes[1, col].imshow(_display_slice(err, plane, index), cmap="magma", vmin=0, vmax=np.percentile(err, 99))
                axes[1, col].set_title("|error|")
            axes[1, col].axis("off")

        fig.suptitle(f"{label}: {case} | linear-to-ACSI ZGE gain {gain:.5f} | {plane} index {index}")
        out_path = OUT_DIR / f"{label}_{case.replace('.nii.gz', '')}_{plane}.png"
        fig.savefig(out_path, dpi=180)
        plt.close(fig)
        written.append(out_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", help="Specific case filename, for example IXI012-HH-1211-T2.nii.gz")
    args = parser.parse_args()

    if args.case:
        cases = [("manual", case, 0.0) for case in args.case]
    else:
        cases = _select_cases()

    written: list[Path] = []
    for label, case, gain in cases:
        written.extend(_plot_case(label, case, gain))

    manifest = OUT_DIR / "visual_qc_manifest.txt"
    manifest.write_text("\n".join(str(path) for path in written) + "\n", encoding="utf-8")
    print(f"Wrote {len(written)} visual QC panels to {OUT_DIR}")


if __name__ == "__main__":
    main()
