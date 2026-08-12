import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "design"))

from rasinet.committee_reliability import (  # noqa: E402
    committee_dispersion,
    risk_coverage_summary,
    target_to_committee_disagreement,
)


class CommitteeReliabilityTests(unittest.TestCase):
    def test_target_to_committee_uses_median_absolute_difference(self):
        target = np.asarray([[2.0, 4.0], [6.0, 8.0]], dtype=np.float32)
        committee = [
            np.asarray([[1.0, 2.0], [7.0, 8.0]], dtype=np.float32),
            np.asarray([[5.0, 5.0], [3.0, 10.0]], dtype=np.float32),
            np.asarray([[2.0, 8.0], [8.0, 4.0]], dtype=np.float32),
        ]

        actual = target_to_committee_disagreement(target, committee)

        expected = np.asarray([[1.0, 2.0], [2.0, 2.0]], dtype=np.float32)
        np.testing.assert_allclose(actual, expected)

    def test_target_prediction_is_not_accepted_as_a_committee_member(self):
        target = np.ones((2, 2), dtype=np.float32)

        with self.assertRaisesRegex(ValueError, "target prediction"):
            target_to_committee_disagreement(target, [target, np.zeros_like(target)])

    def test_committee_dispersion_is_shared_standard_deviation(self):
        committee = [
            np.zeros((2, 2), dtype=np.float32),
            np.full((2, 2), 2.0, dtype=np.float32),
        ]

        actual = committee_dispersion(committee)

        np.testing.assert_allclose(actual, np.ones((2, 2), dtype=np.float32))

    def test_perfect_ranking_matches_oracle_and_beats_random(self):
        errors = np.asarray([4.0, 1.0, 3.0, 2.0], dtype=np.float64)
        scores = errors.copy()

        summary = risk_coverage_summary(errors, scores, coverages=(0.25, 0.5, 0.75))

        np.testing.assert_allclose(summary["risk"], summary["oracle_risk"])
        self.assertAlmostEqual(float(summary["excess_aurc"]), 0.0)
        self.assertAlmostEqual(float(summary["normalized_aurc"]), 0.0)
        self.assertAlmostEqual(float(summary["risk_at_50"]), 1.5)
        self.assertGreater(float(summary["relative_risk_reduction_at_50"]), 0.0)

    def test_shapes_and_finite_values_are_validated(self):
        target = np.zeros((2, 2), dtype=np.float32)

        with self.assertRaisesRegex(ValueError, "same shape"):
            target_to_committee_disagreement(target, [np.zeros((3, 3), dtype=np.float32)])
        with self.assertRaisesRegex(ValueError, "finite"):
            risk_coverage_summary(
                np.asarray([1.0, np.nan]),
                np.asarray([1.0, 2.0]),
                coverages=(0.5,),
            )


if __name__ == "__main__":
    unittest.main()
