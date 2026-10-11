# 已认证开发 batch 的支持范围诊断（运行前）

只读取上一批 real_development_entry receipt 和旧 19series qualification cache_records 的几何元数据，不加载 MRI/GT/model 数组，不重新评分患者。

检查 11 开发患者、19 series、两输入、每 batch 两 patch，共 76 个 plan。两输入的母 grid、crop、flip、pivot、stress primitive 相同，必须逐对产生相同支持 plan。由全物理缓存 shape 与 crop start/flips，将 source 支持范围映回原全 FOV 体素坐标，报告保守包围盒是否可取得。包围盒超界不是最小支持超界证明，另对八个目标角点枚举两级八邻域，若正权重邻居超出真实全 FOV，保存直接证人；没有角点证人不等于全 patch 证明支持充足。

该诊断揭示支持实现资格，不证明原增强医学失败原因，不据 GT/困难例筛选患者，不改变当前四臂。若真实上下文不存在，后续实验必须明确采用 common interior、禁用该增强或保留边界损失风险，不能调用未观测的薄层补造 halo。当前只诊断，无患者剔除。
