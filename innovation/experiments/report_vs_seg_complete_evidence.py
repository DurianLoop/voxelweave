"""Readable full reports bound to completed independent real-data proofs."""
import csv, json
from pathlib import Path
from vs_seg_selection_sensitivity import sha
ROOT=Path(__file__).resolve().parents[1]

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def number(x): return 'null' if x is None else f'{x:.8g}'
def interval(row):
    if row is None: return 'null'
    ci=row['ci95_percentile']
    return number(row['mean_difference'])+(' ['+', '.join(number(v) for v in ci)+']' if ci is not None else ' [undefined]')

def main():
    primary_path=ROOT/'experiments/vs_seg_complete_analysis_cpu/independent_all_frozen_estimates_replay.json';p=read(primary_path)
    selection_path=ROOT/'experiments/vs_seg_selection_sensitivity/independent_real_all_endpoints_replay.json';s=read(selection_path)
    if not p['complete'] or p['errors'] or not s['complete'] or s['errors'] or p['replayed_endpoints']!=58 or s['endpoints_replayed']!=112: raise ValueError('All real-data proofs required')
    completed_path=ROOT/'experiments/vs_seg_full_volume_queue/completed_analysis.json';c=read(completed_path);result_path=ROOT/s['result_file'];r=read(result_path)
    if sha(completed_path)!=p['completed_analysis_sha256'] or sha(result_path)!=s['result_sha256']: raise ValueError('Evidence binding differs')
    a=c['primary_analysis'];rows=r['analysis']['endpoints'];signs=[x for x in rows if any(x['point_estimate_sign_changes'].values())]
    with (primary_path.parent/'primary_patient_differences.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['patient','hat_minus_pipeline_pchip_support_nmse','hat_minus_pipeline_pchip_original_json_full_dice'])
        for patient,image,task in zip(p['endpoints'][0]['included_patients'],p['endpoints'][0]['patient_differences'],p['endpoints'][1]['patient_differences']): writer.writerow([patient,image,task])
    lines=['# 45 CISS完整结果：原主假设被反证','',
           '原83910实际正常退出，322/322推断条件及46人输出proof完成；固定45CISS主名单和1TSE次要病例均保留。重建像素已逐患者独立再生成，保存任务预测的坐标/混淆/边界指标独立重算；没有声称另行重新推断全部分割网络。新增58个完整统计条目及原112个筛选条目各自独立标量bootstrap复核errors=[]，两套统计seed不同，区间不能混写。','',
           f"固定主HAT−pipelinePCHIP支持NMSE：{interval(a['primary_image_difference'])}；45/45患者降低。",
           f"固定主原JSON完整Dice：{interval(a['primary_task_difference'])}；26提高、16降低、3相同。",
           '预写要求图像差与Dice差的区间上限均<0，实际Dice区间完全为正，所以固定负向联合claim被反证并停止。不能换SwinIR、raw基线或病灶子组救主claim。正向Dice结果也不自动变为原预注册成功或新方法贡献。','',
           '| 条件 | 原JSON Dice均值 | Dice中位数 | RT Dice均值 | 支持NMSE均值 | 原JSON绝对相对体积误差均值 | 空预测/边界非有限 |',
           '| --- | ---: | ---: | ---: | ---: | ---: | --- |']
    for condition in ('native','raw_linear','raw_pchip','pipeline_linear','pipeline_pchip','hat','swinir'):
        original=next(x for x in c['condition_summaries'] if x['condition']==condition and x['reference']=='original_json');rt=next(x for x in c['condition_summaries'] if x['condition']==condition and x['reference']=='rtstruct')
        lines.append('| '+condition+' | '+' | '.join(number(original[k]) for k in ('mean_dice','median_dice'))+' | '+number(rt['mean_dice'])+' | '+number(original['mean_support_nmse'])+' | '+number(original['mean_absolute_relative_volume_error'])+' | '+str(original['empty_predictions'])+'/'+str(original['boundary_infinite_or_undefined_patients'])+' |')
    lines += ['', '强基线敏感性：HAT−rawPCHIP完整Dice −.053454294，描述性95%区间[−.099770378,−.015642155]；同一HAT−pipelinePCHIP为+.036381704。比较的基底处理确实影响点估计方向；它们不是相同信息处理合同，当前结果不单独分离面内缩放、抗混叠、裁剪或任务网络的分布响应。HAT对rawLinear的Dice区间跨0，SwinIR对pipelinePCHIP的Dice区间也跨0；全部结果见下表，不挑有利模型。', '',
              'HAT主比较的RT完整Dice+.037034794，区间[+.008048744,+.072598788]；1mm边界带排除后的Dice+.030980474及+.031037905，两个区间均跨0。slab在本批两标签/八对中与full相同，不是另一独立复制。原JSON病灶NMSE按目标等权和按像素加权结论强弱不同，均在112全表保留。001及202改善反证保留；不能把平均收益说成每个患者安全。', '',
              '次要TSE248保持单列：native Dice .93207054；rawLinear .84852836，rawPCHIP .83836341，pipelinePCHIP .70736086；HAT、SwinIR、pipelineLinear均0。它不能补进45CISS主名单，也不能单例确认协议效应。', '',
              '单中心、模拟抽层、单冻结任务网络、原JSON/历史NIfTI精确等价未证实及离散体素中心边界定义均保留。当前45队列已见结果，今后新选择器不能再将其声称全新未见确认。[本批两正文](literature/2026-10-03_task_utility_fulltext_reading.md)进一步排除图像/任务分离的宽首创。[任务评估器后续准备](FROZEN_TASK_EVALUATOR_FOLLOWUP_PREPARATION_2026-10-03.md)区分冻结pipeline与适配后的任务能力。', '',
              '以下八对全部公开；支持NMSE与六种Dice敏感性为描述性未familywise校正区间，每项有效患者45、undefined0。', '',
              '| 模型−基线 | 支持NMSE差[95%] | 标签/范围 | Dice差[95%] | Dice负/零患者 |', '| --- | --- | --- | --- | --- |']
    for pair in a['descriptive_secondary_pairs']:
        for key,value in pair['task_sensitivity'].items():
            estimate=value['estimate'];lines.append('| '+pair['model']+'−'+pair['baseline']+' | '+interval(pair['support_nmse'])+' | '+key+' | '+interval(estimate)+' | '+str(estimate['negative_patients'])+'/'+str(estimate['zero_patients'])+' |')
    lines += ['', '[58条真实复核](experiments/vs_seg_complete_analysis_cpu/independent_all_frozen_estimates_replay.json)、[逐患者主差CSV](experiments/vs_seg_complete_analysis_cpu/primary_patient_differences.csv)、[原完整自动报告](VS_SEG_FULL_VOLUME_COHORT_COMPLETE_RESULT_2026-10-02.md)、[原45完整合同](experiments/vs_seg_full_volume_cohort/run_contract.json)。']
    (ROOT/'VS_SEG_COMPLETE_EVIDENCE_RESULT_2026-10-03.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    lines=['# 旧四目标筛选的全部112真实端点','',
           '原56604实际正常退出，原敏感性脚本单次完成attempt02（attempt01为此前正确拒绝的不完整门槛），112个唯一端点、5,000次同患者draw、组成和目标选择恒等式全量标量重算errors=[]。所有患者端点分母及所有bootstrap单元均没有undefined；未作familywise校正，不提升为新的主要确认。', '',
           'A=全45/全部缺层，B=资格患者/全部缺层，E=排除者/全部缺层，C=同资格患者/旧四目标。原JSON19入选26排除，RT18入选27排除。完整任务指标没有合法四目标C，表中记“—”，不能把它当0。', '',
           f'112行中{len(signs)}行有至少一种点估计反号，包含标签和full/slab重复敏感性，不能称13个独立发现。主HAT−pipelinePCHIP两标签全部端点没有反号。HAT原JSON全体Dice+.036381704、资格Dice+.004817226、排除Dice+.059448053；RT相应+.037034794、+.003739524、+.059231641。旧资格削弱此任务均值收益，但未反转主方向。', '',
           'HAT−pipelineLinear病灶pixel-weighted NMSE在全体与资格/四目标有点估计反号；SwinIR−pipelineLinear Dice在全体与资格有点估计反号。两者都属固定次要分析，必须看以下全部端点及区间，不选择它们挽救原失败主claim。确定性资格没有排除者入选机会，分解只是描述恒等式，非因果选择偏差校正。', '',
           '| 标签资格 | 模型−基线 | 端点 | A[95%] | B[95%] | E[95%] | C[95%] | 点估计反号 |',
           '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for row in rows:
        est=row['estimates'];flag=', '.join(k for k,v in row['point_estimate_sign_changes'].items() if v) or '无'
        lines.append('| '+row['label_and_qualification']+' | '+row['model']+'−'+row['baseline']+' | '+row['endpoint']+' | '+' | '.join(interval(est[k]) for k in ('all','eligible','excluded'))+' | '+(interval(est['four_targets']) if 'four_targets' in est else '—')+' | '+flag+' |')
    lines += ['', '[全部112独立真实重算](experiments/vs_seg_selection_sensitivity/independent_real_all_endpoints_replay.json)、[完整原结果](experiments/vs_seg_selection_sensitivity/attempt_02.json)、[事后次要合同](VS_SEG_SELECTION_SENSITIVITY_PREPARATION_2026-10-02.md)。每行所有组间shift及其相同draw区间保存在JSON，不能从相邻两CI相减代替。']
    (ROOT/'VS_SEG_SELECTION_SENSITIVITY_REAL_RESULT_2026-10-03.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    metadata=dict(report_script_sha256=sha(__file__),primary_proof_sha256=sha(primary_path),selection_proof_sha256=sha(selection_path),main_patients=45,secondary_patients=1,primary_negative_claim_supported=False,all_estimate_replays=58,all_selection_replays=112,selection_point_sign_change_rows=len(signs),new_method_confirmation_patients=0,publication_claim_confirmed=False,files=[dict(path=(ROOT/name).relative_to(ROOT).as_posix(),sha256=sha(ROOT/name)) for name in ['VS_SEG_COMPLETE_EVIDENCE_RESULT_2026-10-03.md','VS_SEG_SELECTION_SENSITIVITY_REAL_RESULT_2026-10-03.md','experiments/vs_seg_complete_analysis_cpu/primary_patient_differences.csv']])
    with (primary_path.parent/'human_report_provenance.json').open('x',encoding='utf-8') as f: json.dump(metadata,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in metadata.items() if k!='files'}))

if __name__=='__main__': main()
