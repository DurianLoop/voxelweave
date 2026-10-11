"""Two fixed, different public author-text routes; byte-preserving extraction is not reading."""
import sys,time,json,gzip,hashlib,re,unicodedata,urllib.request,urllib.error
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard
sys.path.insert(0,str(ROOT/'augmentation_primary_followup_2026_10_08'))
from extract_bigaug_stdlib import Parser,Node
ITEMS=[('vinn','10.1016/j.neuroimage.2022.118933','PMC9801435'),
       ('lesion_ensemble','10.1007/978-3-032-16365-3_41','PMC13148016')]
def norm(s):
    return ' '.join(unicodedata.normalize('NFKC',s).translate(str.maketrans({'‐':'-','‑':'-','–':'-','—':'-'})).split()).rstrip('.').casefold()
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    def guard():
        v=resource_guard();assert time.perf_counter()-started<180
        size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        assert size<1_200_000
        assert v['workspace_free_bytes']-max(0,1_500_000-(ROOT/'resolution_degradation_controls_2026_10_08/full_real_pipeline_attempt01/fields.jsonl.gz').stat().st_size)-150_000-100_000-3_000_000>=8_000_000_000
        return v
    guard();out=HERE/'sources_attempt01';out.mkdir(exist_ok=False)
    index=ROOT/'resolution_and_lesion_followup_2026_10_08/index_attempt01/receipt.json'
    old=read(index);assert old['complete']
    entries={x['doi'].lower():x for r in old['records'] for x in r['entries'] if x['doi']}
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));records=[];errors=[]
    for key,doi,pmcid in ITEMS:
        guard();url=f'https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/'
        record=dict(key=key,DOI=doi,PMCID=pmcid,request_url=url,actual_primary_text_read=False)
        at=time.perf_counter()
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'MRI-public-primary-reading/1.0'})
            try:response=opener.open(req,timeout=30)
            except urllib.error.HTTPError as exc:response=exc
            with response:
                record['HTTP_status']=response.getcode();record['final_url']=response.geturl()
                body=response.read(2_000_001)
            assert len(body)<=2_000_000,'HTTP byte bound exceeded'
            packed=gzip.compress(body,mtime=0);assert len(packed)<=300_000
            p=out/f'{key}.html.gz'
            with p.open('xb') as f:f.write(packed)
            record.update(raw_response_gzip=entry(p),raw_response_bytes=len(body),raw_response_sha256=hashlib.sha256(body).hexdigest())
            assert record['HTTP_status']==200,f'HTTP {record["HTTP_status"]}'
            parser=Parser();parser.feed(body.decode('utf-8'));nodes=list(parser.root.walk())
            meta={n.attrs.get('name'):n.attrs.get('content') for n in nodes if n.tag=='meta'}
            assert meta.get('citation_doi','').lower()==doi,(doi,meta.get('citation_doi'))
            assert pmcid in body.decode('utf-8')
            title=meta.get('citation_title','');assert norm(title)==norm(entries[doi]['title']),(title,entries[doi]['title'])
            articles=[n for n in nodes if n.tag=='article'];assert len(articles)==1
            article=articles[0];blocks=[];selected={'h1','h2','h3','h4','p','figure','table','li'}
            for n in article.walk():
                if n.tag not in selected:continue
                parent=n.parent;duplicate=False;sections=[]
                while parent and parent is not article:
                    if parent.tag in selected:duplicate=True
                    if parent.tag=='section':sections.append(parent.attrs.get('id'))
                    parent=parent.parent
                if duplicate:continue
                content=' '.join(n.text().split())
                if content:blocks.append(dict(index=len(blocks),kind=n.tag,id=n.attrs.get('id'),section_ids=sections,text=content))
            assert len(blocks)>25
            tables=[]
            for n in article.walk():
                if n.tag!='table':continue
                rows=[]
                for tr in n.walk():
                    if tr.tag!='tr':continue
                    cells=[dict(tag=c.tag,text=' '.join(c.text().split()),rowspan=c.attrs.get('rowspan','1'),colspan=c.attrs.get('colspan','1')) for c in tr.children if isinstance(c,Node) and c.tag in ['th','td']]
                    if cells:rows.append(cells)
                tables.append(dict(id=n.attrs.get('id'),rows=rows))
            links=[dict(href=n.attrs.get('href'),text=' '.join(n.text().split())) for n in article.walk() if n.tag=='a' and n.attrs.get('href') and re.search(r'supp|\.pdf|github',n.attrs['href'],re.I)]
            dump(out/f'{key}_blocks.json',blocks);dump(out/f'{key}_tables.json',tables);dump(out/f'{key}_links.json',links)
            record.update(identity_verified=True,citation_title=title,blocks=len(blocks),tables=len(tables),extracted_primary_text_read=False,
                          extraction_bindings=[entry(out/f'{key}_{suffix}.json') for suffix in ['blocks','tables','links']],
                          headings=[dict(index=b['index'],kind=b['kind'],section_ids=b['section_ids'],preview=b['text'][:110]) for b in blocks if b['kind'] in ['h1','h2','h3','h4','table']])
        except Exception as exc:
            record['error']=type(exc).__name__+': '+str(exc);errors.append(dict(key=key,error=record['error']))
        record['elapsed_seconds']=time.perf_counter()-at;records.append(record)
        print(json.dumps(record,ensure_ascii=False),flush=True)
    q=dict(complete=len(records)==2 and not errors,errors=errors,records=records,new_primary_maintexts_actually_read=0,
           medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
           confirmation_patients_opened=False,lockedIXI_opened=False,author_code_executed=False,public_GETs_only=True,
           no_dependencies_installed=True,original_failed_routes_retained=True,resources=guard(),elapsed_seconds=time.perf_counter()-started,
           source_bindings=[entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',index,
             ROOT/'resolution_and_lesion_followup_2026_10_08/PRIMARY_SELECTION.md',
             ROOT/'resolution_and_lesion_followup_2026_10_08/primary_attempt01/HTTP_RECEIPT.json',
             ROOT/'augmentation_primary_followup_2026_10_08/extract_bigaug_stdlib.py']])
    dump(out/'receipt.json',q);guard();print(json.dumps(dict(complete=q['complete'],errors=errors,new_maintexts_read=0,elapsed_seconds=q['elapsed_seconds'])),flush=True)
    return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
