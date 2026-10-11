"""Report every developer label round trip, including original numerical failures."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
from mc_rc_observed_only_training_input import ROOT,read,sha
def fmt(v):return 'undefined' if v is None else f'{v:.8f}' if isinstance(v,float) else str(v)
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    src=ROOT/'experiments/mc_rc_3d_label_roundtrip_v3_2026_10_07/attempt01.json';p=read(src)
    assert p['complete'] and not p['errors'] and len(p['series'])==19 and len(p['patients'])==11
    dest=ROOT/'MC_RC_3D_LABEL_ROUNDTRIP_RESULT_2026-10-07.md';assert not dest.exists()
    lines=['# 开发标签网格往返：完整结果','',
           '仅11开发患者/19series的GT，没有MR读取/训练/验证/八确认。原float32和独立float64坐标映射两路的0.5预测在全部series一致，因此所有hard端点相同。',
           f"患者内先均值后11患者平均：Dice{p['patient_macro_mean']['dice']:.8f}，recall{p['patient_macro_mean']['recall']:.8f}，absRVE{p['patient_macro_mean']['absRVE']:.8f}。",
           f"原float32 strict数值比较仅{p['production_float32_strict_comparisons_passed']}/19满足3e-6；最大概率误差{max(s['probability_max_absolute_error'] for s in p['series']):.9g}，阈值差异总计{sum(s['prediction_disagreements'] for s in p['series'])}。",
           '新增PyTorch float64坐标后cast float32与独立NumPy19/19通过原3e-6及0预测差异；这不改判生产float32的5个概率误差失败。',
           '', '| 患者/series尾号 | native GT | physical GT | full Dice | recall | absRVE | 原float32概率误差 | 原float32数值门槛 | hard诊断gate |',
           '|---|---:|---:|---:|---:|---:|---:|---|---|']
    for s in p['series']:
        m=s['numpy_metrics']['full'];lines.append('| '+s['patient']+'/'+s['uid'][-6:]+' | '+' | '.join(fmt(v) for v in [s['native_gt_foreground'],s['physical_gt_foreground'],m['dice'],m['recall'],m['absRVE']])+f" | {s['probability_max_absolute_error']:.9g} | {s['production_float32_strict_comparison_passed']} | {s['full_diagnostic_gate_passed']} |")
    lines+=['', '18/19满足full Dice>=0.9、recall>=0.9、absRVE<=0.25、TP>0。011为163 native前景/76 physical前景，回映TP136/FP11/FN27，Dice0.87741935、recall0.83435583；未删除这例或降低门槛。',
            '001第一个系列的标签往返Dice0.98328417明显高于目前全tile head的0.67844794，存在高分的人工physical标签参照；当前弱模型分数不能只用这个往返损失来解释。',
            '标签映射参考不是连续预测的数学性能上界，011也不证明任意连续概率无法达0.9。native与physical前景计数处在不同voxel size，不能直接当物理体积损失百分比。',
            '下一开发配方应保留native评分，并单独考虑hard GT重采样/训练概率映射和小目标监督；已知native-space loss/soft GT/改变grid都是能力对照，不能单独包装新颖性。',
            '', '## 全部四域','', '| 患者/series/域 | Dice | recall | precision | absRVE | TP | FP | FN | TN | GT | pred |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for s in p['series']:
        for k,m in s['numpy_metrics'].items():lines.append('| '+s['patient']+'/'+s['uid'][-6:]+'/'+k+' | '+' | '.join(fmt(m[v]) for v in ('dice','recall','precision','absRVE','tp','fp','fn','tn','gt_foreground','pred_foreground'))+' |')
    lines+=['', '## 失败完整保留','',
            'v1在第6系列概率误差3.4570694e-6超过3e-6，退出失败。v2追加来源列表后误用最后一项作为JSON证书路径，产生JSONDecodeError，0系列完成；v3改为明确证书路径，未修改旧文件。',
            '', '[v3完整结果](experiments/mc_rc_3d_label_roundtrip_v3_2026_10_07/attempt01.json)、[v1失败](experiments/mc_rc_3d_label_roundtrip_2026_10_07/attempt01.json)、[v2失败](experiments/mc_rc_3d_label_roundtrip_v2_2026_10_07/attempt01.json)、[坐标控制补充](MC_RC_3D_LABEL_ROUNDTRIP_COORDINATE_ADDENDUM_V2_2026-10-07.md)。']
    with dest.open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(Path(__file__)),
                result_sha256=sha(src),report_file=dest.relative_to(ROOT).as_posix(),report_sha256=sha(dest),
                developer_series=19,developer_patients=11,hard_diagnostic_gates_passed=18,
                original_float32_strict_comparison_passed=14,original_failed_attempts_preserved=True,scientific_confirmation_patients=0)
    with (src.parent/'report_provenance.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(record))
if __name__=='__main__':main()
