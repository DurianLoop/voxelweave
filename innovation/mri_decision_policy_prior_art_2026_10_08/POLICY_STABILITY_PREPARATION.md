# 固定观测下策略探索准备

本文件是新增文献驱动的后续准备，没有启动医学实验、没有冻结新的成功门槛／改变既有协议。已有 [强三臂资源入口](../three_arm_resource_bridge_2026_10_08/run_three_arm_real_resource.py) 与 [正式标签／费用准备](../paired_task_label_adapter_2026_10_08/POSTFIT_EXECUTION_BRIDGE.md) 继续有效。不能复制新dummy label/cost、不能拿native−PCHIP收益当部署动作标签。

| 待验证问题 | 为什么值得保留 | 下一项可证伪证据 |
|---|---|---|
| 充分任务适配后，固定观测的表示／合法修正仍存在病灶余量吗？ | 插值后的性能差距可能来自有限容量／优化偏置；TACKLE、task-adapted inverse问题、L2SR已有强适配先例 | 先通过原能力；三臂同观测／同容量／共同draw／监督，在真实资源基础另冻正式训练与完整FOV结果。无余量则不训练收益策略 |
| 当前状态是否提供超出固定动作、条件成本／defer／DC的患者选择收益？ | Diagnostic已有classification reward policy；普通gain head并不新 | 同动作库／feature集／容量／训练预算，比较相对收益与既有成本表示；完整部署cost纳入probe和selector。强控制无增益则收缩或否定策略claim |
| 随任务适配变化的feature／label是否造成虚假策略优势？ | Diagnostic指出classifier分布漂移；L2SR纠正sampler/reconstructor mismatch | 所有task/action checkpoint先冻，再产生feature／label。每个记录绑定task、action、observed SHA、端点、病例角色、完整成本版本；若模型变动则旧bundle不再适配新模型 |

第三行是实验控制／可检验失配来源，不是新的理论或算法。可在开发阶段比较冻模型feature与重新生成feature的结果，但不能在未见确认集试探checkpoint／选择哪个版本表现更好。任何正式附加实验须先在独立新版本协议写明预算、训练暴露、主要比较、失败处理；本准备不宣称附加实验已实现。

实际执行顺序：原 session99542 两臂均final exit0并冻结；原56完整FOV、全部六gates、独立strict和真实退出；三臂真实资源qualification，测RAM/GPU峰值、resume、最大代表FOV；根据真实资源另冻正式三臂训练，而非把33draw/arm资源测试当正式训练；强适配全FOV；合法固定动作正负／零余量与完整患者费用；开发策略和强控制；所有模型／动作／端点／预算冻结后一次未见确认。资源资格通过仅证明可执行，不证明病灶效果。

状态特征来源可以是已冻结任务模型的便宜probe，但这个probe必须在完整患者cost中出现。GT仅进入训练标签／离线评价，不进入线上决策／特征／定位。开发11患者19series全已参与task模型训练，head-only LOPO依然只是开发选择，不能写整个pipeline患者外。已见4患者9series及未见8患者12series角色保持，locked IXI继续关闭，旧MIRA／MSValid84保留。

完整费用分研究训练／label生成账与部署账。部署按既有九阶段记录启动、IO、定位、feature/selector、动作生成、transfer、任务推断、组合、后处理／失败，并记录父级墙时、同步、设备、dtype、warm/cold和并发。L2SR已有包含policy与reconstructor的算法费用，不把它错写为无policy成本；本项目需要补齐本机完整患者费用，而非把“包括policy”本身当创新。

若强适配消除了插值差距，可以保留“此前收益来自任务模型失配”的负结果机制；是否可发表仍需充分对照和未见证据。如果fullcost下静态路径更优，就保留这一结论，不补造隐藏动作余量或切换成功指标。当前旧弱checkpoint的9对标签只是接口资格，fullcost=null、fit_ready=false保持。

待读原文准备：MASC核simulated metal／fastMRI跨数据与真实患者范围、joint/frozen细节、费用；Cartesian thesis核stochastic LBCS强静态控制及split；TADT核controller自身体积／实测latency与“task”定义；medical fairness核MRI任务端点与patient分母。只记录摘要线索，尚未计这四篇全文。
