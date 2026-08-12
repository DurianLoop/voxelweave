import unittest

import numpy as np

from rasinet.run_candidate_optimization import committee_members, generated, maps_for


class OptimizationProtocolTests(unittest.TestCase):
    def test_target_is_excluded_from_every_committee(self):
        available = {"i3net", "hat", "swinir", "linear", "cubic", "saint"}
        for kind in ("frozen_primary", "full_universal", "neural_only",
                     "analytical_only", "analytical_anchor", "low_cost"):
            members = committee_members(kind, "i3net", available, ("i3net", "saint"))
            self.assertNotIn("i3net", members)

    def test_score_maps_require_predictions_not_ground_truth(self):
        target = np.arange(24, dtype=np.float32).reshape(2, 3, 4)
        committee = {"peer": target + 2, "linear": target - 1}
        maps = maps_for(target, committee, {"target": target, **committee})
        self.assertTrue(np.allclose(maps["median"], 1.5))
        self.assertEqual(set(maps).issuperset({"median", "mean", "center_median"}), True)

    def test_generated_support_excludes_observed_anchors(self):
        self.assertEqual(generated(8, 4).tolist(), [1, 2, 3, 5, 6, 7])

    def test_single_member_median_is_defined(self):
        target = np.zeros((2, 2, 2), dtype=np.float32)
        peer = np.ones_like(target)
        maps = maps_for(target, {"peer": peer}, {"target": target, "peer": peer})
        self.assertTrue(np.allclose(maps["median"], 1.0))


if __name__ == "__main__":
    unittest.main()
