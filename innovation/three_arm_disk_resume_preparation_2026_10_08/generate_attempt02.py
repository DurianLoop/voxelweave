"""Create versioned audit fix with diffs; executed attempt01 files stay untouched."""
import ast,difflib,sys
from pathlib import Path
import disk_resume_core as core

def main():
    sys.stdout.reconfigure(encoding='utf-8'); changes=[]
    src=core.HERE/'qualify_disk_worker.py'; text=src.read_text(encoding='utf-8')
    before="""            if p.name.endswith('.pt') and p.is_relative_to(attempt/'continuous'):
                assert a.mode=='restarted' and p.name in {arm+'_step001.pt' for arm in core.ARMS}
                weight_paths.append(p.relative_to(core.ROOT).as_posix()); return
"""
    after="""            own_checkpoints={directory/(arm+'_step'+f'{step:03d}'+'.pt') for arm in core.ARMS
                             for step in ((1,3) if a.mode=='continuous' else (3,))}
            restore_checkpoints={attempt/'continuous'/(arm+'_step001.pt') for arm in core.ARMS} if a.mode=='restarted' else set()
            if p.name.endswith('.pt') and p in own_checkpoints|restore_checkpoints:
                # These reads include byte hashes; only explicit engine torch.load counts arrays.
                weight_paths.append(p.relative_to(core.ROOT).as_posix()); return
"""
    assert text.count(before)==1; worker=text.replace(before,after)
    pairs=[(src,core.HERE/'qualify_disk_worker_v2.py',worker)]
    src=core.HERE/'qualify_disk_resume.py'; text=src.read_text(encoding='utf-8')
    updated=text.replace("out=core.HERE/'attempt01'","out=core.HERE/'attempt02'")
    updated=updated.replace("'qualify_disk_worker.py'","'qualify_disk_worker_v2.py'")
    updated=updated.replace("'qualify_disk_resume.py'","'qualify_disk_resume_v2.py'").replace("'verify_disk_resume.py'","'verify_disk_resume_v2.py'")
    updated=updated.replace("'--attempt','01'","'--attempt','02'")
    updated=updated.replace("paths=[core.HERE/name for name in ('PROTOCOL.md'","paths=[core.HERE/name for name in ('ATTEMPT02_AMENDMENT.md','generate_attempt02.py','PROTOCOL.md'")
    updated=updated.replace("r['resources_before']=core.guard(start,600,200_000_000-core.saved_bytes())", "r['resources_before']=core.guard(start,600,200_000_000-core.saved_bytes())\n        failed=core.read(core.HERE/'attempt01/receipt.json')\n        assert time.perf_counter()-start+failed['elapsed_seconds']<600")
    updated=updated.replace("r.update(finished_utc=core.now()", "r['combined_qualification_wall_seconds']=time.perf_counter()-start+core.read(core.HERE/'attempt01/receipt.json')['elapsed_seconds']\n    assert r['combined_qualification_wall_seconds']<600\n    r.update(finished_utc=core.now()")
    pairs.append((src,core.HERE/'qualify_disk_resume_v2.py',updated))
    src=core.HERE/'verify_disk_resume.py'; text=src.read_text(encoding='utf-8')
    updated=text.replace("'attempt01", "'attempt02").replace("'independent_attempt01'", "'independent_attempt02'")
    pairs.append((src,core.HERE/'verify_disk_resume_v2.py',updated))
    for src,dst,updated in pairs:
        original=src.read_text(encoding='utf-8'); assert original!=updated
        ast.parse(updated); core.new_bytes(dst,updated.encode('utf-8'))
        diff=''.join(difflib.unified_diff(original.splitlines(True),updated.splitlines(True),fromfile=src.name,tofile=dst.name))
        diffpath=core.HERE/(dst.stem+'.patch'); core.new_bytes(diffpath,diff.encode('utf-8'))
        changes.append(dict(source=core.entry(src),output=core.entry(dst),diff=core.entry(diffpath)))
    core.new_json(core.HERE/'ATTEMPT02_SOURCE_GENERATION.json',dict(created_utc=core.now(),complete=True,errors=[],changes=changes,
        source_bindings=[core.entry(Path(__file__)),core.entry(core.HERE/'ATTEMPT02_AMENDMENT.md')]+[v['source'] for v in changes],
        output_bindings=[b for v in changes for b in (v['output'],v['diff'])],executed_sources_not_modified=True))
    print(core.json.dumps(dict(complete=True,new_versions=3,executed_sources_not_modified=True)),flush=True); return 0
if __name__=='__main__':raise SystemExit(main())
