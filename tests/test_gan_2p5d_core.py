import unittest

import numpy as np

from gan_2p5d.data import make_gan_sample
from gan_2p5d.inference import expected_upsampled_depth


class GAN2p5DCoreTests(unittest.TestCase):
    def test_make_gan_sample_builds_six_channel_condition_and_three_targets(self):
        volume = np.arange(8 * 8 * 8, dtype=np.float32).reshape(8, 8, 8)

        cond, target = make_gan_sample(volume, z=1, stride=4, target_shape=(8, 8))

        self.assertEqual(cond.shape, (6, 8, 8))
        self.assertEqual(target.shape, (3, 8, 8))
        np.testing.assert_allclose(cond[0], volume[:, :, 1])
        np.testing.assert_allclose(cond[1], volume[:, :, 5])
        np.testing.assert_allclose(target[0], volume[:, :, 2])
        np.testing.assert_allclose(target[1], volume[:, :, 3])
        np.testing.assert_allclose(target[2], volume[:, :, 4])
        self.assertTrue(np.allclose(cond[3], 0.25))
        self.assertTrue(np.allclose(cond[4], 0.50))
        self.assertTrue(np.allclose(cond[5], 0.75))

    def test_make_gan_sample_supports_x2_and_x6(self):
        volume = np.arange(8 * 8 * 12, dtype=np.float32).reshape(8, 8, 12)

        cond_x2, target_x2 = make_gan_sample(volume, z=2, stride=2, target_shape=(8, 8))
        self.assertEqual(cond_x2.shape, (4, 8, 8))
        self.assertEqual(target_x2.shape, (1, 8, 8))
        np.testing.assert_allclose(target_x2[0], volume[:, :, 3])
        self.assertTrue(np.allclose(cond_x2[3], 0.5))

        cond_x6, target_x6 = make_gan_sample(volume, z=2, stride=6, target_shape=(8, 8))
        self.assertEqual(cond_x6.shape, (8, 8, 8))
        self.assertEqual(target_x6.shape, (5, 8, 8))
        np.testing.assert_allclose(target_x6[0], volume[:, :, 3])
        np.testing.assert_allclose(target_x6[-1], volume[:, :, 7])
        self.assertTrue(np.allclose(cond_x6[3], 1.0 / 6.0))
        self.assertTrue(np.allclose(cond_x6[-1], 5.0 / 6.0))

    def test_expected_upsampled_depth_matches_x4_sparse_geometry(self):
        self.assertEqual(expected_upsampled_depth(sparse_depth=1, stride=4), 1)
        self.assertEqual(expected_upsampled_depth(sparse_depth=2, stride=4), 5)
        self.assertEqual(expected_upsampled_depth(sparse_depth=10, stride=4), 37)


if __name__ == "__main__":
    unittest.main()
