# 原文 uncertainty 定义的非医学CPU探索

先冻结问题：QCResUNet v2 block180写均值概率；Jungo2020 blocks20/24/25、33/34写均值概率后entropy。枚举两次二值概率draw的11x11网格，分别计算均值、predictive entropy、expected entropy、population variance、MI=H(mean)−meanH，验证数学范围、互补标签对称性和相同均值不同draw离散程度的例子。这里只探索定义信息，不复现作者执行结果或临床收益。

只用Python标准库、CPU1/below-normal，磁盘/RAM各8GB储备、本stage<=5MB。不读MRI/GT/model数组，不生成患者预测、不执行作者代码、不初始化CUDA，不改training session29823。参考原文binding与完整结果保存；公式差异不得推断作者实际程序必然使用错误公式。
