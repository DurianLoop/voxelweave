"""Repair own delta-archive field collision and use separate V2 output names."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE/'record_and_append.py'
source = ORIGINAL.read_text(encoding='utf-8')
replacements = [
    ("['APPEND_INDEX.json','APPEND_PROOF.json','EXECUTION_LEDGER.json']",
     "['APPEND_INDEX_V2.json','APPEND_PROOF_V2.json','EXECUTION_LEDGER_V2.json']"),
    ("verified.append(dict(document=path.relative_to(ROOT).as_posix(), **binding))",
     "verified.append(dict(binding_document=path.relative_to(ROOT).as_posix(), source_binding=binding))")
]
for old, new in replacements:
    assert source.count(old)==1
    source = source.replace(old,new)
if __name__=='__main__':
    exec(compile(source,str(ORIGINAL),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
