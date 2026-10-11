# 执行修订：编码与输入审计

v2 实际工具 1585da 退出 1，准备核验中的中文 PermissionError 字符串被 PowerShell 管道生成成问号；0 次 MRI/标签数组读取、0 次拟合/预测/完整 GT 评分。v2 源码与失败 JSON 保留。

v3 将核验改为与 locale 无关的异常类型/WinError 5 前缀、multiprocessing 与 _winapi.CreateFile traceback，并额外核原 v1 源码 SHA。实际工具 202730 退出 1：新加的原 v1 源码读取没有提前列入允许集合，审计准确阻止；prohibited_access_attempts 有 1 条，仅为原 v1 源码。没有 MRI/标签/模型读取。这是执行错误，不是科学结果或自动审批审查拒绝。

v4 将该明确的原源码路径提前列入 initial 允许集合；v3 不覆盖。科学配置、样本、整患者 LOPO、阈值、ROI、全 19 预测后评分顺序、资源上限均不变。

尚未执行的独立核验改为指向 v4，补核所有汇总计数；森林精确复拟合使用生产合同的 float64 权重表达式 `1/(10*series_count*2*class_sample_count)`。等价的浮点运算结合顺序可能不同，精确 tree 数组比较必须重现同一输入权重，而非改变容差或移除比较。QDA 的矩与 Cholesky、标签坐标、ROI disk、窗口支持与 Fraction 成本仍另行重算。
