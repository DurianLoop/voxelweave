# GIN期刊录用稿的公开来源与阅读

来源为Imperial Spiral DOI-exact landing，文件标Accepted version、4.29MB，date acceptance2022-11-01，DOI10.1109/TMI.2022.3224067。只请求其公开citation_pdf_url，不访问publisher staging或绕过拒绝。不把accepted版称publisher typeset final，也不把已读arxiv2111.12525v5重复计为新distinct paper。

新paper目录总6MB cap，PDF原字节≤5MB，全部正文/参考和page PNG尽量保存并逐页实际读。复用既有pypdf/PDFium/Pillow，不安装。render scale1.0、128色PNG用于图/表/公式布局检查，正文另提取；需要更精细图像则另冻局部render且仍守预算。源PDF不编辑不重导出。每页尚未实际读/看前transport receipt保持false，阅读完成另记录provenance。只读学术源，无医疗数据上传。

CPU1/below-normal、RAM/disk8GB。沿用原prep7MB/FOV20MB/other22.8MB**全部上限**，再保留本新目录6MB的未来余量。disk free本身已扣除当前实际文件，因此只减prep/FOV剩余可写部分（limit减actual）以及本目录剩余部分，不重复减已占用FOV字节。已有live35904的runtime reserve另只读核对，绝不编辑其代码/重启进程。通过fresh guard才下载，wall180s。六臂104156359bytes完整预算不变，也不启动正式训练/改变医学生态gate或确认集。
