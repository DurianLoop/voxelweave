"""Read author-linked public source at an authenticated commit; no installation/execution."""
import json,hashlib,sys,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/unified_focal_author_code_2026-10-03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    paper=ROOT/'source_cache/task_loss_followup_fulltext_2026-10-03/unified_focal_attempt_01.xml'
    assert 'https://github.com/mlyg/unified-focal-loss' in paper.read_text(encoding='utf-8')
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),paper_sha256=sha(paper),
        complete=False,errors=[],requests=[],author_code_executed=False,packages_installed=False,scientific_confirmation_patients=0)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def get(url,name,limit=4000000):
        request=urllib.request.Request(url,headers={'User-Agent':'MRI-literature-source-audit','Accept':'application/vnd.github+json'})
        with opener.open(request,timeout=25) as response:raw=response.read(limit+1);status=response.status
        assert len(raw)<=limit;p=OUT/name;p.write_bytes(raw);r['requests'].append(dict(url=url,http_status=status,file=name,sha256=sha(p),bytes=len(raw)))
        return raw
    try:
        meta=json.loads(get('https://api.github.com/repos/mlyg/unified-focal-loss','repository.response'))
        branch=meta['default_branch'];commit=json.loads(get('https://api.github.com/repos/mlyg/unified-focal-loss/commits/'+urllib.parse.quote(branch,safe=''),'commit.response'))
        r['commit_sha']=commit['sha'];r['commit_timestamp']=commit['commit']['committer']['date']
        tree=json.loads(get('https://api.github.com/repos/mlyg/unified-focal-loss/git/trees/'+commit['commit']['tree']['sha']+'?recursive=1','tree.response'))
        assert not tree.get('truncated',False)
        selected=[x for x in tree['tree'] if x['type']=='blob' and (x['path'].endswith('.py') or x['path'].lower()=='readme.md')]
        assert len(selected)<=20;r['files']=[]
        for item in selected:
            safe=item['path'].replace('/','__');raw=get('https://raw.githubusercontent.com/mlyg/unified-focal-loss/'+r['commit_sha']+'/'+urllib.parse.quote(item['path'],safe='/'),safe,1000000)
            gitsha=hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest();assert gitsha==item['sha']
            r['files'].append(dict(repository_path=item['path'],file=safe,sha256=sha(OUT/safe),git_blob_sha1=gitsha,actual_source_read=False))
        r['complete']=True
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error))
    (OUT/'attempt_01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False));return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
