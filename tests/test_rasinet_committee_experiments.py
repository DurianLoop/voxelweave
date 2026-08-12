import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "design"))

from rasinet.committee_experiments import (  # noqa: E402
    committee_member_names,
    profile_sources,
)


class CommitteeExperimentTests(unittest.TestCase):
    def test_profile_sources_follow_split_repository_roots(self):
        ixi = profile_sources(ROOT, "ixi")
        fastmri = profile_sources(ROOT, "fastmri")
        ningxia = profile_sources(ROOT, "ningxia")

        self.assertEqual([source.name for source in ixi], ["i3net", "hat", "swinir", "acsinet"])
        self.assertEqual(ixi[0].root, ROOT / "baseline" / "ixi_i3net")
        self.assertEqual(ixi[-1].root, ROOT / "design" / "acsinet")
        self.assertEqual(fastmri[1].root, ROOT / "baseline" / "fastmri_brain_hat_2p5d")
        self.assertEqual(ningxia[2].root, ROOT / "baseline" / "ningxia_t2_swinir_2p5d_cv")

    def test_target_is_excluded_from_all_and_neural_committees(self):
        predictions = ["i3net", "hat", "swinir", "linear", "cubic"]

        all_members = committee_member_names("hat", predictions, mode="all")
        neural_members = committee_member_names("hat", predictions, mode="neural")

        self.assertEqual(all_members, ["i3net", "swinir", "linear", "cubic"])
        self.assertEqual(neural_members, ["i3net", "swinir"])
        self.assertNotIn("hat", all_members)

    def test_analytic_and_leave_one_out_membership(self):
        predictions = ["i3net", "hat", "swinir", "linear", "cubic"]

        analytic = committee_member_names("swinir", predictions, mode="analytic")
        leave_hat_out = committee_member_names(
            "swinir",
            predictions,
            mode="all",
            excluded_member="hat",
        )

        self.assertEqual(analytic, ["linear", "cubic"])
        self.assertEqual(leave_hat_out, ["i3net", "linear", "cubic"])

    def test_empty_committee_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            committee_member_names("i3net", ["i3net"], mode="neural")


if __name__ == "__main__":
    unittest.main()
