"""Use the project's existing read-only portable PDF reader, preserving failed V1."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORTABLE = HERE.parent / 'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'
assert PORTABLE.is_dir()
sys.path.insert(0, str(PORTABLE))
import prepare_primary as original

original.OUT = HERE / 'primary_attempt02'
if __name__ == '__main__':
    raise SystemExit(original.main())
