"""Read-only original HTML extraction, executed with existing base-environment BeautifulSoup."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'literature/source_cache/3d_context_supervision_2026-10-07'
record = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), papers=[], actual_reading_completed=False)
for name in ('3d_unet_sparse_annotation','deepmedic_multiscale'):
    src = OUT/(name+'_html_attempt01.response')
    soup = BeautifulSoup(src.read_bytes(), 'html.parser')
    article = soup.find('article'); assert article is not None
    blocks = []
    for node in article.find_all(['h1','h2','h3','h4','p','table','figure','li']):
        # Preserve each table/figure as one block, without duplicating nested paragraphs/list items.
        if node.find_parent(['p','table','figure','li']) is not None: continue
        for annotation in node.find_all('annotation'): annotation.decompose()
        text = ' '.join(node.get_text(' ',strip=True).split())
        if text: blocks.append(dict(index=len(blocks), tag=node.name, id=node.get('id'), text=text))
    assert len(blocks) >= 20
    dest = OUT/(name+'_blocks.json'); textpath = OUT/(name+'_maintext.txt')
    with dest.open('x',encoding='utf-8') as f: json.dump(blocks,f,ensure_ascii=False,indent=2); f.write('\n')
    with textpath.open('x',encoding='utf-8') as f:
        f.write('\n\n'.join('[%04d %s] %s' % (b['index'],b['tag'],b['text']) for b in blocks)+'\n')
    record['papers'].append(dict(name=name,title=soup.title.get_text(),source_file=src.name,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                                 blocks=len(blocks),characters=sum(len(b['text']) for b in blocks),block_file=dest.name,
                                 block_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),text_file=textpath.name,
                                 text_sha256=hashlib.sha256(textpath.read_bytes()).hexdigest(),actual_reading_completed=False))
with (OUT/'extraction_attempt01.json').open('x',encoding='utf-8') as f: json.dump(record,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps(record,ensure_ascii=False))
