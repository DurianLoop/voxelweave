from pathlib import Path
import subprocess,json,re,shutil
P=Path(__file__).resolve().parents[1];CV=P/'revised_manuscript';LOG=P/'build_logs'
def main():
    assert (P/'outputs/manuscript_generated.json').exists(),'Do not build an unchanged snapshot as a new result'
    results=[]
    for stem in ['main','supplement']:
        commands=[['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex']]
        if stem=='main':commands.append(['bibtex',stem])
        commands +=[['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex']]*2
        result=dict(document=stem,success=True)
        for i,cmd in enumerate(commands):
            p=subprocess.run(cmd,cwd=CV,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (LOG/f'{stem}_{i+1}.txt').write_bytes(p.stdout)
            if p.returncode:result.update(success=False,stage=i+1,returncode=p.returncode,tail=p.stdout.decode(errors='replace')[-1500:]);break
        if result['success']:
            log=(CV/(stem+'.log')).read_text(errors='replace');shutil.copy2(CV/(stem+'.log'),LOG/(stem+'_final.log'))
            result['issues']=[s for s in log.splitlines() if re.search(r'Overfull|undefined|multiply.?defined|LaTeX Error|^!',s,re.I)]
            p=subprocess.run(['pdftotext','-layout',str(CV/(stem+'.pdf')),str(LOG/(stem+'_text.txt'))],capture_output=True)
            result['text_extraction_returncode']=p.returncode
            if p.returncode==0:
                pages=(LOG/(stem+'_text.txt')).read_text(encoding='utf-8').split('\f');pages=[x for x in pages if x.strip()];result['pages']=len(pages)
                if stem=='main':result['body_pages']=next((j for j,x in enumerate(pages) if 'References' in x),len(pages))
        results.append(result);print(json.dumps(result),flush=True)
    (LOG/'build_audit.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    if not all(r['success'] and not r.get('issues') for r in results):raise SystemExit(1)
if __name__=='__main__':main()
