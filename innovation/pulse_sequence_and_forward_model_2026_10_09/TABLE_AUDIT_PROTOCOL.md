# 原HTML表格的独立核验

从已保存的两份HTTP200原HTML直接解析 article 内39个 table，用新的流式 HTMLParser 累积 cells，逐cell比较 extraction_attempt02，不重新GET、不加载患者数据。39节点包含31公式布局和8非公式表；PSACNN21公式+4结果表，SynthSR2021 10公式+1超参+3结果表。

对PSACNN4结果表用Fraction核每个显示均值，三个体积一致性表按最低值、自动分割互相Dice表按最高值，严格最优与并列分开。不能据显示均值重建p值或人工GT准确性。对SynthSR三个结果表保留全部spacing和方法，计算与cubic的显示差；文本121的7mm fully-supervised volume error2.7%与Table3的2.8%照实登记，不能无来源修表。

公式扁平文字只校验提取，分数/根号/上标MathML布局不靠扁平文字复现。原图像像素、外链supp、作者代码/权重均未读。CPU1/below-normal、wall60s、输出<80KB、本目录3MB，磁盘/RAM8GB另保留3MB医学及2MBfull。真实终态后核验全部分母，研究goal保持active。
