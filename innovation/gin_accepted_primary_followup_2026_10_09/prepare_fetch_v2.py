"""Follow explicit public UI REST content link after download-route HTTP405."""
import gzip,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
old=HERE/'fetch_and_extract_v1.py';before=hashlib.sha256(old.read_bytes()).hexdigest()
receipt=json.loads((HERE/'accepted_pdf_attempt01/receipt.json').read_text('utf-8'))
assert not receipt['complete'] and any('HTTP Error 405' in v for v in receipt['errors']) and not receipt.get('pdf')
source=ROOT/'six_resolution_training_preparation_2026_10_09/gin_imperial_landing_attempt02/landing.html.gz'
html=gzip.decompress(source.read_bytes()).decode('utf-8')
url='https://spiral.imperial.ac.uk/server/api/core/bitstreams/9f1f03f2-fac1-4402-8045-9f9455fdac2d/content'
assert url in html
text=old.read_text('utf-8').replace('accepted_pdf_attempt01','accepted_pdf_attempt02').replace("HERE/'PROTOCOL.md'","HERE/'PROTOCOL_V2.md'")
text=text.replace("    r['requested_url']=url", "    visible_ui=bind(landing['saved_html'])\n    ui=gzip.decompress(visible_ui.read_bytes()).decode('utf-8')\n    url='"+url+"'\n    assert url in ui\n    r['followed_explicit_public_UI_REST_content_link']=True\n    r['requested_url']=url")
text=text.replace('import sys,json,time,ssl,urllib.request,traceback','import sys,json,time,ssl,urllib.request,traceback,gzip')
text=text.replace("    for index in range(len(doc)):",
                  "    r['source_bindings'].extend(entry(p) for p in (HERE/'fetch_and_extract_v1.py',HERE/'accepted_pdf_attempt01/receipt.json',HERE/'prepare_fetch_v2.py',visible_ui))\n    for index in range(len(doc)):")
compile(text,'fetch_and_extract_v2.py','exec')
with (HERE/'fetch_and_extract_v2.py').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
assert hashlib.sha256(old.read_bytes()).hexdigest()==before
print(json.dumps(dict(complete=True,v1_unchanged_sha256=before,content_url_explicitly_present_in_public_UI=True)))
