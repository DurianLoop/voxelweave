# 真实坐标的独立 float64 有限差分

只复用case0/native/step0的CPU图：三视图前向一次完整反向、不更新，重放原GIN payload/母GT/cold-init。使用已冻结 IN 诊断的CPU functional观测实现，不调用GPU，不打开新病例。固定实际传入IN输出的cotangent，把对应卷积权重flat1658引起的输入方向显式写成input channel13的shift；对该IN channel3的 `sum(dn * normalize(z + h*direction))` 用纯NumPy float64正负中心差分，h=[1e-3,1e-4,1e-5]。端点只检查局部IN解析导数，不称full nonlinear loss有限差分或模型质量实验。

三个h事前冻结，分别保存全部正/负目标、数值导数与原解析per-view对照；全部总导数应为负，max总误差<=1e-8（该小型独立导数检查的固定误差标准；既有3e-6/坐标3e-12/二值0和六医学gate不变）。所有失败保留，不改h、不删失败。RAM/disk8GB、CPU1/interop1/below-normal、prep7MB/FOV20MB/other22.8MB/paper6MB剩余预算，wall180秒、receipt60KB；中间数组不落盘。
