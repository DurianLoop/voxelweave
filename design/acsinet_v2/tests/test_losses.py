import sys
import unittest
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from acsinet_v2.losses import z_ncc_profile_loss


class ZNccProfileLossTest(unittest.TestCase):
    def test_is_zero_for_matching_stacks(self) -> None:
        stack = torch.tensor(
            [[[[0.0, 1.0], [2.0, 3.0]], [[1.0, 2.0], [3.0, 4.0]], [[3.0, 1.0], [0.0, 2.0]]]]
        )
        self.assertTrue(torch.isclose(z_ncc_profile_loss(stack, stack), torch.tensor(0.0), atol=1e-6))

    def test_penalizes_wrong_adjacent_similarity(self) -> None:
        target = torch.tensor(
            [[[[0.0, 1.0], [2.0, 3.0]], [[1.0, 2.0], [3.0, 4.0]], [[2.0, 3.0], [4.0, 5.0]]]]
        )
        prediction = target.clone()
        prediction[:, 1] = torch.flip(prediction[:, 1], dims=(-1,))
        self.assertGreater(z_ncc_profile_loss(prediction, target).item(), 0.05)


if __name__ == "__main__":
    unittest.main()
