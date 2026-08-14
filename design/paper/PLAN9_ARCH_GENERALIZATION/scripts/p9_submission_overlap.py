"""Paragraph-level diagnostic textual overlap audit for Plan-9 TMI/CVPR branches."""
from pathlib import Path
import json, math, re
from collections import Counter
from difflib import SequenceMatcher
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve();P9=HERE.parents[1];PAPER=P9.parent;OUT=P9/'outputs'
TMI=PAPER/'TMI/TMI_ARCH_GENERALIZED/main.tex';CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex'
def clean(s):
 s=re.sub(r'%.*',' ',s);s=re.sub(r'\\(?:cite|ref|label|includegraphics|bibliography|bibliographystyle)(?:\[[^]]*\])?\{[^}]*\}',' ',s);s=re.sub(r'\\[A-Za-z@]+\*?(?:\[[^]]*\])?',' ',s);s=re.sub(r'[{}$^_&~\\]',' ',s);return re.sub(r'\s+',' ',s).strip().lower()
def paras(path):
 text=path.read_text(encoding='utf-8');text=re.sub(r'\\begin\{(?:figure\*?|table\*?|equation\*?|align\*?)\}.*?\\end\{(?:figure\*?|table\*?|equation\*?|align\*?)\}',' ',text,flags=re.S);out=[];section='front'
 for block in re.split(r'\n\s*\n',text):
  hit=re.search(r'\\(?:sub)*section\{([^}]*)\}',block)
  if hit:section=clean(hit.group(1))
  q=clean(block);words=re.findall(r'[a-z0-9]+',q)
  if len(words)>=25 and not q.startswith('documentclass'):out.append({'section':section,'text':q,'words':len(words)})
 return out
def vectors(texts):
 docs=[];df=Counter()
 for text in texts:
  w=re.findall(r'[a-z0-9]+',text);c=Counter(w+[f'{a}__{b}' for a,b in zip(w,w[1:])]);docs.append(c);df.update(c)
 n=len(docs);out=[]
 for c in docs:
  v={k:z*(math.log((1+n)/(1+df[k]))+1) for k,z in c.items()};norm=math.sqrt(sum(z*z for z in v.values())) or 1;out.append({k:z/norm for k,z in v.items()})
 return out
def cosine(a,b):
 if len(a)>len(b):a,b=b,a
 return sum(v*b.get(k,0) for k,v in a.items())
def main():
 a=paras(TMI);b=paras(CV);v=vectors([q['text'] for q in a+b]);sim=np.asarray([[cosine(v[i],v[len(a)+j]) for j in range(len(b))] for i in range(len(a))]);rows=[]
 for i,p in enumerate(a):
  j=int(np.argmax(sim[i]));rows.append({'tmi_paragraph':i+1,'tmi_section':p['section'],'cvpr_paragraph':j+1,'cvpr_section':b[j]['section'],'tfidf_similarity':float(sim[i,j]),'sequence_ratio':SequenceMatcher(None,p['text'],b[j]['text']).ratio(),'tmi_words':p['words']})
 x=pd.DataFrame(rows);x.to_csv(OUT/'p9_submission_paragraph_overlap.csv',index=False);payload={'status':'COMPLETE','tmi_paragraphs':len(a),'cvpr_paragraphs':len(b),'paragraphs_tfidf_ge_030':int((x.tfidf_similarity>=.30).sum()),'paragraphs_tfidf_ge_045':int((x.tfidf_similarity>=.45).sum()),'high_similarity_word_fraction':float(x.loc[x.tfidf_similarity>=.45,'tmi_words'].sum()/x.tmi_words.sum()),'method':'diagnostic paragraph TF-IDF; not CrossCheck'};(OUT/'p9_submission_overlap.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2));print(x.sort_values('tfidf_similarity',ascending=False).head(12).to_string(index=False))
if __name__=='__main__':main()
