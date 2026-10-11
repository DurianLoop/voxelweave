"""Preserve failed attempt01 and generate attempt02, reusing only authenticated completed predictions."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    source=ROOT/'experiments/diagnose_mc_rc_frozen_global_local_development_cpu.py'
    target=ROOT/'experiments/diagnose_mc_rc_frozen_global_local_development_attempt02_cpu.py';assert not target.exists()
    text=source.read_text(encoding='utf-8').replace('import json,sys,time,traceback','import json,sys,time,traceback,copy,shutil')
    text=text.replace('from mc_rc_task_metrics_cpu import metrics','from mc_rc_full_affine_task_metrics_cpu import metrics')
    text=text.replace("OUT=ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu'", "FAILED=ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu'\nOUT=ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02'")
    text=text.replace("'diagnose_mc_rc_frozen_global_local_development_cpu.py',", "'diagnose_mc_rc_frozen_global_local_development_attempt02_cpu.py','mc_rc_full_affine_task_metrics_cpu.py',")
    text=text.replace('    write(path,r)\n    try:', '''    failedpath=FAILED/'attempt_01.json';failed=read(failedpath)
    assert not failed['complete'] and failed['errors']==['AssertionError: ']
    assert 'surface_metrics' in failed['traceback'] and len(failed['evaluations'])==3
    for item in failed['code_bindings']:assert sha(ROOT/item['path'])==item['sha256']
    r['source_bindings'].append(dict(path=failedpath.relative_to(ROOT).as_posix(),sha256=sha(failedpath)))
    r['retained_failed_attempt']='experiments/mc_rc_frozen_global_local_development_diagnosis_cpu/attempt_01.json'
    r['reused_complete_predictions']=0
    r['runtime_preflight']=failed['runtime_preflight']
    r['affine_metrics_resume_protocol_sha256']=sha(ROOT/'MC_RC_FROZEN_DEVELOPMENT_AFFINE_RESUME_PROTOCOL_2026-10-03.md')
    write(path,r)
    try:''')
    text=text.replace('            resource_gate();obs=load_authenticated_observed(case,by[case[\'uid\']])', '''            if index<3:
                old=failed['evaluations'][index];assert old['uid']==case['uid'] and old['patient']==case['patient']
                oldfile=ROOT/old['prediction_file'];assert sha(oldfile)==old['prediction_file_sha256']
                with np.load(oldfile,allow_pickle=False) as data:pred=data['prediction_rcz'].copy()
                assert array_sha(pred)==old['prediction_array_sha256']
                obs=load_authenticated_observed(case,by[case['uid']]);label=read_supervised_label(case)
                assert array_sha(label)==old['label_array_sha256']
                row=copy.deepcopy(old);newfile=OUT/oldfile.name;shutil.copyfile(oldfile,newfile)
                row['prediction_file']=newfile.relative_to(ROOT).as_posix();row['metrics']=metrics(pred,label,obs)
                row['reused_from_failed_attempt_complete_row']=True
                row['new_global_forward_calls']=0;row['new_local_forward_calls']=0
                r['evaluations'].append(row);r['reused_complete_predictions']+=1;write(path,r)
                print(json.dumps(dict(patient=case['patient'],uid=case['uid'],completed_prediction_reused=True)),flush=True)
                del pred,label,obs
                continue
            resource_gate();obs=load_authenticated_observed(case,by[case['uid']])''')
    assert 'completed_prediction_reused=True' in text
    target.write_text(text,encoding='utf-8')
    proof=ROOT/'experiments/frozen_development_affine_resume_generation.json'
    proof.write_text(json.dumps(dict(source=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),
        output=target.relative_to(ROOT).as_posix(),output_sha256=sha(target),generator_sha256=sha(__file__)),indent=2)+'\n',encoding='utf-8')
    print('Prepared separate attempt02, original attempt01 and script preserved.')
if __name__=='__main__':main()
