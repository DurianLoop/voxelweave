"""Create new source-bound entry versions, preserving all original immutable files."""
import sys,json,difflib,ast
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OLD=ROOT/'experiments'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
def replace_once(text,old,new):
    assert text.count(old)==1,(old,text.count(old));return text.replace(old,new,1)
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();records=[]
    jobs=[('mc_rc_3d_19series_final_eval_2026_10_07.py','final_eval_lossless_v2.py'),
        ('evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py','evaluate_final_lossless_v2.py'),
        ('verify_mc_rc_3d_19series_common_init_final_2026_10_07.py','verify_final_lossless_v2.py')]
    for original,newname in jobs:
        src=OLD/original;old=src.read_text(encoding='utf-8');new=old
        if newname=='final_eval_lossless_v2.py':
            new=replace_once(new,"OUT=ROOT/'experiments/mc_rc_3d_19series_common_init_final_eval_2026_10_07_attempt01'", "HERE=Path(__file__).resolve().parent\nOUT=HERE/'medical_attempt01'")
            new=replace_once(new,"PROTOCOL=ROOT/'MC_RC_3D_19SERIES_COMMON_INIT_FINAL_EVALUATION_EXECUTION_PROTOCOL_2026-10-07.md'", "PROTOCOL=HERE/'PROTOCOL.md'")
            new=replace_once(new,"EVAL_EXIT=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_EVALUATION_2026-10-07.json'", "EVAL_EXIT=HERE/'OBSERVED_EVALUATION_EXIT.json'")
            new=replace_once(new,'np.savez(path,packed_prediction=p,','np.savez_compressed(path,packed_prediction=p,')
            new=replace_once(new,"reasons=[];p=TRAIN/'invocation02.json'", "reasons=[];p=TRAIN/'invocation02.json'\n    if not (HERE/'compression_qualification/receipt.json').exists():reasons.append('Lossless packing qualification receipt absent')")
            new=replace_once(new,'def frozen_training():\n    status=readiness();', "def frozen_training():\n    qualification=read(HERE/'compression_qualification/receipt.json')\n    assert qualification['complete'] and not qualification['errors'] and qualification['all_lossless_interoperability_checks_passed']\n    for b in qualification['production_bindings']:assert sha(ROOT/b['path'])==b['sha256']\n    status=readiness();")
            new=replace_once(new,'sources.extend(ROOT/b[\'path\'] for b in config[\'source_bindings\']);return checkpoints,sources',
                "sources.extend(ROOT/b['path'] for b in config['source_bindings']);sources.extend([HERE/'compression_qualification/receipt.json',\n        HERE/'final_eval_lossless_v2.py',HERE/'evaluate_final_lossless_v2.py',HERE/'verify_final_lossless_v2.py',\n        ROOT/'experiments/mc_rc_3d_19series_final_eval_2026_10_07.py',\n        ROOT/'experiments/evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py',\n        ROOT/'experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py']);return checkpoints,sources")
        else:
            new=replace_once(new,'from mc_rc_3d_19series_final_eval_2026_10_07 import *','from final_eval_lossless_v2 import *')
            if newname=='evaluate_final_lossless_v2.py':
                new=replace_once(new,"ROOT/'experiments/mc_rc_3d_19series_final_eval_2026_10_07.py'", "HERE/'final_eval_lossless_v2.py'")
                new=replace_once(new,"ROOT/'experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py'", "HERE/'verify_final_lossless_v2.py'")
            else:
                new=replace_once(new,"ROOT/'experiments/mc_rc_3d_19series_final_eval_2026_10_07.py'", "HERE/'final_eval_lossless_v2.py'")
        ast.parse(new);dest=HERE/newname
        with dest.open('x',encoding='utf-8',newline='\n') as f:f.write(new)
        diff=HERE/(newname+'.diff.txt')
        with diff.open('x',encoding='utf-8') as f:f.write(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=original,tofile=newname)))
        records.append(dict(original=client.base.entry(src),new=client.base.entry(dest),diff=client.base.entry(diff)))
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=records,
        source_bindings=[client.base.entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md']]+[r['original'] for r in records],
        output_bindings=[r['new'] for r in records]+[r['diff'] for r in records],resource_snapshot=client.resource_guard(),
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,original_files_modified=False)
    client.base.new(HERE/'BUILD_RECEIPT.json',q);print(json.dumps(dict(complete=True,new_entries=[r['new'] for r in records]),ensure_ascii=False))
    return 0
if __name__=='__main__':raise SystemExit(main())
