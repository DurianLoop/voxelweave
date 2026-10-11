# v2失败已结束，后续从新的数值证据推进

本文件是本轮前面“90446仍live”的文字快照之后的最终事实更新，旧文件不回写。**不要再poll90446**：真实fdcb62 exit1且无session_id，10479.851s，14673/35904成功、2445完整case-kind步后第14674字段失败。原terminal已保存在full_real_intensity_v2_2026_10_09/ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json，observed90446。

feea61独立终态审计exit0：全部14673行是原35904排序的唯一exact-prefix，与原geometry、metadata、schedule、enabled、validity、各患者/series计数和成功maxima一致。next key[2879,1,8,0,0]精确匹配failed_field。full资格仍失败，成功maxima不包含failed值，禁止把prefix继承为新runner已通过。

56d85e单字段重放exit0：患者006、开发case8 native、step2879 patch1 throughplane active，gamma1.2140923402286599、bias/noise关闭。pre1.9073486328125e-6，shared/full3.814697265625e-6，isolated0；support/二值一致。失败不是同输入下gamma两实现不一致，而是前级resolution差异经共同gamma传播。全float64 gamma诊断仍shared3.814697265625e-6，不能据此选修复。

93d71f精确Fraction独立核固定最大post位置[15,37,110]：fine[86,400,400]→coarse[67,400,400]，query[15,327,304]，coarse z198/17。两级插值exact值31100331/2097152=14.829793453216553，正处两float32中点；lower bits1097680597与upper1097680598距离同为1/2097152，ties-to-even应选upper14.829793930053711。原scale/shift后15.795825004577637，与生产一致；SciPy给15.79582405090332，位于另一舍入侧。Torch归一化grid double比exact高4.263256414560601e-14，仅本witness发生最终舍入侧区别。本文前面的“检查不受影响轴”是事前探索，实际结果没有证明它是全误差来源。

该位置生产最终舍入正确并不意味着全部Torch字段更准、SciPy所有字段错或可以重写oracle迎合生产；原独立oracle保持不变。两条double近似在恰好half-ULP处会落不同侧，固定绝对3e-6又在gamma后放大，说明下一步应审计近半ULP舍入稳定性。一个witness不是完整35904修复资格，原医学六gate更未通过。

下一数值准备：另新attempt，用精确rational stencil/二级值对多轴、flip、singleton、padding、inactive、gamma enabled fixtures作独立nearest-float32校验，比较double计算误差的上下界与tie距离；原oracle不改。任何候选新生产/新reference必须先独立证明数学意图和适用域，而不是只消掉失败witness，再完整271stress及全35904从头运行，保留原坐标/强度/二值门槛。不要无条件加epsilon、round decimal、过滤高强度或删失败患者。

六分支runner/cost资格及完整forecast仍未通过，GPU1394MiB也未达到8192准入。领域泛化/区域对比度/QC/UQ阅读与5toy已带来科研准备进展，但没有新模型医学收益、确认集或发表claim。全部新增只innovation，不动用户终端训练、不删历史、不安装、不委派。8确认患者12series/lockedIXI关闭；科研goal active。
