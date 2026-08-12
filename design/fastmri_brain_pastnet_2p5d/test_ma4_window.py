from __future__ import annotations

import unittest

import numpy as np
import torch

from fastmri_brain_pastnet_2p5d.data import MA4_MISSING_OFFSETS, build_ma4_window_sample
from fastmri_brain_pastnet_2p5d.model_ma4 import PASTNetMA4Window2p5D
from fastmri_brain_pastnet_2p5d.settings import PROFILES
from fastmri_brain_pastnet_2p5d.train import _batch_loss_window


class MA4WindowTests(unittest.TestCase):
    def test_window_sample_uses_four_anchors_and_nine_missing_targets(self) -> None:
        volume = np.zeros((8, 8, 17), dtype=np.float32)
        for z in range(volume.shape[2]):
            volume[:, :, z] = z / float(volume.shape[2] - 1)

        sample = build_ma4_window_sample(volume, z=0, stride=4, target_shape=(8, 8))

        self.assertEqual(tuple(sample["cond_window"].shape), (22, 8, 8))
        self.assertEqual(tuple(sample["anchor_window"].shape), (4, 8, 8))
        self.assertEqual(tuple(sample["coarse_missing"].shape), (9, 8, 8))
        self.assertEqual(tuple(sample["target_missing"].shape), (9, 8, 8))
        self.assertEqual(MA4_MISSING_OFFSETS, (1, 2, 3, 5, 6, 7, 9, 10, 11))
        np.testing.assert_allclose(sample["coarse_missing"], sample["target_missing"], atol=1e-6)

    def test_window_model_predicts_missing_slice_stack(self) -> None:
        model = PASTNetMA4Window2p5D(input_channels=22, output_channels=9, base_channels=8, num_blocks=1)
        cond = torch.zeros((2, 22, 16, 16), dtype=torch.float32)
        cond[:, 4:13] = 0.25

        parts = model.forward_components(cond)

        self.assertEqual(tuple(parts["prediction"].shape), (2, 9, 16, 16))
        self.assertEqual(tuple(parts["residual"].shape), (2, 9, 16, 16))
        self.assertTrue(torch.allclose(parts["prediction"], cond[:, 4:13], atol=1e-6))
        self.assertTrue(torch.all(parts["confidence"] >= 0.0))
        self.assertTrue(torch.all(parts["confidence"] <= 1.0))

    def test_ma4_profiles_and_window_loss_are_trainable(self) -> None:
        self.assertEqual(PROFILES["mini_ma4w"].model_variant, "ma4w")
        self.assertEqual(PROFILES["full_ma4w_150"].epochs, 150)

        profile = PROFILES["mini_ma4w"]
        model = PASTNetMA4Window2p5D(input_channels=22, output_channels=9, base_channels=8, num_blocks=1)
        target_missing = torch.full((2, 9, 16, 16), 0.3)
        batch = {
            "cond_window": torch.zeros((2, 22, 16, 16), dtype=torch.float32),
            "coarse_missing": torch.full((2, 9, 16, 16), 0.25),
            "target_missing": target_missing,
            "anchor_window": torch.zeros((2, 4, 16, 16), dtype=torch.float32),
            "target_window": torch.zeros((2, 13, 16, 16), dtype=torch.float32),
        }
        batch["cond_window"][:, 4:13] = batch["coarse_missing"]

        loss, parts = _batch_loss_window(model, batch, profile, torch.device("cpu"))

        self.assertTrue(torch.isfinite(loss))
        self.assertIn("mse", parts)
        self.assertIn("z_smooth", parts)


if __name__ == "__main__":
    unittest.main()
