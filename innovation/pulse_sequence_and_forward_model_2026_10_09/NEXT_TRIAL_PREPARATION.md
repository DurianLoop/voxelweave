# 下一阶段可执行准备

先poll真实session29823和90446，不用rolling receipt推断终止，不重启现有任务，不迁移CPU训练。GPU授权已延续，但新阶段fresh free仍须>=8192MiB；本批实际1394MiB。没有依赖安装、代理委派或其他PID操作。

1. 四臂训练真正整体exit0/无session_id后，保存实际terminal并标29823→原capture_training_terminal.py→原evaluate_matched.py→实际评价terminal→capture_evaluation_terminal.py→summarize_matched.py。四last2992、11968journal、每患者272及输入/GT/几何/primitive配对必须全核。原已见4患者/9series、36production+36functional完整FOV，3e-6 probability/3e-12坐标/零二值差及六医学门槛不降，不提前挑已完成分支。

2. 90446从0起跑35904；必须真正成功terminal加observed_unified_exec_session=90446后执行原audit_full_real_terminal.py。旧74234的6216前缀不继承。任何失败原样保存；不能以271stress成功或目前maxima替代full成功。新控制统一gamma v2，原训练legacy四臂只评价其原合同。

3. 新普通六臂准备继承已有固定schedule2992及原两输入母GT、lr/wd1e-4、AdamW重置、last、同输入初始化/预算/常规增强配对：intensity、intensity+resolution、intensity+合法support roundtrip，各native/raw一臂。完整数值通过后还需起跑资源及训练成本准入，不能把full资格写作training-ready。六final仅payload约33.73MB，本批fresh磁盘储备外约27MB且原training最后写入仍需空间，当前不能启动六臂或11fold；不删历史证据腾空间。

4. 对2021先例新增强reliability-map控制：部署只从observed_package、affine与合法预处理构造原始采样可靠性；如发生非整数物理重采样，地图用同几何插值产生soft0–1。先固定语义（实测vs插值的坐标来源）、通道尺度和费用，不用missing GT重建地图。单通道raw与加入地图的任务网需容量和预算控制，地图本身不能作发表新意。先充分常规增强，再判断采集地图是否还有额外作用。

5. 真实厚层forward model另外立合同：measurement y=A_phi x；phi包含已有资料可支持的spacing、thickness、phase、slice profile与noise假设，不把spacing当thickness，也不把某个box当scanner事实。当前point抽层合同不改。若无真实profile校准，预设box/Gaussian范围和profile误设压力，实测支持限制照实报告；正确A、错误A、点anchor、无DC四控制，同损失/预算/输入。DC与raw和任务能力比较须保留范围越界、病灶假阳性/漏检与失败，不只报Ax=y。

6. 真正收益头实验：11开发患者按patient归组，所有series随患者；任务网、定位、QC/error、gain/cost和校准均折内。任何GT见过外折的parent、特征归一化、ROI定位或超参都不合法。固定动作逐一测完整FOV和missing病灶损害差；部署只使用可见输入/合法模型输出，未观测GT只监督和评分。same-information/same-capacity QC与error-cost/defer、same gain head去采集特征、metadata-only、static/random/always-action均必须进入最终比较。

7. 费用从读取/重采样开始，包含地图/定位、配准、QC、每动作与联合动作、下游task、失败fallback；训练、标签/地图/NMR准备及校准成本另报告。报告全patient的accepted/deferred/failed分母。若强普通基线抹去动作余量，保留负结果并改变假设，不能跳过对照。

8. 完成开发能力、控制、成本和冻结分析后才考虑一次8patient确认。当前2篇阅读、8非公式表、1080+384 toy和数值runner都不是确认资格；未见12series/lockedIXI继续关闭。科研goal保持active。
