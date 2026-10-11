# 真实两通道资源入口与合成执行路径：事前协议

本协议推进当前缺失的真实资源入口实现。当前原训练session99542仍live/native7524；不操作/迁移/重启既有训练，不读取中间任务效果。既有配对sampler、输入、FOV、旧56FOV及所有冻结证据保持原文件。新文件仅innovation。

## 外层入口

stdlib外层先运行旧readiness子进程，真实Python exit与JSON ready均合格，再核本轮合成workflow资格及真实exitreceipt；两者均合格后才能import神经/MRI模块和加载开发数组。当前original training/56FOV/6 gates/strict/actual exits缺失，实际启动入口必须返回exit3、complete=true/statusprerequisite_deferred；实际real_resource_qualification_completed=false，MRI reads/model updates/CUDA initialized均0。不创建训练final或verifier退出receipt，不冻结live invocation02 SHA。

资源资格新attempt不覆盖，save<=5MB，累计<=1200秒，8GB RAM/磁盘余量，自身below-normal；CPU4/interop1/float32。GPU选择明确--device gpu，需先nvidia-smi总量8GB空闲，随后旧loader import可能将自身CUDA_VISIBLE_DEVICES设-1，再仅自身process恢复0，启用float32/noTF32/deterministic cuDNN、.1 allocator fraction、reserved<=2.5GB、free>=4GB。不请求其他PID，也不改变其他进程。

## 真实开发资源路径

使用development_observed_cases仅19series/11开发患者，无validation/confirmation/native MRI像素；observed字段由已冻结模块构造dense、numerator、availability、valid_grid，开发GT只在独立监督入口read_reference_label/physical_label。输入构造及infer不接受GT。逐例核此前19series物理输入SHA和原物理labelSHA。

共缓存5个float32field（共享mask/valid/target）；实际缓存bytes应4,774,280,000，另记RAM/自身peak RSS，数组估算不是进程峰值。沿旧资源stream_for患者等权deck轮转，33 draws覆盖19series且每患者3次。一次物化全部draw，两臂共享centers/flips/s,t/labels；density/padding增强沿已冻结规则。

两臂共同canonical两通道初始化、1,401,795参数，AdamW LR/WD .0001，float32。每臂33资源更新，第一步存model/optimizer/torch RNG到内存，第二步连续与内存恢复重放tree exact，每臂多1次重放，真实总资源更新68；不保存任何更新权重、不进行formal training、不评分病灶效益。

分别计sample/hash、搬运、forward/loss、backward、梯度检查、optimizer wall；全branch/mask第一步梯度有限非零。资源guard开销和draw构造在全attempt wall中保留，不称同时负载下一次timing为稳定benchmark。

代表FOV按19series中固定tile数最大者（同数UID排序首个）选择，非按GT/效果选择；每臂用资源更新后的权重完整原PATCH/batch2 FOV两次，所有native/physical/coverage/tile SHA应逐位一致；只保留SHA/成本，概率数组不落盘，不读取GT评分。它不是19series全部FOV评价：资源FOV只验证最大tile数代表，完整任务仍须后续正式评价。最大tile数也不必是所有资源维度的最坏，另记全部shape/tile计划和maxvolume，不能据此夸称所有MRI峰值皆已实测。

资格权重丢弃，返回真实资源通过后另立正式公平训练预算；不得把资源资格作为训练能力、MRI净收益或发表claim。

## 当前可执行的合成workflow资格

在原gates缺失时，只合成资格可运行：core65x129x133、padding后68x132x136，PATCH64x128x128/batch2；两个synthetic UID、固定3draw，每臂3更新并恢复第二步，共8synthetic更新；共享draw、labels/masks、两个输入UID可区分。新worker完整走checkpoint、更新、FOV/资源callbacks，不能用小patch替代。每臂代表8tile FOV重复两次、SHA一致；不运行独立functional网络，该功能此前已资格通过。

合成cache不能证明真实19series RAM/GPU资格。审计钩子禁止data/、MRI zip/NIfTI、validation/confirmation读；updated weights仅内存，保存只JSON。完成后核实际exit，再运行真实外层当前延期入口验证其先验gate阻止神经import/MRI读。后续对source SHA、流/更新/覆盖/退出证据作独立校验。旧direct理想absolute gate失败继续保留，未修改旧数值门槛。

