"""Literal indexed article text, compact framing only."""
import sys,json,gzip
from pathlib import Path
HERE=Path(__file__).resolve().parent
key=sys.argv[1];start=int(sys.argv[2]);stop=int(sys.argv[3]);assert key in ['dgtta','missing','peil']
rows=json.loads(gzip.decompress((HERE/'primary_xml_attempt01'/f'{key}.blocks.json.gz').read_bytes()))
assert 0<=start<=stop<=len(rows)
for row in rows[start:stop]:print(str(row['index'])+' ['+row['kind']+'] '+row['text'])
