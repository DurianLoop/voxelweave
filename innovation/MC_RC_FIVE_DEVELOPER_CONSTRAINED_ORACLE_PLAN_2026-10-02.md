# 五开发患者的病灶约束动作上限：结果后诊断合同

本方案在新约束系数计算/求解前保存，明确为看到001/002 raw开发失败后的事后诊断。三人pipeline主门槛失败、五人raw无约束门槛失败均保留，不改原门槛、不训练收益头。本次仍开发/target-assisted，并不是新理论、可部署守卫或未见确认。

科学问题：在完全相同的raw PCHIP→已有HAT线段和tile32动作空间内，加入两项病灶图像误差约束后是否仍有支持域改善？无约束全支持损失oracle失败不能证明这个动作空间不存在联合可行解；本诊断量化剩余空间，不把优化器当MRI方法创新。

## 固定输入和目标

合并已独立核验的001/002两开发结果与004/005/006三开发结果：五人240个内部缺层、各最早既定时间点，不重跑HAT或改源/尺度/phase。读原MR、label和保存HAT，核各run_contract/input/output/proof hash；原3D/label来源及角色不改。raw PCHIP用独立Hermite实现，先核baseline/candidate/unconstrained的全部固定端点与已核结果吻合，失败停止，不求有利解。

人工label、隐藏MR reference明确用于约束和系数，部署不可用。各tile α_i∈[0,1]，只含原支持域非空tile。对区域r的平方误差写成 b_ri−2m_ri α_i+d_ri α_i²；这是标准凸二次式。主目标是所有内部缺层支持域NMSE目标等权：每tile系数除以该层支持像素数和目标层数。

约束1：病灶目标等权NMSE≤raw/HAT两固定输出该指标的较小值；每tile lesion系数除以该层病灶像素数和非空病灶目标数。约束2：病灶像素加权NMSE≤raw/HAT该指标较小值；系数除以所有内部病灶支持像素总数。空病灶不造0值、不删除人；本五人已有非空病灶目标。label∩观测支持域定义不变。

该两个约束可偏好不同固定端点，不能假设常数0或1必然同时可行。原无约束tile32作参考，五个常数仍描述，不以病灶mask选部署动作。

## 固定求解和数值认证

使用两个非负拉格朗日乘子，box内最小化闭式 `alpha_i=clip((m_si+λ1*m_ei+λ2*m_pi)/(d_si+λ1*d_ei+λ2*d_pi),0,1)`，零分母取0。优化负dual，解析gradient为负约束违例，L-BFGS-B λ≥0、初值(0,0)、maxiter2000、maxls50、ftol1e-15、gtol1e-12，无多初值/尺度搜索。

保存每tile支持域/病灶的三组系数、alpha、lambda、优化器状态/迭代、约束实值/上限/违例、primal/dual和gap。数值认证条件固定：两个约束违例均≤1e-10 NMSE、primal−dual在[-1e-10,1e-8]内、box stationarity残差≤1e-8，所有finite、alpha∈[0,1]。这是数值精度容差，非允许病灶退化的临床界值；不追溯修改原严格守卫。优化器success与certificate分别报告，不通过时pending而非成功。

每患者报告相对较佳raw/HAT固定支持域输出的dB改善、约束满足及unconstrained改变量。只有五人全部数值认证且各改善≥0.1dB，才称“本开发动作空间存在值得进一步验证的病灶约束上限”；仍不恢复原门槛或启动训练。不得仅算四人/挑某病灶指标。

## 独立复查与边界

保存coef NPZ和全部端点/源码hash；独立从原MR/HAT重新算解析raw、用不同逐tile实现核coef；用保存alpha在实际像素上重算目标等权/像素加权两病灶端点和支持域，避免只验dual/JSON。独立检查box KKT、dual lower bound、primal gap和目标/约束，在数值容差内判断，保留failed/pending。

最多一个CPU数组/优化进程，单线程/低优先级、RAM8GB/磁盘15GB底线，不占GPU、不干预终端训练。没有新HAT/分割网络推断，人工标签和reference可见只为oracle。本次不能证明观测特征能预测alpha、临床Dice改善、真实厚层恢复或安全保证；仍需先例对照和新未见患者/完整任务确认。
