import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "design"))

from rasinet.check_paper_consistency import (  # noqa: E402
    check_latex_log,
    check_main_table_values,
    check_manuscript_claims,
)


class PaperConsistencyTests(unittest.TestCase):
    def test_mismatched_table_value_is_reported(self):
        rows = [
            {
                "Dataset": "IXI",
                "Target": "I3Net",
                "Cases": "115",
                "PixelCorrFG": "0.4567",
                "CaseSpearman": "0.6543",
                "NormalizedAURC": "0.2345",
                "RRR50": "0.321",
            }
        ]
        tex = "IXI & I3Net & 115 & 0.111 & 0.654 & 0.234 / 32.1\\%"

        errors = check_main_table_values(rows, tex)

        self.assertTrue(any("0.457" in error for error in errors))

    def test_smoke_and_mini_claims_are_rejected(self):
        errors = check_manuscript_claims("Results on the smoke profile were strong.")

        self.assertTrue(any("smoke" in error.lower() for error in errors))

    def test_explicit_probability_boundary_is_allowed(self):
        errors = check_manuscript_claims("The score is not a calibrated probability.")

        self.assertEqual(errors, [])

    def test_clean_latex_log_has_no_errors(self):
        clean = "Output written on main.pdf (8 pages)."
        dirty = "LaTeX Warning: Citation `x' on page 1 undefined."
        overflow = r"Overfull \hbox (12.0pt too wide)"

        self.assertEqual(check_latex_log(clean), [])
        self.assertTrue(check_latex_log(dirty))
        self.assertTrue(check_latex_log(overflow))


if __name__ == "__main__":
    unittest.main()
