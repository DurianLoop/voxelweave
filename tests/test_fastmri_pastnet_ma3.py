import sys
import unittest
from pathlib import Path

import torch
import torch.nn.functional as F


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pre"))
sys.path.insert(0, str(ROOT / "design"))

from fastmri_brain_pastnet_2p5d.model_ma import PASTNetMultiAnchor2p5D
from fastmri_brain_pastnet_2p5d.settings import Profile
from fastmri_brain_pastnet_2p5d.train import _batch_loss_ma, _load_compatible_state_dict, _reverse_multi_anchor_input


class FastMRIPASTNetMA3Tests(unittest.TestCase):
    def test_temporal_refinement_returns_detail_component(self):
        torch.manual_seed(7)
        model = PASTNetMultiAnchor2p5D(
            input_channels=13,
            base_channels=8,
            num_blocks=1,
            temporal_refine=True,
            refine_scale=0.5,
        )
        x = torch.rand(2, 13, 17, 19)

        parts = model.forward_components(x)

        self.assertEqual(parts["prediction"].shape, (2, 1, 17, 19))
        self.assertEqual(parts["detail_residual"].shape, (2, 1, 17, 19))
        self.assertEqual(parts["confidence"].shape, (2, 1, 17, 19))
        self.assertEqual(parts["gate"].shape, (2, 5, 17, 19))
        self.assertTrue(torch.isfinite(parts["prediction"]).all())
        self.assertGreater(float(parts["detail_residual"].detach().abs().mean()), 0.0)

    def test_rich_multi_anchor_reverse_preserves_curvature_and_swaps_outer_deltas(self):
        x = torch.zeros(1, 13, 2, 2)
        for channel in range(13):
            x[:, channel] = float(channel)

        reversed_x = _reverse_multi_anchor_input(x)

        self.assertTrue(torch.equal(reversed_x[:, 0], x[:, 3]))
        self.assertTrue(torch.equal(reversed_x[:, 1], x[:, 2]))
        self.assertTrue(torch.equal(reversed_x[:, 2], x[:, 1]))
        self.assertTrue(torch.equal(reversed_x[:, 3], x[:, 0]))
        self.assertTrue(torch.equal(reversed_x[:, 10], -x[:, 11]))
        self.assertTrue(torch.equal(reversed_x[:, 11], -x[:, 10]))
        self.assertTrue(torch.equal(reversed_x[:, 12], x[:, 12]))

    def test_ma3_can_warm_start_from_ma2_common_weights(self):
        ma2 = PASTNetMultiAnchor2p5D(input_channels=13, base_channels=8, num_blocks=1)
        ma3 = PASTNetMultiAnchor2p5D(input_channels=13, base_channels=8, num_blocks=1, temporal_refine=True)
        source = ma2.state_dict()
        expected = source["slice_encoder.0.weight"].clone()

        report = _load_compatible_state_dict(ma3, source)

        self.assertGreater(report["loaded"], 0)
        self.assertGreater(report["missing"], 0)
        self.assertTrue(torch.equal(ma3.state_dict()["slice_encoder.0.weight"], expected))
        self.assertIn("detail_refiner.1.weight", report["missing_keys"])

    def test_ma3_loss_can_include_mse_term_for_psnr_tuning(self):
        torch.manual_seed(11)
        model = PASTNetMultiAnchor2p5D(
            input_channels=13,
            base_channels=8,
            num_blocks=1,
            temporal_refine=True,
            refine_scale=0.3,
        )
        profile = Profile(
            name="unit_ma3_psnr",
            model_variant="ma3",
            lambda_grad=0.0,
            lambda_res=0.0,
            lambda_sym=0.0,
            lambda_edge=0.0,
            lambda_mse=0.25,
        )
        batch = {
            "cond_ma": torch.rand(2, 13, 16, 16),
            "coarse": torch.rand(2, 1, 16, 16),
            "target": torch.rand(2, 1, 16, 16),
        }

        loss, parts = _batch_loss_ma(model, batch, profile, torch.device("cpu"))

        with torch.no_grad():
            recon = model.forward_components(batch["cond_ma"])["prediction"].clamp(0.0, 1.0)
            expected_mse = F.mse_loss(recon, batch["target"])
        self.assertIn("mse", parts)
        self.assertAlmostEqual(parts["mse"], float(expected_mse), places=6)
        self.assertAlmostEqual(float(loss.detach()), parts["charbonnier"] + 0.25 * parts["mse"], places=5)


if __name__ == "__main__":
    unittest.main()
