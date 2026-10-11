"""Post-result six-contrast max-t interval for HAT/SwinIR response placebos."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
PLAN = ROOT / "RESPONSE_PLACEBO_SIX_FAMILY_PLAN_2026-10-01.md"
OUT = EXPERIMENTS / "response_placebo_six_family"
COLS = ("influence", "placebo_a", "placebo_b", "alignment")
CONFIGS = ("hat", "swinir", "hat_to_swinir")


def partial(values: np.ndarray, index: int) -> float:
    ranked = np.stack([rankdata(values[:, index]), rankdata(values[:, 3])], axis=1)
    ranked = ranked.reshape(-1, 4, 2)
    residual = ranked - ranked.mean(axis=1, keepdims=True)
    residual -= residual.mean(axis=0, keepdims=True)
    x, y = residual[:, :, 0].ravel(), residual[:, :, 1].ravel()
    return float(x @ y / np.sqrt((x @ x) * (y @ y)))


def contrast(values: np.ndarray) -> float:
    return partial(values, 0) - .5 * (partial(values, 1) + partial(values, 2))


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    by_dataset = {}
    source_hashes = {}
    for dataset in ("fastmri", "ixi"):
        old_path = EXPERIMENTS / f"acquired_response_id_placebo_{dataset}/per_context.csv"
        cross_path = EXPERIMENTS / f"cross_arch_acquired_response_{dataset}/per_context.csv"
        old, cross = pd.read_csv(old_path), pd.read_csv(cross_path)
        source_hashes[dataset] = {
            "within": hashlib.sha256(old_path.read_bytes()).hexdigest(),
            "cross": hashlib.sha256(cross_path.read_bytes()).hexdigest()}
        frames = {"hat": old[old.model == "hat"],
                  "swinir": old[old.model == "swinir"],
                  "hat_to_swinir": cross}
        groups = {}
        for config, frame in frames.items():
            frame = frame.sort_values(["case", "z", "context"])
            cases = sorted(frame.case.unique())
            contexts = tuple(sorted(frame.context.unique()))
            assert len(frame) == len(cases) * 12 and len(contexts) == 4
            assert frame.groupby(["case", "z"]).context.apply(
                lambda x: tuple(x) == contexts).all()
            groups[config] = (cases, frame[list(COLS)].to_numpy().reshape(len(cases), 12, 4))
        assert groups["hat"][0] == groups["swinir"][0] == groups["hat_to_swinir"][0]
        by_dataset[dataset] = groups
    names = [(dataset, config) for dataset in ("fastmri", "ixi") for config in CONFIGS]
    points = np.array([contrast(by_dataset[dataset][config][1].reshape(-1, 4))
                       for dataset, config in names])
    rng = np.random.default_rng(20261028)
    boot = np.empty((2000, len(names)))
    for b in range(len(boot)):
        selected = {dataset: rng.integers(0, len(by_dataset[dataset]["hat"][0]),
                                           len(by_dataset[dataset]["hat"][0]))
                    for dataset in ("fastmri", "ixi")}
        for j, (dataset, config) in enumerate(names):
            sample = by_dataset[dataset][config][1][selected[dataset]].reshape(-1, 4)
            boot[b, j] = contrast(sample)
    se = boot.std(axis=0, ddof=1)
    if not np.isfinite(se).all() or (se <= 0).any():
        raise AssertionError("Invalid bootstrap standard errors")
    max_t = np.max(np.abs((boot - points) / se), axis=1)
    critical = float(np.quantile(max_t, .95))
    results = [{"dataset": dataset, "configuration": config,
                "point": float(points[j]), "se": float(se[j]),
                "simultaneous_low": float(points[j] - critical * se[j]),
                "simultaneous_high": float(points[j] + critical * se[j])}
               for j, (dataset, config) in enumerate(names)]
    OUT.mkdir(parents=True)
    pd.DataFrame(boot, columns=[f"{ds}_{cfg}" for ds, cfg in names]).to_csv(
        OUT / "bootstrap_estimates.csv", index=False)
    summary = {"status": "post-result six-contrast max-t sensitivity",
               "plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "source_sha256": source_hashes, "bootstrap_draws": len(boot),
               "critical_max_t": critical, "results": results}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
