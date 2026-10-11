"""Preserve Windows source CRLF in exact byte replay; retain failed first attempt."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=(HERE/'qualify_shared_journal_encoding.py').read_text(encoding='utf-8')
replacements=[
 ("shared_journal_attempt01","shared_journal_attempt02"),
 ("payload=dict(format_version=1,record_key_order=keys,shared=shared,branch=branch)",
  "payload=dict(format_version=2,record_key_order=keys,shared=shared,branch=branch,newline_by_branch={n:'\\r\\n' if b.endswith(b'\\r\\n') else '\\n' for n,b in old.items()})"),
 ("raw=(''.join(json.dumps(x,separators=(',',':'))+'\\n' for x in recovered)).encode()",
  "raw=(''.join(json.dumps(x,separators=(',',':'))+p['newline_by_branch'][name] for x in recovered)).encode()")
]
for old,new in replacements:
 assert source.count(old)==1,old
 source=source.replace(old,new)
if __name__=='__main__':exec(compile(source,str(HERE/'qualify_shared_journal_encoding.py'),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
