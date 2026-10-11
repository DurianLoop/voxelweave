# 19开发系列：部署可见观测留出特征，执行前合同

推进[此前准备第4项](PROJECTION_AND_SELFSUPERVISED_ACTION_PREPARATION_2026-10-08.md)：合法heldout一致性可以是动作收益预测器的普通特征，但不是MRI任务收益或Noise2Self风险证书。保持旧[三IXI选核失败](KNOWN_PROFILE_HOLDOUT_PILOT_RESULT_2026-10-01.md)，不重复其核估计、隐藏原生层评分或选择规则。本阶段不选择插值核、不调fold/ROI/阈值、不读任何任务模型/GT；原训练99542和确认关闭不变。

数据固定为上一[共同投影生产资格](experiments/common_projected_observed_qualification_2026_10_08/attempt01.json)的19开发observed NPZ、11患者，包/数组/shape/affine/索引逐一核SHA或精确元数据。全部原observed z=0,4,…为部署合法数据；只在其中做留出，不访问缺失MR/native完整体积、验证、确认、lockedIXI。

1. 固定两fold：原observed ordinal奇偶。首/末observed始终保留；其余ordinal%2==fold的内层留出，另一些保留。两fold的heldout集合不交，合起来恰是所有内部observed；source的统计和预测只使用retained层。每fold记录retained/heldout原native z、affine列范数所给实际层距mm、两者之间间隔。不对边界首末做外推评分。
2. **mask在统计前**：先从实际包复制retained planes，再仅以retained的float64 mean/population std归一化、cast float32；std=0时divisor=1。逐层bilinear align_corners=False到上一相同physical target r/c，得到只读float32 source。pure prediction API只接source和已冻结query位置，不接全observed/target/GT。normalized references只能使用同retained统计，reference projection只在prediction完成后评分；不重估heldout统计。
3. 固定两个已知预测：linear；local PCHIP（目标位于两个retained anchors之间，若其前后另各有一retained anchor，则用这四个实际mm位置；否则linear fallback）。采用原local/fallback原则的非均匀留出推广，不冒称原uniform reconstruct原地执行或新方法；本阶段只预测heldout observed层，不生成完整MR。
4. 两预测都对每个heldout层完整physical r/c评分，保存normalized mean error/MAE/MSE/RMSE/max error和pixel count。每series按两个fold完整像素合并SSE/count等，不丢负差；患者内部series等权，再11患者等权。描述PCHIP−linear的观测MSE差和混合方向，不推断缺层/病灶收益，不选择winner部署。background/FOV误差不是病灶专用特征；GT ROI禁止。
5. 每个真实series×fold做一次固定counterfactual：只把heldout原值加10000（float32，有限），retained原值不变；重新构造source并重新预测，要求retained统计/source SHA/两个完整预测SHA逐位不变。另记录unmasked全observed mean/std是否改变，仅作预处理依赖诊断；它不证明任意denormalized算法也变，更不重写任何旧MRI失败。
6. 第二作业独立重新读取同19包，独立fold/retained统计、Torch bilinear全source SHA重放（共享库），独立显式float32坐标四角样点核；独立非均匀weighted harmonic slopes和Hermite全heldout预测核atol=rtol=3e-5。全prediction/score的SciPy/Torch hash重放和独立NumPy数学分开记，不称共享库为独立数学证明。counterfactual38次重新核，统计/聚合以各自独立实现复算。预测变化只许改变target reference评分，不许进入source。
7. 固定合成补充：6×6×8 observed全值7、indices=0,4,…28、r/c投影5×5；两foldstd0/divisor1，原预测和评分0，heldout+10000后source/预测不变、评分改变。验证zero_std处理，不用synthetic成功替代真实38fold资格。
8. 生产/独立各1200s，CPU1/interop1/BLAS1、CUDA不可见、below-normal、RAM/disk各8GB余量；新阶段20MB。逐series释放，输出只JSON/hash/feature rows，不保存完整MR/模型。预计observed包load19+19=38，实际成功/失败逐数；新神经/GPUforward/训练更新0。失败原attempt/source/protocol保留，修复另存version；不见效果后改容差。

这只核函数的信息依赖和观测误差特征。MRI magnitude噪声无偏/条件独立、与真实缺层风险等价、病灶任务价值、动作成本或临床效果都没有证明。ordinary empirical feature比较不额外要求这些理论条件，但不得发风险证书。只有原两臂真实final exit0/冻结后，先原56FOV/6gates/strict，再配对实际动作任务收益、强同成本控制，冻结后才8确认与第二任务网。fresh calibration只限制正式风险保证。
