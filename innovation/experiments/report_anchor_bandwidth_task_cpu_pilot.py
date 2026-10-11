"""Report the complete fixed pilot; no new inference or selective endpoints."""
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/anchor_bandwidth_task_cpu_pilot'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    result = read(OUT / 'attempt_01.json')
    proof = read(OUT / 'independent_inputs_and_all36_estimates.json')
    contract = read(OUT / 'run_contract.json')
    assert result['complete'] and proof['complete']
    assert not result['errors'] and not proof['errors']
    assert proof['result_sha256'] == sha(OUT / 'attempt_01.json')
    assert proof['contract_sha256'] == sha(OUT / 'run_contract.json')
    assert len(result['patients']) == 12 and len(result['analysis']) == 36
    assert proof['normalized_inputs_replayed'] == 12
    assert proof['fixed_missing_identities_verified'] == 6
    assert proof['task_analysis_endpoints_verified'] == 36
    records = []
    metric_rows = []
    for entry in result['patients']:
        assert sha(ROOT / entry['file']) == entry['sha256']
        assert sha(ROOT / entry['verification_file']) == entry['verification_sha256']
        record = read(ROOT / entry['file'])
        assert record['complete'] and not record['cuda_initialized']
        records.append(record)
        for reference, domains in record['task_metrics'].items():
            for domain, m in domains.items():
                metric_rows.append(dict(patient=record['patient'], condition=record['condition'],
                    reference=reference, domain=domain, tp=m['tp'], fp=m['fp'], fn=m['fn'],
                    dice=m['dice'], dice_status=m['dice_status'],
                    signed_relative_volume_error=m.get('signed_relative_volume_error'),
                    assd_mm=m.get('boundary', {}).get('assd_mm'),
                    hd95_mm=m.get('boundary', {}).get('hd95_mm'),
                    missing_network_input_unchanged=record['missing_network_input_bitwise_equal_to_baseline']))
    endpoint_rows = []
    paired_rows = []
    for entry in result['analysis']:
        values = [x['difference'] for x in entry['patient_differences']]
        assert len(values) == entry['defined_n']
        assert math.isclose(math.fsum(values) / len(values), entry['mean'], abs_tol=1e-12)
        endpoint_rows.append(dict(comparison=entry['comparison'], reference=entry['reference'],
            domain=entry['domain'], original_denominator=entry['original_denominator'],
            defined_n=entry['defined_n'], undefined_patients=';'.join(entry['undefined_patients']),
            mean_difference=entry['mean'], positive=sum(v > 0 for v in values),
            negative=sum(v < 0 for v in values), zero=sum(v == 0 for v in values)))
        for patient in entry['patient_differences']:
            paired_rows.append(dict(comparison=entry['comparison'], reference=entry['reference'],
                domain=entry['domain'], **patient))
    paths = [OUT / 'all36_descriptive_task_endpoints.csv', OUT / 'all108_patient_differences.csv',
             OUT / 'all72_condition_label_domain_metrics.csv']
    for path, rows in zip(paths, [endpoint_rows, paired_rows, metric_rows]):
        write_csv(path, rows)
    lines = ['# 三人 anchors-only × 归一化任务预检：完整结果', '',
        '固定 VS-SEG-202/203/204，各四条件，12 次新增 CPU 前向。producer session55424、最终输入/标量 verifier11226 均实际 exit0。12 个保存预测的指标复核、12 个完整网络输入 SHA 重放、6 个 fixed 缺层身份与全部 36 个配对端点均通过。没有使用 GPU；科学独立确认患者为 0。', '',
        '这是开发机制诊断。四条件都改变 observed anchors，违反原 observed-preserving SR 合同，因此其结果不能当作可部署 SR 方法改进。fixed 使用相应 raw/post 基线的全体积均值和标准差；缺层及 tail 网络输入逐位不变。own 使用干预自己的统计量，会同时改变缺层的归一化输入。', '',
        '| 预先固定比较 | JSON full 平均 ΔDice | RTSTRUCT full 平均 ΔDice |',
        '| --- | ---: | ---: |']
    for comparison in dict.fromkeys(x['comparison'] for x in result['analysis']):
        values = [next(x['mean'] for x in result['analysis'] if x['comparison'] == comparison
            and x['reference'] == ref and x['domain'] == 'full') for ref in ('original_json', 'rtstruct')]
        lines.append(f'| {comparison} | {values[0]:+.8f} | {values[1]:+.8f} |')
    lines += ['', '| 患者 | JSON full post_fixed−post | RTSTRUCT full post_fixed−post |',
              '| --- | ---: | ---: |']
    for patient in contract['roster']:
        values = [next(v['difference'] for x in result['analysis'] if x['comparison'] == 'post_anchor_fixed-post'
            and x['reference'] == ref and x['domain'] == 'full' for v in x['patient_differences']
            if v['patient'] == patient) for ref in ('original_json', 'rtstruct')]
        lines.append(f'| {patient} | {values[0]:+.8f} | {values[1]:+.8f} |')
    lines += ['', '主要关注的 JSON full post_fixed−post 均值为 −.00505496，三人分别 −.00149780、−.02975063、+.01608354。RTSTRUCT full 均值为 −.00507443。当前结果不支持“同时处理 anchors、平衡带宽就能恢复 post 分割表现”的固定解释；停止这一恢复主张，不盲目扩展到全 45 人。', '',
        'raw_fixed−raw 的 full 平均为正（JSON +.00958135、RT +.00944103），但 202 仍变差；不能改用 raw 条件挽救原 post 恢复解释。post 的 own−fixed 平均为负（JSON −.00307727），只能描述这个实现下归一化选择的条件效应，不能说全体积归一化解释了全部损失。', '',
        '保留域反例：JSON 去 1mm reference 边界的 post_fixed−post 为 +.02011658，RT 为 +.01731318，与 full 的负均值不同。去边界域同时排除带内的 FP/FN，不是独立“病灶核心恢复”证据。该三人 full/slab Dice 相同，不能当作重复的独立成功。n=3，不进行 bootstrap 显著性声明，不挑患者、标签、域或条件。', '',
        '| 比较 | 标签 | 域 | n | 平均 ΔDice | 正/负/零 |',
        '| --- | --- | --- | ---: | ---: | --- |']
    for row in endpoint_rows:
        lines.append(f"| {row['comparison']} | {row['reference']} | {row['domain']} | {row['defined_n']} | {row['mean_difference']:+.8f} | {row['positive']}/{row['negative']}/{row['zero']} |")
    lines += ['', 'fixed 条件保持缺层网络输入相同，但改变邻层上下文；3D 网络及滑窗仍可使缺层输出变化。该事实只在实际 checkpoint/预处理/阈值下成立，不证明局部解剖损伤、临床危害或恢复机制。输入重放共享 decoder/PCHIP/resize/NumPy；不是独立来源、独立任务模型或完整第二软件栈复现。', '',
        '后续先检查任务评估器暴露与完整操作链，保持 raw 原网格强对照；将来训练使用跨输入 × 跨任务网络矩阵，且需要真正未用于选择的确认患者。不得重启已结束队列，也不得把当前失败用新名字覆盖。', '',
        '证据：[事前方案](ANCHOR_BANDWIDTH_TASK_CPU_PILOT_PLAN_2026-10-03.md)、[全部36端点](experiments/anchor_bandwidth_task_cpu_pilot/all36_descriptive_task_endpoints.csv)、[108逐人配对值](experiments/anchor_bandwidth_task_cpu_pilot/all108_patient_differences.csv)、[72条件/标签/域指标](experiments/anchor_bandwidth_task_cpu_pilot/all72_condition_label_domain_metrics.csv)、[最终独立输入与标量复核](experiments/anchor_bandwidth_task_cpu_pilot/independent_inputs_and_all36_estimates.json)。']
    report = ROOT / 'ANCHOR_BANDWIDTH_TASK_CPU_PILOT_RESULT_2026-10-03.md'
    report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    provenance = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__),
        result_sha256=sha(OUT / 'attempt_01.json'), proof_sha256=sha(OUT / 'independent_inputs_and_all36_estimates.json'),
        outputs=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in [report, *paths]],
        new_neural_forwards=0, publication_claim_confirmed=False, main_recovery_explanation_supported=False)
    (OUT / 'report_provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(report=report.name, endpoints=len(endpoint_rows), paired_rows=len(paired_rows),
        metric_rows=len(metric_rows), new_neural_forwards=0, errors=[]), ensure_ascii=False))


if __name__ == '__main__':
    main()
