# 新原文核读与创新判断

本轮新增完整原文1篇：Acar/Çukur/Öksüz，*Segmentation-Aware MRI Reconstruction*，MLMIR2022，LNCS13587，pp53–61，DOI10.1007/978-3-031-17247-2_6。九个文字页完整核读，第9页纯参考、第8页结论/参考混合；实际看图1–8。下载官方机构记录给出的匿名PDF，SHA `9595f36c962fa53876c6323ab59c9419ae560bda144c12a4e70ccf763717c768`。上一阶段记录“尚未取得全文”是历史状态，此阶段已取得；不改旧档案或重复算旧摘要。

## 数据与训练曝光

OCMR CINE有74 subjects，总183 slices，coil-combined后模拟single-coil。训练155 slices、测试28 slices，作者明确无subject overlap，但没有打印两组subject个数、ID或按frame/slice汇总细则，不能把28 slices当28患者。不是CISS缺层/多线圈原始完整验证。

R4/R8回顾性k-space undersampling，Gaussian密度含8条autocalibration lines。分割标签由in-house专家在senior radiologist指导下手工制作。magnitude reconstruction进入segmentation。重建loss为原文所写ℓ1−ℓ2项，分割用Dice项，等权；没有给精确loss实现或可直接复算的所有权重/归一化定义。

Adam β1=.99/β2=.999、LR1e-4、batch16，RTX3090；总epochs、stabilization patience P、epsilon、pretraining/ResNet34初始化、validation/checkpoint选择、完整训练/推理费没有充分打印。不能补猜训练50epoch/Imagenet预训练并称作者复现。

## 方法是训练期语义梯度与采样课程

顺序reconstruction→segmentation联合训练，通过分割loss反传使reconstruction产生pseudo-attention。Fig1没有SERANet式部署循环的任务概率attention反馈；文中“guidance”主要通过训练梯度，不等同部署时value预测/动作路由。作者称推理图像来自重建网，segmentation为auxiliary map，未给完整计费边界。

第一组两UNet，depth4、filters32/64/128/256、kernel3；另用共同encoder/双decoder控制。第二组CascadeNet六cascades、每个五层64filters+DC/残差，配MANet/ResNet34。等backbone不证明总参数、标签监督、预训练和曝光匹配。

为避免弱重建输入导致分割训练失效，Eq1从接近全采样1−epsilon降到目标r：`r_i=(1−epsilon)*(r/(1−epsilon))^((i−1)/P)`（1≤i≤P），i>P时r。公式的r是保留比例/采样密度意义，正文用“undersampling rate”升/降措辞不一致，按公式解释避免混淆acceleration倍数。该字面式在第P个epoch仍略高于r，第P+1直接设r；CPU演示只用明确假设的P/epsilon，作者实际schedule/epoch尺度未核，不能把演示计成训练复现。

该课程给早期任务网更多采样信息/更容易输入，和固定R的普通网只有相同steps仍不充分公平。后续如果在本项目试类似训练难度课程，必须给静态、risk/value控制相同合法训练信息、采样日程与总曝光，不改现有原CPU两臂合同。

## 原文端点是局部图像质量，没有报告病灶任务收益

全图MSE/PSNR/SSIM，另针对分割图选区域的focused（F）端点。Fig2显示心脏红色矩形；正文没有充分说明所有模型是否用严格同一固定ROI、GT或预测mask、以及ROI/患者汇总规则。因此不能称局部metric完全排除了分母选择混杂，也不能断定确有模型依赖ROI；需实现或补充细节核实。

Table1的F列顺序F-PSNR/F-MSE/F-SSIM；Table2为F-MSE/F-PSNR/F-SSIM。两张表16行已视觉转录并逐行对照提取文本、Decimal复算。Table2明确MSE×10³；Table1无同等明确说明，不跨表合并MSE缩放。

CascadeNet→MANet(S)相对solo CascadeNet：

| 加速 | F-PSNR差dB | F-SSIM差 | 全图PSNR差dB | 全图SSIM差 |
|---|---:|---:|---:|---:|
| R4 | +0.8747 | +0.0497 | −0.7660 | −0.0122 |
| R8 | +0.8265 | +0.0203 | −0.9406 | −0.0042 |

局部MSE改善、全图MSE退化也在同表中并存。相对无stabilization的弱joint，改善更大；不能用仅胜弱未稳定对照证明方法优于已充分适配的最强静态方案。Table1也显示多decoder在某些focused端点优于两个UNet，不能笼统说联合顺序结构全优。

正文没有报告segmentation Dice、病灶recall/FP/FN、显著性检验、置信区间、完整runtime/cost。公开算术没有新项目MRI输入、患者级统计或神经forward。该论文支持“语义loss+curriculum改善局部图像质量”的先例，不能把它或本项目PSNR改善称临床task效应。

## Xu/Öksüz：取得完整摘要，仍没有全文

已核DOI10.1016/j.imavis.2024.105200的标题、作者、2024年来源。OpenAlex/S2均没有摘要或PDF；但ITU实际机构landing提供完整摘要。本次实际读到：policy network输入reconstructed image+segmented category probability feature map，用RL选择下一条Cartesian k-space line；ACDC retrospective测试，比较无segmentation reward variants，目标心脏局部和整体图像质量。

这说明任务语义引导动作选择在MRI采样领域已有明确摘要先例。本项目固定观测后合法修正与“新增采样观测”的action不同，但有限摘要不能证明全部算法/目标函数排重已完成，也不能核患者分母、任务Dice、参数/成本和原始结果。

出版社实际Crossref text/plain匿名GET为HTTP400 INVALID_INPUT/view；另条实际text/xml为HTTP200但只有1857bytes coredata、openaccess=0，没有abstract/body。虽然根标签叫full-text-retrieval-response，不能称全文。正常表示修复不是自动批准拒绝，不使用认证或绕过访问控制。

## 作者实现补查范围

GitHub共六个repo search请求：SERANet、teacher短词、SERANet arXiv ID in:readme、teacher题名、Acar/Xu精确题名。SERANet两次total16但各仅筛首5；十条repo元数据为图片SR/一般软件/论文集等，未核任何作者实现。四个其它窄查询真实0，不推断作者没有代码。未读取repo README/源码、未复现作者实验，不能解决ITFS原文formula/body差异。

[精确来源记录](READING_PROVENANCE.json) · [CPU表结果](table_audit_attempt01/receipt.json) · [下一步对照补充](FIXED_OBSERVATION_AND_ROI_CONTROLS.md)。当前无经独立确认的可发表MRI效应，goal active。
