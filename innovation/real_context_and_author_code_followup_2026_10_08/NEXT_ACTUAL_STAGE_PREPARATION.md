# 当前真实实验之后的具体接续

## 先真实轮询现有医学任务

原四臂 session29823仍live，native两臂都2992，raw intensity最后有输出7ef5e1到440/2992，fad2e9空但含session29823；raw spatial未观察完成。原device CPU/AdamWreset/lr1e-4/11968总更新不改。GPU最近5d4969 free1394MiB/total24455/util92%，授权有效但不满足原8192MiB储备。不枚举/干预其他PID，不安装依赖或委派。

真正terminal exit0、无session_id后，实际工具JSON加observed_unified_exec_session=29823，保存原spatial目录ACTUAL_TRAINING_TERMINAL_TOOL.json；使用已有 `D:/conda/envs/MRI/python.exe` 运行capture_training_terminal.py。它核四last2992、11968日志、每患者272步、input/label/geometry/primitive配对。通过才evaluate_matched.py；其真正exit0后capture_evaluation_terminal.py、summarize_matched.py。本轮24be97已完整核读入口，评价保存 allowance3MB、wall3600、CPU4，不初始化CUDA。必须fresh资源守卫；磁盘最近约8.028GB，不能放宽8,000,000,000bytes储备或删旧证据。

9已见验证series/4患者×4臂=36production+36独立functional完整FOV。所有原六医学门槛、3e-6概率/3e-12坐标/二值0保持。这里只作已见验证开发，不称独立确认。8未见/12series和lockedIXI仍关闭。

## 新强baseline被一个实际覆盖结果拦住

全5984候选往返geometry资格a4b6f8和原sample_batch独立审计402242均真正exit0。18前景支持不足反例已保留；整个target的固定支持gate只有272 active可执行，5患者及9series为0，绝不是完整患者上的充分增强认证。decision SHA `5ac83d7315c5460da75330d9721dcc599c1a8d2b88f7686ec750fa33f165b05f`；全部失效/identity保留、无按GT删样本。不要立即把该policy跑成新四/六臂，再拿稀少事件分布称强基线。

下一可做的CPU工作是**新的候选资格**：保持原crop/flip/schedule，仅比较文献普通in-plane image roundtrip或image-only resolution degradation的物理域、母padding行为及完整患者事件覆盖。明确只从真实cache读取；padding和缺坐标有明确定义，不反射/复制伪造组织。若改“只在原有效域不新增缺失”的相对支持标准，必须新协议、新完整数值资格、保持padding输入的实际行为和InstanceNorm依赖审计；当前绝对gate资格不自动认证它。不能把修改支持语义称为原门槛通过，更不能用FG GT筛policy或四验证选超参。

先进行metadata/synthetic/source-domain资格，失败同样保存；成立后再读11开发/19series合法MRI、固定完整intensity管线、实测cache/support/forward/backward费用。达到完整覆盖和新GPU储备再冻结同parent/schedule/last/optimizer/总更新的matched训练。文献VINN内部尺度扰动和TorchIO降采样都已有先例，作为普通控制，不列创新。

## 创新假设的医学链不变

充分模型后先测具体动作是否存在真实损害改善余量，再训练采集可见性→该动作损害差/费用头，比较strong QC/error-cost/defer、static best、always/random及去采集信息。所有learned component按患者折外；全11GT的19998parent不可用于宣称独立外折。现有ranker只做指标静态排序，不补OOF/ensemble源码缺口；GT radiomics分层不等于部署可用特征。

如果充分任务无动作余量，保留负结果，不靠PSNR或支持资格制造病灶收益。完整protocol/selection冻结后才一次打开8未见确认，独立任务实现复核。目标active，当前没有新患者分割效果或发表claim。
