# 本阶段完成结果和边界

## 完整合成与几何检查

原脚本因项目已设置interop=1而再调用set_num_interop_threads触发RuntimeError，16bc17 exit1，在attempt创建和患者数据前。原稿保留。V2只改harness：断言已有interop=1，并将synthetic cache释放移到全部geometry之后；算子、独立实现和门槛不变。

V2真正session69075/7b5ed8 exit0：270合成完整字段、17952 metadata控制记录（5984几何×3候选）。image最大2.384185791015625e-7，support最大7.327471962526033e-15，coordinate最大1.1368683772161603e-13，二值差0，耗时19.8815343秒。全部11开发患者/19series每模式都有事件；每模式1785 enabled/effective，患者149–182事件。每模式valid曝光6,041,370,624、继承padding曝光233,308,160。metadata决策journal SHA757842c8c2af8ece4137839a0b580d9fb6371de9118e3fd0ae507264dacb08fa，398485bytes。这一过程MRI/GT/model新数组均0，不是完整真实MRI认证。

## 完整228真实字段及强度组合

真实stress session5725/868f3b exit0：19series×2输入×2母patch×3模式228，全target Torch/SciPy独立重算，38MRI/19GT数组加载，输入/母GT/cache SHA匹配原资格。image最大1.9073486328125e-6，support最大7.327471962526033e-15，coordinate最大1.1368683772161603e-13，二值差0，母label不变。所有support mask等于母unpadded域；仅分辨率算子阶段原padding逐位保持。239,075,328 target、228,655,104 valid曝光体素是重复patch曝光，不是独立解剖体素或患者数。

此检查实际588.3140553秒：cache载入82.0069735、生产81.8164329、独立355.6123945秒。差额包括GT重建、来源哈希、比较、GC及输出等，未全部分解；不能称这些是完整训练/部署费用。

同生产强度组合session31866/ee6557真正exit0：全部228完成、失败列表空，最大post-intensity误差仍1.9073486328125e-6，594.9972579秒；MRI38/GT19再次读取同19series，不能合计为76独立扫描。cache85.6709970、分辨率生产79.4360840/独立352.0426114、两份结果同生产强度组合4.7484124秒。此前使用同一个旧gamma/bias/noise函数，证明组合误差传播，不是独立强度资格。完整receipt保持training_ready=false。

独立強度参考不调用旧生产函数，单独实现统计gamma、指数bias和noise接口，但共享NumPy PCG64 float32-normal抽样规范，不宣称独立RNG。696add真实exit0：40完整合成字段、完整5984 primitive合法性检查，最大9.5367431640625e-7，1.4293672秒，无患者数组。各变换边界float32，统计量参考float64。详情见[协议](INDEPENDENT_INTENSITY_PROTOCOL.md)。

## 正在执行与未执行

session74234已启动完整真实MRI+独立强度：35,904目标字段、5984几何×两种输入×三模式；真实8bf93b仍live，到1344 fields，已完成字段最大full-chain error2.384185791015625e-6。未观察最终完成，不能写all35904通过。各字段记录pre/shared-post/isolated/full-chain四种强度误差、support/coordinate/binary及母padding检查，按原3e-6/3e-12/zero binary门槛逐项拦截。

另进程终端/分母审计已编写并做AST检查，当前没有执行。[审计协议](FULL_REAL_TERMINAL_AUDIT_PROTOCOL.md)明确必须真实exit0后才核完成日志；不把日志审计称第二次生成全部mask。原四臂 session29823 最新raw intensity2310/2992，仍live；完整36production+36functional FOV评价、六医学门槛和所有患者分母尚待。

本轮新增不同论文正文0、新模型forward/backward0、新训练0、新医学效益0。8未见确认及lockedIXI关闭；发表目标active、claim未确认。三轴候选仍须完整实际分布和全部训练/推理费用资格，普通降质本身不是创新。
