# 007/009/010七系列来源及标签资格执行合同

本合同在本批任何新MR传输/头读取/label解码之前保存。依据[已冻结来源准备](experiments/mc_rc_visible_joint_development_diagnostic/next_developer_source_preparation.json)，固定007/009/010所有7条有真实官方标签的T2系列、API527对象。包含007 MPR cor，不按描述预删；来源资格透明拒绝/pending，不按病灶大小或效果筛选。三人全部时间点归开发，不是未见确认。原五人可见政策失败保持，不恢复其固定回归或原收益头。

## 传输与原生头

公开TCIA getImage精确SeriesUID，顺序单连接，每系列1次、无自动重试；单请求socket timeout30s，整体deadline180s。单系列cap=max(5MB,ceil(1.15×API FileSize)+1MB)，七条总实际传输含错误响应上限350,000,000bytes。预算超/网络错保留partial/错误/固定名单，不把成功子集当全部来源。API FileSize合计261,941,288不是实际ZIP传输。

只用已保存官方getImage endpoint；复用旧download/inspect函数，所有目录/总预算/geometry只在本进程配置，旧冻结源码不改。成功ZIP逐头stop_before_pixels=True，不请求pixel_array；核患者/Study/Series/SOP/modality、唯一对象和API计数、FrameUID、经典单帧Rows/Columns/PixelSpacing/IOP/IPP/名义SliceThickness及MRAcquisitionType。全IPP中心线性拟合，spacing非退化且偏差/affine residual≤.02mm、IOP正交及一致性沿用原阈值。需统一ORIGINAL无DERIVED、无MPR/Reformat/localizer证据、全部3D、spacing及名义SliceThickness≤1.5mm；缺字段pending，派生透明拒绝，不制造field或注册修复。spacing不是PSF。

逐请求保存原始ZIP或partial/错误响应、时间、URL/status、bytes/hash、每头记录与汇总hash；固定527头可能因源API/传输失败无法全核，不能静默调整。

## 原标签与grid

只使用此前认证的官方2023 label ZIP及CSV/artifact一致性proof，按精确SeriesUID/PatientID/StudyUID/API对象数和SegmentationPath联结，提取七个确实存在的成员；新网络标签下载为0。ZIP成员单≤50MB、合计≤150MB，CRC读取认证并保存payload/hash。

label需3D、有限、值∈{0,1}，q/sform有效且角点差≤.05mm，原生grid仅整数signed-axis置换/翻转，角点世界误差≤.05mm；不允许任意插值/注册修复。名义全数组单≤400MB、七条合计≤2GB；scaled代理按max(itemsize,8)估算，全部解码前核预算，不因结果改预算。实际读取≤32MB slab，累计值域/foreground/finite/bytes，空label可记录但不改source资格。派生头不合格也检查对应label以透明记录。

失败不改原阈值/来源分母；另保存提取完整性、label检查完整性、头资格、grid资格、原生source资格，不能把其中任一等同模型性能。若某头没有affine则grid pending，不生成假affine。

## 独立验证与资源

从原ZIP重新读全部原头、以全矩阵lstsq代替中心公式重建IPP affine；独立按原标签反解整数grid/角点/extent，固定4-plane label slab核全部值域与foreground，复核来源联结/hash与原资格。缺字段或几何不能解析时按实际记录核拒绝/pending，不删这些条目。独立实现不得只比较布尔值/JSON。最多一个CPU数组worker；资源gate保持可用RAM≥8GB、磁盘≥15GB，自身低优先级、单线程、隐藏CUDA。MR数组、重建/任务网络、病灶性能统计本批均不执行。

本批结果只是开发来源资格。未来新的病灶可见表征/更多开发MR解码/任务运行需要另合同，原五患者oracle/可见失败均保留，确认仍0。原session83910持续、不重启/终止、不动态效果评分；研究goal active，直到实际可发表且独立验证claim。
