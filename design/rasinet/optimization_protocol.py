from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCALES = (2, 4, 6)
PRIMARY_TARGETS = ("i3net", "hat", "swinir")
ANALYTICAL = ("linear", "cubic")
UNIVERSAL_NEURAL = (
    "i3net", "hat", "swinir", "arssr", "cycleinr", "pix2pixgan",
    "smamba_unet", "acvtt", "ressrdiff", "resunet", "saint",
)

FAMILIES = {
    "i3net": "cnn_inter_intra", "hat": "transformer", "swinir": "transformer",
    "arssr": "implicit", "cycleinr": "implicit", "pix2pixgan": "gan_cnn",
    "smamba_unet": "state_space_unet", "acvtt": "attention_cnn",
    "ressrdiff": "diffusion", "resunet": "cnn_unet", "saint": "attention_cnn",
    "acsinet": "cnn_attention", "linear": "analytical", "cubic": "analytical",
}


@dataclass(frozen=True)
class SourceSpec:
    name: str
    root: Path
    run_name: str
    output_dir: str = "model_outputs"
    cross_validation: bool = False
    gt_dir: str = "eval_gt"

    def run_dir(self, fold: str | None = None) -> Path:
        if self.cross_validation:
            if fold is None:
                raise ValueError(f"fold required for {self.name}")
            return self.root / "runs" / fold / self.run_name
        return self.root / "runs" / self.run_name

    def prediction_dir(self, fold: str | None = None) -> Path:
        return self.run_dir(fold) / self.output_dir


def _run(scale: int) -> str:
    return "full" if scale == 4 else f"full_x{scale}"


def profile_sources(dataset: str, scale: int) -> dict[str, SourceSpec]:
    b = REPO_ROOT / "baseline"
    d = REPO_ROOT / "design"
    if dataset == "ixi":
        if scale != 4:
            raise ValueError("IXI optimization profile is factor four")
        return {
            "i3net": SourceSpec("i3net", b / "ixi_i3net", "full_test115_stable", gt_dir="eval_inputs/gt"),
            "hat": SourceSpec("hat", b / "ixi_hat_2p5d", "full_test115", gt_dir="eval_inputs/gt"),
            "swinir": SourceSpec("swinir", b / "ixi_swinir_2p5d", "full_test115", gt_dir="eval_inputs/gt"),
            "acsinet": SourceSpec("acsinet", d / "acsinet", "full_test115", gt_dir="eval_inputs/gt"),
        }
    if dataset == "fastmri":
        run = _run(scale)
        roots = {
            "i3net": (b / "fastmri_brain_i3net", run, "model_outputs"),
            "hat": (b / "fastmri_brain_hat_2p5d", run, "model_outputs"),
            "swinir": (b / "fastmri_brain_swinir_2p5d", run, "model_outputs"),
            "arssr": (b / "fastmri_brain_arssr", run, "model_outputs"),
            "cycleinr": (b / "fastmri_brain_cycleinr", run, "model_outputs"),
            "pix2pixgan": (b / "fastmri_brain_gan_2p5d", run, "model_outputs"),
            "smamba_unet": (b / "fastmri_brain_smamba_unet_2p5d", run, "model_outputs"),
            "acvtt": (b / "fastmri_brain_acvtt_2p5d", "full_tiny" if scale == 4 else run, "model_outputs"),
            "ressrdiff": (b / "fastmri_brain_ressrdiff_2p5d", "full_tiny" if scale == 4 else run, "model_outputs"),
            "resunet": ((b / "fastmri_brain_t2_resunet", "full", "resunet_outputs") if scale == 4 else (b / "fastmri_brain_saint", run, "resunet_outputs")),
            "saint": ((b / "fastmri_brain_t2_saint_expanded", "full", "saint_outputs") if scale == 4 else (b / "fastmri_brain_saint", run, "saint_outputs")),
        }
        return {name: SourceSpec(name, root, run_name, output_dir) for name, (root, run_name, output_dir) in roots.items()}
    if dataset == "ningxia":
        run = _run(scale)
        base = b if scale == 4 else REPO_ROOT
        run_overrides = {"acvtt": "full_tiny", "ressrdiff": "full_tiny"} if scale == 4 else {}
        roots = {
            "i3net": "ningxia_t2_i3net_cv", "hat": "ningxia_t2_hat_2p5d_cv",
            "swinir": "ningxia_t2_swinir_2p5d_cv", "arssr": "ningxia_t2_arssr_cv",
            "cycleinr": "ningxia_t2_cycleinr_cv", "pix2pixgan": "ningxia_t2_gan_2p5d_cv",
            "smamba_unet": "ningxia_t2_smamba_unet_2p5d_cv", "acvtt": "ningxia_t2_acvtt_2p5d_cv",
            "ressrdiff": "ningxia_t2_ressrdiff_2p5d_cv", "resunet": "ningxia_t2_resunet_cv",
            "saint": "ningxia_t2_saint_cv",
        }
        output_dirs = {"resunet": "resunet_outputs", "saint": "saint_outputs"}
        return {
            name: SourceSpec(name, base / root, run_overrides.get(name, run), output_dirs.get(name, "model_outputs"), True)
            for name, root in roots.items()
        }
    raise ValueError(dataset)


def folds(dataset: str) -> tuple[str | None, ...]:
    return tuple(f"fold_{i:02d}" for i in range(8)) if dataset == "ningxia" else (None,)


def case_names(source: SourceSpec, fold: str | None) -> tuple[str, ...]:
    directory = source.prediction_dir(fold)
    return tuple(sorted(p.name[5:] for p in directory.glob("diff_*.nii.gz")))


def prediction_path(source: SourceSpec, fold: str | None, case: str) -> Path:
    return source.prediction_dir(fold) / f"diff_{case}"


def gt_path(reference: SourceSpec, fold: str | None, case: str) -> Path:
    return reference.run_dir(fold) / reference.gt_dir / case


def sparse_path(reference: SourceSpec, fold: str | None, case: str) -> Path:
    candidate = reference.run_dir(fold) / "eval_sparse" / case
    return candidate if candidate.exists() else gt_path(reference, fold, case)


def analytical_path(reference: SourceSpec, fold: str | None, method: str, case: str) -> Path:
    return reference.run_dir(fold) / "baseline_outputs" / method / f"{method}_{case}"
