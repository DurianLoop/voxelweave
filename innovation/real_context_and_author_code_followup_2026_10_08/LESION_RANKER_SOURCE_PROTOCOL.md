# 2026 病灶集成论文所链 ranker：只读来源核查

此前已读作者稿 PMC13148016，正文链接 `Pediatric-Accelerated-Intelligence-Lab/BraTS-Unofficial-Ranker`。当前只尝试官方公开 Git refs 和固定 HEAD commit 的 README，用于分清“单次指标排名工具”“折外预测组织”“集成权重”和“部署预测动作净收益”的责任范围；不从工具名称补造 OOF 或权重归一化。

两次顺序 HTTPS GET，TLS 开启；每响应最多200000字节，总文件400000字节，wall90秒，阶段5MB/既有8GB磁盘RAM守卫保持。只取得公开源，不clone/fetch对象、不下载数据/模型、无Git工作区修改、不执行作者代码。若README给出确切路径，后续有界获取另存，不猜一串文件名重试。404/403等失败如实保留，不宣布代码不存在。没有新增不同论文正文、患者像素或医学效果；fullschedule和原四臂照常真实轮询。
