"""Reuse the bounded JATS acquisition code under new filenames, preserving source SHA."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    source=ROOT/'fetch_global_local_task_fulltexts_2026_10_03.py'
    target=ROOT/'fetch_task_loss_followup_fulltext_2026_10_03.py'
    assert not target.exists()
    text=source.read_text(encoding='utf-8')
    text=text.replace('Acquire two selected primary JATS bodies; retain front-only failures.',
                      'Acquire selected loss primary JATS body; retain front-only failures.')
    text=text.replace('global_local_task_fulltexts_2026-10-03','task_loss_followup_fulltext_2026-10-03')
    text=text.replace("PAPERS=[('vs_cascade','PMC11903922','10.1002/lary.31979'),('olfactory','PMC8473894','10.1016/j.neuroimage.2021.118464')]",
                      "PAPERS=[('unified_focal','PMC8785124','10.1016/j.compmedimag.2021.102026')]")
    text=text.replace('2026-10-03_global_local_task_selection.md','2026-10-03_task_loss_followup_selection.md')
    target.write_text(text,encoding='utf-8')
    (ROOT/'source_cache/task_loss_followup_search_2026-10-03/fetch_generation.json').write_text(
        json.dumps(dict(source=source.name,source_sha256=sha(source),target=target.name,
                        target_sha256=sha(target),generator_sha256=sha(__file__)),indent=2)+'\n',encoding='utf-8')
    print('Prepared one-paper JATS fetcher, no live training edits.')
if __name__=='__main__':main()
