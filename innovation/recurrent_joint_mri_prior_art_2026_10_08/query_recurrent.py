"""Read two previously unscreened title pages and a direct recurrent/attention query."""
import sys,json,time,subprocess,traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
from datetime import datetime,timezone
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'index_attempt01'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def fetch(job):
    key,query,start=job;url='https://export.arxiv.org/api/query?'+urlencode(dict(search_query=query,start=start,max_results=8))
    row=dict(key=key,query=query,start=start,max_results=8,requested_url=url,complete=False,errors=[])
    p=OUT/(key+'.xml');tick=time.perf_counter()
    try:
        r=subprocess.run(['curl.exe','--noproxy','*','--fail','--silent','--show-error','--location',
          '--max-redirs','3','--proto','=https','--proto-redir','=https','--max-time','30','--max-filesize','3000000',
          '--dump-header',str(OUT/(key+'_headers.txt')),'--output',str(p),'--write-out','%{http_code}\\n%{url_effective}',url],capture_output=True,timeout=35)
        (OUT/(key+'_stderr.txt')).write_bytes(r.stderr)
        row.update(curl_exit=r.returncode,status_and_effective_url=r.stdout.decode('utf-8',errors='replace'))
        assert r.returncode==0,r.stderr.decode('utf-8',errors='replace')
        tree=ET.fromstring(p.read_bytes());ns={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
        row['total_results']=tree.findtext('o:totalResults',namespaces=ns)
        row['entries']=[dict(id=e.findtext('a:id',namespaces=ns),title=' '.join((e.findtext('a:title',namespaces=ns) or '').split()),
           published=e.findtext('a:published',namespaces=ns),updated=e.findtext('a:updated',namespaces=ns),
           authors=[a.findtext('a:name',namespaces=ns) for a in e.findall('a:author',ns)],
           summary=e.findtext('a:summary',namespaces=ns),links=[dict(v.attrib) for v in e.findall('a:link',ns)])
           for e in tree.findall('a:entry',ns)]
        row.update(complete=True,file=base.entry(p))
    except Exception as e:row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    row['elapsed_seconds']=time.perf_counter()-tick;return row
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();resource_guard()
    OUT.mkdir(exist_ok=False)
    cutoff=' AND submittedDate:[199101010000 TO 202610082359]'
    title='ti:Joint AND (ti:MRI OR ti:"Magnetic Resonance") AND ti:Segmentation'+cutoff
    jobs=[('joint_title_page2',title,8),('joint_title_page3',title,16),
       ('recurrent_attention','(all:MRI OR all:"magnetic resonance") AND ti:reconstruction AND ti:segmentation AND (all:attention OR all:recurrent)'+cutoff,0)]
    tick=time.perf_counter()
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,jobs))
    old=ROOT/'joint_segmentation_mri_prior_art_2026_10_08/index_followup_attempt01/receipt.json'
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),errors=[],records=rows,
       source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',old,
       ROOT/'task_adaptation_compute_prior_art_2026_10_08/query_primary.py')],
       new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0,
       public_GET_only=True,TLS_verification_disabled=False,elapsed_seconds=time.perf_counter()-tick)
    base.new(OUT/'receipt.json',result);print(json.dumps(result,ensure_ascii=False),flush=True);return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())

