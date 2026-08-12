from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CV_ROOT = ROOT / "dataset" / "NingXiaData" / "processed_saint_cv"
DEFAULT_ARSSR_RUN_ROOT = ROOT / "ningxia_t2_arssr_cv" / "runs"


def _fold_roots(cv_root: Path, fold_limit: int | None) -> list[Path]:
    folds = sorted(path for path in cv_root.glob("fold_*") if path.is_dir())
    if fold_limit is not None:
        folds = folds[:fold_limit]
    if not folds:
        raise RuntimeError(f"No fold roots found under {cv_root}. Run processing.ningxia_case_cv first.")
    return folds


def _run_one(fold_root: Path, run_root: Path, profile: str, force: bool, paper_table: bool) -> None:
    fold_name = fold_root.name
    fold_run_root = run_root / fold_name
    profile_run_dir = fold_run_root / profile
    summary_path = profile_run_dir / "metrics" / "summary_metrics.csv"
    if summary_path.exists() and not force:
        print(f"[skip] ArSSR {fold_name}: {summary_path} exists")
        return

    env = os.environ.copy()
    env["FASTMRI_BRAIN_ARSSR_DATA_ROOT"] = str(fold_root)
    env["FASTMRI_BRAIN_ARSSR_RUN_ROOT"] = str(fold_run_root)

    cmd = [sys.executable, "-u", "-B", "-m", "fastmri_brain_arssr.run_all", "--profile", profile]
    print(f"[run] ArSSR {fold_name}")
    print(f"      DATA_ROOT={fold_root}")
    print(f"      RUN_ROOT={fold_run_root}")
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)

    if paper_table:
        table_cmd = [sys.executable, "-u", "-B", "-m", "fastmri_brain_arssr.paper_table", "--profile", profile]
        subprocess.run(table_cmd, cwd=ROOT, env=env, check=True)

    if not summary_path.exists():
        raise RuntimeError(f"Expected fold output missing: {summary_path}")
    print(f"[done] ArSSR {fold_name}: {profile_run_dir}")


def run_cv(cv_root: Path, profile: str, fold_limit: int | None, run_root: Path, force: bool, paper_table: bool) -> None:
    for fold_root in _fold_roots(cv_root, fold_limit):
        _run_one(fold_root, run_root, profile, force, paper_table)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NingXia case-level CV folds for ArSSR-style reproduction.")
    parser.add_argument("--cv-root", type=Path, default=DEFAULT_CV_ROOT)
    parser.add_argument("--profile", choices=["smoke", "mini", "full"], default="full")
    parser.add_argument("--fold-limit", type=int, default=None)
    parser.add_argument("--arssr-run-root", type=Path, default=DEFAULT_ARSSR_RUN_ROOT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-paper-table", action="store_true")
    args = parser.parse_args()
    run_cv(
        cv_root=args.cv_root,
        profile=args.profile,
        fold_limit=args.fold_limit,
        run_root=args.arssr_run_root,
        force=args.force,
        paper_table=not args.no_paper_table,
    )


if __name__ == "__main__":
    main()
