import json
import sys
import unittest
from pathlib import Path

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pre"))
sys.path.insert(0, str(ROOT / "design"))

from ixi_ecsinet_2p5d.acceptance import (
    analyze_checkpoint,
    component_statistics,
    evaluate_mask_gate,
    evaluate_quality_gate,
    gpu_preflight,
    run_static_validation,
)
from ixi_ecsinet_2p5d.efficiency import (
    benchmark_inference,
    run_ecsinet_profile,
    timing_statistics,
)
from ixi_ecsinet_2p5d.one_click import parse_nvidia_smi_snapshot, stage_sequence


class ECSINetAcceptanceTests(unittest.TestCase):
    def test_component_statistics_detects_change_aware_nonconstant_mask(self):
        coarse = torch.zeros(1, 1, 4, 4)
        target = torch.zeros_like(coarse)
        target[:, :, 2:, :] = 1.0
        mask = torch.full_like(coarse, 0.1)
        mask[:, :, 2:, :] = 0.8
        residual = torch.full_like(coarse, 0.25)
        correction = mask * residual
        parts = {
            "coarse": coarse,
            "recon": coarse + correction,
            "mask": mask,
            "residual": residual,
            "correction": correction,
            "change": target.clone(),
            "coarse_grad": torch.zeros_like(coarse),
        }

        mask_row, residual_row, corr_row = component_statistics(parts, target)

        self.assertAlmostEqual(mask_row["mask_mean"], 0.45, places=6)
        self.assertGreater(mask_row["mask_std"], 0.01)
        self.assertGreater(mask_row["mask_high_change_mean"], mask_row["mask_low_change_mean"])
        self.assertAlmostEqual(residual_row["residual_abs_max"], 0.25, places=6)
        self.assertGreater(corr_row["mask_vs_target_linear_error_corr"], 0.99)

    def test_quality_gate_requires_ecsinet_to_beat_linear_and_cubic_in_all_directions(self):
        passing = [
            {"method": "ecsinet", "psnr_mean": 31.0, "ssim_mean": 0.92, "ncc_mean": 0.95, "mae_mean": 0.02, "mse_mean": 0.003},
            {"method": "linear", "psnr_mean": 29.0, "ssim_mean": 0.89, "ncc_mean": 0.92, "mae_mean": 0.03, "mse_mean": 0.005},
            {"method": "cubic", "psnr_mean": 30.0, "ssim_mean": 0.90, "ncc_mean": 0.93, "mae_mean": 0.025, "mse_mean": 0.004},
        ]
        failing = [dict(row) for row in passing]
        failing[0]["ssim_mean"] = 0.88

        passed = evaluate_quality_gate(passing)
        failed = evaluate_quality_gate(failing)

        self.assertTrue(passed["passed"])
        self.assertEqual(passed["failed_checks"], [])
        self.assertFalse(failed["passed"])
        self.assertIn("ecsinet.ssim_mean > cubic.ssim_mean", failed["failed_checks"])

    def test_gpu_preflight_blocks_on_foreign_busy_process(self):
        snapshot = {
            "gpu_utilization_percent": 98.0,
            "memory_used_mib": 18158.0,
            "memory_total_mib": 24455.0,
            "compute_processes": [{"pid": 41184, "used_memory_mib": 18000.0}],
        }

        blocked = gpu_preflight(snapshot, own_pid=1234, max_utilization_percent=20.0, max_memory_fraction=0.25)
        allowed = gpu_preflight(snapshot, own_pid=41184, max_utilization_percent=100.0, max_memory_fraction=1.0)

        self.assertFalse(blocked["passed"])
        self.assertIn("foreign_compute_process", blocked["reasons"])
        self.assertTrue(allowed["passed"])

    def test_mask_gate_rejects_constant_mask(self):
        passing_rows = [{"mask_mean": 0.3, "mask_std": 0.08}]
        failing_rows = [{"mask_mean": 0.3, "mask_std": 0.001}]
        residual_rows = [{"correction_abs_max": 0.4}]

        self.assertTrue(evaluate_mask_gate(passing_rows, residual_rows)["passed"])
        failed = evaluate_mask_gate(failing_rows, residual_rows)
        self.assertFalse(failed["passed"])
        self.assertIn("mask_std >= 0.01", failed["failed_checks"])

    def test_static_validation_writes_machine_and_human_readable_reports(self):
        output_dir = ROOT / "tests"
        names = ["static_validation.json", "static_validation.md"]
        try:
            result = run_static_validation(output_dir)

            self.assertTrue(result["passed"])
            checks = {item["name"]: item for item in result["checks"]}
            self.assertIn("parsed 8 Python files", checks["ast_parse"]["detail"])
            self.assertTrue(checks["stride_mismatch_guard"]["passed"])
            for name in names:
                self.assertTrue((output_dir / name).is_file(), name)
        finally:
            for name in names:
                path = output_dir / name
                if path.exists():
                    path.unlink()

    def test_analyze_checkpoint_writes_component_statistics(self):
        from ixi_ecsinet_2p5d.model import ECSINet

        output_dir = ROOT / "tests"
        checkpoint = output_dir / "_ecsinet_analysis_checkpoint.pth"
        names = [
            "mask_statistics.csv",
            "residual_statistics.csv",
            "mask_correlation.csv",
            "component_acceptance.json",
            "component_acceptance.md",
        ]
        model = ECSINet(channels=8, num_blocks=1)
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "stride": 4,
                "model_config": {
                    "channels": 8,
                    "num_blocks": 1,
                    "expansion": 2,
                    "kernel_size": 5,
                    "residual_scale": 1.0,
                    "mask_bias": -2.0,
                    "amp": False,
                },
            },
            checkpoint,
        )
        try:
            result = analyze_checkpoint(
                checkpoint=checkpoint,
                profile_name="smoke",
                metrics_dir=output_dir,
                report_dir=output_dir,
                max_samples=1,
                visual_count=0,
                device_name="cpu",
            )

            self.assertEqual(result["samples"], 1)
            for name in names:
                self.assertTrue((output_dir / name).is_file(), name)
        finally:
            if checkpoint.exists():
                checkpoint.unlink()
            for name in names:
                path = output_dir / name
                if path.exists():
                    path.unlink()

    def test_parse_nvidia_smi_snapshot_combines_gpu_and_process_rows(self):
        snapshot = parse_nvidia_smi_snapshot(
            gpu_line="NVIDIA GeForce RTX 5090 D v2, 24455, 18158, 98",
            process_lines="41184, 18000\n123, N/A\n",
        )

        self.assertEqual(snapshot["gpu_name"], "NVIDIA GeForce RTX 5090 D v2")
        self.assertEqual(snapshot["memory_total_mib"], 24455.0)
        self.assertEqual(snapshot["gpu_utilization_percent"], 98.0)
        self.assertEqual(snapshot["compute_processes"][0]["pid"], 41184)
        self.assertIsNone(snapshot["compute_processes"][1]["used_memory_mib"])
        json.dumps(snapshot, allow_nan=False)

    def test_stage_sequence_stops_at_requested_gate(self):
        self.assertEqual(stage_sequence("static"), ["static"])
        self.assertEqual(stage_sequence("smoke"), ["static", "preflight", "profile", "smoke"])
        self.assertEqual(stage_sequence("mini"), ["static", "preflight", "profile", "smoke", "mini"])

    def test_timing_statistics_reports_distribution_in_milliseconds(self):
        stats = timing_statistics([0.010, 0.020, 0.030])

        self.assertAlmostEqual(stats["forward_ms_mean"], 20.0, places=6)
        self.assertAlmostEqual(stats["forward_ms_p50"], 20.0, places=6)
        self.assertAlmostEqual(stats["forward_ms_p95"], 29.0, places=6)
        self.assertGreater(stats["forward_ms_std"], 0.0)

    def test_benchmark_inference_records_shape_params_and_forward_timing(self):
        model = torch.nn.Conv2d(4, 1, 3, padding=1)

        row = benchmark_inference(
            name="tiny-conv",
            model=model,
            device=torch.device("cpu"),
            input_shape=(1, 4, 8, 8),
            warmup=1,
            iterations=3,
        )

        self.assertEqual(row["method"], "tiny-conv")
        self.assertEqual(row["input_shape"], "1x4x8x8")
        self.assertEqual(row["params"], 37)
        self.assertEqual(row["iterations"], 3)
        self.assertGreaterEqual(row["forward_ms_mean"], 0.0)
        self.assertEqual(row["definition"], "model forward only; excludes IO, resize, and metrics")

    def test_run_ecsinet_profile_writes_all_required_artifacts(self):
        output_dir = ROOT / "tests"
        names = [
            "efficiency_profile.csv",
            "memory_profile.csv",
            "inference_profile.csv",
            "profile_environment.json",
            "profile_summary.md",
        ]
        try:
            result = run_ecsinet_profile(
                output_dir=output_dir,
                device=torch.device("cpu"),
                configurations=[{"name": "test", "channels": 8, "num_blocks": 1, "batch_sizes": [1]}],
                image_size=16,
                warmup=0,
                inference_iterations=1,
                training_iterations=1,
            )

            for name in names:
                self.assertTrue((output_dir / name).is_file(), name)
            self.assertEqual(result["configurations"], 1)
            self.assertEqual(result["training_rows"], 1)
        finally:
            for name in names:
                path = output_dir / name
                if path.exists():
                    path.unlink()


if __name__ == "__main__":
    unittest.main()
