"""Fix a plot label occlusion and summarize frozen diagnostics; no model or data values loaded."""
import hashlib, json, shutil, sys
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, value):
    with p.open('x', encoding='utf-8') as f:
        if isinstance(value, str): f.write(value)
        else: json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    fitpath = ROOT/'experiments/mc_rc_3d_backbone_context_refit_v2_2026_10_07/attempt01.json'
    diagpath = ROOT/'experiments/mc_rc_3d_backbone_collapse_diagnostic_2026_10_07/attempt01.json'
    fit, diag = read(fitpath), read(diagpath)
    assert fit['complete'] and diag['complete'] and not fit['errors'] and not diag['errors']
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    directory = ROOT/'figures/mc_rc_3d_backbone_context_refit_2026_10_07'
    png = directory/'final_training_domains_and_gates.png'; before = directory/'final_training_domains_and_gates_attempt01.png'
    assert not before.exists(); shutil.copy2(png, before)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), constrained_layout=True)
    domains = ['full','anchors','missing','tail']; x = np.arange(4)
    for i, a in enumerate(fit['arms']):
        values = [a['metrics'][d]['dice'] for d in domains]
        axes[0].bar(x+(i-.5)*.35, [np.nan if z is None else z for z in values], width=.35, label=a['kind'])
        for j, z in enumerate(values):
            axes[0].text(j+(i-.5)*.35, .03 if z is None else z+.02, 'undefined' if z is None else f'{z:.3f}',
                ha='center', fontsize=8, rotation=90 if z is None else 0)
    axes[0].set(xticks=x, xticklabels=domains, ylim=(0,1.13), ylabel='Native-grid Dice', title='Final full-FOV domains')
    axes[0].axhline(.9, color='gray', ls='--', lw=1)
    axes[0].legend(fontsize=7, loc='center right', bbox_to_anchor=(1,.6), framealpha=1)
    x = np.arange(3)
    for i, a in enumerate(fit['arms']):
        m = a['metrics']['full']; values = [a['original_augmented_patch_metrics'][0]['dice'],m['dice'],m['recall']]
        axes[1].bar(x+(i-.5)*.35, [np.nan if z is None else z for z in values], width=.35)
        for j, z in enumerate(values):
            if z is not None: axes[1].text(j+(i-.5)*.35,z+.02,f'{z:.3f}',ha='center',fontsize=8)
    axes[1].set(xticks=x,xticklabels=['FG crop Dice','Full Dice','Full recall'],ylim=(0,1.13),title='Original fit gates (threshold 0.9)')
    axes[1].axhline(.9,color='gray',ls='--',lw=1)
    fig.suptitle('One already-seen development series; 1024 resumed backbone updates per arm',fontsize=11)
    fig.savefig(png,dpi=160);plt.close(fig)
    write(directory/'plot_revision_attempt02.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        original_image=before.relative_to(ROOT).as_posix(),original_sha256=sha(before),revised_image=png.relative_to(ROOT).as_posix(),
        revised_sha256=sha(png),reason='First render legend covered missing-domain numeric label; moved legend to empty tail area.',
        scientific_values_changed=False,actual_revised_view_image_completed=False))
    lines = ['# native接续失败：无更新诊断结果','','主训练、独立核验及本诊断均实际exit0；MRI任务更新0，不评价四验证/八确认。', '',
        '| 输入/模型状态 | 主head全部tile前景概率最大值 | 主head TP（tile实例） | 固定pair BCE encoder L2梯度 | 固定pair soft-Dice encoder L2梯度 |',
        '|---|---:|---:|---:|---:|']
    for m in diag['models']:
        vals = [t['heads'][0]['fg_probability']['max'] for t in m['tiles'] if t['heads'][0]['fg_probability']['n']]
        grads = {g['term']:g['branch_L2_norm']['encoder'] for g in m['fixed_pair_gradient_diagnostic']}
        lines.append(f'| {m["kind"]}/{m["phase"]} | {max(vals):.9g} | {sum(t["heads"][0]["tp"] for t in m["tiles"])} | {grads["bce"]:.9g} | {grads["soft_dice"]:.9g} |')
    lines += ['', '全部16tile、所有3个head、初始/最后checkpoint均纳入，未选择有利head或中途模型。重叠tile TP的分母是tile voxel instances，不是去重完整FOV。native最后三head均无二值预测，其前景概率最大值依次1.07209e-7、1.37078e-6、2.99730e-5。', '',
        'native最后64步含前景的53batch平均loss1.010795；空GT的11batch平均.010529。PCHIP对应.007026/.007151。空batch低loss没有代表病灶拟合成功。', '',
        'native初始主head权重范围[-6.22638,2.49883]，PCHIP为[-3.54885,2.43862]；固定pair native初始soft-Dice encoder L2梯度13.8400，最终2.39979e-7，而最终BCE梯度仍非零。这支持当前存在强负logit/极小soft-Dice梯度的优化状态，不能证明LR、IN、采样或初始化的唯一因果解释，也不证明作者方法问题。', '',
        '下一对照只将恒定lr=.001降为.0001，两臂从原各自相同初始checkpoint重新运行同1024完整tile流；原gate和失败保留。此时不能启动有条件的19series资格，更不能打开确认病例。', '',
        '[完整诊断](experiments/mc_rc_3d_backbone_collapse_diagnostic_2026_10_07/attempt01.json)、[训练端点](MC_RC_3D_BACKBONE_CONTEXT_REFIT_RESULT_2026-10-07.md)、[低LR预定协议](MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_CONTROL_PROTOCOL_2026-10-07.md)。','']
    write(ROOT/'MC_RC_3D_BACKBONE_COLLAPSE_DIAGNOSTIC_RESULT_2026-10-07.md','\n'.join(lines))
    overview = '''# 本轮研究总览：完整context骨干、原文排重与后续对照

目前可发表claim仍未独立确认。11开发患者/19series、4已见验证/9series、8保留确认/12series角色不变；本次任务训练仅一个开发001series，科学确认患者0。所有新增文件在innovation，用户终端训练进程、根环境和.gitignore保持。

## 新的可核验结果

- 两臂各1024次全骨干接续更新，共2048；完整同16tile流、含空tile、最后模型冻结后评分。native full/foreground crop Dice均0、二值预测为空；PCHIP full Dice=.973981、recall=.981207、absRVE=.014837、foreground crop Dice=.930993，过原单series拟合gate，但背景增强crop有278 FP。两臂门槛并未全部通过，不能称强任务能力或SR收益。
- 独立module/functional/四域计数/全部history与SHA重放通过；两臂生产float32与NumPy坐标严格比较本次均过3e-6/0二值差异，独立float64坐标也通过。此前标签往返的5个float32严格失败和1个诊断失败仍保留。
- 无更新的全tile/三head诊断确认native全部head处于强负logit状态，主headFG概率最大1.07209e-7、soft-Dice骨干梯度极小；不能只因空batch loss低判断能力成功。
- 19series共有1139tile，341个起点非下采样步幅8倍数，涉及11series。合成IN反例说明外部变化可改变内部输出；只改对齐/halo不能保证当前eval-IN整图等价。背景中心clamp与均匀合法起点有明显不同采样质量，MRI因果效果仍未验证。
- 新核读Exact Tile、TIN、KIN、KernelNorm共4篇原文，PDF可提取文字55物理页、Exact Tile完整XML176提取块；关键原文8物理页实际渲染核看，其余图像像素未完整检查。旧三篇登记与KernelNorm追加登记分开保留。
- 原KNConv矩差原型float32失败保留；显式中心化窗口原型通过合成float32/float64输出、梯度和局部性资格，float32最大误差6.19465e-7。任务更新0，未做MRI训练、完整网络或作者随机配方复现。

## 创新边界与优先候选

TIN Eq2已覆盖外部参考统计标准化，KIN已有邻域缓存统计及下游分类；Exact Tile已有halo/格点约束，KernelNorm已有局部归一化。因此“换参考统计、做局部统计、修滑窗再评任务”作为机制控制或实现准备，不能独立包装首创。

剩余候选仍是：任务模型充分适配后，仅由真实observed预测一个明确缺层修正动作的paired病灶任务收益。必须超过强PCHIP、同observed直接任务、普通误差/风险头和预算匹配随机控制，并受已读SafeRestore/MoEDiff约束。旧addback、QDA、线性等价/失败和45CISS宽损害反证都保留。原8确认及第二独立训练任务网络只在模型/动作/阈值/端点冻结后使用。

## 已准备的下一步

当前native失败，19series资源资格的条件未满足。下一新阶段为标准低学习率控制：从与本次相同的两臂初始checkpoint重新开始，只将恒定LR降为.0001，同完整tile流、预算、损失和原门槛，不从失败后权重接续、不挑最佳checkpoint。若仍失败，再依据真实结果设计共同初始化/已知优化配置对照，不能改阈值救结果。

GPU已授权，但最近nvidia-smi仍仅free1394MiB（1,461,714,944bytes）、util88%，未达原8,000,000,000bytes启动门槛；完整GPU totals_v2 attempt02入口已准备、仍未运行。当前可用CPU4线程两臂2048更新及评价实测3314.34秒，低LR控制上限5400秒；全19series的实际采样/推断成本仍需独立资格后另冻正式预算。

## 入口

[最后模型及全部域](MC_RC_3D_BACKBONE_CONTEXT_REFIT_RESULT_2026-10-07.md) · [native无更新诊断](MC_RC_3D_BACKBONE_COLLAPSE_DIAGNOSTIC_RESULT_2026-10-07.md) · [三篇原文](literature/2026-10-07_exact_tiling_TIN_KIN_primary_reading.md) · [KernelNorm补读与数值准备](literature/2026-10-07_kernel_norm_primary_reading_and_numerical_preparation.md) · [低LR协议](MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_CONTROL_PROTOCOL_2026-10-07.md) · [19series条件准备](MC_RC_3D_19SERIES_CPU_QUALIFICATION_PREPARATION_2026-10-07.md) · [公开对话](SESSION_VISIBLE_DIALOGUE_BACKBONE_CONTEXT_2026-10-07.md)。

本总览不替代原始记录/分母。用户提供的两份摘要均另存，未展示的历史逐字对话不能重建，不伪造完整聊天导出；本轮可见用户请求、公开进度、脚本、结果、论文来源和失败已保留并将做SHA归档。
'''
    write(ROOT/'SESSION_RESULT_BACKBONE_CONTEXT_2026-10-07.md',overview)
    print(json.dumps(dict(complete=True,summary_written=True,diagnosis_written=True,figure_revised=True)))
if __name__=='__main__':main()
