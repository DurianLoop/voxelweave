"""One alternate representation already supplied by the exact Crossref DOI record."""
import sys,json
from pathlib import Path
import query_author_sources as client
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'publisher_xml_attempt01'
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.previous.resource_guard()
    index=ROOT/'seranet_identity_prior_art_2026_10_08/index_attempt03/receipt.json'
    q=json.loads(index.read_text(encoding='utf-8'))
    e=next(e for r in q['records'] for e in r.get('entries',[]) if e.get('DOI')=='10.1016/j.imavis.2024.105200')
    url=next(e['URL'] for e in e['link'] if e['content-type']=='text/xml')
    OUT.mkdir(exist_ok=False);client.OUT=OUT
    row=client.fetch(('xu_publisher_xml',url,'landing'))
    result=dict(complete=row['complete'],errors=row['errors'],records=[row],
        source_bindings=[client.base.entry(p) for p in (Path(__file__),HERE/'PUBLISHER_FORMAT_REPAIR.md',index,HERE/'index_attempt03/receipt.json')],
        resource_snapshot=client.previous.resource_guard(),metadata_or_abstract_not_fulltext_verified=True,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    client.base.new(OUT/'receipt.json',result)
    print(json.dumps({k:row.get(k) for k in ('complete','HTTP_status','effective_url','response_binding','errors')},ensure_ascii=False))
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
