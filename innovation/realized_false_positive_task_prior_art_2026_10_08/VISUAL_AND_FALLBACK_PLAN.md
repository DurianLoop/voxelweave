# 关键页与作者公开仓库核查

使用既有 PDFium 渲染 MIRTO 物理页 1、3、5、6、9、13、15、16、21、25、32、35、40，分别核身份/探索边界、Jaccard 与阈值、CRC、bootstrap、转移分解、公开表、作者链接、附录推导与费用。渲染 receipt 保持 visual_reviewed=false；实际逐张查看后另存阅读 provenance，不改 receipt。

作者 API metadata 已成功，但 tree 请求 HTTP403 rate limit exceeded。保留该失败；改用正常匿名 GitHub 公开网页 GET，仅核页面列出的文件和 README。若页面明确列出 README.md，再取 master 的公开 raw README。只读、不执行作者代码，不请求凭据或修改环境。网页最多3MB，GET30秒、最多3次 HTTPS 重定向；本目录总保存30MB以内，RAM/disk各保留十进制8GB。新作业 GPU 条件未满足，不启动医学 forward。
