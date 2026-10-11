"""Report every final arm/domain/gate after actual training and independent verification exits."""
import json, sys
from pathlib import Path
from datetime import datetime, timezone
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT, read, sha, np
def write(p, text):
    with p.open('x', encoding='utf-8') as f: f.write(text)
def number(v): return 'undefined' if v is None else f'{v:.6f}'
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    path = ROOT/'experiments/mc_rc_3d_backbone_context_refit_v2_2026_10_07/attempt01.json'
    r = read(path); vpath = path.parent/'independent_both1024_and_full_fov_attempt01.json'; v = read(vpath)
    assert all(o['complete'] and not o['errors'] for o in (r, v)) and v['result_sha256'] == sha(path)
    assert r['actual_cpu_backbone_updates'] == 2048 and not r['cuda_initialized'] and not v['cuda_initialized']
    lines = ['# 完整context骨干接续拟合：最后模型结果', '',
        '本阶段仅开发VS-MC-RC-001的一个已见series；两臂各1024次更新所有参数，共2048。主训练与独立核验的工具退出码均实际观察为0。两臂最后checkpoint均冻结后才评分；未选择中途/最佳模型。', '',
        f'4 intra-op/1 interop、自身below-normal、AdamW恒定lr=.001、weight_decay=.0001、原三尺度BCE+Dice、同一冻结16tile流的128轮、含空tile、无增强。训练及主评价总墙钟{r["elapsed_seconds"]:.2f}秒；独立核验{v["elapsed_seconds"]:.2f}秒。GPU训练0、CUDA未初始化。', '',
        '## 原门槛逐项结果', '', '| 输入 | 原foreground crop Dice | full Dice | full recall | full absRVE | TP | 全部原gate |', '|---|---:|---:|---:|---:|---:|---|']
    for a in r['arms']:
        m = a['metrics']['full']; c = a['original_augmented_patch_metrics'][0]
        lines.append(f'| {a["kind"]} | {number(c["dice"])} | {number(m["dice"])} | {number(m["recall"])} | {number(m["absRVE"])} | {m["tp"]} | {"通过" if a["training_fit_gate_passed"] else "失败"} |')
    lines += ['', '固定gate：foreground crop Dice≥.9；full Dice≥.9、recall≥.9、absRVE≤.25、TP>0。任一失败保持失败，不以其他域或数值实现的有利结果替换。', '',
        '## 全部域与分母', '', '| 输入 | 域 | GT前景 | 预测前景 | TP | FP | FN | Dice | recall | precision | absRVE |', '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for a in r['arms']:
        for domain, m in a['metrics'].items():
            values = [a['kind'], domain, *[str(m[k]) for k in ('gt_foreground','pred_foreground','tp','fp','fn')],
                *[number(m[k]) for k in ('dice','recall','precision','absRVE')]]
            lines.append('| '+' | '.join(values)+' |')
    lines += ['', 'anchors为真实每4层观测；missing仅最后anchor之前未观测层；tail为最后anchor之后。空GT/空预测与undefined保留，未删除或视为Dice=1。', '',
        '## 原两个增强crop（包括背景crop）', '', '| 输入 | crop编号 | GT前景 | 预测前景 | TP | FP | FN | Dice | recall | absRVE |', '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for a in r['arms']:
        for i, m in enumerate(a['original_augmented_patch_metrics']):
            values = [a['kind'], str(i), *[str(m[k]) for k in ('gt_foreground','pred_foreground','tp','fp','fn')],
                *[number(m[k]) for k in ('dice','recall','absRVE')]]
            lines.append('| '+' | '.join(values)+' |')
    lines += ['', 'PCHIP原背景增强crop存在278个FP；其通过预定foreground/full-FOV拟合gate不等于所有输入context均无FP。', '',
        '## 独立实现与坐标精度', '', '| 输入 | 生产坐标重放概率最大差 | 阈值不一致 | float32/NumPy坐标最大差 | 阈值不一致 | 原严格坐标gate | float64/NumPy坐标最大差 | 阈值不一致 |', '|---|---:|---:|---:|---:|---|---:|---:|']
    for a in v['arms']:
        f32 = a['production_float32_vs_numpy_coordinate']; f64 = a['independent_float64_coordinate']
        lines.append(f'| {a["kind"]} | {a["production_coordinate_replay_max_probability_error"]:.9g} | {a["production_coordinate_replay_threshold_disagreements"]} | {f32["max_probability_error"]:.9g} | {f32["threshold_disagreements"]} | {"通过" if f32["original_strict_gate_passed"] else "失败（保留）"} | {f64["max_probability_error"]:.9g} | {f64["threshold_disagreements"]} |')
    lines += ['', '两臂完整1024行history、同一随机tile stream、每batch真实GT计数、所有16tile每轮覆盖、checkpoint/预测SHA和参数变更已核。module与functional逐tile所有三个head核验通过；四域contingency table及原crop gate独立重算一致。生产坐标与float64坐标结果分开；float64通过不改判float32失败。原端点以生产float32坐标、threshold=.5为准。', '',
        '## 与旧诊断的联系及限制', '',
        '旧两个固定crop全网络512更新、冻结骨干两个crop head1024更新、全16tile head1024更新的失败均保留。本次接续同时改变可训练参数集合、输入context与采样域；它是已见series拟合诊断，不能单独归因于某个机制。历史head模型没有被替换或重命名。', '',
        f'两臂全部原gate是否通过：{r["both_original_fit_gates_passed"]}。即使通过也只证明此已见series和这些训练条件；不能称完整11患者/19series能力、四验证能力、SR损害或收益、第二独立任务网络、患者外科学确认。', '',
        '原始记录：[训练](experiments/mc_rc_3d_backbone_context_refit_v2_2026_10_07/attempt01.json)、[独立核验](experiments/mc_rc_3d_backbone_context_refit_v2_2026_10_07/independent_both1024_and_full_fov_attempt01.json)、[论文核读](literature/2026-10-07_exact_tiling_TIN_KIN_primary_reading.md)、[KernelNorm补读与数值准备](literature/2026-10-07_kernel_norm_primary_reading_and_numerical_preparation.md)。', '']
    write(ROOT/'MC_RC_3D_BACKBONE_CONTEXT_REFIT_RESULT_2026-10-07.md', '\n'.join(lines))
    ledger = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__),
        training_observed_tool_session_id=49978, training_observed_tool_exit=0, independent_verifier_observed_tool_exit=0,
        own_live_runs=[], all_own_runs_terminal_from_observed_tool_exits=True, new_cpu_backbone_updates=2048,
        cpu_resource_qualification_updates_discarded=12, new_gpu_updates=0, synthetic_local_operator_task_updates=0,
        prior_failed_attempts_preserved=True, training_patient_ids=r['training_patient_ids'], training_series=1,
        validation_effects_opened=False, confirmation_patients_opened=False, scientific_confirmation_patients=0,
        publication_claim_confirmed=False, goal_status='active', root_environment_or_gitignore_modified=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in (path, vpath)])
    write(ROOT/'SESSION_EXECUTION_LEDGER_BACKBONE_CONTEXT_2026-10-07.json', json.dumps(ledger, ensure_ascii=False, indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figdir = ROOT/'figures/mc_rc_3d_backbone_context_refit_2026_10_07'; figdir.mkdir(exist_ok=False)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), constrained_layout=True)
    domains = ['full','anchors','missing','tail']; x = np.arange(4)
    for i, a in enumerate(r['arms']):
        values = [a['metrics'][d]['dice'] for d in domains]
        axes[0].bar(x+(i-.5)*.35, [np.nan if z is None else z for z in values], width=.35, label=a['kind'])
        for j, z in enumerate(values):
            axes[0].text(j+(i-.5)*.35, .03 if z is None else z+.02, 'undefined' if z is None else f'{z:.3f}',
                ha='center', fontsize=8, rotation=90 if z is None else 0)
    axes[0].set(xticks=x, xticklabels=domains, ylim=(0,1.13), ylabel='Native-grid Dice', title='Final full-FOV domains')
    axes[0].axhline(.9, color='gray', ls='--', lw=1); axes[0].legend(fontsize=8, loc='upper right')
    labels = ['FG crop Dice','Full Dice','Full recall']; x = np.arange(3)
    for i, a in enumerate(r['arms']):
        m = a['metrics']['full']; values = [a['original_augmented_patch_metrics'][0]['dice'], m['dice'], m['recall']]
        axes[1].bar(x+(i-.5)*.35, [np.nan if z is None else z for z in values], width=.35)
        for j, z in enumerate(values):
            if z is not None: axes[1].text(j+(i-.5)*.35, z+.02, f'{z:.3f}', ha='center', fontsize=8)
    axes[1].set(xticks=x, xticklabels=labels, ylim=(0,1.13), title='Original fit gates (threshold 0.9)')
    axes[1].axhline(.9, color='gray', ls='--', lw=1)
    fig.suptitle('One already-seen development series; 1024 resumed backbone updates per arm', fontsize=11)
    fig.savefig(figdir/'final_training_domains_and_gates.png', dpi=160); plt.close(fig)
    print(json.dumps(dict(complete=True, result_report_written=True, figure_written=True,
        both_original_fit_gates_passed=r['both_original_fit_gates_passed'])))
if __name__ == '__main__': main()
