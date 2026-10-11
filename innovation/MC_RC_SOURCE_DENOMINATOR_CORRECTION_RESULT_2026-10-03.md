# 来源名单更正：16合格系列，旧15遗漏002第二时点

实际执行[预写名单审计](MC_RC_SOURCE_DENOMINATOR_CORRECTION_PLAN_2026-10-03.md)，exit0，errors=[]：[全部24来源资格和16个case](experiments/mc_rc_source_denominator_correction/attempt_01.json)。这是来源proof谱系与分母审计，不是新的MR/label数组解码或独立临床验证。

| 范围 | 系列 | 开发患者 |
| --- | ---: | ---: |
| 三批原来源 | 24 | 不作为新确认人数 |
| 当前独立来源资格通过 | 16 | 8 |
| 当前拒绝/pending | 8 | 不按性能筛选 |
| 旧覆盖/区域/预测冻结子集 | 15 | 8 |
| 已合格但遗漏 | 1 | 仍为原开发患者002 |

遗漏UID：`1.3.6.1.4.1.14519.5.2.1.213711595575218613093188251544325434833`，002第二个Ax3D FIESTA时间点。初始头/label格子因端点拟合位置误差被拒；后来全IPP线性拟合几何修正和独立raw proof已经通过。后续实验再次按初始label结果中的布尔值筛选，遗漏了追加资格。这是范围错误；不能继续无条件说「当前全部15合格来源」。

核旧15均仍合格，当前合格减旧名单仅这一系列。审计逐项匹配初始/追加result与独立source proof SHA256、每个ZIP/头/label文件hash、qualified集合及patient分组，不依据MRI评分修改来源资格。002当前第二时点为7046前景体素，数量仅沿用来源审计结果，没有在名单审计中读取label array。

旧合同、预测、失败和论文笔记保持历史原貌；本更正作为最新范围解释。补充按[新的16系列CPU合同](MC_RC_NATIVE_COMPETENCE_CPU_PLAN_2026-10-03.md)运行，同稀疏输入、冻结分割器、2mm主区域和完整native参考。旧15 affine/spacing沿用其原输入配置以保持可比，遗漏系列采用已复核fitted affine和integer grid。该时间点不算新患者，不作科学独立确认。历史文件中的「全部15」必须结合此更正阅读。
