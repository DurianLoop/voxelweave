# 归档后的作者来源定位

本项在6823不可变index之后另增，不修改已冻结源。针对1907.13418v1数据代码声明的rtanno21609/SaferNeuroimageEnhancement，只做GitHub公共API三个顺序GET：repo metadata、默认branch精确commit、commit tree。接受官方HTTPS重定向且记录最终repo identity；不在未知重定向后自行换repo。每GET30秒/200kB，至多3HTTPS跳，无认证/重试。固定commit后才选明确涉及nested uncertainty propagation的源码，先定位、再另读；不下载权重/数据或执行作者模型。

目的是核Eq20/21字面式与实际实现是否一致；repo404或无代码都保留失败，不推断作者实现错误。所有结果仅新建，stage仍<=2MB、live预算及8GB储备保持。新作者读取只有实际取得并完整读过才登记。
