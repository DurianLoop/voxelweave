# 用户提供交接摘要：保留事实与接续依赖

本文件保存本轮实际收到的外部模型交接摘要的完整事实索引；摘要是用户提供的资料，不作为本助手隐含推理导出。此前未在本上下文展示的历史逐字对话不伪造，已归档历史继续从上轮入口和appendices追溯。摘要中“本轮未创建文件”为交接瞬间状态，本轮新增事实另见当前账本，不能把交接状态冒充现在状态。

## 收到的目标、约束与训练状态

- goal active，持续研究探索验证直到可发表claim，尚未达成；不以输入诊断替代MRI任务收益。GPU已授权，不操作/重启/迁移用户终端训练，不枚举/修改其他PID，不委派代理。
- 所有新增只写D:\MRI\innovation，不改根.gitignore和environment.yml，已执行/冻结文件不覆盖，修复另存version/attempt。PowerShell，D:\conda\envs\MRI\python.exe -X utf8 -B，脚本命令末尾exit $LASTEXITCODE以真实工具退出记账。
- 11开发患者/19series；4已见验证/9series；8确认患者/12series与lockedIXI关闭；旧MIRA/MSValid84保留。fresh calibration只限制正式风险保证，不是经验MRI效益论文额外门槛。日期2026-10-08，Asia/Shanghai。
- 接续首先poll原live session99542，不重启。收到的最近poll634909为native14751、invocation02新增14652、cumulative33278.30104109994s，无terminal。GPU93e991 exit0：2026/10/08 01:02:57.477，free1394MiB/total24455/util89%，新作业8GB预留未满足。
- 原两臂各19998/总39996，CPU4/interop1、float32、共同初始化/监督/增强、AdamW lr/wd=.0001、30h/8GB/250MB不变，仍native顺序训练。真实训练exit0且两个最终模型冻结后，登记退出→原56FOV→全部6能力gates→独立strict；中间模型/loss不作MRI效益选择，旧direct absolute失败不能用浮点解释覆盖。

## 上阶段已经完成、不要重复的内容

主入口SESSION_RESULT_PROJECTION_INFO_2026-10-08.md，科学结果OBSERVED_PROJECTION_INFORMATION_RESULT_2026-10-08.md，后续准备PROJECTION_AND_SELFSUPERVISED_ACTION_PREPARATION_2026-10-08.md，阅读literature/2026-10-08_selfsupervised_selection_primary_reading.md，receipt SESSION_CHECKPOINT_RECEIPT_PROJECTION_INFO_2026-10-08.json，manifest literature/projection_info_stage_manifest_2026-10-08.json。

真实退出：生产f505cc=0/主体.042580s，独立078eec=0/.142675s；获取terminal1c612b=0/启动17392；渲染f65930=0；record854d3b=0；archive4bb920=0，109新stage文件/12441574bytes、新增绑定118/13261512bytes、累计3319冻结证据，前3201SHA不变，全部最终hash/local links核验；finalize cd1366=0。上轮receipt SHA7946266d8adeb58f2ebd1aff8228073fd055757334aeb1980f103f794fe3fdab，3585bytes。

下一stage须纳前阶段postappendices（尚未在3319内）：SESSION_FINAL_TOOL_OBSERVATIONS_PROJECTION_INFO_2026-10-08.json、SESSION_POST_ARCHIVE_PROJECTION_INFO_UPDATE_2026-10-08.md、SESSION_CHECKPOINT_RECEIPT_PROJECTION_INFO_2026-10-08.json、SESSION_OBSERVED_EXITS_FINALIZE_PROJECTION_INFO_2026-10-08.json、SESSION_DELIVERY_PROJECTION_INFO_2026-10-08.md、experiments/finalize_projection_info_checkpoint_2026_10_08.py，及上一manifest/proof。

已完成源码experiments/observed_projection_information_2026_10_08.py、verify_observed_projection_information_2026_10_08.py；结果同名目录attempt01.json及independent_modular_rational_attempt01.json。只读冻结两通道资格JSON/源码，上阶段新增医学/模型数组、神经/GPUforward和训练更新全部0。

1. 稀疏normalized numerator→physical grid理想实数线性秩：22不同axis map，生产Fraction稀疏消元；独立整数系数在预定prime1000003/1000033达到matrix维数上界，构成有理数rank证书。19/19 observed z全列秩，12/19面内零空间。observed强度维数86999040，rank58334368，完整患者维数合并后比值再患者等权.6746856073384448。它是ambient维数比例，不是MRI信息量/解剖损失百分比，不证明float32可逆/良好条件数或实际信号落入丢失方向。PCHIP非线性，不宣称总信息更多。
2. 实际原模块固定合成见证native r4/c1/z16，observed=[0,4,8,12]，physical r2/c1/z12。A=[[0,0,3,3],[0,2,1,3],[0,1,2,3],[0,1,2,3]]；C=[[0,0,1,3],[0,2,3,3],[0,1,2,3],[0,1,2,3]]。同mean1.5/variance1.5/16元素；direct numerator、availability、先投影anchors和共同投影后PCHIP逐位相同，native先localPCHIP后physical不同，max差.042525842785835266。独立有理数Hermite差.042525863589985724，输出误差≤3.81e-7。仅合成反例，不是实际MRI或任务收益。同raw观测workflow比较有意义，但最终表示不宣称严格信息等价，后续加共同投影控制。
3. OBSERVED_PROJECTION_INFORMATION_PROTOCOL v1因执行前源码检查澄清为v2；v1未运行任何数组/评分，保留，不是效果后调参。原reconstruct首尾间隔linear fallback，只有内部四anchorPCHIP，tail复制，不能用全局PCHIP冒充原实现。

## 已读两篇自监督原文，无需重复计数

缓存literature/source_cache/selfsupervised_selection_primary_2026-10-08。Noise2Self arXiv1901.11365v2取得16页，实际文字1–8/视觉2、6；SSDU arXiv1912.07669取得61页，实际文字[1,2,4..28,36,40,45,46,54,55]共33页，视觉36、40、45、54。合计77取得页，41文字/6视觉；未读范围有provenance，不是作者复现。

Noise2Self平方风险等价需要无偏、条件噪声独立、J-invariance，不保证Dice/任务收益，mask须先于混合目标值的操作。SSDU Θ用于DC、Λ用于k-space loss，测试全Ω；MRI编码与整层image-domain不同。kneeR4、brain19healthy/10train9test、prospectiveR2再retrospectiveR4/6/8，无fullysampled brain reference；R8退化、不同loss/reader端点保留。不能将heldout误差当无标签任务收益证书；旧3IXI训练病例known-profile留出选核已失败，不重复计新或改写。

## 交接时当前工作与建议（收到时尚未执行）

交接已先poll原训练并读准备与旧两通道生产/独立源码，本轮当时尚无新protocol/module/result。已经公开：“上一轮完成了输入信息诊断和独立核验，属于实质进展。我会先检查原训练，再把‘共同投影观测’的控制实现为独立输入模块，并在全部19个开发系列上核验，为后续公平任务比较做好准备。”

接续目标是在真实19开发observed-only包实现先共同投影observed anchors再分支，不跑神经网/训练/GT，保留原模块。建议：先协议→新纯输入module→19生产hash/摘要、逐series释放→独立重读19包、显式coords/PCHIP/Hermite→结果/准备/对话/compaction提示归档及核3319/postappendices；原训练未最后退出，不先做任务效果/新增正式训练。

旧module mc_rc_3d_direct_observed_2026_10_07.py提供development_observed_cases（19）、load_development_observed（认证NPZ）、native_fields（全部observed stats、normalize、PCHIP、sparse numerator和binarymask）、physical_fields（原3Dtrilinear）、augment_pair（dense s*x+t*valid，direct s*num+t*availability，mask不灰度变换、padding0）。旧资格和独立分别mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json与mc_rc_3d_direct_observed_independent_2026_10_07/attempt01.json，新puremodule可复用loader但不接GT/native参数。

拟设计：原全部observed mean/std先normalize，每observed plane2D bilinear align_corners=False到grid r/c，两路只用同float32投影normalized anchors；direct插native z后z-only map/padding，dense原localPCHIP/首尾linear/tail复制后z-only map/padding，不重估stats或再normalize。此控制是任务输入因素，不冒称原native-anchor preserving SR。中间affine须native affine乘r/c像素中心scale=nativeRC/targetRC、translation=scale/2-.5、z保持native；final沿原grid。availability沿旧binarymask→physical_mr构造一次，两路共享以旧mask SHA exact；两阶段和原3Dtrilinear数学相同但float32可能不同，需如实核验；不修改原资格direct/PCHIP，不把inputMSE当任务效益。

旧独立verify_mc_rc_3d_direct_observed_2026_10_07.py使用每series512固定随机physical coords及每anchor附近3z×3面内点，显式8cornertrilinear，atol=rtol=3e-5并全native/physical SHA重放（physical仍共享Torch）。不能突然用1e-5要求高梯度实际MRI的float64坐标与Torchfloat32全体素完全相同。新资格预定适当容差，区分全执行重放和独立抽样；完整NumPy面内/Hermite需预定数学vsfloat32误差，不见失败后追容差。

CPU新工作1/interop1/BLAS1、below-normal、CUDA不可见、逐series释放；旧qualifier CPU4不可照搬或增加原训练并发压力。建议各900或1200s、RAM/disk8GB储备、stage20MB执行前冻结，输出只hash/summary，不存大体积。

收到时最近只读8d4f3c=0（准备/后归档状态/旧qualifier）和79256b=0（旧独立和baseline）；当时新turn无失败/审批拒绝/新增医学数组。根.gitignore SHA7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524、environment.yml SHA dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257。可参考record/archive/finalize_projection_info_stage脚本，但须另建名称，不覆盖。

本轮实际执行后来出现独立v1数值失败并用v2区分后端坐标精度；实际source/protocol/result/退出详见新[结果](COMMON_PROJECTED_OBSERVED_INPUT_RESULT_2026-10-08.md)，不回填上述交接资料。
