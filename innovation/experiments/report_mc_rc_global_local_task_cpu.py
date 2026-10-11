"""Human-readable complete capability results from frozen validated JSON, without inference."""
import os
for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[name]='1'
import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def fmt(value):return 'undefined' if value is None else '%.6f'%value
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    trainfile=ROOT/'experiments/mc_rc_global_local_task_training_cpu/attempt_01.json'
    valfile=ROOT/'experiments/mc_rc_global_local_task_validation_cpu/attempt_01.json'
    proofile=valfile.parent/'independent_metrics_and_checkpoint_attempt_01.json'
    inputfile=ROOT/'experiments/mc_rc_validation_task_input_cpu/independent_all9_observed_inputs_and_label_axes_attempt_01.json'
    geometryfile=ROOT/'experiments/mc_rc_global_local_geometry_cpu/attempt_01.json'
    diagnosisfile=ROOT/'experiments/mc_rc_global_local_supervision_cpu/attempt_01.json'
    records=[read(p) for p in (trainfile,valfile,proofile,inputfile,geometryfile,diagnosisfile)]
    assert all(r['complete'] and not r['errors'] for r in records)
    train,val,proof,inputs,geometry,diagnosis=records
    assert proof['result_sha256']==sha(valfile)
    report=ROOT/'MC_RC_GLOBAL_LOCAL_TASK_CPU_RESULT_2026-10-03.md'
    calls=train['global_forward_calls']+train['local_forward_calls']+val['global_forward_calls']+val['local_forward_calls']+proof['global_forward_calls']+proof['local_forward_calls']
    lines=['# 全视野/局部任务基线：完整 CPU 验证结果','',
        '**预写能力门槛：'+('通过' if val['capability_gate_passed'] else '未通过')+'。** 这是任务能力基线，不是新重建方法。四验证患者只用于开发验证，八确认保留患者未开效果；科学确认 0，没有可发表的新 claim。','',
        '随机初始化 981,602 参数，全 11 开发人/19 系列、固定 seed20261004、20,000 updates，最后 checkpoint 与 .5 阈值。只用真实 observed 层所生成的 raw PCHIP/observed_shared，平面约 .5 mm、物理 z±2/±1/0 mm 上下文。无中途验证、早停、GT crop、标签定位或后处理。训练、验证和独立重放都已实际结束。','',
        '验证固定 020/022/024/025 四人全部九系列、PCHIP/linear 两条件共 18 项，完整 FOV 和全部原生 z。概率回原生后阈值，计分标签保持原生。两条件相同模型；linear 不是匹配训练对照，不能将差距直接归于重建收益。','',
        '## 患者先聚合的能力端点','',
        '| 输入 | full Dice | supported missing Dice | full recall | full absRVE | 全漏检系列 |','|---|---:|---:|---:|---:|---:|']
    for method in ('raw_pchip','raw_linear'):
        a=val['aggregate'][method];full=a['patient_first_means']['full'];missing=a['patient_first_means']['missing']
        lines.append('| %s | %s | %s | %s | %s | %d |'%(method,fmt(full['dice']),fmt(missing['dice']),fmt(full['recall']),fmt(full['absolute_relative_volume_error']),len(a['series_complete_misses'])))
    lines+=['','各系列先在同患者内等权，再四患者等权。任何 undefined 不按已定义项悄悄缩小分母。','',
            '| 预写检查 | 结果 |','|---|---|']
    for name,passed in val['capability_gate_checks'].items():lines.append('| '+name+' | '+('通过' if passed else '失败')+' |')
    lines+=['','## 全部系列与空间/体积端点','',
        '| 患者 | Series UID | 输入 | full Dice | missing Dice | recall | precision | signed RVE | absRVE | ASSD mm | HD95 mm |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for e in val['evaluations']:
        f=e['metrics']['full'];s=e['metrics']['full_surface']
        lines.append('| '+' | '.join([e['patient'],e['uid'],e['method'],fmt(f['dice']),fmt(e['metrics']['missing']['dice']),fmt(f['recall']),fmt(f['precision']),fmt(f['signed_relative_volume_error']),fmt(f['absolute_relative_volume_error']),fmt(s['assd_mm']),fmt(s['hd95_mm'])])+' |')
    lines+=['','完整 anchors/tail 的 TP/FP/FN、空标记与各端点保留在 [原始结果](experiments/mc_rc_global_local_task_validation_cpu/attempt_01.json)。ASSD/HD95 是双向六邻接 voxel surfaces 距离合并统计，与某些论文的 AVD 定义不同。','',
        '## 输入与独立核验','',
        '- 九个 observed-only 输入：145 个原始观测层、36 个输入条件、九个标签轴完成独立证明；未解码隐藏 MR。',
        '- 几何：三个非方形/边界合成条件、12 个物理 z 检查、九系列×三个完整切面重采样；neural forward 0。',
        '- 18 完整预测分别独立核 bincount 计数与 cKDTree 物理表面距离；固定首/中/末共 54 个完整原生 plane 重放，全体素相等。重放共享冻结 architecture，不是第二独立训练模型。',
        '- checkpoint、初/终权重、训练患者/UID、protocol/code/input SHA 和冻结 diagnostic split 都已对应；四验证患者不转确认。','',
        '本批真实训练 20,000 updates；训练含合成预检的 global/local 调用 '+str(train['global_forward_calls'])+'/'+str(train['local_forward_calls'])+'；验证 '+str(val['global_forward_calls'])+'/'+str(val['local_forward_calls'])+'；复核 '+str(proof['global_forward_calls'])+'/'+str(proof['local_forward_calls'])+'，总模型分支调用 '+str(calls)+'。分支调用不是独立患者、训练步或科学证据数。GPU 初始化 0。','',
        '## 监督规模诊断与结论边界','',
        '只读 19 开发标签、以零值 placeholder MRI 作 608 次固定采样，没有 MR 像素、checkpoint 或网络前向。患者先平均的原生前景比例 '+fmt(diagnosis['patient_first_means']['native_foreground_ratio'])+'；global256 target 前景 mass '+fmt(diagnosis['patient_first_means']['global_positive_mass_mean'])+'；local128 target 前景 mass '+fmt(diagnosis['patient_first_means']['local_positive_mass_mean'])+'。这些是固定诊断分布，不能当本次训练真实梯度或失败原因。','',
        ('能力通过只允许下一步 native 能力和公平曝光×统计×输入矩阵，尚不能判断新方法收益。' if val['capability_gate_passed'] else '能力未通过，这个固定模型不作为重建优劣评价器。不得用它的 PCHIP/linear 差距否证重建或直接任务路线；下一能力方案需另立开发协议，先核可拟合性、loss/采样与原生能力。'),'',
        '新文献三篇/334 文字块加旧文补读 19 块，见 [全视野与小结构阅读](literature/2026-10-03_global_local_task_fulltext_reading.md)和 [loss 阅读](literature/2026-10-03_task_loss_followup_fulltext_reading.md)。级联、复合loss、体积/空间分离和分辨率适应均有先例，不作为宽首创。八名保留患者和第二独立任务网络、正式矩阵与具体可观测修正尚未执行。','']
    report.write_text('\n'.join(lines),encoding='utf-8')
    paths=(trainfile,valfile,proofile,inputfile,geometryfile,diagnosisfile)
    provenance=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        report=report.relative_to(ROOT).as_posix(),report_sha256=sha(report),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths],
        training_updates=20000,total_model_branch_calls=calls,scientific_confirmation_patients=0,
        publication_claim_confirmed=False)
    (valfile.parent/'report_provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(capability_gate_passed=val['capability_gate_passed'],total_model_branch_calls=calls,report=report.name)))
if __name__=='__main__':main()
