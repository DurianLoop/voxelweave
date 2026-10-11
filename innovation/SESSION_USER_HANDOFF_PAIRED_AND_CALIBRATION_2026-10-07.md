# 用户范围与继承状态

本文件保存当前可见用户请求和压缩接续摘要。可见请求如下：

> 接着基于我的MRI项目读论文找创新点

> 目前GPU正在被占用着，你批量地读论文和根据我之前的工作找创新点，能验证的先试着探索一下，不能验证的也做好记录和准备后续尝试，把这轮对话所有的内容放进D:\MRI\innovation里

> 可以用gpu

长期 goal 的实际读取结果为 active，目标原文：一直研究探索验证下去，直到达成一个可发表的claim，注意不要动我现在终端训练的进程。

本轮继承的摘要是接续状态，不等于此前完整逐字对话。只保留能观察到的公开对话、用户摘要、工具执行记录、源码及结果，不重构缺失的历史原文。新文件仅写 innovation，不修改冻结文件、根环境、.gitignore，不委派代理。

## 用户提供的继承摘要所记事实

- 原 CPU 训练 session 99542 仍 live，不重启、不迁移；native 最近 6633、新增 6534，累计 14221.390370999929 秒。PCHIP 99 仅旧快照。两臂各 19998，合计 39996；CPU4/interop1、float32、共同初始化/GT/增强，AdamW LR/WD .0001，累计30h、8GB余量、250MB保存限额。
- 11 开发患者/19 series、4 已见验证患者/9 series；8 保留确认患者/12 series和 locked IXI test 关闭。仅训练真实 exit0 且最终权重冻结后，执行原56FOV和独立复核。6项能力判据：full Dice>=.70、missing Dice>=.65、full recall>=.70、full absRVE<=.50、四患者 full/missing Dice 均正、9series无complete miss。
- 上一轮 Uhrig1708.06500v2、Eldesokey1811.01791v2、Jaritz1808.00769v2：39PDF页，完整选读29页，6页实际render/view。mask、confidence、直接稀疏分割均有先例。19开发两通道输入资格及独立核验通过，非MRI效益。
- 上一冻结归档 chunk c5b1db exit0：94新stage文件、1130累计冻结证据、40858779bytes；前1032SHA不变。权威入口为 literature/direct_observed_stage_manifest_2026-10-07.json 和 SESSION_CHECKPOINT_RECEIPT_DIRECT_OBSERVED_2026-10-07.json。
- 继承轮新增配对sampler/FOV：draw一次共享centers/start/flips/scale/shift；dense增强s*value+t*valid_grid，direct增强s*numerator+t*availability；mask不变，padding0；infer不接受GT/ROI。PATCH64x128x128、batch2；合成core65x129x133、padding后68x132x136、native33x35x17。
- 主合成资格 session61161/chunk3e7ef8 exit0，43.48189519997686秒：24组draw、独立batch逐位一致，两臂各2步及恢复重做step2，共6合成更新；全branch/mask梯度非零有限，恢复tree exact；生产/functional各8tile，physical逐位一致，native threshold差0。mask置0概率最大改变 .0007798075675964355。
- 主资格事前combined atol3e-6/rtol1e-5通过，但理想float64坐标绝对误差dense2.0265579223632812e-6、direct3.2186508178710938e-6；direct不满足旧absolute<=3e-6，不得冒称旧strict通过。
- 独立坐标诊断 session79318/chunkf9749d exit0，9.848931199987419秒：原SHA重放；float32解释器两臂最大差1.7881393432617188e-7，float64与torchfloat64最大差3.3306690738754696e-16，threshold均0；保留旧ideal absolute gate的direct=false；原一通道56FOV不改。两个合成physical概率npy合计约8.9MB。
- 真实退出receipt脚本chunkc4f8f5 exit0。readiness首次chunk47847f tool exit1，JSON complete=true/ready=false/errors=[]，PowerShell未显式转交Python exit3；第二次显式exit LASTEXITCODE，chunkef9927真实exit3，预期deferred；不得抹掉首次退出记录。
- 缺原训练final receipt、主评价、评价exit、独立结果、独立verifier exit。live invocation02的SHA仅mutable_read_observations_not_frozen，不归档冻结。未来verifier receipt名称 SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_VERIFIER_2026-10-07.json，真实exit0后才写。
- 最近GPU查询chunk018d7c，19:32:19.412，free1394MiB/total24455MiB/util84%，低于新GPU8,000,000,000bytes门槛。CPU loader本进程import设CUDA_VISIBLE_DEVICES=-1，未来GPU入口沿既有pilot仅自身process恢复0的顺序；不改他人进程。
- 当前真实19series两通道资源资格未实现/运行，只有readiness入口。原gates过后才做资源资格、公平dense/direct/SR充分适配；有真实余量才推进GT-free候选、联合效益、全部成本、risk/defer/union-greedy/random；冻结后8确认。
- 旧MIRA有MSValid84人确认，旧机制/新意未过发表gate；当前病灶线确认0不等于全项目确认0。新可发表claim未确认。

继承摘要原段落顺序及措辞未全部逐字保留；以上保留所有执行条件、退出事实、数量、限制和接续路径。此前公开记录原件继续通过既有manifest追溯。

## 本轮实际起始状态

工具chunk9e00ad读取同session99542：native6732/6831，最后新增6732、累计14689.236578600015秒，仍live。工具chunka9579c：2026/10/07 19:55:40.114 free1394MiB/total24455MiB/util90%。不读取中间MRI效益、不控制用户训练。

