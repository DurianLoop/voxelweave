# Design1 代码位置

为保持 Python 模块名、历史命令和 checkpoint 初始化路径稳定，代码不移动到本目录。

| 数据集 | 实际代码包 | 入口 |
|---|---|---|
| fastMRI | `D:\MRI\design\fastmri_brain_pastnet_2p5d` | `python -m fastmri_brain_pastnet_2p5d.run_all` |
| IXI | `D:\MRI\design\ixi_pastnet_2p5d` | `python -m ixi_pastnet_2p5d.run_all` |

PAST-Net v2 若进行根本性重构，应建立新的 `D:\MRI\design\pastnet_v2` 包，不再向旧 `settings.py` 继续追加 G091+。
