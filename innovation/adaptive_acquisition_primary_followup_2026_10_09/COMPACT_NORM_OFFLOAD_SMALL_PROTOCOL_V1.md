# 新模型CPU保存/恢复关系

前置：compact norm数学v2、原小图CPU以及GPU/CPU两步全部完成。新模型和同16³人工协议不变，GPU分支全forward/loss/backward包在独立保存hooks里：pack独立CPU副本，unpack验证原CPU保存值SHA未变，恢复原device/dtype/shape，再验证roundtrip bitwise与SHA相同。CPU reference仍原独立functional图，不应用hooks。

保留所有54参数/162state、三head/三view概率、binary、两步同初始化/同人工input/target、3e-6/binary0；原资源/严格deterministic/无医学读取限制不变。保存gzip journal、真实pack/unpack数、CPU逻辑peak；成功只认证这套小图的新offload关系。
