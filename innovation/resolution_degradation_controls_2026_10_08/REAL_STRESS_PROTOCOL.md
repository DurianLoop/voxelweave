# 228真实开发MRI字段资格（启动前）

270synthetic+17952三候选metadata记录真正7b5ed8 exit0；原3e-6强度/3e-12坐标/二值0门槛保持，源码/thread/fixture修正原样保留。后续metadata证明不替代真实MRI核验。

仅11开发/19series，读取已认证native_reference及observed-only raw-PCHIP，重算原两个stress母patch的三轴候选：19×2输入×2patch×3模式=228字段。primitive固定旧stress scale=.85/1.15→factor=1.1/1.5，强度基本scale/shift、原crop/flip、母GT SHA不改。真实输入cache SHA先匹配旧QPATH/母baseline，19GT只重放母label，不传给resolution API或policy筛选。

全部target生产双通道Torch float64和独立SciPy重算；强度<=3e-6、坐标<=3e-12、支持二值0，支持二值SHA等于原unpadded母域，原padding输入位级保持，inactive另由synthetic验证。数据域仍是既有resampled cache，不是每格点真实采集；不承诺信息无损/病灶受益。

记录缓存加载、两次生产插值、独立全字段重算、有效/继承padding曝光体素和中间数组体积；费用不是完整训练部署费用。GPU/model/forward/训练更新均0，4已见验证及8未见/lockedIXI像素不读。CPU1/低优先级，wall1800s，整个stage5MB/RAMdisk各8,000,000,000bytes。使用现有D:/conda/envs/MRI/python.exe，不安装依赖，不改旧源或根配置。228stress通过之后，全5984实际MRI和完整gamma/bias/noise等仍待下一完整资格，不启动新训练。
