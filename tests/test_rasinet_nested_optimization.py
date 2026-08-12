import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from rasinet.cross_scale_physical import matches
from rasinet.nested_analysis import relative, transform
from rasinet.nested_precompute import common_metrics, generated, threshold_mask
from rasinet.nested_selection import candidate_subsets, score_from_matrix


class NestedOptimizationTests(unittest.TestCase):
    OUTPUT=Path(__file__).resolve().parents[1]/"design"/"rasinet"/"outputs"/"nested_optimization"
    def test_common_support_is_prediction_independent(self):
        gt=np.zeros((3,3,4),dtype=np.float32); gt[1,1,1:]=10
        indices=generated(4,2); support=threshold_mask(gt,indices)
        a=common_metrics(gt+1,gt,support,indices)
        b=common_metrics(gt+2,gt,support,indices)
        self.assertAlmostEqual(a["mae"],1.0)
        self.assertAlmostEqual(b["mae"],2.0)

    def test_candidate_subsets_exclude_target(self):
        for subset in candidate_subsets(["a","b","c","linear"],"b"):
            self.assertNotIn("b",subset)

    def test_trim_max_removes_casewise_outlier(self):
        matrix=np.asarray([[1.,2.,100.],[2.,3.,4.]])
        score=score_from_matrix(matrix,[0,1,2],np.ones(3)/3,"trim_max")
        np.testing.assert_allclose(score,[1.5,2.5])

    def test_size_one_committee_is_well_defined(self):
        matrix=np.asarray([[1.25],[3.5]])
        score=score_from_matrix(matrix,[0],np.ones(1),"uniform")
        np.testing.assert_allclose(score,[1.25,3.5])

    def test_target_calibration_uses_training_distribution(self):
        train=np.asarray([1.,2.,3.,4.]); test=np.asarray([.5,2.5,5.])
        np.testing.assert_allclose(transform(train,test,"empirical_cdf"),[0,.5,1.])

    def test_relative_score_centers_each_examination(self):
        values=np.asarray([[1.,2.,5.],[4.,4.,8.]])
        centered=relative(values,"centered")
        np.testing.assert_allclose(np.median(centered,axis=1),0.)

    def test_physical_plane_matching_ignores_array_depth(self):
        a={1:np.asarray([0.,0.,5.]),3:np.asarray([0.,0.,15.])}
        b={1:np.asarray([0.,0.,5.])}
        result=matches(a,b)
        self.assertEqual([(x[0],x[1]) for x in result],[(1,1)])

    def test_outer_manifest_is_self_excluded_and_label_free(self):
        paths=[self.OUTPUT/"ningxia_nested_selection_manifest.csv",
               self.OUTPUT/"ningxia_robust_selection_manifest.csv"]
        manifest=pd.concat([pd.read_csv(path) for path in paths],ignore_index=True)
        self.assertFalse(manifest.selection_used_outer_labels.astype(bool).any())
        self.assertTrue(all(row.target_model not in row.members.split(";") for row in manifest.itertuples()))

    def test_outer_profiles_have_all_cases(self):
        predictions=pd.concat([
            pd.read_csv(self.OUTPUT/"ningxia_nested_predictions.csv"),
            pd.read_csv(self.OUTPUT/"ningxia_robust_predictions.csv")],ignore_index=True)
        counts=predictions.groupby(["method","scale","target_model"]).case.nunique()
        self.assertTrue(counts.eq(22).all())

    def test_profile_aligned_bootstrap_has_fixed_replicates(self):
        paired=pd.read_csv(self.OUTPUT/"nested_paired_bootstrap.csv")
        counts=paired.groupby(["level","key","method","comparator"]).replicate.nunique()
        self.assertTrue(counts.eq(2000).all())

    def test_physical_audit_matches_generated_planes(self):
        pairs=pd.read_csv(self.OUTPUT/"cross_scale_physical_pair_scores.csv")
        self.assertTrue(pairs.status.eq("matched_physical_planes").all())
        self.assertTrue(pairs.matched_generated_planes.gt(0).all())


if __name__=="__main__": unittest.main()
