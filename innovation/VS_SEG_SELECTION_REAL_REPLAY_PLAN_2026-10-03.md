# 原45人队列之后的自动次要分析与真实数据重算

本计划不改变[既有敏感性合同](VS_SEG_SELECTION_SENSITIVITY_PREPARATION_2026-10-02.md)的任何比较、名单、标签、指标或统计。现有验证程序只验证合成已知答案，不能当真实112端点的独立复核。新增程序在整个原队列complete及完成报告/全部patient proof通过后，单次调用原敏感性脚本，再从保存逐患者/逐层记录重新构建全部112端点及其5,000个相同患者bootstrap。

重新生成的资格和四目标索引来自既有coverage；四目标SSE/像素和target平均另用标量重算，不调用分析器selected_image/summarise/analyse。bootstrap使用既有已合成核验的独立逐draw标量循环和手写分位插值；共享原始文件加载/hash验证库、RNG和这段标量库明确记录。逐端点核A/B/E/C、有限人数、undefined次数、95%区间、各selection shift与恒等式及方向标记。112全部保留，不挑阳性端点；次要未familywise校正区间继续只作描述。

不增加MR/神经网络推断，不使用GPU，不修改原83910或冻结分析代码。新queue只轮询已运行原队列状态，最大六小时，每15秒；failed立即停止，无重启、无自动retry。只有complete后才进入效果文件读取。所有新脚本/状态/log/proof在innovation。末尾不自动宣布可发表，完整主结果需要另作人工核读；001/202 Dice改善反证及固定HAT−pipelinePCHIP主比较保留。
