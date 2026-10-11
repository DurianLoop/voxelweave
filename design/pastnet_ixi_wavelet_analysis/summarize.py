"""Verify the completed frozen IXI evaluation and write a Chinese result report."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from pastnet_v2.common import sha256,write_json
from pastnet_ixi_wavelet.run import ROOT,hashes


def main():
    out=ROOT/'results/test115_seed3407'
    report=json.loads((out/'report.json').read_text())
    lock=json.loads((out/'lock.json').read_text())
    audit=json.loads((ROOT/'results/full_train_audit.json').read_text())
    manifest=json.loads((ROOT/'manifest.json').read_text())
    train=ROOT/'runs/full_wavelet3_ixi_seed3407'
    assert report['completed'] and not report['smoke'] and report['patients']==115
    assert lock['code_hashes']==hashes() and lock['split']=='test'
    assert sha256(train/'best.pth')==lock['candidate_sha256']==audit['best_sha256']
    expected={x['patient_id'] for x in manifest['records'] if x['split']=='test'}
    old=json.loads((ROOT.parents[1]/'baseline/ixi_i3net/runs/full_test115_stable/run_manifest.json').read_text())
    lengths={Path(x['source']).name.split('-')[0]:((x['source_depth']-1)//4)*3 for x in old['eval_cases']}
    slices=pd.read_csv(out/'per_slice.csv')
    metrics=list(report['metrics'])
    assert not slices.duplicated(['method','patient_id','z']).any()
    assert np.isfinite(slices[metrics].to_numpy()).all()
    assert (slices.z%4!=0).all()
    patients=slices.groupby(['method','patient_id'])[metrics].mean()
    x=patients.loc['past_wavelet'].sort_index();y=patients.loc['i3net'].sort_index()
    assert set(x.index)==set(y.index)==expected and x.index.equals(y.index)
    for method in ('past_wavelet','i3net'):
        counts=slices[slices.method==method].groupby('patient_id').size().to_dict()
        assert counts==lengths
    draw=np.random.default_rng(73019).integers(0,115,(10000,115))
    lower={'mae','mse','hd95_proxy','tail10_mse'}
    quality_ok=True
    for metric in metrics:
        d=(x[metric]-y[metric]).to_numpy();record=report['metrics'][metric]
        assert abs(x[metric].mean()-record['past_mean'])<1e-10
        assert abs(y[metric].mean()-record['i3net_mean'])<1e-10
        assert abs(d.mean()-record['delta'])<1e-10
        assert np.allclose(np.quantile(d[draw].mean(1),[.025,.975]),record['ci95'],atol=1e-10,rtol=0)
        if metric!='psnr':quality_ok &= record['delta']<=0 if metric in lower else record['delta']>=0
    p=report['metrics']['psnr'];psnr_ok=p['delta']>0 and p['ci95'][0]>0
    comprehensive=bool(psnr_ok and quality_ok and p['past_patient_wins']/115>=.6)
    efficiency=json.loads((out/'efficiency.json').read_text())
    e=pd.DataFrame(efficiency['cases']);assert set(e.patient_id)==expected
    cost=dict(past_seconds=float(e.past_seconds.sum()),i3_seconds=float(e.i3_seconds.sum()),missing_slices=int(e.missing_slices.sum()),
        past_ms_per_missing_slice=float(1000*e.past_seconds.sum()/e.missing_slices.sum()),
        i3_ms_per_missing_slice=float(1000*e.i3_seconds.sum()/e.missing_slices.sum()),
        past_peak_gib=float(e.past_peak_gib.max()),i3_peak_gib=float(e.i3_peak_gib.max()))
    verify=dict(passed=True,patients=115,missing_slices_per_method=int(sum(lengths.values())),all_cases_and_slices_included=True,
        independently_recomputed_patient_metrics_and_bootstrap=True,psnr_superiority=bool(psnr_ok),
        quality_point_estimates_all_nonworse=bool(quality_ok),comprehensive_preregistered_screen=comprehensive,
        sota_claim=False,seed_count=1,efficiency=cost,
        report_sha256=sha256(out/'report.json'),per_slice_sha256=sha256(out/'per_slice.csv'),lock_sha256=sha256(out/'lock.json'))
    write_json(out/'independent_verification.json',verify)
    if psnr_ok:verdict='本次单 seed 的 PSNR 显著超过现有 I3Net 权重'
    elif p['ci95'][1]<0:verdict='PSNR 显著低于 I3Net，未超过它'
    else:verdict='尚未证实 PSNR 超过 I3Net（配对置信区间包含 0）'
    lines=['# 小波主干 IXI-T2 x4 结果（2026-10-03）','',f'**结论：{verdict}。当前不能宣称新的 SOTA。**','',
        f'固定 seed3407，404 train / 58 validation / 115 test。训练完整完成 {audit["completed_epochs"]} 轮，validation 最优 epoch={audit["best_epoch"]}，未裁剪 PSNR={audit["validation_psnr"]:.4f} dB。test 之前锁定该权重，未根据 test 改模型、预算或后处理。',
        '',f'以下为 test 全部 115 名患者、每个方法 {sum(lengths.values())} 张缺失层的同口径结果。先逐层评分再按患者等权平均；10,000 次患者配对 bootstrap。差值为 PAST−I3Net。','',
        '| 指标 | 小波 PAST | I3Net | 差值 | 差值 95% CI | PAST 胜出患者 |',
        '|---|---:|---:|---:|---|---:|']
    for k,r in report['metrics'].items():
        precision=7 if k in ('mae','mse','tail10_mse') else 4
        lo,hi=r['ci95']
        lines.append(f'| {k} | {r["past_mean"]:.{precision}f} | {r["i3net_mean"]:.{precision}f} | {r["delta"]:+.{precision}f} | [{lo:+.{precision}f}, {hi:+.{precision}f}] | {r["past_patient_wins"]}/115 |')
    lines.extend(['',f'PSNR 患者胜率为 {100*p["past_patient_wins"]/115:.1f}%。按 I3Net PSNR 最低的四分之一患者定义困难组，PAST−I3Net={report["hard_quartile_delta"]:+.4f} dB。',
        '',f'PSNR 优势门槠通过：{psnr_ok}；质量各指标点估计均不退化：{bool(quality_ok)}；PSNR CI 下界>0 + 质量不退 + ≥60%患者胜出综合门槠通过：{comprehensive}。质量各项 CI 见表；Dice/HD95 仅为强度阈值代理，不是组织分割性能。',
        '', '## 推理与训练效率','',
        f'记录的缺失层平均推理耗时：PAST {cost["past_ms_per_missing_slice"]:.2f} ms/层，I3Net {cost["i3_ms_per_missing_slice"]:.2f} ms/层。峰值 allocated：PAST {cost["past_peak_gib"]:.3f} GiB，I3Net {cost["i3_peak_gib"]:.3f} GiB。',
        '', '耗时包含按 volume 推理的 CPU 拷贝与输入打包，不包含磁盘 IO、缓存准备和质量评分；两模型同时驻留。PAST 使用 AMP，I3Net 保留其原 FP32 配置，不能解释为相同精度的纯算子基准。',
        '',f'PAST 本轮训练耗时 {audit["total_seconds"]/3600:.2f} 小时；峰值分配 {audit["max_allocated_gib"]:.2f} GiB；{audit["optimizer_attempts"]} 次尝试更新中记录 {audit["overflow_skips"]} 次 AMP 溢出跳过。最优在预算末端，最后 30 轮 best 仍增长 {audit["last30_best_gain_db"]:.4f} dB，不能据此说完全收敛，也不能在已经看到 test 后自动续训择优。',
        '', '## 比较范围与后续约束','',
        '此表比较已有两个 checkpoint 在统一推理和评分条件下的效果。双方使用 observed-only min/max、256×256、仅缺失层、输出 clamp(0,1)。I3Net 保留完整 4→13 滑窗、逐窗口裁剪后重叠平均。target 不裁剪。旧主表 31.3058 dB 是 native-volume 流程，不能拿本表分数直接与它相减。',
        '', 'I3Net 的完整滑窗重叠融合使内部缺失区间汇集至多 3 个窗口的预测，合计可利用 6 个不同真实观测锚点；PAST 每个区间使用 4 个锚点。这里保留双方各自完整推理流程，统一的是可用观测网格和评分，不是有效输入窗口或融合次数。因此不能把全部差距单独归因于小波模块。',
        '', 'PAST 继承 fastMRI 预训练，I3Net 历史训练使用不同的归一化、损失与预算。因此本结果不构成匹配训练合同的架构排名。目前只有一个 IXI 微调 seed；未运行另外两 seeds，不把这次结果包装成三 seed 确认。此次 test 已用于用户指定的探索性比较，不可用于反复选择超参数。',
        '', '完整数据：`results/test115_seed3407/report.json`、`per_patient.csv`、`per_slice.csv`、`efficiency.json`、`independent_verification.json`。训练审计：`results/full_train_audit.json`。',
        '',f'候选 SHA256：`{lock["candidate_sha256"]}`。I3Net SHA256：`{lock["i3net_sha256"]}`。',''])
    (ROOT/'RESULTS_ZH.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(verify,indent=2));print(json.dumps(report['metrics'],indent=2))


if __name__=='__main__':main()
