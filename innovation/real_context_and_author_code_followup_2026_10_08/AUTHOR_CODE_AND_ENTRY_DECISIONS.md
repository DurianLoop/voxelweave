# 真实上下文入口通过；完整训练分布资格仍需收齐

本轮为科研目标的实际进展，尚未出现可发表且独立确认的医学claim。上一轮已核读VINN与2026病灶集成作者稿，本轮没有新增不同论文正文计数；新取得并逐行核读FastSurfer v2.3.0四个源码文件，且完成76真实开发MRI字段独立重算。后续具体动作净收益方向仍须充分任务能力、严格患者折外和未见确认。

## 真实MRI上下文的实际结果

首跑eb79d9 exit1：来源链查找错误，发生在MRI/GT读取前；空attempt01和原脚本保留。V2经上轮full_support已认证binding查旧receipt，不放宽任何数值门槛，session55568真实563565 exit0，236.428秒。

11开发患者/19series，native_reference与合法observed-only raw-PCHIP各38patch，共76输入特定fields、79691776强度体素；独特geometry38/39845888 target体素。MRI输入数组38、GT数组19、checkpoint/model数组/患者forward/更新/验证效益均0。全部缓存image SHA、19physical_label SHA、旧母batchlabel与basecrop SHA匹配；76source extraction向量索引与独立切片+flip逐位一致，中心原crop保持位级一致。

生产Torch双float64采样与独立物理旋转矩阵/SciPy全目标MRI重算最大强度误差`5.960464477539063e-08`，支持误差`6.783462680459706e-14`；原3e-6/3e-12/零binary门槛通过，76support二值SHA匹配上一轮无padding域；原label保持位级不变。全部76fields的FG支持不足=0，背景不足仍存在。此结果只证明入口和数值实现，不证明增强病灶收益或医学标签正确。

API不接GT，只从physical cache实际坐标取值，不存在坐标明确0+validity0；缓存内padding有基本强度变换但validity仍0。**完整source box不等于完整真实halo**，zero是明确缺失填充值，不能说补造了真实组织；无padding域也不是raw-PCHIP每格点真实采集证书。新算子不自动决定mask-loss/identity，不是可直接启动2992新训练的完成配置。

计时是此CPU1/below-normal、当前并行原CPU训练下76输入字段的实测，包含诊断support，不包含最终gamma/bias/noise、任务forward/backward、缓存长期存取或部署成本：

| 项目 | 76fields合计秒 | 单field中位秒 | 最小–最大秒 |
|---|---:|---:|---:|
| 生产context extraction | 6.976 | .08797 | .04692–.14474 |
| 独立context extraction | 3.064 | .03968 | .01990–.06980 |
| 生产双采样：MRI+support | 39.379 | .50979 | .27970–.87923 |
| 独立双采样：MRI+support | 55.468 | .66656 | .38913–1.05055 |

38输入cache加载总82.793秒（包含各自source_image和physical_mr），单source value array23,183,040–32,798,304bytes，另有float64validity、双channel中间值及坐标grid，不能把这个array范围当进程peakRAM，更不能用它替代GPU训练reserved/free测量。

## 作者源码的版本和阅读边界

GitHub API标签查询e0096c exit1（403 rate limit），未立即重试。新公开smart-HTTP refs GET没有clone/fetch对象或git工作区变更：b9f50a exit0取得v2.3.0 lightweight tag直接commit `550e84596b7adbc01bd0f2e93f1a127b1cb2df99`，四个raw文件均固定此commit。GOUHFI明确使用v2.3.0；此tag不是经证实的2022论文精确训练版本。

逐行未截断核读：interpolation_layer.py650行、networks.py410行、sub_module.py820行、data_loader/augmentation.py481行，共2361行。原字节、响应头、Git advertisement、SHA及实际读取返回全部保留。四文件均Apache2.0文件头。**没有import或执行作者源码，没有取得权重/config/dataset/trainer，也没有复现作者模型**。

- networks.py353–377：原native输入进入inp_block得到skip_encoder_0，Zoom2d返回encoder_output0和实际rescale_factor；最后反向Zoom2d优先用实际factor，将target_shape临时改回native skip大小，再与skip拼接。是2D特征前后两次尺度转换，不能等同我们的3D图像往返。
- interpolation_layer.py307–366：按target_shape×SF确定source_size，整数截断，center对奇偶还特殊处理；若超输入范围，先插值到较小尺寸再padding，并返回**经实际整数尺寸修正的**SF。473–505明确crop position、align_corners=False和_F.pad。反向缩放只用名义SF倒数而忽略整数修正/crop/pad，不是这个版本的精确实现；存在padding也不等于它证明信息無损。
- 默认networks crop_position是top_left，但最终配置未取得，不能说作者所有实验必用top_left。该版本Zoom3d并非FastSurferVINN实际路径，源码626调用的_calculate_crop_size在所读base里未定义；仅是静态疑点，未执行、未认证作者模型运行失败，不移植这条3D路径。
- augmentation.py343：`sf + torch.randn(1)*std + mean`，默认std.1/mean0；同一delta广播到两个2D尺度轴，确认加性内部尺度扰动的类语义。尚未读dataset/trainer/config，不能凭类存在认证其具体启用概率或每项作者实验配置。它不修改label，也不能证明任意尺度都合法。
- sub_module.py中的gn1/gn2等实际是BatchNorm2d（不是GroupNorm/InstanceNorm）。native输入、输出skip blocks有多个3³卷积，再normalized blocks/maxout和concat。不能因为名字gn就移植成我们TaskUNet中的InstanceNorm，亦不能用该作者模型结论取消上一轮InstanceNorm反例。
- augmentation ToTensor/Test先/255再clip[0,1]，与本项目observed-shared z-score不同，噪声单位和域不可照搬。未核作者损失/optimizer/datastream/完整config，论文表格矛盾、2026ensemble归一化/OOF映射仍未解决。

## 当前下一动作

已实际启动全schedule几何任务，见FULL_SCHEDULE_SUPPORT_PROTOCOL。它独立重放2992步/5984patch，只读开发labels/metadata；active逐体素Torch/SciPy支持，inactive独立identity域。只做候选往返增强分布资格，**不是正在运行单次spatial四臂的效果审计**。真实exit0及另一个进程核5984journal之前，不能称完整训练分布资格通过。

mask不直接读取GT的说法是条件于已冻结训练geometry：forced-FG crop/pivot本来由训练GT确定。这在训练采样中合法，但不能作为未来部署GT-free定位证据；新support policy不按GT额外筛增强/病例。InstanceNorm非局部依赖和background监督代价都须保留。

现四臂原session29823继续实际轮询，收全部真实exit0和last2992/11968journal后原完整FOV评价，不打开8未见确认/lockedIXI。几何资格收齐之后，才按开发内固定策略和同parent/schedule预算冻结ordinary强基线；mask/halo本身不当创新。动作收益研究仍需fold外重新训练/合法预训练来源，不能用全11GT见过的19998parent冒充独立。
