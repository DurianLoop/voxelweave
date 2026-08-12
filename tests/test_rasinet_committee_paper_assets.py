import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "design"))

from rasinet.committee_paper_assets import (  # noqa: E402
    asset_source_manifest,
    require_columns,
)


class CommitteePaperAssetTests(unittest.TestCase):
    def test_require_columns_rejects_missing_input_fields(self):
        rows = [{"profile": "full_test115", "target": "i3net"}]

        with self.assertRaisesRegex(ValueError, "normalized_aurc"):
            require_columns(rows, {"profile", "target", "normalized_aurc"}, "summary")

    def test_source_manifest_lists_every_numeric_artifact_input(self):
        sources = {
            "main_table": Path("summary_committee.csv"),
            "composition": Path("committee_composition.csv"),
            "risk_figure": Path("risk_coverage_committee.csv"),
        }

        manifest = asset_source_manifest(sources)

        self.assertEqual(len(manifest), 3)
        self.assertEqual(manifest[0]["artifact"], "composition")
        self.assertEqual(manifest[-1]["source_csv"], "risk_coverage_committee.csv")


if __name__ == "__main__":
    unittest.main()
