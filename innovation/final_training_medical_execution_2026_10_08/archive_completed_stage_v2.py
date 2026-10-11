"""Retain first failure; classify old non-evidence document links instead of asserting availability."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=(HERE/'archive_completed_stage.py').read_text(encoding='utf-8')
replacements=[
    ("indexpath=HERE/'APPEND_INDEX.json';proofpath=HERE/'APPEND_PROOF.json'", "indexpath=HERE/'APPEND_INDEX_V2.json';proofpath=HERE/'APPEND_PROOF_V2.json'"),
    ("verified=[];scanned=set();links=[]", "verified=[];scanned=set();links=[];unresolved_links=[]"),
    ("target=(p.parent/raw.split('#',1)[0]).resolve();assert target.exists() and target.is_relative_to(ROOT),raw",
     "target=(p.parent/raw.split('#',1)[0]).resolve()\n                    if not target.exists() or not target.is_relative_to(ROOT):\n                        assert not p.is_relative_to(HERE) and not p.is_relative_to(pilot), 'New stage link must resolve: '+raw\n                        unresolved_links.append(dict(document=p.relative_to(ROOT).as_posix(),raw_link=raw,exists=target.exists(),within_innovation=target.is_relative_to(ROOT),reason='Retained legacy project reference, not a bound research-evidence file'));continue"),
    ("source_bindings_verified=verified,local_links_verified=links,", "source_bindings_verified=verified,local_links_verified=links,retained_legacy_links_not_verified=unresolved_links,"),
    ("new_evidence_hashes_verified=True,newly_bound_files=len(new),", "new_evidence_hashes_verified=True,newly_bound_files=len(new),retained_legacy_links_not_verified=len(unresolved_links),")
]
for old,new in replacements:
    assert source.count(old)==1,old
    source=source.replace(old,new)
if __name__=='__main__':exec(compile(source,str(HERE/'archive_completed_stage.py'),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
