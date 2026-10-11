"""Validate only explicit tuple indexing against the official MONAI 0.4 code."""
from __future__ import annotations

import ast
import hashlib
import json
import time
import traceback
from pathlib import Path

from vs_seg_task_cpu_support import ROOT, STAGE, resource_gate, load_model


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out = ROOT / "experiments/vs_seg_001_tuple_equivalence"
    out.mkdir(parents=True, exist_ok=True)
    attempt = len(list(out.glob("attempt_*.json"))) + 1
    report = {"attempt": attempt, "complete": False, "patient": "VS-SEG-001", "author_split": "training", "independent_confirmation": False, "script_sha256": sha(Path(__file__))}
    start = time.perf_counter()
    try:
        report["resource_gate"] = resource_gate()
        model, proof = load_model()
        import nibabel as nib
        import numpy as np
        import torch
        import monai.inferers.utils as utils
        from monai.transforms import NormalizeIntensity
        from vs_seg_001_label_pixel_feasibility import load_pair
        volume, _, _ = load_pair()
        previous_file = ROOT / "experiments/vs_seg_001_native_task_preflight/attempt_01.json"
        previous = json.loads(previous_file.read_text())
        affine = np.asarray(previous["geometry"]["native_ras_affine"])
        orientation = nib.orientations.ornt_transform(nib.orientations.io_orientation(affine), nib.orientations.axcodes2ornt("RAS"))
        image = np.ascontiguousarray(nib.orientations.apply_orientation(volume, orientation))
        inputs = torch.from_numpy(np.ascontiguousarray(NormalizeIntensity()(image[None].copy()))).unsqueeze(0)
        source_path = STAGE / "vendor/monai/inferers/utils.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        class TupleIndices(ast.NodeTransformer):
            changed = 0
            def visit_Subscript(self, node):
                self.generic_visit(node)
                if isinstance(node.slice, ast.Name) and node.slice.id in {"win_slice", "original_idx", "final_slicing"}:
                    node.slice = ast.Call(func=ast.Name(id="tuple", ctx=ast.Load()), args=[node.slice], keywords=[])
                    self.changed += 1
                return node
        transform = TupleIndices()
        patched = ast.fix_missing_locations(transform.visit(tree))
        if transform.changed != 4:
            raise ValueError("Expected exactly four list-to-tuple indexing changes")
        patched_source = ast.unparse(patched) + "\n"
        target = out / "monai_0_4_tuple_inferer.py"
        target.write_text(patched_source, encoding="utf-8")
        namespace = vars(utils).copy()
        exec(compile(patched, str(target), "exec"), namespace)
        timings = {}
        logits = []
        for name, infer in (("official_lists", utils.sliding_window_inference), ("explicit_tuples", namespace["sliding_window_inference"])):
            t = time.perf_counter()
            with torch.inference_mode():
                output = infer(inputs, roi_size=(384, 384, 64), sw_batch_size=1, predictor=lambda x: model(x)[0], mode="gaussian")
            timings[name] = time.perf_counter() - t
            if not bool(torch.isfinite(output).all()) or torch.cuda.is_initialized():
                raise ValueError("Invalid CPU output")
            logits.append(output)
        before, after = logits
        max_diff = float((before - after).abs().max())
        equal = bool(torch.equal(before, after))
        old_prediction = np.load(previous_file.parent / "prediction_attempt_01.npz")["prediction_ras"]
        current = before.argmax(dim=1)[0].numpy().astype(bool)
        same_saved_prediction = bool(np.array_equal(current, old_prediction))
        report.update({"runtime": proof, "official_inferer_sha256": sha(source_path), "tuple_inferer_sha256": sha(target), "changed_indexing_sites": transform.changed, "bitwise_logits_equal": equal, "max_absolute_logit_difference": max_diff, "prediction_voxel_differences": int((before.argmax(dim=1) != after.argmax(dim=1)).sum()), "official_prediction_equals_previous_native_preflight": same_saved_prediction, "forward_seconds": timings, "cuda_initialized": torch.cuda.is_initialized()})
        if not equal or not same_saved_prediction:
            raise ValueError("Tuple compatibility or native preprocessing equivalence failed")
        report["complete"] = True
    except Exception as exc:
        report.update({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    report["elapsed_seconds"] = time.perf_counter() - start
    (out / f"attempt_{attempt:02d}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
