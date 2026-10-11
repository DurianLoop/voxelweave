# GIN19真实资格 v2：完整scope的无损metadata序列化

完整继承 GIN19_REAL_EXECUTION_PROTOCOL_V1.md 的38分支/两设备/两步、所有数据/标签/模型/损失/严格数值gate、费用、内存/磁盘/wall和确认集约束。

v1实际7ea18e exit1，在写frozen_config前，indent JSON超过原250000bytes上限；MRI/GT/CPU/GPU updates均0，没有实际医学资格失败。保留v1源码和失败receipt。v2使用compact JSON并立即json.loads与完整结构核同，保持相同预算上限，不删除字段、病例或来源绑定。每个步骤完整54参数NumPy检查及全部54跨设备比较只放journal一次，receipt存摘要与最差3个参数；journal完整record仍包含所有字段和最差位置两侧参数/梯度。此避免重复存储，不减少核验scope或任何失败证据。receipt350000/journal1200000/config250000bytes上限保持，输出新attempt02；v1失败绑定到新版本。
