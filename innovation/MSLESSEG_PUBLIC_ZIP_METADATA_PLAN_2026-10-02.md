# MSLesSeg官方包：先核文件目录和非影像元数据

请求前固定。根据正式论文DOI10.1038/s41597-025-05250-y与Figshare article27919209 v1，公开CC BY4.0文件：

- registered Dataset.zip，file52771814，1473284755 bytes，公开MD5 cb30cfb13b0981443c300a5e51dd91cd。
- RAW.zip，file53623946，1295472528 bytes，公开MD5 8bae58b902c8b6ce4afb0bc5fc227959。
- README.md，file54605609，2059 bytes，公开MD5 50ea39d80230c06b9bcd6018f3f4ab46。

仅读两个ZIP central directory和小型README。后者必须核实际MD5；前两个不整包下载，故目录header/CRC/metadata与分段sha不能称整包MD5认证。每个HTTP range必须206且准确Content-Range/总长，单请求<=1MB、总传输<=10MB。服务器若忽略range就立即拒绝，不读取整包。请求原始公开地址，重定向临时签名不在日志明文打印；不接受条款/登录。

保存全部目录项（名字、压缩大小、解压大小、method、CRC和offset），只据文件名计患者/时间点与模态，明确名单规则。若出现CSV/JSON/README等非像素元数据，最多读取6个、每个解压<=1MB、总range仍受限，所有选定名字先留存再读。标签/图像像素不解码，不根据它们评分。

此步核75/115 vs论文77/24矛盾和RAW是否确有逐扫描信息；如果没有精确原始层距/3D采集证据，不能凭1mm MNI网格放行。后续原生NIfTI非像素头需另写全名单协议，不在本步偷偷挑薄例或扩整包下载。当前83910主队列、GPU/终端训练/锁定IXI test不受影响。
