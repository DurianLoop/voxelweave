# 幻觉图直接先例与MRI创新边界

本批新增完整科学主文及同一页面内嵌Supplementary Material：[Bhadra等，On hallucinations in tomographic image reconstruction](https://arxiv.org/html/2012.00646v3)。版本2012.00646v3，索引published2020-12-01/updated2021-09-27；精确题名和四作者与DOI [10.1109/TMI.2021.3077857](https://doi.org/10.1109/TMI.2021.3077857)的Crossref记录一致。期刊记录2021-11，不冒充已核publisher final PDF。HTML452484bytes、SHA136969c6751f003a8bd281a31c04501e9d1f2c9fcd4c85c31da696e0a2cd0ea3；178提取块，包括科学主文、图表文字、Algorithm1、内嵌补充。参考文献列表未逐篇阅读，图像像素、PDF及完整模型未核。

原两个大输出在编排显示层被截断，但内层exec_command原返回JSON完整且可解析；补读36–64、65–96、拆开97–116/117–139及157–162，确保实际可见科学内容覆盖。截断显示不回写成无截断；最终来源登记核完整内层返回并保留补读记录。

41个HTML table节点中40是公式/算法布局，1是真实结果表TableI（S5.T1.3），该表位于figure内；不能把41全计结果表或因其kind=figure漏记数值表。

## 先例直接覆盖的方向

Eq11/12用截断伪逆将图像分为广义measurement/null组件；广义null包含小奇异值的不稳定方向，只有P=rank(H)时才退化为真正null。文章不是只讲缺失像素或高频，也没有把所有false structures都定义成同一种hallucination。

Eq17的measurement-space HM = P_meas(xhat) − H_P^+g，不需要真实对象，但它衡量与可稳定重建测量分量的相符。噪声/forward-model失配会影响这一量；补充S.III明确它不等于与真实measurement分量比较的error。因而“从采集一致性计算GT-free风险”“保留观测使measurement误差小”已有直接先例，不能单独作为新意或安全证明。

Eq21的null-space HM = 1[xhat_null != 0]·(xhat_null − x_null)，**需要真实null组件**；作者明确这一依赖。其indicator使完全不恢复null的伪逆解被定义为零hallucination，但作者同时明确它可能有严重缺失artifacts。不能用该HM直接作部署特征，也不能把零hallucination解释成没有漏结构。这个量是在图像强度的null组件上定义，不能未经定义直接套成二值病灶分割的FP/FN。

Eq23已经提出application/observer-specific transformation T，用于task-informed hallucination maps，结论还指出sampling patterns对应不同H/null特性。因此“任务相关幻觉图”“采样可见性/测量-null分解”“按采集模式解释重建失败”也都有直接先例。该形式不等于已实现本项目合法信息下的paired病灶动作收益头，但差异本身不证明后者首创。

## 原实验究竟证明什么

| 设计 | 原文实际范围 | 本项目不能借用的结论 |
| --- | --- | --- |
| 模拟单coil二维MRI、FFT、均匀kspace×3 | 作者明确不是真实scanner准确模型；加complex iid Gaussian noise，测试另加随机phase模拟失配，无coil sensitivity/bias field | 不能当真实厚层CISS point x4或scanner slice-profile校准，也不能以其测量噪声模型认证本项目 |
| 2500训练/500验证，69IND+69OOD images | IND成人fastMRI；OOD儿科癫痫切除MRI，年龄/系统/人群同时不同，320² | counts是images，不是已核独立患者；不称单因素采样分布效应或病灶临床确认 |
| UNet、PLS-TV、DIP | UNet MAE/RMSProp；DIP同UNet架构、逐图优化，另有TV；PLS/DIP lambda在dataset子集按最低RMSE选 | 训练/推断成本差异未匹配；子集是否独立于最终报告未交代，不视为严格未见所有调参选择 |
| T将raw HM结构化 | Otsu支持、equalization、Gaussian、95th-percentile、移除<100pixels组件，作者称heuristic | 支持与阈值不自动是合法部署方案；不能照搬为VS裁剪、LCC或漏检守卫 |
| TableI结构化null-HM区域内median SSIM | IND：UNet.84/PLS-TV.71/DIP.73；OOD：.75/.73/.76 | ROI由各重建对应HM产生，不是固定相同病灶ROI；无病灶Dice/recall、paired动作净收益或临床费用结论 |

原文block120明确false-positive/false-negative分类超出本研究；结论138把ensemble FOM/发生概率留作后续。不能用本文SSIM排序认证当前024的严重漏检是SR幻觉或全部由先验引起。

## 固定作者实现

主文代码URL经GitHub官方200重定向到[comp-imaging-sci/hallucinations-tomo-recon](https://github.com/comp-imaging-sci/hallucinations-tomo-recon/tree/d640d6b8b134572c06cb883b73fbd9694f808c87)。repo ID346122526与homepage2012.00646确认；第一次严格旧owner断言9be351失败，保留源码/响应，随后只从已存repo继续ref/tree两个GET，22ef80成功，不重取repo。固定commit d640d6b8b134572c06cb883b73fbd9694f808c87，只表示本次版本。

三文件逐Git blob SHA1/bytes核验且全文实际读完，共336行：README144、compute_raw_maps109、compute_specific_maps83。未读/运行全部UNet/PLS/DIP训练与权重，不下载其MRI/GT样例，不装旧环境。

- raw_maps的null_hm函数明确接收gt，line43以recon_null==0严格置零；meas_hm分支只读g/mask/recon，不读gt。零比较没有浮点tolerance，若后续复现需单独分析数值行为，不默改作者定义。
- 保存展示前取绝对值；convert_to_uint依img.max−img.min，无常量图分支。该静态观察不是实测pipeline故障，本批未执行作者代码。
- specific_maps加载预存seg_mask，三个已读文件没有显示它如何产生；不能确认这是合法observed-only支持，也不能擅称必定GT脑mask。后续部署需有明确支持生成与费用方案。
- 原文称Gaussian kernel width7；固定实现实际gaussian_filter(sigma=7.0)，不是可直接移植的7体素有限kernel。转uint8/全图95%阈值/组件移除也需照实际顺序报告。

## 对当前项目的决定

原四last2992模型全部未过六医学门槛，024 recall约.112–.136。不能把“更少虚构结构”作为唯一端点：真实漏病灶、过分割、signed/absolute体积损害必须同时保留。论文HM只作为有GT时的机制审计候选，部署gain/风险特征必须仅用合法observed信息；measurement一致性与真实病灶效用分开评分。

条件mask/GMM/Papago先例及此前QC/收益/成本敏感先例继续有效。目前保留的假设只是：强任务基线及普通增强之后，合法采集信息能否带来超过同信息同容量QC/error、action-conditioned posterior risk差和完整费用控制的paired病灶收益增量。尚未证实新意、有效性或独立确认。

Tanno等的另一DOI精确身份已获取，Crossref给期刊2021-01（本地摘要旧记录写2020，需要保留在线/卷期之别）。publisher TDM返回200但只有1980bytes minimized metadata，明确body_elements0；没有正文，不计第二篇本批全文。EuropePMC503和OpenAlex429保留，不循环重试；只用另一个公开arXiv索引匹配取得上面的新主文。
