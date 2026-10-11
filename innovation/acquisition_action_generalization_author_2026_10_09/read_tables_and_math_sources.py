"""Literal structured tables; inspect missing rendered math provenance without inference."""
import sys,json,gzip,collections,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent/'primary_xml_attempt01'
if sys.argv[1]=='tables':
    key=sys.argv[2];tables=json.loads(gzip.decompress((HERE/f'{key}.tables.json.gz').read_bytes()))
    for table in tables:
        print('TABLE '+str(table['id']))
        for row in table['rows']:print(json.dumps(row,ensure_ascii=False))
else:
    key=sys.argv[2];root=ET.fromstring(gzip.decompress((HERE/f'{key}.xml.gz').read_bytes()))
    wanted={'tex-math','math','inline-formula','disp-formula','inline-graphic','alt-text'}
    counts=collections.Counter(e.tag.rsplit('}',1)[-1] for e in root.iter());print(json.dumps({k:counts[k] for k in wanted}))
    for e in root.iter():
        kind=e.tag.rsplit('}',1)[-1]
        if kind in ['tex-math','disp-formula']:print(ET.tostring(e,encoding='unicode'))
        if kind=='supplementary-material':print(ET.tostring(e,encoding='unicode'))
