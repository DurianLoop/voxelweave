# 用户提供的上一模型摘要（原样保存）

当前目标仍是：**持续研究、探索和验证，直到形成经验证的可发表 MRI claim；不动用户现有终端训练。** Goal active，尚未达成。上一轮已归档论文阅读；本轮取得并读完 SADFN，尚未归档。

### 约束和实时状态

- 不重启、迁移、停止现有训练或操作其他 PID；不委派代理。
- 用户已授权 GPU，但最近空闲 **1394 MiB**，新增医学 GPU 作业仍需 **8,000,000,000 bytes** 启动储备。
- 新文件只写 `D:\MRI\innovation`；已执行、绑定、冻结文件不改，修复另存版本。
- RAM、磁盘各保留十进制 8 GB，不删历史证据，不改 conda 环境。
- 开发 **11 患者/19 series**；已见验证 **4/9**；未见确认 **8/12**、locked IXI 继续关闭。
- 使用：
  ```powershell
  & 'D:\conda\envs\MRI\python.exe' -X utf8 -B '脚本路径'
  exit $LASTEXITCODE
  ```
- 根 SHA：
  - `.gitignore`：`7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524`
  - `environment.yml`：`dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257`

**接续先 poll session `99542`。** 最近真实 poll `92bb26` 仍 live，无 terminal exit：
```json
{"kind":"raw_pchip","updates":5346,"loss":0.8209606409072876,
 "new_updates":25146,"cumulative_wall_seconds":58058.41503059992}
```
`new_updates` 为 invocation02 新增累计，不是 raw 单臂步数。native 19998 已完成，raw 未 final。两臂各19998、总39996、30h合同不改。

### 上一轮成功归档

目录：`innovation/recurrent_joint_mri_prior_art_2026_10_08`

- MMAR2610.00553v1：文字1–30；XLSTM-HVED2412.07804v3：文字1–5。
- **35完整文字页（含1参考文献页）、23不同视觉页、7同页裁图**。
- CPU 公开表复核发现 XLSTM 三个打印均值与15行等权平均不一致：
  - Ours WT HD95：17.86 vs18.0626667。
  - mmformer ET Dice：52.99 vs53.0606667。
  - Ours ET Dice：53.83 vs53.404。
- v1 `fe7098=1` 保留；v2 `bea7fa=0` 显式记录差异，不称论文均值全正确。
- MMAR split2：15个组合宏平均全部低于普通多通道U-Net；corruption训练使用合成损坏标记辅助监督，测试也模拟损坏。普通实验15组合各选checkpoint，corruption用final。
- 已准备监督、容量、训练曝光、checkpoint选择机会和完整费用的公平对照。
- 候选贡献仍为：**固定 observed CISS 下，充分适配后按病灶任务净收益及完整成本选择合法局部修正**；不是宽泛 attention/联合重建首创，尚无MRI效应证据。
- Archive `ce87a0=0`，前4825 SHA未改，新增117，累计 **4942**。
- Manifest SHA：
  `b6fa940613941ac14ce6786b839a75924538a296a0783d16fbbfea85e1166fdd`
- Proof SHA：
  `fe1003e24bd1685e7e0700e9d177d522c67d92be1fe47dff5aa5cf87b1356088`
- Post `6d6167=0`。
- 下次归档纳入此阶段 manifest/proof 和 post三文件，共五文件。
- 可见用户交接原文、公开对话、最终回复已保存。不要修改成功档案。

### 本轮进行中：SERANet身份补查

目录：
`D:\MRI\innovation\seranet_identity_prior_art_2026_10_08`

目前**没有** PRIMARY_READING、READING_PROVENANCE、RESULT、EXECUTION_LEDGER、归档及post；需要完成。

已有协议、检索/下载/修订/渲染脚本及各attempt。不要修改已执行文件。

真实检索和失败：

1. `query_seranet.py`，`2461dd=1`
   - 三个 curl GET 均 Schannel35/SEC_E_NO_CREDENTIALS；没有HTTP题名结果，不是零命中。
   - `index_attempt01/receipt.json` 保存失败。
2. `query_seranet_python_v2.py`，`b1aa49=1`
   - `requests` 未安装，import失败，未请求、未创建index_attempt02。
   - 不安装环境；保留源。
3. `query_seranet_stdlib_v3.py`，`65cf88=0`
   - 标准库 urllib/ssl 正常证书验证成功。
   - Crossref SERANet题名：真实0。
   - Crossref segmentation-aware MRI reconstruction：模糊总848123，仅返回8。
   - arXiv segmentation-aware MRI措辞：2条。
   - **10题名已筛，只有3条有完整可用摘要**，不是10摘要。
   - `index_attempt03/receipt.json`。
4. `query_identity_followup.py`，`be6a7f=0`
   - Acar重建作者查询、Xu+Oksuz subsampling查询各0。
   - `index_attempt04/receipt.json`。
5. 最终评价 readiness-only，`3042c6=3`：
   ```json
   {"status":"execution_deferred","ready":false,
    "reasons":["Final actual-tool-exit receipt absent",
      "Full training is not a successful terminal result",
      "Both last19998 weights are not frozen",
      "raw_pchip final checkpoint absent"],
    "MR_or_GT_arrays_loaded":0,"CUDA_initialized":false}
   ```
   不重复合成资格，不执行医学评价。

检索得出的重点真实身份：

- **SADFN**：Fan等，*A Segmentation-aware Deep Fusion Network for Compressed Sensing MRI*，`1804.01210v1`。
- Acar/Çukur/Öksüz，*Segmentation-Aware MRI Reconstruction*，2022，DOI `10.1007/978-3-031-17247-2_6`。
- Xu/Öksüz，*Segmentation-aware MRI subsampling for efficient cardiac MRI reconstruction with reinforcement learning*，2024-10，DOI `10.1016/j.imavis.2024.105200`；目前只有题名/作者，未取得原文。

**SERANet仍未取得身份及原文，不把Acar章节自动等同这个缩写。**

### SADFN已经实际读完

`fetch_selected_stdlib.py`，`2a557b=1`：
- 总体失败因为另一本章节没下载。
- **SADFN独立record成功HTTP200**，16页，2,284,719bytes。
- 文件 `primary_attempt01/sadfn.pdf`
- SHA `fc01a83a218d4f699c39a96b94a4080523b5bf548f07207f6b8d8aad580aa903`
- **16页文字全部完整核读**：
  - `e02a2f` 页1–3；
  - `f7b0f0` 页4–6；
  - `265470` 页7–10；
  - `3bcc75` 页11–13；
  - `186f13` 页14–16。
- 页15结论+参考文献混合，页16参考文献。可记16完整页、15非纯参考页、1纯参考页。
- `render_sadfn.py`，`f19019=0`。
- **12不同页实际view_image已完成**：
  `[1,2,6,7,8,9,10,11,12,13,14,15]`
- 未读作者代码，未复现训练。

核读结论：

- MRBrainS **5 scans**，随机4训练/192 slices，1测试/48 slices；只T1。不要把48 slices当48患者，正文没有可核患者ID。
- 输入30% Cartesian k-space；另20% random展示。不是CISS through-plane。
- Pre-RecNet/DC-CNN预训练32000更新、batch4；Pre-SegNet在完整MRI+人工组织标签预训练32000、batch16裁128²；SADFN fine-tune12000、batch4。
- 推理：先Pre-RecNet重建→固定Pre-SegNet提取10层特征→MLFA→另一个fusion reconstruction路径。fine-tune时固定Pre-RecNet/Pre-SegNet，优化fusion和1×1聚合，loss为完整MRI L2。
- WOS控制尽量匹配fusion building block，但没有segmentation训练监督；整个pipeline参数/全部预训练曝光/费用未完整配平。
- Table5用固定预训练Pre-SegNet评估所有重建输入，**没有每种重建结果各自充分适配分割网**。
- 全部组织标签GM/WM/CSF，不是病灶。
- Figure4/6的PSNR/SSIM有图中文字数值；如用精确数值，建议放大核看，尚未正式转录/CPU审计。
- Table4报告runtime：Pre-RecNet .03s、Liu .03s、WOS .07s、SADFN .06s；是否含完整特征路径、warmup/同步/全FOV没说明，不称完整病灶净效用。
- Table5视觉和文本已核，但**CPU算术尚未执行**。主要三组织[DC%,HD,AVD]：
  - Pre-RecNet：`[83.63,1.795,2.874,75.16,1.378,1.813,78.99,1.668,2.386]`
  - WOS：`[83.85,1.782,2.838,75.84,1.357,1.762,79.25,1.661,2.364]`
  - Liu：`[84.08,1.776,2.814,76.30,1.335,1.724,79.37,1.661,2.357]`
  - SADFN：`[85.76,1.690,2.579,81.29,1.143,1.381,80.08,1.649,2.305]`
  - full：`[87.30,1.596,2.328,86.89,.973,1.092,80.76,1.617,2.225]`
  - GBRWT CSF HD **1.647**，优于SADFN1.649，不能称全部端点最优。
- 后续有价值的控制：分别匹配语义监督/预训练、普通static的额外训练和完整特征生成成本；不能靠固定任务网失配制造收益。本文进一步限制“语义指导重建”的首创说法。

### Acar官方章节：只有摘要，PDF尚未取得

- 原Crossref PDF链接缺`.pdf`，`2a557b`返回303循环，原error headers/body保留。
- `read_publisher_metadata.py` 用标准匿名内存CookieJar，`2bdd49=0`，官方chapter HTML HTTP200，308032bytes。
- `extract_publisher_metadata.py`，`10ff71=0`：
  - 保存 `publisher_metadata_attempt01/extracted_metadata.json`。
  - 官方摘要完整读到：分割proxy误差反传产生pseudo-attention；full-sampled逐渐加undersampling稳定训练；OCMR cardiac。
  - **摘要不是全文，不能核患者数、模型名、预算或结果。**
  - 实际citation_pdf_url为 `https://link.springer.com/content/pdf/10.1007/978-3-031-17247-2_6.pdf`
- `fetch_chapter_pdf_v2.py`，`a4c3ba=1`：303最终URL明确cookies_not_supported。
- `fetch_chapter_pdf_cookie_v3.py`，`482eee=1`：正常匿名CookieJar后HTTP200，但返回chapter HTML，**不是PDF**。
  - `chapter_pdf_attempt03/acar_segmentation_aware.pdf` 实际保存原HTML响应，不能交PDFium或称PDF原文！不删改，记录类型失败。
- 全部访问正常TLS、无认证/付费/环境改动；没有自动审批拒绝。
- 可在后续查公开作者仓库（例如OpenAlex/SemanticScholar实际DOI metadata）寻找合法作者稿；不要猜URL或称全文排重完成。

### 最终评价入口已有，不要重复实现

已读真实源码/协议，历史准备“尚未实现”不再代表现状：

- `experiments/evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py`
- `experiments/mc_rc_3d_19series_final_eval_2026_10_07.py`
- `experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py`
- `MC_RC_3D_19SERIES_COMMON_INIT_FINAL_EVALUATION_EXECUTION_PROTOCOL_2026-10-07.md`
- 旧preflight/overlap资格已存在，不重复算新。

必须依次：原两臂final真实exit0/冻结 → 原56完整FOV、两臂全六能力gates及独立strict实际exit → 三臂真实19-series资源 → 另冻充分适配医学预算/runner → 固定合法动作/task model的真实余量与完整成本 → 强静态、等额外曝光、双cost/defer/DC等 → 全组件冻结后8未见患者确认。

### 下一步

1. poll99542并核GPU/RAM/disk；保持原训练。
2. 完成本轮SADFN公开表视觉转录和Decimal CPU核算；不称MRI项目效应。
3. 写 PRIMARY_READING、精确READING_PROVENANCE、额外语义监督/特征费用的后续准备、RESULT、执行/失败账和可见对话。
4. 归档接前 **4942** SHA，纳入上一五文件；排除rolling训练文件。成功后追加post三文件，不改manifest。
5. 本轮公开进度已发4条，需保存：
   - 上一轮实质进展，继续训练/评估准备和SERANet查新。
   - 最终评价入口已实现；TLS失败改正常Python客户端。
   - SADFN取得、4训练/1测试扫描和固定分割网；章节重定向失败。
   - 第一条原文是本次开头，具体逐字可从本轮上下文获取；不要伪造不可见历史。
6. 附带命令问题要保留：`9d2ecd` 的rg扫描临时pip目录权限错误（GPU查询成功），`c03bef` 搜索含大量manifest/cache输出截断，不能称完整核读该输出。

当前阶段有真实新原文和就绪证据，属于progress；0新医学数组/神经/GPU forward、0头拟合、0新医学训练。Goal仍active，不能把论文或软件准备替代可发表MRI效应。
