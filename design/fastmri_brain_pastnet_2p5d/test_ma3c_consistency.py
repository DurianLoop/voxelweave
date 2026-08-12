from __future__ import annotations

import unittest

import numpy as np
import torch

from fastmri_brain_pastnet_2p5d.data import MA3C_MISSING_OFFSETS, build_ma3c_interval_sample
from fastmri_brain_pastnet_2p5d.model_ma import PASTNetMultiAnchor2p5D
from fastmri_brain_pastnet_2p5d.model_ma3j import PASTNetMA3Joint2p5D
from fastmri_brain_pastnet_2p5d.settings import PROFILES
from fastmri_brain_pastnet_2p5d.train import _batch_loss_ma3c, _batch_loss_ma3j


class MA3CConsistencyTests(unittest.TestCase):
    def test_interval_sample_groups_three_offsets_for_one_anchor_pair(self) -> None:
        volume = np.zeros((8, 8, 10), dtype=np.float32)
        for z in range(volume.shape[2]):
            volume[:, :, z] = z / float(volume.shape[2] - 1)

        sample = build_ma3c_interval_sample(volume, z=1, stride=4, target_shape=(8, 8))

        self.assertEqual(MA3C_MISSING_OFFSETS, (1, 2, 3))
        self.assertEqual(tuple(sample["cond_ma_stack"].shape), (3, 13, 8, 8))
        self.assertEqual(tuple(sample["coarse_stack"].shape), (3, 1, 8, 8))
        self.assertEqual(tuple(sample["target_stack"].shape), (3, 1, 8, 8))
        self.assertEqual(tuple(sample["anchor_pair"].shape), (2, 1, 8, 8))
        np.testing.assert_allclose(sample["coarse_stack"], sample["target_stack"], atol=1e-6)

    def test_ma3c_profile_and_loss_are_trainable(self) -> None:
        self.assertEqual(PROFILES["mini_ma3c"].model_variant, "ma3c")
        self.assertEqual(PROFILES["full_ma3c_150"].epochs, 150)

        profile = PROFILES["mini_ma3c"]
        model = PASTNetMultiAnchor2p5D(
            input_channels=13,
            base_channels=8,
            num_blocks=1,
            temporal_refine=True,
            refine_scale=0.3,
        )
        batch = {
            "cond_ma_stack": torch.zeros((2, 3, 13, 16, 16), dtype=torch.float32),
            "coarse_stack": torch.full((2, 3, 1, 16, 16), 0.25, dtype=torch.float32),
            "target_stack": torch.full((2, 3, 1, 16, 16), 0.3, dtype=torch.float32),
            "anchor_pair": torch.zeros((2, 2, 1, 16, 16), dtype=torch.float32),
        }
        batch["cond_ma_stack"][:, :, 4:5] = batch["coarse_stack"]

        loss, parts = _batch_loss_ma3c(model, batch, profile, torch.device("cpu"))

        self.assertTrue(torch.isfinite(loss))
        self.assertIn("mse", parts)
        self.assertIn("z_smooth", parts)
        guarded = PROFILES["full_ma3cg_150"]
        self.assertEqual(guarded.model_variant, "ma3cg")
        self.assertEqual(guarded.epochs, 150)
        self.assertTrue(guarded.freeze_backbone)
        self.assertGreater(guarded.lambda_teacher, 0.0)

    def test_ma3j_joint_head_starts_from_single_slice_backbone(self) -> None:
        profile = PROFILES["mini_ma3j"]
        model = PASTNetMA3Joint2p5D(
            input_channels=13,
            base_channels=8,
            num_blocks=1,
            refine_scale=0.3,
            joint_scale=0.2,
        )
        cond = torch.zeros((2, 3, 13, 16, 16), dtype=torch.float32)
        cond[:, :, 4] = 0.25
        cond[:, :, 5] = torch.tensor([0.25, 0.5, 0.75]).view(1, 3, 1, 1)
        batch = {
            "cond_ma_stack": cond,
            "coarse_stack": torch.full((2, 3, 1, 16, 16), 0.25, dtype=torch.float32),
            "target_stack": torch.full((2, 3, 1, 16, 16), 0.3, dtype=torch.float32),
            "anchor_pair": torch.zeros((2, 2, 1, 16, 16), dtype=torch.float32),
        }

        parts = model.forward_components(cond)
        loss, loss_parts = _batch_loss_ma3j(model, batch, profile, torch.device("cpu"))

        self.assertEqual(tuple(parts["prediction"].shape), (2, 3, 1, 16, 16))
        self.assertTrue(torch.allclose(parts["prediction"], parts["base_prediction"], atol=1e-6))
        self.assertTrue(torch.isfinite(loss))
        self.assertIn("z_smooth", loss_parts)
        joint = PROFILES["full_ma3j_150"]
        self.assertEqual(joint.model_variant, "ma3j")
        self.assertEqual(joint.epochs, 150)
        self.assertGreater(joint.lambda_teacher, 0.0)
        fixed = PROFILES["full_ma3jf_150"]
        self.assertEqual(fixed.model_variant, "ma3j")
        self.assertTrue(fixed.freeze_backbone)
        self.assertEqual(fixed.lambda_teacher, 0.0)
        self.assertGreater(fixed.joint_scale, joint.joint_scale)


if __name__ == "__main__":
    unittest.main()
