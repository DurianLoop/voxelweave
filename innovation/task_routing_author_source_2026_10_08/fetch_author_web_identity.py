"""Read the author's actual paper-linked public repository and its pinned README only."""
import sys,json,re
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'identity_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
sys.path.insert(0,str(ROOT/'realized_false_positive_task_prior_art_2026_10_08'))
import fetch_mirto_web_fallback as fetcher
class PageParser(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.scripts=[];self.collect=False;self.parts=[]
    def handle_starttag(self,tag,attrs):
        data=dict(attrs)
        if tag=='a' and data.get('href'):self.links.append(data['href'])
        if tag=='script' and data.get('type')=='application/json':self.collect=True;self.parts=[]
    def handle_data(self,data):
        if self.collect:self.parts.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.collect:
            self.collect=False
            try:self.scripts.append(json.loads(''.join(self.parts)))
            except json.JSONDecodeError:pass
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.resource_guard();OUT.mkdir(exist_ok=False);fetcher.OUT=OUT
    rows=[fetcher.get('repository_web','https://github.com/Tillyhere/TADT','html')]
    identity={};parser=PageParser()
    if rows[0]['complete']:
        parser.feed((ROOT/rows[0]['response_binding']['path']).read_text(encoding='utf-8'))
        payload=next((s['payload'] for s in parser.scripts if isinstance(s,dict) and isinstance(s.get('payload'),dict) and 'codeViewRepoRoute' in s['payload']),None)
        assert payload is not None,'Expected GitHub code page identity payload absent'
        route=payload['codeViewRepoRoute'];ref=route['refInfo'];oid=ref['currentOid'];assert re.fullmatch(r'[a-f0-9]{40}',oid)
        identity=dict(paper_repo='Tillyhere/TADT',current_commit=oid,ref_name=ref['name'],
            root_tree_items=route['tree']['items'],repo_metadata=route.get('repo',{}),complete_recursive_tree_verified=False)
        client.base.new(OUT/'visible_identity.json',identity)
        files=[v['path'] for v in identity['root_tree_items'] if v['contentType']=='file' and v['name'].lower()=='readme.md'];assert len(files)==1
        rows.append(fetcher.get('README','https://raw.githubusercontent.com/Tillyhere/TADT/'+oid+'/'+files[0],'source.txt'))
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
        errors=[e for r in rows for e in r['errors']],records=rows,identity=identity,
        source_bindings=[client.base.entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',
            ROOT/'realized_false_positive_task_prior_art_2026_10_08/fetch_mirto_web_fallback.py',
            ROOT/'task_routing_and_reconstruction_shift_prior_art_2026_10_08/tadt_text_attempt05/tadt_page001.txt']],
        author_README_read=False,author_source_files_read=0,author_code_executed=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        resource_snapshot=client.resource_guard())
    client.base.new(OUT/'receipt.json',q)
    print(json.dumps(dict(complete=q['complete'],errors=q['errors'],records=rows,identity=identity),ensure_ascii=False),flush=True)
    return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
