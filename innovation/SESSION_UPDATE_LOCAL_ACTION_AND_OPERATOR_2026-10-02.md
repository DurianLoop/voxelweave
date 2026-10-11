# 继续研究：开发例固定动作空间与近期摘要访问

本轮继续用户原目标：“一直研究探索验证下去，直到达成一个可发表的claim，注意不要动我现在终端训练的进程”。上一目标回合分类为 progress：四篇近邻全文/12个事实锚点的核读和筛选敏感性准备实际增加了证据与可运行代码；本轮不是只重述状态。用户还要求所有对话、来源、代码、结果、失败和后续准备保存在 D:/MRI/innovation。

## 实际 CPU 研究进展

对既有开发病例001保存数组执行了[固定动作上限试验](VS_SEG_001_LOCAL_ACTION_ORACLE_RESULT_2026-10-02.md)。病例/基底/动作/粒度/指标/停止门槛先记录于[方案](VS_SEG_001_LOCAL_ACTION_ORACLE_PLAN_2026-10-02.md)，再写输入/程序哈希合同，计算57内部缺失层的支持域与病灶误差。没有模型前向、数据下载或GPU任务；没有读取当前45人动态效果量。

主32像素 raw PCHIP→HAT 的支持域增加收益0.11825 dB且两种病灶NMSE守卫通过；pipeline PCHIP→HAT 增加0.10078 dB但病灶目标等权守卫失败。它们是看真值的oracle、一个已见分割器训练患者，不能宣布可部署方法或独立临床确认。16像素/像素上限和五个固定混合全部保留，不用更自由的上限替换预写32像素失败。

[独立数组复查](experiments/vs_seg_001_local_action_oracle/independent_verification.json)用不同的批量最小二乘/区间投影验证86,184 tile与88个策略终点，零错误。原目标辅助公式仍是常规二次恒等式；验证正确性不是论文新定理。该主报告附PNG/SVG权衡图，已视觉检查并修正标注/页边距；旧图与代码快照保留。

从同表进一步计算可观测动作幅度d/像素数对真实收益符号的描述性AUC，并由独立SciPy平均秩实现核验。主32像素 raw/PCHIP AUC为0.45408/0.71628；动作完整采用HAT时改善支持域的tile比例88.26%/70.19%。这不是患者外推、校准或预测头训练，不能把8208 tile说成8208患者或把低于0.5改反向评分后当新主结果。

## 文献推进与实际访问深度

八个精确DOI元数据请求（四篇各Europe PMC + OpenAlex）成功，另取得三份Crossref正式卷期/来源路径。新增正文数为0；三篇近期候选仍是摘要层，Kuestner摘要层门槛也未关闭。[摘要/可用性矩阵](literature/2026-10-02_operator_multicontrast_abstract_access_result.md)及[公开响应](literature/source_cache/operator_multicontrast_candidates_2026-10-02/attempt_01.json)记录确切身份和输入预算。

Target-driven论文摘要首次在本项目归档取得，说明其用于放疗中每个旋转2D采集片都穿过靶区，再以parallel imaging和SR恢复局部细节；不能从题名误读成固定轴向缺片插值。TMI implicit sampling/TTA使用高分辨率参考模态；knee GAN+healthy-counterfactual diffusion报告多中心OAI、perceptual/读者与分割指标；均不足以认证未读正文里的患者划分/真值/训练细节。

访问：[三篇公开路径索引](literature/source_cache/public_operator_candidate_bodies_2026-10-02/attempt_01.json)中，IEEE202且0字节；两个Elsevier200只返回coredata，无article body；arXiv两个429、一个读取超时。没有拿HTTP200/root名字当全文，也没有把限流/超时当无预印本的证明。Kuestner最新索引没有新增正文地址，未重复所有之前已失败的403/401路线。

## 原固定队列

同一个 session83910 多次实际轮询确认活跃，没有重新启动或终止。2026-10-02 10:33:58 UTC（18:33:58上海）观察到9/45主患者完成七条件，212 native完成；仍在inference，逐患者再生成除202认证例外尚待自动后续。此时完整主分母、合同和主要比较不变；不作不断增长子集的效果量或显著性判断。

合同SHA256仍为061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5。主目标尚未实现，无可发表claim，goal保持active。当前用户GPU训练、锁定IXI test、环境和.gitignore不进入新增工作。

## 失败、修复与完整记录

1. 起始两份合并读取输出超过显示预算，有截断；随后针对必要方法/来源分块读取。不把未显示文字称已核读。
2. 只读元数据提取对null DOI调用lower出现AttributeError，随后改(r.get('doi') or '').lower，精确取得target-driven记录；没有修改原来源响应。
3. 一次Windows rg路径使用未展开通配符报错，改为实际目录/文件名；猜测local_oracle旧目录有attempt_01.json但实际为manifest.json，后用目录查明。它们只是读取错误。
4. IEEE202零字节、Elsevier200元数据、arXiv429/超时均单独记录。未绕过登录、付费、限流或调用用户凭证。
5. 首次能量AUC独立复查为保存结果的shell cell；随后将代码写为可复用.py，生成带script/tile/diagnostic哈希的v2 proof，初次proof保留。
6. 图初版边缘标注/底注间距偏小，第二版32像素标签邻近曲线，均保留各版图/代码/哈希；最终版经view_image检查，无标注遮挡，数值来源不变。

[可见对话](SESSION_VISIBLE_DIALOGUE_LOCAL_ACTION_AND_OPERATOR_2026-10-02.md)保存用户目标与本轮公开进度。原研究的原始来源和核验历史仍在此前阶段档案，未改写。

## 下一步与归档

只保留主队列83910活跃；本轮数组分析、两种独立复查、图生成和公开请求均已结束。继续同一队列，全部输出与自动再生成完成后审固定主要联合方向、强raw PCHIP、双标签/范围/边界/空值和病灶两种汇总，再运行已准备的旧筛选次要分析。

开发例raw动作仅支持扩展多开发患者可行性；尚不启动收益头训练。GPU可用也不能跳过多患者空间、任务缺口、可观测收益预测及强误差头/固定混合对照。[原GPU准备](GPU_FOLLOWUP_TASK_FIDELITY_PREPARATION_2026-10-02.md)增加了本次结果链接，但没有制造新训练成果或授权控制已有进程。当前45病例评分后不得又当下一新方法的未见确认。

静态新增证据使用[独立阶段manifest](literature/source_cache/local_action_and_operator_stage_archive_2026-10-02.json)与[核验程序](literature/verify_local_action_and_operator_archive.py)；运行中的主队列日志不纳入固定snapshot验证。初次write核验57文件、138,931,852字节，八个DOI响应、零个新增article body、86,184 tile、88策略终点、六个AUC和189主冻结代码/协议文件，零错误；对话追加之后再write/verify。全局论文/来源/链接清单刷新后复查；XML/HTML新来源不增加29个注册PDF计数。动态VS-SEG整阶段manifest待队列真正结束后再刷新。
