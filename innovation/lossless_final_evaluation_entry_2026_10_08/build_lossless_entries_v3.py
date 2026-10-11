"""Create separate V3 entries after preserving the actual V2 import failure."""
import sys,json,difflib,ast
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();records=[]
    first=json.loads((HERE/'BUILD_RECEIPT.json').read_text(encoding='utf-8'));assert first['complete']
    for record in first['records']:
        source=ROOT/record['new']['path'];assert client.base.entry(source)==record['new']
        old=source.read_text(encoding='utf-8');new=old.replace('_lossless_v2','_lossless_v3')
        new=new.replace("'compression_qualification/receipt.json'","'compression_qualification_v3/receipt.json'")
        new=new.replace("'medical_attempt01'","'medical_attempt03'")
        new=new.replace("'OBSERVED_EVALUATION_EXIT.json'","'OBSERVED_EVALUATION_EXIT_V3.json'")
        if source.name=='final_eval_lossless_v2.py':
            marker='from pathlib import Path\n';assert new.count(marker)==1
            new=new.replace(marker,marker+"import sys\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent/'experiments'))\n",1)
            marker="HERE/'final_eval_lossless_v3.py',HERE/'evaluate_final_lossless_v3.py',HERE/'verify_final_lossless_v3.py',"
            assert new.count(marker)==1;new=new.replace(marker,marker+"HERE/'REPAIR_V3.md',",1)
        ast.parse(new);dest=HERE/source.name.replace('_v2','_v3');assert dest!=source
        with dest.open('x',encoding='utf-8',newline='\n') as f:f.write(new)
        diff=HERE/(dest.name+'.diff_from_v2.txt')
        with diff.open('x',encoding='utf-8') as f:f.write(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=source.name,tofile=dest.name)))
        records.append(dict(original=client.base.entry(ROOT/record['original']['path']),v2=client.base.entry(source),new=client.base.entry(dest),diff=client.base.entry(diff)))
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=records,
        actual_v2_readiness_failure=dict(chunk_id='1a864d',exit_code=1,error='ModuleNotFoundError: mc_rc_3d_baseline_v2_2026_10_07'),
        source_bindings=[client.base.entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',HERE/'REPAIR_V3.md',HERE/'BUILD_RECEIPT.json']]+[r['v2'] for r in records],
        output_bindings=[r['new'] for r in records]+[r['diff'] for r in records],resource_snapshot=client.resource_guard(),
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,original_files_modified=False)
    client.base.new(HERE/'BUILD_RECEIPT_V3.json',q);print(json.dumps(dict(complete=True,new_entries=[r['new'] for r in records]),ensure_ascii=False))
    return 0
if __name__=='__main__':raise SystemExit(main())
