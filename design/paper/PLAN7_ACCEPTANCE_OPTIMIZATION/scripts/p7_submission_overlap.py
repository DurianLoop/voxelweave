"""Paragraph-level textual overlap audit for the two final-candidate TeX files."""
from pathlib import Path
import json, math, re
from collections import Counter
from difflib import SequenceMatcher

import numpy as np

HERE=Path(__file__).resolve(); P7=HERE.parents[1]; PAPER=P7.parent; OUT=P7/"outputs"
TMI=PAPER/"TMI"/"TMI_MANUSCRIPT_SUBMISSION_FINAL"/"main.tex"
CV=PAPER/"CVPR"/"CVPR_UPGRADE"/"PAPER_FINAL"/"main.tex"

def clean(s):
    s=re.sub(r"%.*", " ", s)
    s=re.sub(r"\\(?:cite|ref|label|includegraphics|bibliography|bibliographystyle)(?:\[[^]]*\])?\{[^}]*\}", " ", s)
    s=re.sub(r"\\[A-Za-z@]+\*?(?:\[[^]]*\])?", " ", s)
    s=re.sub(r"[{}$^_&~\\]", " ", s)
    s=re.sub(r"\s+", " ", s).strip().lower()
    return s

def paras(path):
    text=path.read_text(encoding="utf-8")
    text=re.sub(r"\\begin\{(?:figure\*?|table\*?|equation\*?|align\*?)\}.*?\\end\{(?:figure\*?|table\*?|equation\*?|align\*?)\}"," ",text,flags=re.S)
    out=[]; section="front"
    for block in re.split(r"\n\s*\n",text):
        hit=re.search(r"\\(?:sub)*section\{([^}]*)\}",block)
        if hit: section=clean(hit.group(1))
        q=clean(block)
        words=re.findall(r"[a-z0-9]+",q)
        if len(words)>=25 and not q.startswith("documentclass"):
            out.append({"section":section,"text":q,"words":len(words)})
    return out

def tfidf_vectors(texts):
    documents=[]; df=Counter()
    for text in texts:
        words=re.findall(r"[a-z0-9]+",text)
        terms=words+[f"{a}__{b}" for a,b in zip(words,words[1:])]
        c=Counter(terms); documents.append(c); df.update(c.keys())
    n=len(documents); vecs=[]
    for c in documents:
        v={term:count*(math.log((1+n)/(1+df[term]))+1) for term,count in c.items()}
        norm=math.sqrt(sum(q*q for q in v.values())) or 1.; vecs.append({k:q/norm for k,q in v.items()})
    return vecs

def cosine(a,b):
    if len(a)>len(b):a,b=b,a
    return sum(v*b.get(k,0.) for k,v in a.items())

def main():
    OUT.mkdir(parents=True,exist_ok=True); a=paras(TMI); b=paras(CV)
    corpus=[q["text"] for q in a+b]; vec=tfidf_vectors(corpus)
    sim=np.asarray([[cosine(vec[i],vec[len(a)+j]) for j in range(len(b))] for i in range(len(a))])
    rows=[]
    for i,p in enumerate(a):
        j=int(np.argmax(sim[i])); ratio=SequenceMatcher(None,p["text"],b[j]["text"]).ratio()
        rows.append({"tmi_paragraph":i+1,"tmi_section":p["section"],"cvpr_paragraph":j+1,"cvpr_section":b[j]["section"],"tfidf_similarity":float(sim[i,j]),"sequence_ratio":ratio,"tmi_words":p["words"],"classification":"shared_background" if sim[i,j]>=.45 else "tmi_only_or_distinct"})
    import pandas as pd
    frame=pd.DataFrame(rows); frame.to_csv(OUT/"p7_submission_paragraph_overlap.csv",index=False)
    payload={"experiment":"P7-BOTH-E01","status":"COMPLETE","tmi_paragraphs":len(a),"cvpr_paragraphs":len(b),
             "tmi_paragraphs_tfidf_ge_0.30":int((frame.tfidf_similarity>=.30).sum()),
             "tmi_paragraphs_tfidf_ge_0.45":int((frame.tfidf_similarity>=.45).sum()),
             "tmi_words_in_ge_0.45_matches":int(frame.loc[frame.tfidf_similarity>=.45,"tmi_words"].sum()),
             "tmi_total_words_in_audited_paragraphs":int(frame.tmi_words.sum()),
             "approx_high_similarity_word_fraction":float(frame.loc[frame.tfidf_similarity>=.45,"tmi_words"].sum()/frame.tmi_words.sum()),
             "method":"pure-Python paragraph TF-IDF unigram+bigram cosine; figures/tables/equations removed; threshold is diagnostic and not CrossCheck"}
    (OUT/"p7_submission_overlap.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(payload,indent=2)); print(frame.sort_values("tfidf_similarity",ascending=False).head(20).to_string(index=False))
if __name__=="__main__":main()
