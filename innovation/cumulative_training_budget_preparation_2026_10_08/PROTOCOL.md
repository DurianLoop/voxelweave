# 长训练累计预算的CPU执行准备

本阶段补未来正式三臂长runner的累计账原语，不是MRI算法、医学资源或任务能力验证。上一轮两论文/15文字页/10视觉页与CPU原表是progress；当前真实e64eea仍确认session99542 live，无新输出不是terminal。GPU5c0ad2（2026-10-08 07:06:44.674）free1394MiB，新医学作业8GB启动储备仍缺。用户终端训练和其他PID不控制，不委派代理，所有新增只本目录。

现有disk-resume已验证model/optimizer/RNG/config/log精确恢复，资格合同是600秒；training_engine.py调用外部guard且不携带正式长预算。不得再跑16人工神经forward当新进展。本阶段只标准库、CPU单进程controller+自有child；零MRI/GT/旧或人工checkpoint数组、零神经/GPUforward。实现可复用累计账，以未来trusted医学入口给出的冻结contract为准；现在只接受synthetic accounting资格入口，正式充分适配预算和医学长runner仍未冻结/完成。

资格合同：三arm名字不变，但每臂仅3个SHA256工作标记（不叫训练更新），共9实际CPU work units。拆成三次独立child，绑定逐arm序号、共同step-token和ledger parent SHA。controller从chain核查开始到关闭transaction，记录实际perf_counter_ns前缀，加收固定1秒封闭余量；封闭写入/解绑pending后实际完整区间必须不超过这个保守charge，才将新head交给caller。累计的是保守计费纳秒，不声称其与实际秒精确相等。范围包含child启动、imports、work、结果读取/验证、journal和封闭IO；controller自身进程启动和qualification外层夹具准备/汇总不在此原语范围，不能称完整训练/部署全部cost。阶段自身另按整个600秒计账。

每次调用先核contract、源码SHA、外部expected-head及封闭receipt chain，累积已支付duration和每臂work计数，然后校验剩余预算/预留下一transaction/更新quota。正常封闭receipt不可覆盖。写pending marker后才能工作；child非0退出或日志未提交保留pending和failure观察，后续拒绝恢复，不能默默忽略未付费工作/尾部或从零重置预算。失败区间已知elapsed独立保存，未知power-loss时间保持未知；不声称自动恢复崩溃账。

正常资格总controller预算60s；这些数值仅人工执行资格，不是未来医学预算。第一正常receipt后另提出60s reserve，必须因已支付耗时而在新工作前拒绝。quota满后拒绝额外work。新崩溃fixture复制第1封闭receipt，在第2 child实际完成3个SHA工作并写journal后exit17；必须记录真实exit/elapsed/pending并拒绝恢复。它增加3个真实CPU work，资格总计12，神经更新0。

另外在7个新的只验证Python进程中，核正确第1receipt可跨controller进程重载，以及预算reserve、quota、unsealed失败和3个fault（duration声明不符、joint-step/arm序号错、expected-head SHA错）。这些进程仅核标准库文件，不跑work child；拒绝返回3、正确返回0，输出完整保留。4个work child与7个验证子进程合计11，真实CPU work仍12。独立verifier不用新core重算各receipt/journal SHA、sum整数纳秒、三arm序号、shared token、source绑定和crash实际三工作，核所有负例/实际退出。不得把人工严格检查等同MRI充分能力。

阶段保存上限2,000,000 bytes；整个qualification600s，各child20s；保存前另留2MB写入后仍8GBdisk，RAM8GB。自己的进程below-normal，不枚举其他PID，不sleep/占用GPU，不改conda或根文件；Python -X utf8 -B，禁止pyc。失败源码/夹具均保留，修复另存版本不覆盖已执行文件。前4759证据和前post五文件接入下一归档。

科学依赖仍是原两臂final真实exit/冻结→原56完整FOV/六能力gates/独立strict实际exit→三臂真实资源→据资源另冻充分适配budget、医学provenance与完整longrunner→合法动作余量/全费用/强静态cost-defer/DC→冻结全部组件后8未见patient确认。当前11/19dev、已见4/9、未见8/12和lockedIXI边界保持；旧weak gain不作正式label。Goal active，publishable claim未成立。

