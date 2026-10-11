"""Identity-checked two primary JATS sources; extraction is not the reading audit."""
import sys,time,ssl,json,gzip,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,dump
ITEMS=[('routing','10.1038/s41598-026-48187-x','PMC13230987'),('active','10.3390/brainsci16030300','PMC13023837')]
def val(e):return ' '.join(''.join(e.itertext()).split()) if e is not None else ''
def tag(e):return e.tag.rsplit('}',1)[-1]
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=resource_guard()
    assert before['workspace_free_bytes']-18_800_000>=8_000_000_000
    out=HERE/'primary_xml_attempt01';out.mkdir(exist_ok=False)
    dump(out/'frozen_selection.json',dict(items=ITEMS,source_bindings=[entry(Path(__file__)),entry(HERE/'PRIMARY_SELECTION.md')]))
    context=ssl.create_default_context();opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context));records=[]
    for key,doi,pmcid in ITEMS:
        row=dict(key=key,doi=doi,pmcid=pmcid,complete=False,maintext_actually_read=False)
        try:
            resource_guard();assert time.perf_counter()-started<300
            url='https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML'
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
                data=response.read(700_001);assert len(data)<=700_000;row.update(requested_url=url,effective_url=response.url,http_status=response.status)
            root=ET.fromstring(data);meta=root.find('./front/article-meta');ids={e.get('pub-id-type'):val(e) for e in meta.findall('./article-id')}
            assert ids['doi'].casefold()==doi and any(v.removeprefix('PMC')==pmcid.removeprefix('PMC') for k,v in ids.items() if 'pmc' in str(k))
            blocks=[]
            def walk(e,scope):
                if e is None:return
                if tag(e)=='sec':scope=scope+[e.get('id') or val(e.find('./title'))]
                if tag(e) in {'title','p','fig','table-wrap','disp-formula'}:
                    text=val(e)
                    if text:blocks.append(dict(index=len(blocks),kind=tag(e),scope=scope,id=e.get('id'),text=text))
                    return
                for child in e:walk(child,scope)
            for e in meta.findall('./abstract'):walk(e,['abstract'])
            walk(root.find('./body'),['body'])
            tables=[dict(id=e.get('id'),text=val(e),rows=[[val(c) for c in tr if tag(c) in {'th','td'}] for tr in e.iter() if tag(tr)=='tr']) for e in root.iter() if tag(e)=='table-wrap']
            formulas=[dict(id=e.get('id'),text=val(e),xml=ET.tostring(e,encoding='unicode')) for e in root.iter() if tag(e)=='disp-formula']
            source=[]
            for name,content in [('xml',data),('blocks.json',(json.dumps(blocks,ensure_ascii=False)+'\n').encode()),('tables.json',(json.dumps(tables,ensure_ascii=False)+'\n').encode()),('formulas.json',(json.dumps(formulas,ensure_ascii=False)+'\n').encode())]:
                p=out/(key+'.'+name+'.gz');p.write_bytes(gzip.compress(content,mtime=0));source.append(entry(p))
            row.update(complete=True,identity_verified=True,title=val(meta.find('./title-group/article-title')),article_ids=ids,
                blocks=len(blocks),tables=len(tables),display_formulas=len(formulas),source_bindings=source,
                headings=[dict(index=b['index'],text=b['text']) for b in blocks if b['kind']=='title'],figure_pixels_read=False,external_supplement_read=False)
        except Exception as e:row['error']=dict(type=type(e).__name__,message=str(e))
        records.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
    result=dict(complete=all(r['complete'] for r in records),records=records,new_distinct_maintexts_actually_read=0,
        source_bindings=[entry(Path(__file__)),entry(HERE/'PRIMARY_SELECTION.md')],resources_before=before,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started,
        medical_arrays_loaded=0,patient_information_uploaded=False,publication_claim_confirmed=False,goal_status='active')
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000;dump(out/'receipt.json',result)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
