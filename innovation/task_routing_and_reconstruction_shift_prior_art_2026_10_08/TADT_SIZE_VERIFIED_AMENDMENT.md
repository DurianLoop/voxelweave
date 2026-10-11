# TADT实际文件大小修订

第二次获取927c4f / exit1：medical_shift成功；TADT的curl exit63，未产生PDF。保存的TADT HTTP200 headers给出Content-Length=10,036,939bytes（仅比10,000,000限额多36,939），类型application/pdf、filename2408.08736v2.pdf。

第三次只取TADT，在新的tadt_size_verified_attempt03目录，单文件上限改为10,050,000bytes；必须核实际字节长度等于headers所报10,036,939。阶段30,000,000bytes和RAM/disk8GB保持，下载前磁盘再留50MB。保留前两失败，medical_shift不重复下载，不覆盖任何源代码或receipt。仍仅公开HTTPS GET、TLS验证开启。

已见ETag sha256:c75737c8c8d20511dfe4a50711d679178e80e0426a50bc4654e04d944104bd97。ETag与实际body的关系独立记录，不事先声称相同；若不同，保留差异，依据实际字节SHA及本地PDF题名/作者/arXiv版本检查决定是否作为该版本阅读来源。
