# Windows HANDLE 本地调用修复

原机制 runner 实际47e55a exit1，在建立 attempt 输出目录和读取数据之前，GetPriorityClass 的默认 ctypes 参数把64位 HANDLE 当成32位整数，触发 OverflowError。保留原脚本和实际返回。已设置的当前进程 priority 不涉及其他 PID。

用单独 wrapper 显式声明 GetCurrentProcess / SetPriorityClass / GetPriorityClass 的 Windows HANDLE / DWORD 类型，运行原 main。所有科学计算、预定1080+384分母、阈值、输出和资源门槛不变。该修复不会产生医学结果；wrapper、协议、原失败和新实际终态须同时归档。
