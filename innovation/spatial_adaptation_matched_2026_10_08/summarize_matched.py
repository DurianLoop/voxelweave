"""Spatial effect against same-budget intensity; parent reported separately, no confirmation claim."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    resource_guard();p=HERE/'evaluation_attempt01/receipt.json';q=read(p);ex=read(HERE/'ACTUAL_EVALUATION_EXIT.json')
    assert ex['observed_tool_exit']==0 and ex['result_sha256']==sha(p)
    assert q['complete'] and not q['errors'] and q['all36_strict_gates_passed'] and len(q['arms'])==4
    parentfile=ROOT/'final_training_medical_execution_2026_10_08/precision_v4_attempt01/receipt.json';parent=read(parentfile)
    parentexit=ROOT/'final_training_medical_execution_2026_10_08/ACTUAL_PRECISION_V4_EXIT.json';pex=read(parentexit)
    assert pex['observed_tool_exit']==0 and pex['result_sha256']==sha(parentfile)
    rows=[];comparisons=[]
    for kind in ['native_reference','raw_pchip']:
        pa=next(a for a in parent['arms'] if a['kind']==kind)
        ia=next(a for a in q['arms'] if a['kind']==kind and a['augmentation']=='intensity')
        sa=next(a for a in q['arms'] if a['kind']==kind and a['augmentation']=='spatial')
        for name,a in [('parent',pa),('intensity2992',ia),('spatial2992',sa)]:
            agg=a['validation_aggregate'];f=agg['patient_first_means']['full'];m=agg['patient_first_means']['missing']
            rows.append(dict(kind=kind,condition=name,full_Dice=f['dice'],missing_Dice=m['dice'],full_recall=f['recall'],
                full_absRVE=f['absolute_relative_volume_error'],gates_passed=sum(a['validation_gates'].values()),
                zero_TP_series=len(agg['complete_miss_series']),empty_prediction_series=len(agg['empty_prediction_series'])))
        for control,ba in [('intensity2992',ia),('parent',pa)]:
            s=sa['validation_aggregate'];b=ba['validation_aggregate'];assert set(s['patients'])==set(b['patients']) and len(s['patients'])==4
            deltas=[]
            for patient in sorted(s['patients']):
                sm=s['patients'][patient]['metrics'];bm=b['patients'][patient]['metrics']
                deltas.append(dict(patient=patient,series=s['patients'][patient]['series'],
                    full_Dice_delta=sm['full']['dice']-bm['full']['dice'],missing_Dice_delta=sm['missing']['dice']-bm['missing']['dice'],
                    full_recall_delta=sm['full']['recall']-bm['full']['recall'],full_absRVE_delta=sm['full']['absolute_relative_volume_error']-bm['full']['absolute_relative_volume_error']))
            comparisons.append(dict(kind=kind,contrast='spatial2992-minus-'+control,matched_update_budget=control=='intensity2992',
                patient_deltas=deltas,patient_first_mean_full_Dice_delta=sum(c['full_Dice_delta'] for c in deltas)/4,
                positive_full_Dice_patients=sum(c['full_Dice_delta']>0 for c in deltas)))
    r=dict(complete=True,errors=[],rows=rows,comparisons=comparisons,validation_patients=4,validation_series=9,new_FOVs=36,
        all_strict_numeric_passed=True,all_new_branches_medical_gates_passed=q['all_four_branches_medical_gates_passed'],
        interpretation='Already-seen validation, fixed2992step matched augmentation continuation. No independent confirmation, significance or SR/action-utility attribution.',
        primary_contrast='spatial2992-minus-intensity2992 within each input',primary_patient_denominators_unchanged=True,
        intermediate_checkpoint_selection=False,statistical_significance_claimed=False,medical_arrays_loaded=0,GT_arrays_loaded=0,
        model_arrays_loaded=0,neural_forwards=0,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in [Path(__file__),p,HERE/'ACTUAL_EVALUATION_EXIT.json',parentfile,parentexit]])
    with (HERE/'FINAL_MATCHED_COMPARISON.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    md=['# 固定2992步匹配空间增强：完整结果','',
        '以下为原已见4患者/9series患者先均值；同输入spatial2992-minus-intensity2992为预算匹配的增强对照。parent未接受本轮续训，仅作描述。','',
        '| 输入 | 条件 | full Dice | missing Dice | recall | absRVE | 六门槛通过 | 零TP series | 空预测 series |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for s in rows:md.append('| '+s['kind']+' | '+s['condition']+' | '+' | '.join(f'{s[k]:.6f}' for k in ['full_Dice','missing_Dice','full_recall','full_absRVE'])+f" | {s['gates_passed']}/6 | {s['zero_TP_series']} | {s['empty_prediction_series']} |")
    md.extend(['','全部36生产+36functional完整FOV严格数值、坐标、二值、独立计数与患者聚合通过。两实现同进程，不是跨进程重跑或未见确认。','',
        '逐患者效应和体积误差完整保留在JSON。不能以parent或旧99步对比替代本轮匹配control；不能把增强收益归因SR或动作收益。', '',
        '8未见确认患者/12series和locked IXI未打开，六医学门槛保持原定义。标准增强本身不当创新，科研goal仍active。'])
    with (HERE/'FINAL_MATCHED_COMPARISON.md').open('x',encoding='utf-8') as f:f.write('\n'.join(md)+'\n')
    print(json.dumps(dict(complete=True,rows=rows,all_new_branches_medical_gates_passed=q['all_four_branches_medical_gates_passed']),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
