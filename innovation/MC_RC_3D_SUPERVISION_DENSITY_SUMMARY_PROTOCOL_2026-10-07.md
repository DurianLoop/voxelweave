# 既有监督证据的密度与体积离散误差汇总

只分析已完成608draw审计JSON，不重新读取MRI/label、不新增神经前向或训练。三尺度patch voxel数为1048576、131072、16384；强制前景patch及整batch占比分开算，不把半batch强制前景当50%前景体素。

对半/quarter尺度记录`coarse_FG * factor^3 / full_patch_FG - 1`，作为相同规则网格上最近邻标签相对细尺度的体积离散误差。只有full_patch_FG>0时该比值有定义；原本空样本保留、标记undefined，不补0。另数uniform crop中fine_GT>0但coarse_GT=0的次数，这与“强制patch/整batch非0”是不同端点。

对19series各32draw给描述性范围、中位数及计数，不估计患者外显著性，不将draw作为独立患者、不推断该量必然造成拟合失败。均值密度监督有体积守恒的数学动机，但尚未实现或训练，不当已验证的改进。科学确认仍0。
