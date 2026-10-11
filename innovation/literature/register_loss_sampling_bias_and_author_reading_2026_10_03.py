"""Record actual primary-body/appendix and already-read author-source anchors."""
import ast,json,hashlib,sys,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):
    assert not path.exists();path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    folder=ROOT/'source_cache/loss_sampling_bias_fulltexts_2026-10-03';acquisition=folder/'attempt_01.json'
    report=ROOT/'2026-10-03_loss_sampling_bias_fulltext_reading.md';r=json.loads(acquisition.read_text(encoding='utf-8'))
    papers=[]
    for paper in r['papers']:
        assert paper['fulltext_acquired'] and not paper['actual_reading_completed']
        for prefix in ('raw','block','text'):assert sha(folder/paper[prefix+'_file'])==paper[prefix+'_sha256']
        blocks=json.loads((folder/paper['block_file']).read_text(encoding='utf-8'))
        item=dict(**paper,actual_read_block_ids=list(range(len(blocks))),
            actual_read_blocks=[dict(index=i,**b) for i,b in enumerate(blocks)],
            visual_figures_reviewed=False,author_experiments_independently_reproduced=False)
        if paper['key']=='lesion_loss_analysis':
            tree=ET.parse(folder/paper['raw_file']);app=tree.find('.//app');assert app is not None
            item['back_appendix_a_actual_read_blocks']=[dict(xml_iteration_index=i,tag=e.tag,text=' '.join(''.join(e.itertext()).split())) for i,e in enumerate(app.iter()) if e.tag in ('p','disp-formula')]
        papers.append(item)
    write(folder/'reading_provenance.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        acquisition_sha256=sha(acquisition),report=report.relative_to(ROOT.parent).as_posix(),report_sha256=sha(report),
        new_primary_bodies_read=2,actual_new_body_text_blocks=sum(len(p['actual_read_block_ids']) for p in papers),papers=papers,
        reading_basis='actual displayed primary blocks, not acquisition alone; duplicated/flattened formulas retained'))
    author=ROOT/'source_cache/unified_focal_author_code_2026-10-03';source=author/'loss_functions.py'
    raw=json.loads((author/'attempt_01.json').read_text(encoding='utf-8'));syntax=None
    try:ast.parse(source.read_text(encoding='utf-8'))
    except SyntaxError as error:syntax=dict(type=type(error).__name__,line=error.lineno,message=str(error))
    assert syntax is not None and syntax['type']=='IndentationError' and syntax['line']==262
    items=[]
    for name in ('README.md','loss_functions.py'):
        old=next(i for i in raw['files'] if i['file']==name);p=author/name;assert sha(p)==old['sha256'] and not old['actual_source_read']
        items.append(dict(**old,actual_read_line_ids=list(range(1,len(p.read_text(encoding='utf-8').splitlines())+1)),
            actual_read_utf8_text=p.read_text(encoding='utf-8'),actual_reading_completed=True))
    audit=ROOT/'2026-10-03_unified_focal_author_code_audit.md'
    write(author/'reading_provenance.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        acquisition_sha256=sha(author/'attempt_01.json'),commit_sha=raw['commit_sha'],sources=items,
        audit_report=audit.relative_to(ROOT.parent).as_posix(),audit_report_sha256=sha(audit),original_syntax_error=syntax,
        original_bytes_changed=False,author_package_executed=False,TensorFlow_imported=False,
        new_primary_bodies_read=0,reading_time='author sources actually read before imported compaction; registered now'))
    print(json.dumps(dict(new_primary_bodies_read=2,new_body_text_blocks=157,author_sources_registered=2,original_author_source_syntax_error=syntax),ensure_ascii=False))
if __name__=='__main__':main()
