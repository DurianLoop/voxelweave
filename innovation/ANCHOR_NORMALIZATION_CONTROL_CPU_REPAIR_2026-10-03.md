# 归一化预检首失败与追加尝试

session51036实际exit1。三个固定患者的两baseline共6对数组已完成；固定stats下missing/tail逐位一致的断言均通过。最后断言`'torch' not in sys.modules`失败，因为共享`reconstruct()`内部导入包含模型预测器的模块，间接导入torch，即使当前分支只做解析PCHIP。首结果原`torch_imported=false`静态标记不能当实际模块状态证明。

保留原计划、脚本、run_contract和attempt_01，追加独立attempt02脚本与输出目录，不改首文件。修正版保持相同三人、相同归一化类源码、同数组/指标，不改变科学门槛；只修正真实过程标记，读取`torch.cuda.is_initialized()`确认未初始化，禁止已初始化状态。导入库不等于运行GPU，禁止CUDA操作仍有效；本修正不加载模型、没有神经前向。

原计划“不导入MONAI/torch”中的torch部分实际未满足；追加尝试明确允许共享模块的间接torch导入，继续不导入完整MONAI环境、不加载checkpoint、不使用GPU。所有数字仍是预处理技术预检，不是Dice验证或科学独立确认。
