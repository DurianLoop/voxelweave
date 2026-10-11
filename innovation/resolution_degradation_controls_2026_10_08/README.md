# 分辨率对照资格与后续医学验证

本轮接续用户“批量读论文、结合MRI项目探索创新，能验证的先试、不能验证的做记录和准备，全部保存到D:\MRI\innovation”的任务；GPU授权有效。发表目标仍active，尚无独立确认的医学claim。

已完成的资格及其真实terminal：

| 检查 | 完整分母 | 最大强度误差 | 实际结束 |
|---|---:|---:|---|
| 合成分辨率字段 | 270完整字段 | 2.3842e-7 | 7b5ed8 exit0 |
| 完整几何metadata | 5984几何×3模式=17952 | 不读取真实MRI | 与上一行同一过程 |
| 真实MRI stress | 19series×2输入×2母patch×3模式=228 | 1.90735e-6 | 868f3b exit0 |
| 同生产强度组合误差传播 | 同228字段 | 1.90735e-6 | ee6557 exit0 |
| 新独立强度参考 | 40合成字段+5984 primitive元数据 | 9.53674e-7 | 696add exit0 |

记录见[阶段结果](RESULTS.md)、[来源登记](READING_PROVENANCE.json)与ACTUAL_TOOL_OBSERVATIONS_PART01/02。固定三轴候选metadata在全部11开发患者、19series都有enabled/effective降质事件；不再把旧绝对whole-target gate仅272可执行、5患者无事件的policy当充分增强。原失败harness及18前景支持不足反例保留，未降低门槛。

完整真实管线已启动session74234，计划35904字段（5984母几何×两输入×三模式），当前仍为运行状态；最新真实poll 8bf93b看到1344字段。该历史观察不是完整通过。固定方案见[完整管线协议](FULL_REAL_PIPELINE_PROTOCOL.md)，入口[脚本](qualify_full_real_pipeline.py)。原session29823最新3a681d到raw_pchip_intensity2310/2992，两native臂已完成2992，raw spatial尚待；空输出且含session_id仍live。GPU最新c94093空闲1394MiB/total24455MiB，未达到8192MiB起跑储备。

本轮没有新增不同论文正文核读；复核了VINN/FastSurfer源码判断以及QC、病灶级集成的既有阅读笔记。作者FastSurfer固定commit11文件3970行与unofficial ranker162行的既有证据不重复计数、不声称执行作者代码。普通分辨率降质、标签不变、病灶阈值/ensemble/QC排序均不作为新意。当前保留的差异是**合法采集可见性→具体动作真实病灶损害差及全费用**，见[创新判断与准备](RESEARCH_DECISIONS_AND_NEXT_STEPS.md)。

所有完成资格仍只有软件数值/来源/分母证据，没有本轮模型forward/backward或医学收益。分辨率阶段原padding保留；gamma之后padding与identity逐位一致不宣称，支持mask不能认证InstanceNorm安全。11开发/19series；4已见验证/9series只等原四臂完整结束后按既定评价，不用于选择这里的规则。8未见确认/12series与lockedIXI继续关闭。

本目录总5MB、RAM/磁盘各8,000,000,000bytes储备不降。原CPU训练不迁移/重启，不枚举或干预用户及其他PID，未改根.gitignore/environment，未安装依赖/委派。完整真实管线rolling receipt/journal和原训练rolling输出不冻结归档；仅其frozen_config允许。当前公开对话及用户交接见[对话记录](VISIBLE_DIALOGUE_TURN28.md)，更早阶段内容沿既有累计6324来源链保留。
