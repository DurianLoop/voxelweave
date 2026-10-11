# 当前19开发序列：真实稀疏输入CPU流水线核验

本轮从最新来源修正与独立原头/标签证明构建真实case，不沿用旧15条可见性清单。上一轮角色CSV错误把002第二个FIESTA时点记为源拒绝：UID 1.3.6.1.4.1.14519.5.2.1.213711595575218613093188251544325434833；最新least-squares几何与独立grid证明已通过，旧16 native能力队列也使用它。追加修正角色表，不改患者分配，不覆盖旧结果或旧科学反例。

预定19序列：旧8人当前16条合格开发序列 + 011/012/013各1条源合格系列。对应11名开发训练候选。仅这些MR和标签可解码；4验证/8确认保留人及其他未分配人不打开MR或标签。当前科学split未启用，pipeline核验不是任务模型效果。

固定phase0、stride4，observed index=0,4,...，supported missing为首尾观测之间非anchor层；末尾无右端点区域复制末个anchor并单列tail，不称重建。原生全FOV，MR按SOP/PatientID/StudyUID/SeriesUID/IPP排序与来源SHA验证，逐个打开observed DICOM member，不解码其他MR层。

实现分离ObservedMRI与SupervisedLabel：重建/归一化接口只收observed pixels、观测索引及几何，完整label不能提供ROI/crop/统计；native完整MR参照不在稀疏接口中。raw linear与既有four-neighbor raw PCHIP都由同一observed数据生成；mean/std仅observed，全体素包括background；full自有统计作为另一明确输入条件。标签另读并按已验证整数轴变换映射，不参与重建。RAS重定向对MR/label/支持域使用同一signed permutation，无插值。

真实数据CPU核验：保存observed-only包（累计压缩上限500MB，单case名义MR重建上限256MB），不保存全native MR。独立脚本从原始MR ZIP重新只解码observed层，逐字节核包与既有旧16 observed hash，用独立Hermite+harmonic-slope公式重算PCHIP、逐轴roll/transpose重定位标签世界坐标，手工统计复核mean/std，检查全部anchors/tail/support。用改变隐藏位置的非有限/巨大数值反事实检验稀疏接口；标签任意变更不能影响输入。只读developer完整标签，不计算Dice/MSE/方法效果，不运行网络。

所有数值任务自身CPU单线程低优先级，GPU不可见且不导入torch，不碰用户训练，磁盘15GB/可用内存8GB底线。首次工具错误停止、记录原attempt；不按资格或模型效果换系列。方法与科学确认仍未完成。
