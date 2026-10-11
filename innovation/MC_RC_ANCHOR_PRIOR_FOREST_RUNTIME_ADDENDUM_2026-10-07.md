# 隔离运行时取得方式修订（数据实验前）

首安装tool405648实际exit1。pip已正常取得候选metadata URL，但其临时unpack目录写metadata遭PermissionError；既有MRI环境未改，没有完成sklearn安装，也没有任何新MRI/GT/模型拟合。原脚本、失败JSON、stdout/stderr和临时残留保留，不删除或改判成功。

改用公开PyPI版本JSON取得预先固定的官方wheel URL/SHA256（sklearn1.7.2的cp312-cp312-win_amd64；joblib1.5.2/threadpoolctl3.6.0的py3-none-any），bounded公开GET，核官方SHA后仅在新的innovation任务目录安全解包。逐ZIP路径解析必须在该目录内，单文件/总解包预算检查；不运行安装脚本、不安装其他依赖、不改根环境。固定包版本和科学合同不变。包导入/版本通过后再运行19系列诊断。
