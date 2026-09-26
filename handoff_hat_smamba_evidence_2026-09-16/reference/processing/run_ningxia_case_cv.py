from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CV_ROOT = ROOT / "dataset" / "NingXiaData" / "processed_saint_cv"
DEFAULT_SAINT_RUN_ROOT = ROOT / "ningxia_t2_saint_cv" / "runs"
DEFAULT_RESUNET_RUN_ROOT = ROOT / "ningxia_t2_resunet_cv" / "runs"
DEFAULT_ARSSR_RUN_ROOT = ROOT / "ningxia_t2_arssr_cv" / "runs"
DEFAULT_CYCLEINR_RUN_ROOT = ROOT / "ningxia_t2_cycleinr_cv" / "runs"
DEFAULT_SWINIR_RUN_ROOT = ROOT / "ningxia_t2_swinir_2p5d_cv" / "runs"
DEFAULT_I3NET_RUN_ROOT = ROOT / "ningxia_t2_i3net_cv" / "runs"
DEFAULT_HAT_RUN_ROOT = ROOT / "ningxia_t2_hat_2p5d_cv" / "runs"
DEFAULT_SMAMBA_RUN_ROOT = ROOT / "ningxia_t2_smamba_unet_2p5d_cv" / "runs"
DEFAULT_GAN_RUN_ROOT = ROOT / "ningxia_t2_gan_2p5d_cv" / "runs"
DEFAULT_ACVTT_RUN_ROOT = ROOT / "ningxia_t2_acvtt_2p5d_cv" / "runs"
DEFAULT_RESSRDIFF_RUN_ROOT = ROOT / "ningxia_t2_ressrdiff_2p5d_cv" / "runs"


def _fold_roots(cv_root: Path, fold_limit: int | None, fold_names: list[str] | None = None) -> list[Path]:
    if fold_names:
        normalized = [name if name.startswith("fold_") else f"fold_{int(name):02d}" for name in fold_names]
        folds = [cv_root / name for name in normalized]
        missing = [path for path in folds if not path.is_dir()]
        if missing:
            raise RuntimeError(f"Requested fold roots not found: {missing}")
        return folds
    folds = sorted(path for path in cv_root.glob("fold_*") if path.is_dir())
    if fold_limit is not None:
        folds = folds[:fold_limit]
    if not folds:
        raise RuntimeError(f"No fold roots found under {cv_root}. Run processing.ningxia_case_cv first.")
    return folds


def _run_one(
    fold_root: Path,
    run_root: Path,
    module: str,
    profile: str,
    force: bool,
    env_prefix: str,
    source_note: str,
) -> None:
    fold_name = fold_root.name
    fold_run_root = run_root / fold_name
    profile_run_dir = fold_run_root / profile
    summary_path = profile_run_dir / "metrics" / "summary_metrics.csv"
    if summary_path.exists() and not force:
        print(f"[skip] {module} {fold_name}: {summary_path} exists")
        return

    env = os.environ.copy()
    env[f"{env_prefix}_DATA_ROOT"] = str(fold_root)
    env[f"{env_prefix}_RUN_ROOT"] = str(fold_run_root)
    env[f"{env_prefix}_DATASET_NAME"] = "NingXia-T2 case-level CV"
    env[f"{env_prefix}_SOURCE_NOTE"] = source_note

    cmd = [sys.executable, "-u", "-B", "-m", module, "--profile", profile]
    print(f"[run] {module} {fold_name}")
    print(f"      DATA_ROOT={fold_root}")
    print(f"      RUN_ROOT={fold_run_root}")
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)

    if not summary_path.exists():
        raise RuntimeError(f"Expected fold output missing: {summary_path}")
    print(f"[done] {module} {fold_name}: {profile_run_dir}")


def run_cv(
    cv_root: Path,
    profile: str,
    models: list[str],
    fold_limit: int | None,
    saint_run_root: Path,
    resunet_run_root: Path,
    arssr_run_root: Path,
    cycleinr_run_root: Path,
    swinir_run_root: Path,
    i3net_run_root: Path,
    hat_run_root: Path,
    smamba_run_root: Path,
    gan_run_root: Path,
    acvtt_run_root: Path,
    ressrdiff_run_root: Path,
    force: bool,
    fold_names: list[str] | None = None,
) -> None:
    folds = _fold_roots(cv_root, fold_limit, fold_names)
    scale = profile.removeprefix("full_") if profile.startswith("full_x") else "x4"
    model_to_module = {
        "saint": ("fastmri_brain_saint.run_all", saint_run_root, "FASTMRI_BRAIN_SAINT", f"SAINT local NingXia-T2 {scale} case-level CV reproduction"),
        "resunet": ("fastmri_brain_saint.run_resunet", resunet_run_root, "FASTMRI_BRAIN_SAINT", f"ResUNet residual local NingXia-T2 {scale} case-level CV reproduction"),
        "arssr": ("fastmri_brain_arssr.run_all", arssr_run_root, "FASTMRI_BRAIN_ARSSR", f"ArSSR local NingXia-T2 {scale} case-level CV reproduction"),
        "cycleinr": ("fastmri_brain_cycleinr.run_all", cycleinr_run_root, "FASTMRI_BRAIN_CYCLEINR", f"CycleINR local NingXia-T2 {scale} case-level CV reproduction"),
        "swinir": ("fastmri_brain_swinir_2p5d.run_all", swinir_run_root, "FASTMRI_BRAIN_SWINIR", f"SwinIR 2.5D local NingXia-T2 {scale} case-level CV reproduction"),
        "i3net": ("fastmri_brain_i3net.run_all", i3net_run_root, "FASTMRI_BRAIN_I3NET", f"I3Net TMI 2024 official architecture, local NingXia-T2 {scale} case-level CV reproduction"),
        "hat": ("fastmri_brain_hat_2p5d.run_all", hat_run_root, "FASTMRI_BRAIN_HAT", f"HAT 2.5D local NingXia-T2 {scale} case-level CV reproduction adapted from XPixelGroup/HAT"),
        "smamba": ("fastmri_brain_smamba_unet_2p5d.run_all", smamba_run_root, "FASTMRI_BRAIN_SMAMBA", f"SMamba-UNet/MambaIR 2.5D local NingXia-T2 {scale} case-level CV reproduction"),
        "gan": ("fastmri_brain_gan_2p5d.run_all", gan_run_root, "FASTMRI_BRAIN_GAN", f"Inherited pix2pix/GAN 2.5D local NingXia-T2 {scale} case-level CV reproduction"),
        "acvtt": ("fastmri_brain_acvtt_2p5d.run_all", acvtt_run_root, "FASTMRI_BRAIN_ACVTT", f"Official ACVTT public code adapted to local NingXia-T2 {scale} case-level CV protocol"),
        "ressrdiff": ("fastmri_brain_ressrdiff_2p5d.run_all", ressrdiff_run_root, "FASTMRI_BRAIN_RESSRDIFF", f"Official Res-SRDiff diffusion core adapted to local NingXia-T2 {scale} case-level CV protocol"),
    }
    for fold_root in folds:
        for model in models:
            module, run_root, env_prefix, source_note = model_to_module[model]
            _run_one(fold_root, run_root, module, profile, force, env_prefix, source_note)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NingXia case-level CV folds for T2 x4 interpolation baselines.")
    parser.add_argument("--cv-root", type=Path, default=DEFAULT_CV_ROOT)
    parser.add_argument(
        "--profile",
        choices=[
            "smoke", "mini", "full", "full_x2", "full_x6", "full_safe", "full_tiny", "full_stable",
            "full_extend60", "full_x2_extend60", "full_x6_extend60", "full_x2_extend90", "full_60_scratch",
        ],
        default="full",
    )
    parser.add_argument("--models", nargs="+", choices=["saint", "resunet", "arssr", "cycleinr", "swinir", "i3net", "hat", "smamba", "gan", "acvtt", "ressrdiff"], default=["saint", "resunet"])
    parser.add_argument("--fold-limit", type=int, default=None)
    parser.add_argument("--folds", nargs="+", default=None, help="Optional explicit folds, e.g. fold_06 fold_07 or 6 7.")
    parser.add_argument("--saint-run-root", type=Path, default=DEFAULT_SAINT_RUN_ROOT)
    parser.add_argument("--resunet-run-root", type=Path, default=DEFAULT_RESUNET_RUN_ROOT)
    parser.add_argument("--arssr-run-root", type=Path, default=DEFAULT_ARSSR_RUN_ROOT)
    parser.add_argument("--cycleinr-run-root", type=Path, default=DEFAULT_CYCLEINR_RUN_ROOT)
    parser.add_argument("--swinir-run-root", type=Path, default=DEFAULT_SWINIR_RUN_ROOT)
    parser.add_argument("--i3net-run-root", type=Path, default=DEFAULT_I3NET_RUN_ROOT)
    parser.add_argument("--hat-run-root", type=Path, default=DEFAULT_HAT_RUN_ROOT)
    parser.add_argument("--smamba-run-root", type=Path, default=DEFAULT_SMAMBA_RUN_ROOT)
    parser.add_argument("--gan-run-root", type=Path, default=DEFAULT_GAN_RUN_ROOT)
    parser.add_argument("--acvtt-run-root", type=Path, default=DEFAULT_ACVTT_RUN_ROOT)
    parser.add_argument("--ressrdiff-run-root", type=Path, default=DEFAULT_RESSRDIFF_RUN_ROOT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    run_cv(
        cv_root=args.cv_root,
        profile=args.profile,
        models=args.models,
        fold_limit=args.fold_limit,
        saint_run_root=args.saint_run_root,
        resunet_run_root=args.resunet_run_root,
        arssr_run_root=args.arssr_run_root,
        cycleinr_run_root=args.cycleinr_run_root,
        swinir_run_root=args.swinir_run_root,
        i3net_run_root=args.i3net_run_root,
        hat_run_root=args.hat_run_root,
        smamba_run_root=args.smamba_run_root,
        gan_run_root=args.gan_run_root,
        acvtt_run_root=args.acvtt_run_root,
        ressrdiff_run_root=args.ressrdiff_run_root,
        force=args.force,
        fold_names=args.folds,
    )


if __name__ == "__main__":
    main()
