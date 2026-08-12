import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "design"))

from rasinet.committee_statistics import (  # noqa: E402
    bootstrap_reliability_metrics,
    leave_one_member_out_rows,
    paired_bootstrap_difference,
)


class CommitteeStatisticsTests(unittest.TestCase):
    def test_paired_bootstrap_is_deterministic_and_uses_paired_differences(self):
        first = np.asarray([4.0, 5.0, 6.0, 7.0])
        second = np.asarray([1.0, 2.0, 3.0, 4.0])

        result_a = paired_bootstrap_difference(first, second, samples=200, seed=17)
        result_b = paired_bootstrap_difference(first, second, samples=200, seed=17)

        self.assertEqual(result_a, result_b)
        self.assertAlmostEqual(result_a["mean_difference"], 3.0)
        self.assertAlmostEqual(result_a["ci95_low"], 3.0)
        self.assertAlmostEqual(result_a["ci95_high"], 3.0)

    def test_leave_one_member_out_uses_remaining_member_scores(self):
        rows = [
            {"profile": "full_test115", "case": "a", "target": "i3net", "member": "hat", "mean_member_disagreement": 1.0, "mean_abs_error": 2.0},
            {"profile": "full_test115", "case": "a", "target": "i3net", "member": "swinir", "mean_member_disagreement": 3.0, "mean_abs_error": 2.0},
            {"profile": "full_test115", "case": "a", "target": "i3net", "member": "linear", "mean_member_disagreement": 5.0, "mean_abs_error": 2.0},
            {"profile": "full_test115", "case": "b", "target": "i3net", "member": "hat", "mean_member_disagreement": 2.0, "mean_abs_error": 4.0},
            {"profile": "full_test115", "case": "b", "target": "i3net", "member": "swinir", "mean_member_disagreement": 4.0, "mean_abs_error": 4.0},
            {"profile": "full_test115", "case": "b", "target": "i3net", "member": "linear", "mean_member_disagreement": 8.0, "mean_abs_error": 4.0},
        ]

        output = leave_one_member_out_rows(rows)

        leave_hat = [row for row in output if row["excluded_member"] == "hat"]
        self.assertEqual([row["case"] for row in leave_hat], ["a", "b"])
        self.assertEqual([row["committee_score"] for row in leave_hat], [4.0, 6.0])
        self.assertTrue(all("hat" not in row["committee_members"].split(";") for row in leave_hat))

    def test_leave_one_member_out_rejects_incomplete_case_membership(self):
        rows = [
            {"profile": "p", "case": "a", "target": "m", "member": "x", "mean_member_disagreement": 1.0, "mean_abs_error": 1.0},
            {"profile": "p", "case": "a", "target": "m", "member": "y", "mean_member_disagreement": 2.0, "mean_abs_error": 1.0},
            {"profile": "p", "case": "b", "target": "m", "member": "x", "mean_member_disagreement": 3.0, "mean_abs_error": 2.0},
        ]

        with self.assertRaisesRegex(ValueError, "membership"):
            leave_one_member_out_rows(rows)

    def test_bootstrap_reliability_metrics_preserves_perfect_ranking(self):
        result = bootstrap_reliability_metrics(
            errors=np.asarray([1.0, 2.0, 3.0, 4.0]),
            scores=np.asarray([1.0, 2.0, 3.0, 4.0]),
            pixel_correlations=np.asarray([0.5, 0.5, 0.5, 0.5]),
            samples=200,
            seed=9,
        )

        self.assertAlmostEqual(result["pixel_corr_mean"]["point"], 0.5)
        self.assertAlmostEqual(result["pixel_corr_mean"]["ci95_low"], 0.5)
        self.assertAlmostEqual(result["case_spearman"]["point"], 1.0)
        self.assertAlmostEqual(result["normalized_aurc"]["point"], 0.0)


if __name__ == "__main__":
    unittest.main()
