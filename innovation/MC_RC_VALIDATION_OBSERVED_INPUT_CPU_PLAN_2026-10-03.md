# 固定4验证患者9系列的真实稀疏输入证明

沿用原患者排序与当前40合格系列角色表，固定020/022/024/025的全部9合格系列。只读这些患者的observed DICOM层和源监督标签，不打开8确认保留人的MR像素或标签进行任务评价。标签只做源网格/输入轴核验，在重建/归一化完成后独立读取；原标签元数据已资格通过，不按大小或效果换人。

phase0/stride4、raw linear/raw四邻PCHIP×observed_shared/full_own、全FOV/整数RAS重定向，与开发19一致；只保存observed-only NPZ，500MB压缩上限。新IO allowlist明确11开发+4验证，其他患者拒绝。MRI重建/统计仍不接受label/native参数，未解码任何隐藏MR，不导入torch或运行模型。

独立从原MR ZIP按IPP投影重新排序、重读全部observed，独立Hermite/harmonic slope/PCHIP、逐plane手工统计、源NIfTI transpose/flip与RAS轴，核9×4=36输入。复核可调用生产reconstruct进行数组比较，独立公式/轴实现不等于完全不引用生产代码；资源沿用单线程/自身低优先级、磁盘15GB/内存8GB。

当前全FOV/local基线权重冻结前不得跑验证任务效果。生产/独立输入证明可以与当前训练等待同步推进，但不读loss来换验证身份/条件；只有资格/接口证据不是科学split、任务能力或科学确认。后续正式诊断启用需绑定最终训练checkpoint/协议/代码和角色SHA。最终8保留人继续禁止载入。
