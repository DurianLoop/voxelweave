from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np


PRIMARY_NEURAL = ("i3net", "hat", "swinir")
EXPANDED_NEURAL = PRIMARY_NEURAL + ("arssr", "cycleinr", "pix2pixgan", "smamba_unet")
ANALYTICAL = ("linear", "cubic")
SCALES = (2, 4, 6)
DATASETS = ("fastmri", "ningxia")


@dataclass(frozen=True)
class ScaleSource:
    name: str
    root: Path
    run_name: str
    cross_validation: bool = False

    def run_dir(self, fold: str | None = None) -> Path:
        if self.cross_validation:
            if fold is None:
                raise ValueError(f"fold is required for {self.name}")
            return self.root / "runs" / fold / self.run_name
        return self.root / "runs" / self.run_name


FASTMRI_ROOTS = {
    "i3net": "fastmri_brain_i3net",
    "hat": "fastmri_brain_hat_2p5d",
    "swinir": "fastmri_brain_swinir_2p5d",
    "arssr": "fastmri_brain_arssr",
    "cycleinr": "fastmri_brain_cycleinr",
    "pix2pixgan": "fastmri_brain_gan_2p5d",
    "smamba_unet": "fastmri_brain_smamba_unet_2p5d",
}

NINGXIA_ROOTS = {
    "i3net": "ningxia_t2_i3net_cv",
    "hat": "ningxia_t2_hat_2p5d_cv",
    "swinir": "ningxia_t2_swinir_2p5d_cv",
    "arssr": "ningxia_t2_arssr_cv",
    "cycleinr": "ningxia_t2_cycleinr_cv",
    "pix2pixgan": "ningxia_t2_gan_2p5d_cv",
    "smamba_unet": "ningxia_t2_smamba_unet_2p5d_cv",
}


def run_name(scale: int) -> str:
    if scale not in SCALES:
        raise ValueError(f"unsupported scale: {scale}")
    return "full" if scale == 4 else f"full_x{scale}"


def sources_for(repo_root: Path, dataset: str, scale: int, expanded: bool = False) -> dict[str, ScaleSource]:
    if dataset not in DATASETS:
        raise ValueError(f"unknown dataset: {dataset}")
    names = EXPANDED_NEURAL if expanded else PRIMARY_NEURAL
    selected: dict[str, ScaleSource] = {}
    if dataset == "fastmri":
        for name in names:
            selected[name] = ScaleSource(
                name=name,
                root=repo_root / "baseline" / FASTMRI_ROOTS[name],
                run_name=run_name(scale),
            )
        return selected

    # The original x4 OOF predictions live under baseline/. The later x2/x6
    # runs use the same eight folds at repository root.
    base = repo_root / "baseline" if scale == 4 else repo_root
    for name in names:
        selected[name] = ScaleSource(
            name=name,
            root=base / NINGXIA_ROOTS[name],
            run_name=run_name(scale),
            cross_validation=True,
        )
    return selected


def folds_for(dataset: str) -> tuple[str | None, ...]:
    return tuple(f"fold_{index:02d}" for index in range(8)) if dataset == "ningxia" else (None,)


def prediction_path(source: ScaleSource, fold: str | None, case_id: str) -> Path:
    return source.run_dir(fold) / "model_outputs" / f"diff_{case_id}"


def ground_truth_path(reference: ScaleSource, fold: str | None, case_id: str) -> Path:
    return reference.run_dir(fold) / "eval_gt" / case_id


def sparse_input_path(reference: ScaleSource, fold: str | None, case_id: str) -> Path:
    return reference.run_dir(fold) / "eval_sparse" / case_id


def analytical_path(reference: ScaleSource, fold: str | None, method: str, case_id: str) -> Path:
    if method not in ANALYTICAL:
        raise ValueError(f"unknown analytical method: {method}")
    return reference.run_dir(fold) / "baseline_outputs" / method / f"{method}_{case_id}"


def case_ids(source: ScaleSource, fold: str | None) -> tuple[str, ...]:
    directory = source.run_dir(fold) / "model_outputs"
    if not directory.exists():
        raise FileNotFoundError(directory)
    names = tuple(sorted(path.name[len("diff_") :] for path in directory.glob("diff_*.nii.gz")))
    if len(names) != len(set(names)):
        raise ValueError(f"duplicate prediction identities in {directory}")
    return names


def case_set_id(case_names: tuple[str, ...] | list[str]) -> str:
    payload = "\n".join(sorted(case_names)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def common_model_intersection(model_sets: list[set[str] | frozenset[str]]) -> tuple[str, ...]:
    if not model_sets:
        raise ValueError("at least one model set is required")
    common = set(model_sets[0])
    for model_set in model_sets[1:]:
        common.intersection_update(model_set)
    return tuple(sorted(common))


def paired_bootstrap_indices(number_of_cases: int, samples: int, seed: int) -> np.ndarray:
    if number_of_cases < 2:
        raise ValueError("paired bootstrap requires at least two cases")
    if samples < 1:
        raise ValueError("bootstrap sample count must be positive")
    return np.random.default_rng(seed).integers(
        0,
        number_of_cases,
        size=(samples, number_of_cases),
    )


def ningxia_case_group(case_id: str) -> str:
    return case_id.split("_", 1)[0]


def ningxia_test_group(repo_root: Path, fold: str) -> str:
    path = (
        repo_root
        / "dataset"
        / "NingXiaData"
        / "processed_saint_cv"
        / fold
        / "splits"
        / "nifti_seed3407"
        / "test_cases.txt"
    )
    groups = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(groups) != 1:
        raise ValueError(f"expected one held-out group in {path}, found {groups}")
    return groups[0]
