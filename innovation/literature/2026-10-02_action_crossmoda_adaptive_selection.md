# 自适应收紧检索与作者全文/官方版本页面选择

首批OpenAlex四query返回32条，排名明显被泛MRI/图像关键词和高引用综述主导。例如选择query顶项SENSE、PROMIS，不是动作收益预测先例；不将搜索总数当相关工作数，也不下载这些无关正文。已查看返回标题，摘要分块阅读，不用截断输出当全部阅读。

新增精确query：OpenAlex `"MRI" AND "mixture of experts"`、`"image restoration" AND "model selection"`、`"image restoration" AND "performance prediction"`，每query8条、日期上限2026-10-02；EuropePMC `TITLE_ABS:(MRI OR "magnetic resonance") AND TITLE_ABS:reconstruction AND TITLE_ABS:("model selection" OR "mixture of experts" OR "selective prediction")`，最多12条。用其结果选方法正文，不宣称搜索穷尽。

crossMoDA2026精确DOI记录实际给出作者稿机构PDF、arXiv2506.12006及出版版本。选固定机构URL `https://kclpure.kcl.ac.uk/ws/files/385489735/Crossmoda_summary_paper_rebuttal_unmarked_arxiv.pdf`，这是acceptedVersion元数据链接，PDF响应上限20MB；先检PDF magic，提取/渲染后核题名/作者、年份/版本、表格与数据段。阅读使用PDF技能，只读不重导出。若已安装MiKTeX提供的Poppler工具可读则不装包，不改MRI环境。

官方2021首页直接链接2021 `https://crossmoda.grand-challenge.org/Data/` 和2022 `https://crossmoda2022.grand-challenge.org/`，本次只读普通HTML。2023页面和公开数据文件地址必须由实际返回链接或作者正文获取，再单列followup，不能猜路径/自动注册。HTML每响应4MB、timeout30s、最多3线程、无自动重试；不下载MRI像素或label。

来源读取与文献索引结果分别保存；正文取得后至少完整核数据/评价/限制段和相关表/图，引用保留版本。未认证患者身份去重、T2人工标签或原生grid的来源继续pending。
