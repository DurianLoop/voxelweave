# 第二批 MC-RC 来源：八系列、六条原生头/标签预检通过

本批 VS-MC-RC-004/005/006 全部八条既定 T2 系列已完成来源读取，701 个 DICOM 对象，实际 ZIP 传输 133,512,951 bytes，低于500MB合同。六个系列、三名患者通过原生头与标签网格预检；两条004派生/MPR系列即使标签grid吻合仍不放行。来源检查不等于新方法独立确认。

依据：[执行前合同](MC_RC_004_006_NATIVE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md)、[下载/头部ledger](literature/source_cache/mc_rc_004_006_native_headers_2026-10-02/attempt_01.json)、[几何v2](experiments/mc_rc_native_header_geometry_v2.py)。全IPP拟合版本在本批读取前固定；原0.02mm几何、0.05mm角点门槛不变，无配准修复。spacing和名义层厚分别记录，未认证PSF/物理分辨率。

## 真实标签资源失败和追加读取

首跑 [标签attempt01](experiments/mc_rc_004_006_native_label_gate/attempt_01.json) 返回exit1/complete=false：八个标签均已按精确UID提取，三个数组读完，五个在解码前被原100MB单标签/300MB合计预算挡住。不能把这些五条说成缺标签、网格失败或性能负例。

NIfTI头查明六个标签为float64、两个uint16；最大名义数组327,680,000 bytes，八份合计1,366,927,360 bytes。当前RAM约99GB，磁盘约18.48GB。[追加合同](MC_RC_004_006_LABEL_RESOURCE_FOLLOWUP_PLAN_2026-10-02.md)明确结果后资源修订：名义单数组400MB、八份总2GB，实际以≤32MB slab逐块读取，只追加五个此前未读数组，重用三个已读结果；不改文件dtype、几何阈值或患者名单。原方案/代码/失败未覆盖。

[追加结果](experiments/mc_rc_004_006_native_label_gate/resource_followup_attempt_01.json)实际complete=true，六系列/三人预检通过。此complete仅表示固定八条处理完成，完整487条标签覆盖仍false；2026新增126T2标签缺失与旧八行legacy UID联结缺口继续保留。

| 患者/系列 | DICOM r,c,z spacing mm | 名义层厚 mm | 标签前景体素 | 最大grid角点误差 mm | 原生头+grid |
| --- | --- | ---: | ---: | ---: | --- |
| 004 SPC COR | 0.3125,0.3125,0.4000 | 1.0 | 355,252 | 0.000146 | 拒绝：派生/MPR |
| 004 MPR cor | 0.291667,0.291667,0.291667 | 0.292 | 20,176 | 0.000414 | 拒绝：MPR |
| 004 t2_spc_tra_iso | 0.546875,0.546875,0.5500 | 0.5500 | 2,959 | 0.004355 | 通过 |
| 005 Ax 3D FIESTA | 0.507819,0.507815,0.4000 | 0.8 | 13,724 | 0.001962 | 通过 |
| 005 3D FIESTA HIGH RESOLUTION | 0.4297,0.4297,0.4000 | 0.8 | 49,735 | 0.002556 | 通过 |
| 006 t2_spc_tra_iso_384 | 0.520833,0.520833,0.5000 | 0.5 | 9,300 | 0.000650 | 通过 |
| 006 t2_spc_rst_tra_p2_iso | 0.3125,0.3125,0.6000 | 0.6000 | 22,452 | 0.000181 | 通过 |
| 006 FIESTA-C | 0.3516,0.3516,0.5000 | 1.0 | 23,703 | 0.001210 | 通过 |

标签体素数是来源诊断，不用于病例选择；跨时间点差不能直接解释成病灶进展。标签grid吻合也不证明与另一模态完全独立的标注协议。

## 独立核验和合并边界

[独立脚本](experiments/verify_mc_rc_004_006_native_label_preflight.py)重新从八MR ZIP读701头、以完整lstsq/首末法核v2 geometry；全部八标签用独立固定四层slab重读，以逆affine整数变换核grid。实际exit0/errors=[]，见 [proof](experiments/mc_rc_004_006_native_label_gate/independent_raw_geometry_grid_verification.json)。六合格系列均MONOCHROME2、显式little-endian、16bit，rescale slope1/intercept0，支持后续CPU解码的技术可行性。

合并首批：17个MR系列、1,174头、14个标签检查，十条头+grid/五名患者（001/002/004/005/006）通过；003继续无标签。这仍是来源/开发材料，不是71名候选已全部合格或五名新方法未见确认。

本批头/标签检查未解码MR像素。后续另按 [开发oracle合同](MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_PLAN_2026-10-02.md)实际解码了004/005/006各一个系列，CPU运行固定HAT；其结果/失败详见 [动作结果](MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_RESULT_2026-10-02.md)，不能把该后续阶段的MR读取隐去。GPU与终端训练未干预，科学确认人数仍0。
