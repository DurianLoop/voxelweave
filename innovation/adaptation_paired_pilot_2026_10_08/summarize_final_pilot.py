"""All frozen final branches versus matched controls and unchanged parent, descriptive only."""
import json,hashlib,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    resource_guard();p=HERE/'evaluation_attempt01/receipt.json';q=json.loads(p.read_text());ex=json.loads((HERE/'ACTUAL_EVALUATION_EXIT.json').read_text())
    assert ex['observed_tool_exit']==0 and ex['result_sha256']==sha(p)
    assert q['complete'] and not q['errors'] and q['all36_strict_gates_passed'] and len(q['arms'])==4
    parentfile=ROOT/'final_training_medical_execution_2026_10_08/precision_v4_attempt01/receipt.json';parent=json.loads(parentfile.read_text())
    rows=[];all_arms={};comparisons=[]
    for kind in ['native_reference','raw_pchip']:
        a=next(a for a in parent['arms'] if a['kind']==kind);arms=[('parent',a)]
        arms.extend((aug,next(a for a in q['arms'] if a['kind']==kind and a['augmentation']==aug)) for aug in ['basic','strong'])
        for name,a in arms:
            agg=a['validation_aggregate'];f=agg['patient_first_means']['full'];m=agg['patient_first_means']['missing']
            rows.append(dict(kind=kind,condition=name,full_Dice=f['dice'],missing_Dice=m['dice'],full_recall=f['recall'],full_absRVE=f['absolute_relative_volume_error'],
                gates_passed=sum(a['validation_gates'].values()),zero_TP_series=len(agg['complete_miss_series']),empty_prediction_series=len(agg['empty_prediction_series'])))
            all_arms[(kind,name)]=a
        for control in ['basic','parent']:
            strong=all_arms[(kind,'strong')]['validation_aggregate'];base=all_arms[(kind,control)]['validation_aggregate']
            assert set(strong['patients'])==set(base['patients']) and len(strong['patients'])==4
            changes=[]
            for patient in sorted(strong['patients']):
                s=strong['patients'][patient]['metrics'];b=base['patients'][patient]['metrics']
                changes.append(dict(patient=patient,full_Dice_delta=s['full']['dice']-b['full']['dice'],
                    missing_Dice_delta=s['missing']['dice']-b['missing']['dice'],full_recall_delta=s['full']['recall']-b['full']['recall'],
                    full_absRVE_delta=s['full']['absolute_relative_volume_error']-b['full']['absolute_relative_volume_error']))
            comparisons.append(dict(kind=kind,contrast='strong-minus-'+control,patient_deltas=changes,
                patient_first_mean_full_Dice_delta=sum(c['full_Dice_delta'] for c in changes)/4))
    r=dict(complete=True,errors=[],rows=rows,comparisons=comparisons,validation_patients=4,validation_series=9,
        new_branches_complete_FOVs=36,all_strict_numeric_passed=True,all_new_branches_medical_gates_passed=q['all_four_branches_medical_gates_passed'],
        interpretation='Exploratory fixed99step continuation on already-seen validation; no independent confirmation or sufficient adaptation established',
        primary_patient_denominators_unchanged=True,intermediate_checkpoint_selection=False,statistical_significance_claimed=False,
        new_training_updates_this_summary=0,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,
        publication_claim_confirmed=False,goal_status='active',source_bindings=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x))
            for x in [Path(__file__),p,HERE/'ACTUAL_EVALUATION_EXIT.json',parentfile]])
    with (HERE/'FINAL_DESCRIPTIVE_COMPARISON.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    md=['# 固定99步配对续训：完整评价','', '原父模型与四个新最后state一起报告；所有数字为已见4患者/9series的患者先均值。', '',
        '| 输入 | 条件 | full Dice | missing Dice | recall | absRVE | 六门槛通过 | 零TP series | 空预测 series |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for s in rows:
        md.append('| '+s['kind']+' | '+s['condition']+' | '+' | '.join(f'{s[k]:.6f}' for k in ['full_Dice','missing_Dice','full_recall','full_absRVE'])+f" | {s['gates_passed']}/6 | {s['zero_TP_series']} | {s['empty_prediction_series']} |")
    md.extend(['','四个新分支共36生产+36functional完整FOV，严格数值/坐标/二值/计数/患者聚合均完成；不是第三次跨进程重跑。',
        '', 'strong-minus-basic与strong-minus-parent逐患者差异见JSON。训练配方只有99步续训；重置optimizer对两个匹配分支相同，父模型未作该次更新。强度增强优于本次basic不等于优于原父模型或达到医学能力。',
        '', '没有新独立确认、显著性或充分适配结论；8确认患者与lockedIXI未打开，科研goal仍active。'])
    with (HERE/'FINAL_DESCRIPTIVE_COMPARISON.md').open('x',encoding='utf-8') as f:f.write('\n'.join(md)+'\n')
    print(json.dumps(dict(complete=True,rows=rows,all_new_branches_medical_gates_passed=q['all_four_branches_medical_gates_passed']),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
