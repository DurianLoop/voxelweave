# 全目标体素支持核验与分辨率基线原文接续

上一轮为progress：完成两新原文、16非医学synthetic与76开发几何plan，并冻结6164份证据。新轮实际38391b仍含session29823，无terminal，不重启/迁移/改正在运行的四分支。GPU授权有效，6094dd仍free1394MiB，不满足原8192MiB启动门槛。

本轮首要验证缺口：上一轮仅32点独立强度oracle/角点支持证人，不能证明整张支持mask。使用已经认证的11开发患者19series中38个不同几何patch，每个64×128×128（总39845888目标体素）；两输入同geometry，所以不重复模拟并冒充76独立样本。

仅由fullFOV shape、crop start、flips、变换和spacing创建几何source-validity 0/1 mask，完全不读取MRI/GT/model数组。source mask为1表示实际全FOV存在的格点，0表示不存在，仅作几何支持指示，不代表已经取得真实halo影像。比较旧crop-only中间FOV与充分intermediate-FOV两条路径，报告不可避免的原全FOV缺失与人工crop损失。

生产实现Torch float64 grid_sample；独立SciPy float64 affine_transform，order1、mode=grid-constant、cval0、prefilterFalse，以物理体素映射重建matrix，不能复用Torch grid。独立坐标3e-12、所有目标体素support数值3e-6、阈值1−1e-9得到的二值support零差异；任何失败保存，不放宽阈值。

保存计数/统计和独立固定角点直接证人的复核，输出必要时逐位packed二值mask，可用于后续训练入口资格。每个patch所有体素独立核验，但依旧只证明几何mask实现，不是插值信息无损、label医学正确、全训练分布已认证或患者收益。

新增原文目标是前次HTTP500的VINN：原索引已证明EuropePMC Open Access，尝试不同公开服务端点获取作者正文，不重复运行已失败脚本、不把下载当阅读。另核查2026病灶集成如果存在合法可访问作者文本；失败继续记录。

全部新增文件仅innovation，stage5MB、wall600秒、CPU1/低优先级、磁盘/RAM8GB储备，零依赖安装/零其他PID干预/零代理委派。4已见验证不用于新参数，8未见确认12series与lockedIXI关闭；可发表claim尚未达成，科研goalactive。
