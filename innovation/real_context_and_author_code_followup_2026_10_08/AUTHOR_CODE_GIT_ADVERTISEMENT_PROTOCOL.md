# GitHub API限流后的公开Git引用读取

e0096c真实exit1：GitHub API ref GET返回403 rate limit exceeded，原attempt01保留，不马上重复API请求。新attempt02对同一公开repo读取Git smart-HTTP `info/refs?service=git-upload-pack`一次。此GET仅取得公开引用广告，不clone、不fetch对象、不执行git、不改本地repo，不发送用户数据。

逐pkt-line解析并保存原响应，明确提取refs/tags/v2.3.0以及若存在的peeled refs/tags/v2.3.0^{}；annotated tag必须使用peeled commit，不能把tag object当commit。上限400000bytes、TLS验证/30秒/最多3跳；未能解析固定tag则停止源码获取。固定commit后沿原四个源码路径限额GET；原文件保留，保存内容SHA及响应头，禁止import/执行作者代码。版号与2022精确训练版本未证实，表格矛盾不据此擅自改写。
