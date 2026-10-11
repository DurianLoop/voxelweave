"""Primary follow-ups after index identities; retain zero-hit and non-matching results."""
import json,sys,time,xml.etree.ElementTree as ET
from urllib.parse import urlencode
from retrieve_stronger_adaptation_primary import HERE,ROOT,OUT,fetch,dump,sha,resource_guard
from datetime import datetime,timezone

def blocks_xml(p):
    tree=ET.parse(p);root=tree.getroot();out=[]
    if root.tag=='collection':
        for passage in root.findall('.//passage'):
            text=passage.findtext('text')
            if text:out.append(dict(kind='bioc_passage',section={x.attrib.get('key'):x.text for x in passage.findall('infon')},text=text))
    else:
        for node in root.iter():
            tag=node.tag.rsplit('}',1)[-1]
            if tag in ['article-title','abstract','p','table-wrap','fig','ref']:
                text=' '.join(' '.join(node.itertext()).split())
                if text:out.append(dict(kind=tag,text=text))
    return out
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();tick=time.perf_counter()
    idx=json.loads((OUT/'index_receipt.json').read_text(encoding='utf-8'));assert idx['complete']
    jobs=[('genesis2021_bioc','https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC7726094/unicode','.xml'),
        ('stu_mri2025_jats','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11983000/fullTextXML','.xml'),
        ('stacked_crossref','https://api.crossref.org/works?'+urlencode({'query.title':'Deep stacked transformation for generalizable medical image segmentation','rows':3}),'.json'),
        ('stu_original_crossref','https://api.crossref.org/works?'+urlencode({'query.title':'STU-Net Scalable and Transferable Medical Image Segmentation Models Empowered by Large-Scale Supervised Pre-training','rows':3}),'.json')]
    records=[]
    for job in jobs:
        r=fetch(*job)
        if r['complete'] and job[2]=='.xml':
            try:
                blocks=blocks_xml(ROOT/r['file']);assert blocks and any('segmentation' in x['text'].lower() for x in blocks)
                p=OUT/(job[0]+'_blocks.json');dump(p,blocks)
                r.update(extracted_blocks=len(blocks),extracted_file=p.relative_to(ROOT).as_posix(),extracted_sha256=sha(p),actual_reading_completed=False)
            except Exception as e:r['extraction_error']=type(e).__name__+': '+str(e)
        elif r['complete']:
            q=json.loads((ROOT/r['file']).read_text(encoding='utf-8'))
            r['entries']=[{k:x.get(k) for k in ['title','DOI','author','published','URL']} for x in q['message']['items']]
        records.append(r);assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<6_000_000
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in records),
        errors=[e for r in records for e in r['errors']],records=records,primary_papers_actually_read=0,
        automatic_retries=False,public_GET_only=True,medical_arrays_loaded=0,GPU_forwards=0,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [Path(__file__),OUT/'index_receipt.json']],
        resource_snapshot=resource_guard(),elapsed_seconds=time.perf_counter()-tick)
    dump(OUT/'fulltext_receipt.json',receipt)
    print(json.dumps(records,ensure_ascii=False),flush=True);return int(not receipt['complete'])
from pathlib import Path
if __name__=='__main__':raise SystemExit(main())
