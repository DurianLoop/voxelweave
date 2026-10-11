"""Write the failed fixed-baseline report only after independent actual-data replay."""
import json
from pathlib import Path
from residual_addback_cpu import ROOT, OUT, read, sha

def main():
    result=read(OUT/'attempt_01.json');proof=read(OUT/'independent_algebra_and_roi_replay.json')
    if not result['complete'] or result['errors'] or not proof['complete'] or proof['errors'] or proof['result_sha256']!=sha(OUT/'attempt_01.json'): raise ValueError('Real complete independent proof required')
    passed=sum(x['development_gate_passed'] for x in result['series'])
    lines=['# 固定残差相加CPU探索：2/6通过，整体停止','',
           '候选为rawPCHIP+(HAT−pipelinePCHIP)，alpha=1，不新增clip。已见MC-RC五开发缓存及VS-SEG001作者training缓存全部纳入，共297内部缺层。原缓存/两解析基底重算一致，候选另一相加次序的float32完整数组SHA一致；全部四条件、每层支持与病灶ROI及两种加权指标独立dot-product/math.fsum重算errors=[]。共享旧native解码/坐标与解析构造，未复现新神经推断、未做新任务Dice、未新增独立患者。','',
           f'逐项要求相对rawPCHIP/HAT较好者≥0.1dB支持域收益，同时两病灶误差均≤rawPCHIP；实际仅{passed}/6通过。001、002、006及VS-SEG001失败均保留，因此按事前门槛停止固定alpha=1对照，不筛004/005成功子集或后调alpha/clip救结果。','',
           '| 开发材料 | 缺层 | 相对较好raw/HAT支持域收益dB | lesion目标等权守卫 | lesion像素加权守卫 | 全门槛 |',
           '| --- | ---: | ---: | --- | --- | --- |']
    for row in result['series']:
        yes=lambda v:'通过' if v else '失败'
        lines.append('| '+row['patient']+' | '+str(row['targets'])+' | '+f"{row['gain_db_vs_better_raw_or_hat']:.9g}"+' | '+yes(row['lesion_guard']['target_equal_nmse'])+' | '+yes(row['lesion_guard']['pixel_weighted_nmse'])+' | '+yes(row['development_gate_passed'])+' |')
    lines += ['', '相加/detail恢复属于已有普通残差基线，即使成功也不自动是方法创新；本失败说明该固定公式不足以提供统一病灶保护，并不证明一切局部可学习修正都无效。旧native/QDA0/16、原岭失败和收益/误差坐标等价继续有效。当前候选不得进入新任务推断或确认队列。', '',
              '| 开发材料 | 条件 | 支持NMSE目标等权 | lesion NMSE目标等权 | lesion NMSE像素加权 |', '| --- | --- | ---: | ---: | ---: |']
    for row in result['series']:
        for condition,m in row['metrics'].items(): lines.append('| '+row['patient']+' | '+condition+' | '+f"{m['support']['target_equal_nmse']:.10g}"+' | '+f"{m['lesion']['target_equal_nmse']:.10g}"+' | '+f"{m['lesion']['pixel_weighted_nmse']:.10g}"+' |')
    lines += ['', '[原计划](RESIDUAL_ADDBACK_CPU_PLAN_2026-10-03.md)、[全部层分母与结果](experiments/residual_addback_cpu/attempt_01.json)、[独立真实复核](experiments/residual_addback_cpu/independent_algebra_and_roi_replay.json)。这不是神经任务能力或临床安全结论。']
    report=ROOT/'RESIDUAL_ADDBACK_CPU_RESULT_2026-10-03.md';report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    metadata=dict(script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),proof_sha256=sha(OUT/'independent_algebra_and_roi_replay.json'),report_sha256=sha(report),development_items=6,missing_targets=297,passed=passed,fixed_candidate_stopped=result['fixed_candidate_stopped'],new_method_confirmation_patients=0,publication_claim_confirmed=False)
    with (OUT/'report_provenance.json').open('x',encoding='utf-8') as f: json.dump(metadata,f,indent=2)
    print(json.dumps(metadata))

if __name__=='__main__': main()
