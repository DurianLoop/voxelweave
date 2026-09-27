# I3Net 第237轮 AMP 溢出恢复

**修复验证已通过，可执行下方恢复命令。** 用epoch236的副本复现了epoch237第52次更新的原错误；修复后同位置跳过1次异常更新、scale从4,194,304降至2,097,152，随后连续8次正常更新成功。共测试60次尝试/59次实际更新，未提交副本epoch，正式checkpoint仍为236轮且SHA未变。正式PowerShell入口preflight已通过。

2026-09-26，直接读取用户PowerShell终端确认报错发生于 `i3net_repaired_reference/run.py:135` 的 `clip_grad_norm_(...,error_if_nonfinite=True)`：

```text
RuntimeError: The total norm of order 2.0 for gradients from `parameters` is non-finite, so it cannot be clipped.
```

第236轮checkpoint可完整加载，模型/Adam状态有限、原源码/数据/配方哈希一致。scaler保存的scale已经增长到4,194,304（初始4,096）。严格裁剪在GradScaler能够跳过异常更新、回退scale之前抛出了异常。

## 修复范围

本独立入口仅在当前GradScaler的`unscale_`已检测到Inf/NaN时绕过本次梯度裁剪；随后由原GradScaler `step`确认跳过Adam、`update`降低scale。没有把Inf/NaN裁剪后送进优化器，也不对梯度做nan_to_num替换。正常梯度仍调用原严格裁剪；有限梯度的异常总范数仍报错。连续8次溢出会停止并报错，避免真正的数值故障被长期跳过掩盖。

旧包Python、协议、full.ps1、manifest均保留；runtime修复源码SHA及对应原源码SHA单独写入每次运行的`recovery_audit/<timestamp>/provenance.json`。这是明确记录的数值执行修复，不是声称恢复时运行代码完全没有变化。

原训练从已提交epoch236恢复，沿用原样本顺序、模型、loss、Adam、学习率调度、batch、checkpoint设置和300轮总预算。标准AMP溢出会少一次实际Adam更新，因此原history的updates字段此后表示尝试数；每次尝试是否实际更新、scale变化均写入`updates.jsonl`，完成时从最终Adam的step计数生成`amp_recovery_summary.json`。后续正式复核必须报告跳过次数，不能仍称精确25,500次实际更新。

## 用户运行

```powershell
Set-Location D:\MRI
powershell -NoProfile -ExecutionPolicy Bypass -File .\design\i3net_amp_recovery\full.ps1
```

该入口固定为恢复，无需加`-Resume`。再次中断仍执行同一命令。完整终端输出自动保存到本目录`logs/`；完成后照常调用原效率评估。用户full由用户运行，助手仅在`scratch/`副本做有限恢复诊断。

测试见`results/checks.json`及`results/real_recovery_verification.json`：合成溢出不得改变参数/Adam状态，scale必须回退，下一次有限更新须成功，正常路径应与原裁剪/Adam逐位一致。真实epoch237副本验证用于确认实际报错和恢复行为；副本中的未提交优化不写回正式训练目录。
