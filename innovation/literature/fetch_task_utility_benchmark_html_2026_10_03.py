"""Read the exact public preprint identified by the archived arXiv index."""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
from extract_mira_neighbour_html import ArticleText
from fetch_task_utility_routes_2026_10_03 import ROOT, OUT, fetch, sha

def main():
 sys.stdout.reconfigure(encoding='utf-8')
 index=json.loads((OUT/'routes_attempt_01.json').read_text(encoding='utf-8'))
 matches=[e for r in index['responses'] if r['key']=='benchmark_arxiv_index' for e in r.get('entries',[]) if e['title']=='Understanding Benefits and Pitfalls of Current Methods for the Segmentation of Undersampled MRI Data']
 if len(matches)!=1: raise ValueError('Unique exact title required')
 paper_id=matches[0]['id'].rsplit('/',1)[1]
 if not re.fullmatch(r'\d{4}\.\d{4,5}v\d+',paper_id): raise ValueError('Unexpected paper ID')
 row=fetch('benchmark_html','https://arxiv.org/html/'+paper_id);row.update(arxiv_id=paper_id,body_obtained=False,actual_reading_completed=False)
 if not row.get('error'):
  try:
   parser=ArticleText();parser.feed((OUT/row['raw_file']).read_text(encoding='utf-8'))
   lines=[' '.join(line.split()) for line in ''.join(parser.parts).splitlines() if line.strip()]
   actual=lines[0] if lines else ''
   if actual!=matches[0]['title']: raise ValueError('Returned HTML article title mismatch: '+actual)
   chunks=[dict(kind='flattened_article_block',text=value) for value in lines]
   if len(chunks)<20 or sum(len(x['text']) for x in chunks)<10000: raise ValueError('Article body absent/too short')
   p=OUT/'benchmark_paragraphs.json';p.write_text(json.dumps(chunks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t=OUT/'benchmark_maintext.txt';t.write_text('\n\n'.join('[%04d %s] %s'%(i,x['kind'],x['text']) for i,x in enumerate(chunks))+'\n',encoding='utf-8')
   row.update(body_obtained=True,title=actual,paragraphs=len(chunks),paragraph_file=p.name,paragraph_sha256=sha(p),text_file=t.name,text_sha256=sha(t),parser_helper_sha256=sha(ROOT/'extract_mira_neighbour_html.py'),extraction_warning='HTML math/tables flattened into article blocks; no supplement or visual figure reading')
  except Exception as exc: row['parse_error']=type(exc).__name__+': '+str(exc)
 path=OUT/'benchmark_html_attempt_01.json'
 with path.open('x',encoding='utf-8') as f: json.dump(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),routes_index_sha256=sha(OUT/'routes_attempt_01.json'),source=row),f,ensure_ascii=False,indent=2)
 print(json.dumps(row,ensure_ascii=False),flush=True)

if __name__=='__main__': main()
