import sys
import unittest
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pre"))

from rasinet.data import build_rasinet_condition
from rasinet.losses import rasinet_group_loss
from rasinet.metrics import evaluate_reliability_volume
from rasinet.model import RASINet2p5D


class RASINetCoreTests(unittest.TestCase):
    def test_condition_builds_group_coarse_phase_and_difference_channels(self):
        left = np.zeros((8, 8), dtype=np.float32)
        right = np.ones((8, 8), dtype=np.float32)

        cond, coarse = build_rasinet_condition(left, right, stride=4, target_shape=(8, 8))

        self.assertEqual(cond.shape, (10, 8, 8))
        self.assertEqual(coarse.shape, (3, 8, 8))
        np.testing.assert_allclose(cond[2], 0.25)
        np.testing.assert_allclose(cond[3], 0.50)
        np.testing.assert_allclose(cond[4], 0.75)
        np.testing.assert_allclose(cond[5], 0.25)
        np.testing.assert_allclose(cond[6], 0.50)
        np.testing.assert_allclose(cond[7], 0.75)
        np.testing.assert_allclose(cond[8], 1.0)
        np.testing.assert_allclose(cond[9], 1.0)

    def test_model_outputs_prediction_confidence_uncertainty_maps(self):
        model = RASINet2p5D(stride=4, base_channels=8, num_blocks=1)
        cond = torch.rand(2, model.input_channels, 16, 16)

        out = model.forward_components(cond)

        for key in ["prediction", "residual", "confidence", "log_variance", "uncertainty"]:
            self.assertEqual(tuple(out[key].shape), (2, 3, 16, 16))
            self.assertTrue(torch.isfinite(out[key]).all())
        self.assertTrue(torch.all(out["confidence"] >= 0.0))
        self.assertTrue(torch.all(out["confidence"] <= 1.0))
        self.assertTrue(torch.all(out["uncertainty"] > 0.0))

    def test_rasinet_loss_is_finite_and_backpropagates(self):
        model = RASINet2p5D(stride=4, base_channels=8, num_blocks=1)
        cond = torch.rand(2, model.input_channels, 16, 16)
        coarse = cond[:, 2:5]
        target = (coarse + 0.05 * torch.randn_like(coarse)).clamp(0.0, 1.0)
        out = model.forward_components(cond)
        pred = out["prediction"].clamp(0.0, 1.0)

        loss, parts = rasinet_group_loss(
            pred=pred,
            target=target,
            coarse=coarse,
            residual=out["residual"],
            log_variance=out["log_variance"],
            uncertainty=out["uncertainty"],
            weights={
                "lambda_unc": 0.5,
                "lambda_logvar": 0.02,
                "lambda_grad_xy": 0.05,
                "lambda_res": 0.001,
                "lambda_cal": 0.05,
            },
        )

        self.assertTrue(torch.isfinite(loss))
        self.assertIn("cal", parts)
        loss.backward()
        grad_norm = sum(
            float(param.grad.abs().sum().item())
            for param in model.parameters()
            if param.grad is not None
        )
        self.assertGreater(grad_norm, 0.0)

    def test_reliability_metrics_capture_error_uncertainty_correlation(self):
        gt = np.zeros((4, 4, 5), dtype=np.float32)
        pred = np.zeros_like(gt)
        uncertainty = np.zeros_like(gt)
        for idx, value in [(1, 0.1), (2, 0.4), (3, 0.9)]:
            pred[:, :, idx] = value
            uncertainty[:, :, idx] = value

        metrics, risk_rows, cal_rows = evaluate_reliability_volume(gt, pred, uncertainty, factor=4)

        self.assertGreater(metrics["pixel_error_uncertainty_corr"], 0.99)
        self.assertEqual(len(risk_rows), 10)
        self.assertGreaterEqual(len(cal_rows), 1)


if __name__ == "__main__":
    unittest.main()
