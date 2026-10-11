# 公开作者正文的替代获取

上一批两篇EuropePMC fullTextXML真正HTTP500。当前原索引声明VINN为Open Access并给出PMC9801435；因此本轮用不同公开NCBI服务获取正文，不修改旧失败记录。

固定三次GET：NCBI BioC JSON VINN、NCBI BioC JSON病灶集成、公开PMC VINN HTML。每请求500KB、TLS验证、≤35秒、最多3次https跳转，最多3并发；总体stage5MB/磁盘RAM8GB储备。正文需确认PMCID/DOI/题名/版本和科学maintext，摘要、错误页或JS框架不当全文。

获取/提取与实际阅读分开记录；不下载MRI/GT/作者模型，不安装依赖，不执行外部作者代码，不打开本项目lockedIXI或8确认患者。
