"""Check reported table aggregates against view means, without inferring author error."""
import hashlib,json,sys,xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path
from datetime import datetime,timezone
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent/'source_cache/task_adaptation_direct_fulltexts_2026-10-03'
p=ROOT/'multiplanar_fibroid_attempt_01.xml';tree=ET.fromstring(p.read_bytes())
def text(x):return ' '.join(''.join(x.itertext()).split())
tables=[]
for table in tree.findall('.//table-wrap'):
    tables.append(dict(id=table.get('id'),label=text(table.find('label')),rows=[[text(c) for c in row if c.tag in ('td','th')] for row in table.findall('.//tr')]))
rows=[]
for table in tables:
    if table['label']!='Table 1':continue
    for cells in table['rows']:
        if len(cells)<6 or cells[0]=='Method':continue
        try:
            views=[Decimal(c.split('±')[0].strip()) for c in cells[1:4]];reported=Decimal(cells[4].split('±')[0].strip())
        except Exception:continue
        simple=sum(views)/3;delta=reported-simple
        rows.append(dict(method=cells[0],transverse=str(views[0]),sagittal=str(views[1]),coronal=str(views[2]),reported_mDSC=str(reported),equal_view_mean=str(simple),reported_minus_equal_view_mean=str(delta),rounding_alone_explains=abs(delta)<=Decimal('0.1')))
r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),raw_xml_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
       complete=len(rows)==7,tables=tables,table1_comparisons=rows,
       interpretation='These are arithmetic comparisons, not independent reproduction or proof of author error. Unequal weighting or another aggregation definition could differ; exact aggregation and underlying predictions remain unavailable.',
       source_parameters_reproduced=False,new_neural_forwards=0,publication_claim_confirmed=False)
out=ROOT/'fibroid_table_aggregate_audit_attempt_01.json';assert not out.exists();out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(complete=r['complete'],table1_comparisons=rows),ensure_ascii=False))
