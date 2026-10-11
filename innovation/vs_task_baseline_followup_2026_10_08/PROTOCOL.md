# 直接VS/T2任务强基线补查，turn21

上一轮为progress：QCResUNet和Jungo2020原文、四作者文件静态核读、两项非医学CPU探索及84新证据归档实际完成，累计6060。原session29823本轮1fc347再次实际poll，仍live，无新输出不是terminal；禁止重启、迁移、改源。GPU授权有效，本轮0a9aac totalsfree1394MiB，未满足原8192MiB启动门槛。

旧nnU-Net/Revisited、3DU-Net/DeepMedic、Dice区域偏置、Unified Focal、MS非对称loss、608draw深监督以及TIN/KIN/InstanceNorm/上下文审计均已有材料，不能再包装成新检查。当前目标是直接VS/T2强任务baseline的尚未覆盖条件，不凭发表分数认定本项目达到能力。

定向筛查两条固定Europe PMC TITLE_ABS query，各最多8记录，日期<=2026-10-08；记录原始响应、总命中、返回条数、题名/摘要与查重。优先仅原始研究（不是review）且直接MRI VS segmentation，在公开XML/HTML可取得时按身份/方法/患者划分/模态/训练/全病例指标/费用完整核读。已有ciss_vs_2026、crossMoDA2022/2023、COBRAI、VS-SEG等按原记录去重，不把标题/摘要当读过全文。

仅公开HTTPS GET，沿用30秒/2MB/最多3跳/TLS验证/无自动retry；不绕登录或下载模型权重。CPU1/below-normal，磁盘/RAM各8GB储备，新stage<=5MB，不安装、不委派、不枚举/操作其他PID。新文件仅本目录；原训练stage45MB、wall27000秒等合同不变。

新医学实验必须有独立前置协议并限定合法开发病例；当前不加载MRI/GT/model数组，不运行作者模型、不评分中间state，不打开四验证或8确认/lockedIXI。原四分支真正terminal及11968日志/四state核验后，才运行既定36FOV评价。若能力未达，先补强普通基线，再探索实际动作收益。最终发表claim条件保持，不降低原六医学门槛或患者分母。
