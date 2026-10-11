"""Target-assisted common-alpha control after the fixed-five numerical audit."""
from __future__ import annotations
import json
import math
import os
import sys
from datetime import datetime, timezone
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_runtime import sha

BASE = ROOT / "experiments/mc_rc_five_developer_constrained_oracle"
OUT = ROOT / "experiments/mc_rc_constrained_constant_diagnostic"
PLAN = ROOT / "MC_RC_CONSTRAINED_CONSTANT_DIAGNOSTIC_PLAN_2026-10-02.md"

def read(p):
    return json.loads(p.read_text(encoding="utf-8"))

def write(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resource_gate()
    result, proof = read(BASE / "attempt_01.json"), read(BASE / "independent_pixel_and_dual_verification.json")
    if not result["complete"] or proof["errors"] or proof["result_sha256"] != sha(BASE / "attempt_01.json") or proof["run_contract_sha256"] != sha(BASE / "run_contract.json"):
        raise ValueError("Independent fixed-five input not current")
    OUT.mkdir(exist_ok=False)
    paths = [PLAN, __file__, BASE / "attempt_01.json", BASE / "run_contract.json", BASE / "independent_pixel_and_dual_verification.json"]
    from pathlib import Path
    paths = [Path(p) for p in paths] + [ROOT / p["coefficients_file"] for p in result["patients"]]
    contract = {"created_utc": datetime.now(timezone.utc).isoformat(), "post_result_diagnostic": True, "files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in paths]}
    write(OUT / "run_contract.json", contract)
    rows, errors = [], []
    for p in result["patients"]:
        resource_gate()
        path = ROOT / p["coefficients_file"]
        if sha(path) != p["coefficients_sha256"]:
            raise ValueError("Coefficient hash mismatch")
        with np.load(path) as bundle:
            coef, alpha, ua = [bundle[k] for k in ("coefficients", "constrained_alpha", "unconstrained_alpha")]
            limits = bundle["lesion_limits"]
        sums = coef.sum(axis=0).reshape(3, 3)
        lower, upper = 0., 1.
        feasible = True
        for (b, m, d), limit in zip(sums[1:], limits):
            c = b - limit
            if d > 0:
                discriminant = m * m - d * c
                if discriminant < 0:
                    feasible = False
                    break
                rad = math.sqrt(discriminant)
                lower, upper = max(lower, (m - rad) / d), min(upper, (m + rad) / d)
            elif m > 0:
                lower = max(lower, c / (2 * m))
            elif m < 0:
                upper = min(upper, c / (2 * m))
            elif c > 1e-10:
                feasible = False
        feasible = feasible and lower <= upper
        changed = np.abs(alpha - ua) > 1e-12
        lesion_tiles = coef[:, 5] > 0
        row = {"patient": p["patient"], "shared_constant_feasible": feasible, "feasible_interval": [lower, upper] if feasible else None,
               "tile_constrained_gain_db": p["constrained_support_gain_db_vs_better_fixed"], "tiles": len(alpha), "changed_tiles": int(changed.sum()), "lesion_action_tiles": int(lesion_tiles.sum()), "changed_lesion_action_tiles": int((changed & lesion_tiles).sum()), "max_alpha_change": float(np.abs(alpha - ua).max()), "mean_alpha_change_all_tiles": float(np.abs(alpha - ua).mean())}
        if feasible:
            b, m, d = sums[0]
            a = float(np.clip(m / d if d else 0., lower, upper))
            losses = sums[:, 0] - 2 * sums[:, 1] * a + sums[:, 2] * a * a
            # Different arithmetic path evaluates every original tile directly.
            independent = np.array([math.fsum(float(c[k] - 2 * c[k + 1] * a + c[k + 2] * a ** 2) for c in coef) for k in (0, 3, 6)])
            if not np.allclose(losses, independent, rtol=0, atol=1e-12):
                errors.append(p["patient"] + " scalar verification differs")
            violation = independent[1:] - limits
            if not (violation <= 1e-10).all():
                errors.append(p["patient"] + " constant constraints fail")
            # Fixed 1001-point verification, not a parameter search.
            grid = np.linspace(0, 1, 1001)
            gl = np.array([sums[:, 0] - 2 * sums[:, 1] * x + sums[:, 2] * x * x for x in grid])
            gf = (gl[:, 1:] <= limits).all(axis=1)
            if gf.any() and gl[gf, 0].min() < independent[0] - 1e-12:
                errors.append(p["patient"] + " feasible grid beats claimed minimum")
            gain = 10 * math.log10(min(p["baseline_losses"][0], p["candidate_losses"][0]) / independent[0])
            row.update(shared_alpha=a, shared_losses=independent.tolist(), violations=violation.tolist(), shared_support_gain_db_vs_better_fixed=gain,
                       tile_gain_over_best_feasible_shared_db=10 * math.log10(independent[0] / p["solution"]["primal_objective"]), feasible_fixed_grid_points=int(gf.sum()))
        rows.append(row)
        print(json.dumps(row), flush=True)
    output = {"created_utc": datetime.now(timezone.utc).isoformat(), "run_contract_sha256": sha(OUT / "run_contract.json"), "complete": len(rows) == 5, "patients": rows, "errors": errors,
              "verification": "scalar per-tile math.fsum plus fixed-grid feasible-value check, not fresh pixel decoding (in preceding proof)", "post_result_diagnostic": True, "target_assisted_shared_alpha": True,
              "original_raw_gate_passed": False, "deployable_method_tested": False, "gpu_used": False, "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False}
    write(OUT / "attempt_01.json", output)
    return int(bool(errors))

if __name__ == "__main__":
    raise SystemExit(main())
