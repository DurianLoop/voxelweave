# MC-RC 第2版完整联结失败后的分项复核

首次审计 `experiments/mc_rc_v2_nonpixel_identity/attempt_01.json` 返回exit1/complete=false，八项旧VS-SEG UID交叉联结全失败。不可覆盖、放宽为完整来源合格或从序列描述猜匹配。

实际进一步逐列查验：CSV中八个MC-RC UID均存在于新API目录；CSV中八个VS-SEG UID在已冻结旧476序列目录均不存在。新版重导出/官方旧清单陈旧/部分目录缺失等均只是可能性，原因未认证。新旧UID集合交集为0，不能据此证明没有重合；官方正文和页面明确58人/8序列重合。

本次只用已有公开metadata进行独立CPU计数复核：SQLite DISTINCT/GROUP BY代替原脚本Python集合/Counter，检查487series/427studies/160人、manifest全集、58人排除、102候选/100候选T2患者及八行交叉清单MC侧8/旧侧0。复核只能认证上述目录算术，不能签署完整交叉联结、原生geometry、标签空间或科学确认。

无需新请求或训练。保存两个事实：计数是否可复现，以及完整来源资格仍未通过。保持全58人排除；只排除八序列不够。下一阶段原生T2/标签验证须预写新方案。若补旧UID证据，需官方新映射/新版本索引，而不是改UID或按描述强行关联。
