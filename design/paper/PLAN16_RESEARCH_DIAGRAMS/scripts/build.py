from pathlib import Path
import subprocess, json, re, shutil, concurrent.futures

P13=Path(__file__).resolve().parents[1]; PAPER=P13.parent; LOG=P13/'build_logs'; LOG.mkdir(exist_ok=True)
JOBS=[('tmi_baselines',PAPER/'TMI/TMI_ARCH_GENERALIZED','baseline_supplement',False),('cvpr',PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER','main',True),('supplement',PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER','supplement',False),('tmi',PAPER/'TMI/TMI_ARCH_GENERALIZED','main',True)]
def build(job):
    name,cwd,stem,bib=job
    tex=(cwd/(stem+'.tex')).read_text(encoding='utf-8')
    assert not any(ord(c)<32 and c not in '\n\r\t' for c in tex),name+' control characters'
    commands=[['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex']]
    if bib: commands.append(['bibtex',stem])
    commands += [['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex']]*2
    for i,command in enumerate(commands):
        p=subprocess.run(command,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (LOG/f'{name}_{i+1}.txt').write_bytes(p.stdout)
        if p.returncode: return {'document':name,'success':False,'stage':i+1,'tail':p.stdout.decode(errors='replace')[-1800:]}
    log=(cwd/(stem+'.log')).read_text(errors='replace')
    shutil.copy2(cwd/(stem+'.log'),LOG/(name+'_final.log'))
    info=subprocess.run(['pdfinfo',str(cwd/(stem+'.pdf'))],capture_output=True,text=True).stdout
    subprocess.run(['pdftotext','-layout',str(cwd/(stem+'.pdf')),str(LOG/(name+'_text.txt'))],check=True)
    pages=int(re.search(r'Pages:\s+(\d+)',info).group(1))
    errors=[line for line in log.splitlines() if re.search(r'Overfull|undefined|LaTeX Error|^!',line,re.I)]
    return {'document':name,'success':True,'pages':pages,'issues':errors,'bytes':(cwd/(stem+'.pdf')).stat().st_size}
# The supplement and main use different jobnames; build each paper package sequentially
# to keep shared auxiliary-file interactions straightforward.
JOBS=[job for job in JOBS if job[0] in {'cvpr','tmi'}]
result=[]
for job in JOBS:
    r=build(job); result.append(r); print(json.dumps(r),flush=True)
(LOG/'build_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
