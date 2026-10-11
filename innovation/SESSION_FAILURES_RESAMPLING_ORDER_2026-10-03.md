# 本阶段失败与未完成事项

科学结果未达目标不是软件错误。原主负向claim及固定残差相加候选的失败保留在上一阶段；本阶段不能用新对照挽救其预写假设。

1. 读取五篇索引摘要的临时`python -c`命令因默认GBK不能编码`ö`，出现`UnicodeEncodeError: 'gbk' codec can't encode character '\xf6'`。未改变源文件或完成阅读；此后所有新Python命令加`-X utf8`并由脚本显式UTF-8输出。本阶段取得的XML/JSON本身未损坏。
2. 一次只读命令误用缺少日期后缀的`literature/verify_complete_cohort_stage_archive.py`与`verify_native_anchor_stage_archive.py`，两个文件均不存在，命令exit1。随后用`rg --files`找到实际`*_2026_10_03.py`。没有据不存在脚本宣布验证通过。
3. 一次搜索还包括不存在的`experiments/vs_seg_001_full_volume_preflight.py`，rg返回exit2；同批已读的full-volume代码有效。后续从实际导入查到`vs_seg_full_volume_metrics.py`，使用其冻结指标合同。未创建冒名文件来消除失败。
4. 神经母细胞瘤T2论文公开EFetch返回HTTP200但只有front/abstract，body缺失。XML明确说明publisher不允许XML全文下载；[首失败](literature/source_cache/t2_tumor_processing_fulltext_2026-10-03/attempt_01.json)与原始响应保留，不计正文阅读、不重复该受限路径。
5. 文献读取工具输出有几次被token上限截断；相关方法/数据/结果/限制随后分块重读。重点正文阅读按实际88锚点登记，不把整个展平抽取块数量当阅读数量。
6. 第一张解析结果图的legend与RT区间重叠。原PNG/SVG/provenance保留，第二版将legend移到空白处并缩短横轴说明；第二版须实际查看后登记视觉核验。图中的数值和实验结果未改变。

解析producer、全45独立复核、报告生成、图生成、3篇正文获取与阅读证据登记均实际exit0。新post任务队列仍需实际poll到全45终止与独立18端点完成；其观察超时不是终止证据，不得重启或修改被run_contract绑定的脚本/计划。
