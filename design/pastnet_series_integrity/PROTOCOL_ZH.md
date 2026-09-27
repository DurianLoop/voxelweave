# 真实序列身份修复：2026-09-23，full前登记

## 证据与范围

frame-context full为25.562437dB，对control仅+0.000426，CI跨零、困难四分位轻微下降，按原门槛停止，不运行plain消融。

既有审计将训练病例113452254821_ax_t2标记为非单调位置/未知几何。本轮回查全部112train+23validation序列的DICOM头，发现仅此体积包含两个不同SeriesInstanceUID，每组16层。旧转换按相同名称AX T2合并，按InstanceNumber交错为32层；两个序列像素不同，不可去重为一幅。所有32层已逐像素匹配原DICOM，报告仅保存UID哈希，不输出患者身份字段。

旧x4样本z=0中三个目标的真实相对位置约[0,.5,.5]，而模型标签phase=[.25,.5,.75]；z=1约[.5,.5,1]。这不仅是metadata缺失：一个区间内混用了不同DICOM序列，空间标签错误。按SeriesInstanceUID分组、按ImagePositionPatient投影排序后，两组均为16层单调、均匀约5mm层距。不同UID不单独证明它们来自独立重复采集，本修复不作该推断。

## 唯一主要变量：修复这一个训练病例

原NIfTI、manifest、旧checkpoint不修改。本独立包生成两份新NIfTI及独立manifest；像素仅从旧体积重排，不插值、不强度修改。新case_id使用原ID+UID哈希前缀，patient_id和train归属保持。每个序列独立observed-sparse minmax，真实x4间隔约20mm，target同变换不clamp。

其它111个训练series及全部23个validation records逐字段不变。train从112series/1360区间变成113series/1356区间，患者仍111；validation仍23患者69区间。有效batch16，两方案每轮均85次更新，最后一个batch样本数不同。重新枚举导致训练样本排列变化，不能声称逐microbatch完全配对；它是序列修复带来的数据实验，不能当作同数据架构消融。

数据修复的正确性由UID、物理位置和像素匹配判断，不由validation分数决定。不因分数更高就保留错误混序数据。新模型是否晋级是另一个判定；若未晋级，不调数据分组规则挽救。

## 固定训练与门槛

从原G086初始化，原PAST control结构（992179参数），原完整loss、hard-tail、AdamW/warmup cosine/EMA、80轮/min30/patience15、有效batch16、前三轮冻结保持一致；不加入frame-context、方向增强或其它新结构。microbatch2/checkpoint5起测，目标约20GiB/24GB。

继承的G086曾训练过旧混序数据，本轮只能测量后续训练纠正监督的效果，不能称为全流程干净预训练。已有I3Net参照也用过旧训练集合；以后若做最终SOTA比较，需在修复训练数据上重新建立相应基线。当前不更改旧论文表、不评估IXI/NingXia。

完整validation records及指标合同的哈希必须与control一致，允许训练manifest不同且报告其差异，严禁伪装成同一data hash。最终配对为相同23患者、相同validation样本和指标，seed和G086初始化相同。

预登记模型晋级门槛仍为相对control至少+0.10dB，即seed3407至少25.662011dB，10,000配对bootstrap CI下界>0、>=60%患者改善、困难四分位不退、SSIM/MAE/MSE/NCC/Dice/HD95 intensity-proxy均值方向不退、tail10 MSE不退，延迟/显存<=1.5倍。失败停止该候选训练，不追调LR或继续训练。正确的数据修复产物保留。通过后才补配对3seeds，锁定后再做外部评估。

## full前必须通过

全部train/val头审计只有一个混序病例；两组无交叉、32像素层完整匹配；新体积逐层等于原体积对应层，物理坐标单调；修复样本anchors和target都来自同UID且phase为.25/.5/.75；observed-only归一化；其余train/valrecords不变；新旧patient集合一致且train/val隔离；真实修复样本完整反传、trainer smoke、恢复、指标复算、效率和full入口验证。

所有Python、协议、full.ps1、修复映射、新manifest/新数据哈希冻结。DICOM物理坐标解释参考[官方Image Plane Module](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_c.7.6.2.html)。这是数据完整性修复，不宣称新模型、创新方法或已达到SOTA。
