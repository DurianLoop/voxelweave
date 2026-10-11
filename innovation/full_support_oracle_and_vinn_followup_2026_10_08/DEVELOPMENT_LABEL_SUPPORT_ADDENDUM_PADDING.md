# 运行前补充：缓存边界与无 padding 影像域

本轮实际 metadata 返回 db18a3 表明：19 个开发 series 中有 5 个沿 z 轴补零，unpadded z=42、49、58、62、56，缓存均补到至少 64。旧 full_shape_zrc 来自 padded physical cache。因此旧全体素核验仍然是正确的缓存边界核验，但“真实完整 FOV 支持”措辞过宽；8/38 充分指缓存域，不保证无 padding 影像域充分。原已冻结脚本、协议、结果保持原样，通过此新增文件澄清。

继续原 DEVELOPMENT_LABEL_SUPPORT_PROTOCOL：重放38个目标 patch，只读19开发标签及metadata。先重算crop-only和full-cache支持、匹配已保存二值mask SHA；再增加独立的无padding域支持。source indicator 的全局合法区间为 padding_low 到 padding_low+unpadded_shape−1；GT不参与几何mask。生产Torch和独立SciPy对新增38 fields逐体素核验：最大误差≤3e-6，支持阈值1−1e-9、二值差0；物理坐标误差≤3e-12。

无padding域仅表示原影像经已有physical_mr映射的几何域，仍不表示raw-PCHIP中的每个格点都是真实采集，亦不证明最初native→physical插值信息无损。两输入使用相同geometry，不重复计独立样本；不加载MRI/model、不读取任何验证/确认/lockedIXI像素。

按已认证physical_label全target SHA及38母patch batch SHA复原标签，统计三种支持定义与前景/背景重叠。若mask会丢监督，只是开发期方法选择的证据；不按GT筛掉增强或病例，不缩患者分母，不修改正在运行四臂。CPU1/低优先级、wall300秒、stage5MB、磁盘与RAM各8GB储备，其他PID零干预。

另澄清V2准备记录：prepare_full_support_v2记录了实际原源SHA，但未在生成前assert某个硬编码原源SHA。FLOAT64_ORACLE_V2_PROTOCOL的“固定原源SHA”不得解读为已经做了预先固定值断言；V2实际运行通过旧来源binding和独立oracle核验。此补充不改旧文件。
