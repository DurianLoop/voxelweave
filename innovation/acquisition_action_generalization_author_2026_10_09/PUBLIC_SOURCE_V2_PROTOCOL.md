# 公开来源 bounded transport 第二入口

第一次索引结果过宽（未加短语 field 限定）；保留原结果且不计为主文。AMDU repo metadata 成功，commits endpoint response 超过250KB上限而失败。第二入口改为 /git/ref/heads/{default_branch} 获取固定 commit，再读取该 commit tree；不重试同一无限制大 patch response。tree response 上限 2MB，保存 gzip，目录总逻辑 2MB 不变。

Phys_Seg 固定第一入口成功的 commit，只读 README、network_architecture.py、utils.py、data_loading.py、predict_case.py。AMDU tree 读取后另事先固定训练/损失/gradient相关 blob 清单，不先执行源码。新检索限定 TITLE_ABS 的确切短语，逐篇 DOI 去重后主文阅读。GPU/病人/权重均不涉及。
