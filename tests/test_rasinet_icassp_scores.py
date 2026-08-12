import inspect
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "design"))

from rasinet.committee_reliability import risk_coverage_summary  # noqa: E402
from rasinet.icassp_scores import (  # noqa: E402
    deployment_mask,
    examination_score,
    generated_indices,
    normalize_output,
    score_map,
)
from rasinet.run_reliability_evaluation import _file_set, _median_maps  # noqa: E402
from rasinet.icassp_statistics import paired_case_bootstrap, ranking_metrics  # noqa: E402


class ICASSPScoreTests(unittest.TestCase):
    def setUp(self):
        self.target = np.arange(27, dtype=np.float32).reshape(3, 3, 3)
        self.member = self.target + 2.0

    def test_target_identity_is_excluded_by_name(self):
        with self.assertRaisesRegex(ValueError, "excluded"):
            score_map("target", self.target, {"target": self.member}, "target_abs_median")

    def test_scoring_api_has_no_ground_truth_argument(self):
        parameters = inspect.signature(score_map).parameters
        self.assertNotIn("ground_truth", parameters)
        self.assertNotIn("gt", parameters)

    def test_committee_size_one_median_is_absolute_difference(self):
        actual = score_map("target", self.target, {"peer": self.member}, "target_abs_median")
        np.testing.assert_allclose(actual, 2.0)

    def test_small_committee_median_specialization_is_exact(self):
        rng = np.random.default_rng(7)
        maps = [rng.normal(size=(5, 4, 3)).astype(np.float32) for _ in range(5)]
        for size in range(1, 6):
            expected = np.median(np.stack(maps[:size], axis=0), axis=0)
            np.testing.assert_allclose(_median_maps(maps[:size]), expected, rtol=1e-6, atol=1e-6)

    def test_normalizations_are_finite_and_ground_truth_free(self):
        for mode in ("raw", "percentile_p1_p99", "robust_median_iqr", "minmax"):
            actual = normalize_output(self.target, mode)
            self.assertTrue(np.isfinite(actual).all())

    def test_deployment_masks_are_nonempty(self):
        committee = {"peer": self.member}
        for mode in ("target_0.005", "target_0.01", "target_0.02", "target_0.05", "committee_union", "committee_intersection", "committee_median", "input_derived"):
            mask = deployment_mask(self.target, committee, mode, factor=2)
            self.assertTrue(np.any(mask))

    def test_ground_truth_mask_is_not_a_deployment_mask(self):
        with self.assertRaisesRegex(ValueError, "unknown mask mode"):
            deployment_mask(
                self.target,
                {"peer": self.member},
                "ground_truth_offline",
                factor=2,
            )

    def test_case_ordering_does_not_change_summary(self):
        errors = np.asarray([1.0, 4.0, 2.0, 3.0])
        scores = np.asarray([1.1, 3.9, 2.1, 3.2])
        first = risk_coverage_summary(errors, scores)
        order = np.asarray([2, 0, 3, 1])
        second = risk_coverage_summary(errors[order], scores[order])
        self.assertAlmostEqual(float(first["normalized_aurc"]), float(second["normalized_aurc"]))

    def test_random_rankings_have_expected_normalized_aurc_near_one(self):
        errors = np.linspace(1.0, 20.0, 20)
        rng = np.random.default_rng(20260715)
        values = []
        for _ in range(1000):
            values.append(float(risk_coverage_summary(errors, rng.permutation(errors))["normalized_aurc"]))
        self.assertAlmostEqual(float(np.mean(values)), 1.0, delta=0.08)

    def test_oracle_ranking_has_zero_normalized_aurc(self):
        errors = np.asarray([4.0, 1.0, 3.0, 2.0])
        result = risk_coverage_summary(errors, errors)
        self.assertAlmostEqual(float(result["normalized_aurc"]), 0.0)

    def test_top_decile_failure_metrics_detect_perfect_ranking(self):
        errors = np.arange(1.0, 21.0)
        metrics = ranking_metrics(errors, errors)
        self.assertAlmostEqual(metrics["failure_auroc"], 1.0)
        self.assertAlmostEqual(metrics["failure_auprc"], 1.0)

    def test_foreground_and_all_pixel_bootstrap_share_case_resamples(self):
        errors = np.asarray([1.0, 2.0, 3.0, 4.0])
        scores = errors.copy()
        foreground = np.asarray([0.1, 0.2, 0.3, 0.4])
        all_pixel = np.asarray([0.4, 0.3, 0.2, 0.1])
        intervals, samples = paired_case_bootstrap(
            errors,
            scores,
            foreground,
            samples=20,
            seed=7,
            all_pixel_correlations=all_pixel,
        )
        self.assertIn("all_pixel_fisher_z_mean", intervals)
        self.assertTrue(all("all_pixel_fisher_z_mean" in row for row in samples))

    def test_missing_case_directory_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            with self.assertRaises(FileNotFoundError):
                _file_set(missing, "diff_")

    def test_generated_slice_and_aggregation_contract(self):
        indices = generated_indices(5, 2)
        self.assertEqual(indices, (1, 3))
        score = np.ones((3, 3, 5), dtype=np.float32)
        mask = np.ones_like(score, dtype=bool)
        self.assertEqual(examination_score(score, mask, indices), 1.0)


if __name__ == "__main__":
    unittest.main()
