"""A top-level figure holds the HTML table; do not require an additionally duplicated table block."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;OLD=HERE/'extract_stu_original_html.py'
source=OLD.read_text(encoding='utf-8')
old="assert any(x['kind']=='table' for x in q.blocks)"
new="assert p.read_text(encoding='utf-8').count('<table')>0 and any(x['kind']=='figure' and 'Table' in x['text'] for x in q.blocks)"
assert source.count(old)==1;source=source.replace(old,new)
source=source.replace("'stu_original_arxiv_blocks.json'","'stu_original_arxiv_blocks_v2.json'")
source=source.replace("'stu_original_extraction_receipt.json'","'stu_original_extraction_receipt_v2.json'")
if __name__=='__main__':exec(compile(source,str(OLD),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
