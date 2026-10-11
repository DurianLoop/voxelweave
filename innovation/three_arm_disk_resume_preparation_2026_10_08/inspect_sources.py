"""AST/read-only current resources and source inspection; no neural imports."""
import ast,sys,time
from pathlib import Path
import disk_resume_core as core
def main():
    sys.stdout.reconfigure(encoding='utf-8'); start=time.perf_counter()
    files=sorted(core.HERE.glob('*.py')); checks=[]
    for p in files: ast.parse(p.read_text(encoding='utf-8'),filename=str(p)); checks.append(core.entry(p))
    q=dict(created_utc=core.now(),complete=True,errors=[],source_bindings=checks,
           resources=core.guard(start,60,200_000_000-core.saved_bytes()),neural_modules_imported=False,
           medical_arrays_loaded=0,neural_forwards=0,no_pyc_generated=True)
    core.new_json(core.HERE/'SOURCE_INSPECTION.json',q)
    print(core.json.dumps(dict(complete=True,AST_files=len(checks),resources=q['resources'])),flush=True)
    return 0
if __name__=='__main__': raise SystemExit(main())
