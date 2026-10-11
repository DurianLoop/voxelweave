"""Construct a separate transport recovery from preserved failed source."""
import sys,ast,difflib,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');original=HERE/'fetch_and_extract_primary.py';source=original.read_text(encoding='utf-8')
    changes=[('import sys,json,time,re,urllib.request,urllib.parse','import sys,json,time,re,urllib.request,urllib.parse,ssl'),
        ('primary_attempt01','primary_attempt02'),('extraction_attempt01','extraction_attempt02'),('PRIMARY_SELECTION.json','PRIMARY_SELECTION_ATTEMPT02.json'),
        ('            with urllib.request.urlopen(req,timeout=30) as response:',
         '            ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED\n            from retrieve_stronger_adaptation_primary import Redirect\n            op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),Redirect())\n            with op.open(req,timeout=30) as response:'),
        ("[Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION_ATTEMPT02.json',", "[Path(__file__),HERE/'PROTOCOL.md',HERE/'NETWORK_RECOVERY_PROTOCOL.md',HERE/'fetch_and_extract_primary.py',HERE/'build_direct_https_attempt02.py',HERE/'PRIMARY_SELECTION_ATTEMPT02.json',")]
    revised=source;counts=[]
    for before,after in changes:
        count=revised.count(before);assert count>0;counts.append(count);revised=revised.replace(before,after)
    ast.parse(revised);dest=HERE/'fetch_and_extract_direct_attempt02.py'
    with dest.open('x',encoding='utf-8') as f:f.write(revised)
    diff=''.join(difflib.unified_diff(source.splitlines(keepends=True),revised.splitlines(keepends=True),fromfile=original.name,tofile=dest.name))
    with (HERE/'DIRECT_HTTPS_ATTEMPT02.diff').open('x',encoding='utf-8') as f:f.write(diff)
    record=dict(complete=True,errors=[],source_sha256=sha(original),new_runner_sha256=sha(dest),diff_sha256=sha(HERE/'DIRECT_HTTPS_ATTEMPT02.diff'),replacement_counts=counts,
        failed_outputs_preserved=True,only_transport_and_separate_output_binding_changed=True,actual_papers_read=0,publication_claim_confirmed=False,goal_status='active')
    with (HERE/'DIRECT_HTTPS_BUILD_RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(record),flush=True)
if __name__=='__main__':main()
