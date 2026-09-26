from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "dataset" / "NingXiaData" / "processed_saint"
DEFAULT_OUT = ROOT / "dataset" / "NingXiaData" / "processed_saint_cv"


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = []
        for row in csv.DictReader(handle):
            rows.append({str(key).lstrip("\ufeff").strip('"'): str(value).strip('"') for key, value in row.items()})
        return rows


def _write_lines(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(values) + ("\n" if values else ""), encoding="utf-8")


def _case_ids(rows: list[dict[str, str]]) -> list[str]:
    ids = sorted({str(row["case_id"]) for row in rows})
    if len(ids) < 3:
        raise RuntimeError(f"Need at least 3 case ids for case-level CV, found {len(ids)}.")
    return ids


def create_case_cv(source: Path, out: Path, folds: int | None, seed_name: str) -> dict:
    metadata_src = source / "metadata" / "fastmri_brain_nifti_cases.csv"
    if not metadata_src.exists():
        raise FileNotFoundError(f"Missing source metadata: {metadata_src}")

    rows = _read_rows(metadata_src)
    ids = _case_ids(rows)
    max_folds = len(ids)
    n_folds = max_folds if folds is None else min(folds, max_folds)

    out.mkdir(parents=True, exist_ok=True)
    summary_rows = []

    for fold_idx in range(n_folds):
        test_id = ids[fold_idx]
        val_id = ids[(fold_idx + 1) % len(ids)]
        train_ids = [case_id for case_id in ids if case_id not in {test_id, val_id}]

        fold_root = out / f"fold_{fold_idx:02d}"
        metadata_dst = fold_root / "metadata"
        split_root = fold_root / "splits" / seed_name
        metadata_dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(metadata_src, metadata_dst / "fastmri_brain_nifti_cases.csv")

        _write_lines(split_root / "train_cases.txt", train_ids)
        _write_lines(split_root / "val_cases.txt", [val_id])
        _write_lines(split_root / "test_cases.txt", [test_id])

        row = {
            "fold": f"fold_{fold_idx:02d}",
            "train_cases": ";".join(train_ids),
            "val_case": val_id,
            "test_case": test_id,
            "train_n": len(train_ids),
            "val_n": 1,
            "test_n": 1,
            "data_root": str(fold_root),
        }
        summary_rows.append(row)

    summary_path = out / "case_cv_summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["fold", "train_cases", "val_case", "test_case", "train_n", "val_n", "test_n", "data_root"],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    payload = {
        "source": str(source),
        "out": str(out),
        "seed_name": seed_name,
        "case_ids": ids,
        "folds": summary_rows,
        "note": "Case-level leave-one-case-out style CV: each fold uses one subject for test, next subject for val, remaining subjects for train.",
    }
    (out / "case_cv_summary.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Create case-level CV roots for NingXia-T2 SAINT/ResUNet pipelines.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--folds", type=int, default=None, help="Default: one fold per case.")
    parser.add_argument("--seed-name", default="nifti_seed3407")
    args = parser.parse_args()

    payload = create_case_cv(args.source, args.out, args.folds, args.seed_name)
    print(
        f"NingXia case-level CV written: folds={len(payload['folds'])}, "
        f"cases={len(payload['case_ids'])}, out={payload['out']}"
    )
    for row in payload["folds"]:
        print(
            f"{row['fold']}: train={row['train_n']} val={row['val_case']} "
            f"test={row['test_case']}"
        )


if __name__ == "__main__":
    main()
