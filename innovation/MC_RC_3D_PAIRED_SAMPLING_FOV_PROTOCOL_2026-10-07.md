# 配对采样与两通道完整FOV：执行前资格协议

上一goal turn是实质进展：3primary核读，19开发observed输入及独立坐标/合成更新资格，94新stage文件/1130累计immutable evidence冻结。当前真实poll e272c7仍返回live session99542，native6237，新增6138，累计13317.087144799996秒；GPU实际19:32:19.412 free1394MiB。不要重启、迁移或控制任何用户终端训练。

本轮补齐后续任务比较必需的配对抽样和完整FOV两通道推断。既有一通道sample_batch/infer_full_fov与已冻结两通道输入模块保持原文件；所有新实现另立版本。资格数据完全合成，不打开MRI observed/native/GT/validation/confirmation，不运行MRI任务；使用上一轮已冻结的synthetic_direct_after1权重作含非零mask权重的推断解释器检查，不读取当前live MRI权重。

## 合同

1. 新sampler先仅由监督training target及固定rng生成两个draw（forced_foreground/random），沿用原centers、clipped starts、3轴flip、scale[.9,1.1]、shift[-.1,.1]顺序。draw只生成一次，两臂显式消费同一tuple，不各自推进rng。training target仅用于采样与监督，从未传进observed输入构造或infer接口。
2. dense与direct分别构造[channel0,availability]；沿用冻结augment_pair：dense=s*value+t*valid_grid，direct=s*numerator+t*availability，mask灰度不变、padding0。label和两个channel同步flip；不得先给所有voxel加偏移再试图在模型里纠正。draw、array不可被apply函数回写。固定PATCH64×128×128/batch2；允许小patch仅用于额外边界拒绝检查，不以小patch替代主资格。
3. 完整FOV推断只接model、value、availability、grid、native_shape，无target/label/ROI位置参数。输入patch为N×2×64×128×128；原50%overlap tile计划、Gaussian blend及float64累加、padding裁掉、float32align_corners=False回native RCZ、固定threshold .5。这些都不是新方法claim。
4. 资格合成core65×129×133、padding[(1,2),(2,1),(1,2)]，总68×132×136、nativeRCZ33×35×17。八窗口必须覆盖所有physical voxels，并保留最后boundary tile。availability取周期0/.25/.75/1；direct=availability*synthetic signal，dense=signal；不是物理slice profile模拟，也不评MRI效果。

## 实际检查与预固定范围

- 24组rng seed的sampler draw必须与原sample_batch产生的geometry/augmentation primitive完全一致。另以scalar/slice NumPy解释器从draw分别构造dense/direct/target，两个batch逐位等价，same label/mask及输入未回写；padding0和direct无availability处0。至少覆盖三轴flip的真/假及非零shift。
- 原PATCH/batch2真实CPU forward/backward/AdamW：每臂2步，再从完整model/optimizer/RNG after1 checkpoint恢复重做step2；按tree exact复核。共6次合成更新，updated weights不持久保存；序列batch由step种子重造，共同canonical2ch初始化，loss为原3head BCE+Dice。不把合成loss称为task能力。
- 两输入均从含已训练非零mask权重的旧合成checkpoint执行8窗口完整FOV；独立functional_forward/独立tile起点/独立Gaussian/float64blend/独立NumPy8邻回native解释器重放。全tile概率、crop physical probability的atol3e-6/rtol1e-5；native probability的atol3e-6/rtol1e-5。若出现.5 threshold rounding差异如实报告并判失败，不靠概率接近放行binary不一致。
- 资格第一块tile将availability置0，以受训非零mask权重模型验证真实使用第二通道；结果要有非零差异。对tile SHA/coverage/物理与native probability存SHA，可保存合成native probability数组，禁止保存MRI影像。
- 新资源合计CPU4/interop1、float32、自身below-normal，600秒，8GB RAM/磁盘余量，新增保存≤25MB，CUDA未初始化。不是新GPU或真实MRI资源资格。

## 科学接续门槛

当前19series训练仍须两臂各19998并真实exit0，执行冻结56FOV评价/独立重放。旧“原四validation”简称指4已见患者，不是4个数值条件；现有gates函数实际包括6项：meanfullDice≥.70、meanmissingDice≥.65、meanfullrecall≥.70、meanfullabsRVE≤.50、每个四患者full/missingDice>0、全部9series无complete miss。新资格不替代任何一项。

仅原能力通过后，才做真实19series/fullPATCH/batch2两通道资源资格、正式公平dense/direct/SR适配和真实修正余量。如果gate失败，先诊断任务能力而非用弱直接基线制造SR提升。8确认/12series和locked IXI test继续关闭。本轮不宣布可发表claim。
