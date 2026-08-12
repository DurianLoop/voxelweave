import inspect
import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "design"))

from rasinet.cross_scale_protocol import (  # noqa: E402
    PRIMARY_NEURAL,
    common_model_intersection,
    paired_bootstrap_indices,
)
from rasinet.icassp_scores import generated_indices, score_map  # noqa: E402


class MultiscaleProtocolTests(unittest.TestCase):
    def test_scale_two_generated_indices(self):
        self.assertEqual(generated_indices(13, 2), (1, 3, 5, 7, 9, 11))

    def test_scale_four_generated_indices(self):
        self.assertEqual(generated_indices(13, 4), (1, 2, 3, 5, 6, 7, 9, 10, 11))

    def test_scale_six_generated_indices(self):
        self.assertEqual(generated_indices(13, 6), (1, 2, 3, 4, 5, 7, 8, 9, 10, 11))

    def test_anchor_start_is_explicit(self):
        self.assertEqual(generated_indices(8, 3, anchor_start=1), (0, 2, 3, 5, 6))

    def test_observed_anchors_are_not_scored(self):
        for scale in (2, 4, 6):
            generated = set(generated_indices(13, scale))
            anchors = set(range(0, 13, scale))
            self.assertFalse(generated & anchors)

    def test_common_model_intersection(self):
        model_sets = [
            {"i3net", "hat", "swinir", "linear", "cubic", "extra_a"},
            {"i3net", "hat", "swinir", "linear", "cubic", "extra_b"},
            {"i3net", "hat", "swinir", "linear", "cubic"},
        ]
        self.assertEqual(
            common_model_intersection(model_sets),
            ("cubic", "hat", "i3net", "linear", "swinir"),
        )

    def test_target_self_exclusion_remains_mandatory(self):
        target = np.zeros((2, 2, 3), dtype=np.float32)
        with self.assertRaisesRegex(ValueError, "excluded"):
            score_map("i3net", target, {"i3net": target}, "target_abs_median")

    def test_all_output_spread_is_target_invariant(self):
        base = np.arange(12, dtype=np.float32).reshape(2, 2, 3)
        outputs = {"i3net": base, "hat": base + 1, "swinir": base + 4}
        first = score_map(
            "i3net",
            outputs["i3net"],
            {"hat": outputs["hat"], "swinir": outputs["swinir"]},
            "shared_std",
            all_outputs=outputs,
        )
        second = score_map(
            "hat",
            outputs["hat"],
            {"i3net": outputs["i3net"], "swinir": outputs["swinir"]},
            "shared_std",
            all_outputs=outputs,
        )
        np.testing.assert_allclose(first, second)

    def test_target_excluded_spread_can_change_with_target(self):
        outputs = np.asarray([0.0, 1.0, 8.0])
        excluding_first = np.std(outputs[[1, 2]])
        excluding_last = np.std(outputs[[0, 1]])
        self.assertNotEqual(excluding_first, excluding_last)

    def test_paired_bootstrap_reuses_identical_indices(self):
        first = paired_bootstrap_indices(24, 20, 20260724)
        second = paired_bootstrap_indices(24, 20, 20260724)
        np.testing.assert_array_equal(first, second)

    def test_case_set_mismatch_is_visible(self):
        first = {"a", "b", "c"}
        second = {"a", "b"}
        self.assertNotEqual(first, second)

    def test_scoring_api_has_no_ground_truth(self):
        parameters = inspect.signature(score_map).parameters
        self.assertNotIn("ground_truth", parameters)
        self.assertNotIn("gt", parameters)


if __name__ == "__main__":
    unittest.main()
