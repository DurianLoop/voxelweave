# 作者公开代码静态补核

QCResUNet arXiv2412.07156v2主文0–107及同HTML附录172–199已实际核读，无图片像素或独立PDF。论文声明代码 https://github.com/sotiraslab/QCResUNet；本轮只补核subject Dice、SEM标签、uncertainty、loss和ensemble费用的实际实现，解决原文Appendix A/公式和叙述中的歧义。源码不是新患者效果，也不假定当前repo与journal版逐位相同。

先两个公开HTTPS GET取得repo身份和default-branch最新commit metadata，每项30秒/2MB/三HTTPS跳转/TLS校验、无自动retry。再取得该commit对应一次tree，按本地检查选择最多六个纯文本小文件（README/metric/loss/evaluation/label generation），全部固定commit raw URL。文件每个<=300KB，新增目录全部<=5MB；如tree异常/作者repo不符保留失败。

只保存为.source.txt并做标准库AST/文本读取，不import/execute作者代码，不git clone/pull，不安装依赖或权重，不初始化CUDA，不加载MRI/GT/model。8GBRAM/磁盘储备、CPU1/below-normal，训练29823继续且不改source/配方/中间state，验证和确认仍未新开。
