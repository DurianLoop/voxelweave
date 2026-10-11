# 获取前选择与去重

实际arXiv API两请求均200，精确greedy题名返回2010.16262v2（Bakker/van Hoof/Welling）；另六条近期索引含OpenMASC2609.32343v1、主动few-shot2607.22371v1、DiSIINet2607.00058v1、已读MASC2602.00348v1、PathCo-LatticE2512.09779v1、MorphSeek2511.17392v3。本轮实际读七条摘要，摘要不计正文，submittedDate排序不当相关性或优劣排序。

固定补读三候选：greedy2010.16262v2核greedy-vs-long-horizon及adaptivity证据；OpenMASC2609.32343v1核较此前MASC的DC、joint-vs-frozen、跨trajectory及模拟/临床边界；active few-shot2607.22371v1核joint set补充性、监督/预算和患者划分。三个ID在旧主文笔记中暂无明确全文阅读记录（不同ID旧MASC不被记为新发现）。不选择DiSIINet等仅因近期，不声称全面查新或没有先例。

先仅获取版本固定的官方arXiv HTML，每篇原始响应cap1.2MB、timeout25秒、总wall180秒；压缩原HTML及抽取块/MathML/表/图链接落盘，受本目录总cap2MB约束。缺正文/超限/429/错误页完整保存失败摘要；不将获取成功当阅读。HTML公式与图表文字阅读分别记录，未实际下载/查看的图像像素不冒充已读。若HTML不可用，不在本脚本换版、镜像、作者身份或认证路线，不执行外部代码。
