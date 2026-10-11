"""Make a new bounded fetcher, keeping previous fetched bodies untouched."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
old=ROOT/'fetch_bandwidth_consistency_fulltexts_2026_10_03.py'
new=ROOT/'fetch_phase_direct_neighbours_2026_10_03.py'
assert not new.exists()
s=old.read_text(encoding='utf-8')
s=s.replace('Retrieve three DOI-authenticated public bodies, record failures separately.','Retrieve two DOI-authenticated direct-neighbour bodies, preserve failures.')
s=s.replace('source_cache/bandwidth_consistency_fulltexts_2026-10-03','source_cache/phase_direct_neighbour_fulltexts_2026-10-03')
start=s.index('PAPERS=');end=s.index('\ndef sha',start)
s=s[:start]+"PAPERS=[('dstripe','PMC8566280','10.1016/j.media.2021.102255'),('stress','PMC10129053','10.1007/978-3-030-87234-2_19')]"+s[end:]
s=s.replace('2026-10-03_bandwidth_consistency_fulltext_selection.md','2026-10-03_phase_direct_neighbour_fulltext_selection.md')
new.write_text(s,encoding='utf-8');print(new)
