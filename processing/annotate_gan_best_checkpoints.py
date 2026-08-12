from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GLOBS = [
    ROOT / "fastmri_brain_gan_2p5d" / "runs" / "full",
    ROOT / "fastmri_brain_gan_2p5d" / "runs" / "full_stable",
    ROOT / "ixi_gan_2p5d" / "runs" / "full_test115_b64",
    ROOT / "ixi_gan_2p5d" / "runs" / "full_test115_stable",
    ROOT / "ningxia_t2_gan_2p5d_cv" / "runs" / "fold_*" / "full",
    ROOT / "ningxia_t2_gan_2p5d_cv" / "runs" / "fold_*" / "full_stable",
]


def _float_or_nan(value: str | None) -> float:
    if value is None or value == "":
        return float("nan")
    try:
        return float(value)
    except ValueError:
        return float("nan")


def _expand_patterns(patterns: list[Path]) -> list[Path]:
    out: list[Path] = []
    for pattern in patterns:
        text = str(pattern)
        if "*" in text or "?" in text:
            out.extend(sorted(Path(path) for path in pattern.parent.parent.glob(pattern.parent.name + "/" + pattern.name)))
        else:
            out.append(pattern)
    return sorted(dict.fromkeys(out))


def _annotate_run(run_dir: Path) -> bool:
    history_csv = run_dir / "training_history.csv"
    if not history_csv.exists():
        print(f"[skip] missing history: {history_csv}")
        return False

    rows: list[dict[str, str]] = []
    with history_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    finite_rows = [row for row in rows if math.isfinite(_float_or_nan(row.get("val_loss")))]
    if not finite_rows:
        print(f"[skip] no finite val_loss: {history_csv}")
        return False

    best_row = min(finite_rows, key=lambda row: _float_or_nan(row.get("val_loss")))
    final_row = finite_rows[-1]
    best_val = _float_or_nan(best_row.get("val_loss"))
    final_val = _float_or_nan(final_row.get("val_loss"))
    json_path = run_dir / "training_history.json"
    meta = {}
    if json_path.exists():
        try:
            meta = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}
    meta.update(
        {
            "best_val_loss": best_val,
            "best_epoch": int(float(best_row.get("epoch", "nan"))),
            "final_val_loss": final_val,
            "last_vs_best_pct": None if best_val == 0 else (final_val - best_val) / best_val * 100.0,
            "epochs_completed": len(rows),
            "checkpoint_selection": "best validation loss",
            "selected_checkpoint": str(run_dir / "checkpoints" / "gan_epoch_best.pth"),
            "final_checkpoint": str(run_dir / "checkpoints" / "gan_epoch_final.pth"),
        }
    )
    json_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[ok] {run_dir} best_epoch={meta['best_epoch']} last_vs_best_pct={meta['last_vs_best_pct']:.2f}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotate GAN runs with best-validation checkpoint metadata.")
    parser.add_argument("--run-dir", action="append", type=Path, default=None, help="Specific run directory to annotate.")
    args = parser.parse_args()
    run_dirs = args.run_dir if args.run_dir else _expand_patterns(DEFAULT_GLOBS)
    done = sum(1 for run_dir in run_dirs if _annotate_run(run_dir))
    print(f"Annotated {done} GAN run(s).")


if __name__ == "__main__":
    main()
