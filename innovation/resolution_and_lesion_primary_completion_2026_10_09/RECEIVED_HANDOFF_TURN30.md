## 目标与约束

目标仍 **active**：研究、探索、验证直到获得可发表且独立确认的 claim；不得缩成软件资格通过。

- 所有新增放 `D:\MRI\innovation`；不安装依赖、不委派代理。
- GPU 已授权，但新 GPU 阶段既定起跑储备 **8192 MiB** 不降。最近 GPU 观察仍仅 free1394 MiB。
- 不枚举、终止、重启、迁移或干预用户及其他 PID。原训练冻结 CPU。
- 11 开发患者/19 series；4 已见验证/9 series。
- **8 未见确认患者/12 series、lockedIXI 继续关闭。**
- 六医学门槛、完整患者分母、last checkpoint、概率/强度 `3e-6`、坐标 `3e-12`、二值零差保持。
- 使用 `D:\conda\envs\MRI\python.exe`；此环境无 `requests`，HTTP 改用标准库 urllib。中文输出要 `sys.stdout.reconfigure(encoding='utf-8')`。
- 真实工具含 `session_id` 即 live；空输出不代表停止。

## 必须先真实轮询的两个句柄

### 原四臂训练：session **29823**

最新实际 **673a86** 仍 live：

- native_reference_intensity、native_reference_spatial、raw_pchip_intensity 三臂均完成 **2992**。
- raw_pchip_spatial **110/2992**，median2.15854645秒，累计19395.7758555秒。
- 同批 **19d364** rolling receipt 确认前三臂 complete/2992、第四110。这份 rolling 不能冻结。

真正整个过程 exit0、无 session_id 后：

`capture_training_terminal.py → evaluate_matched.py → capture_evaluation_terminal.py → summarize_matched.py`

先四 last2992/11968日志/每患者272，再36 production+36独立 functional完整FOV。**医学评价优先**。不能提前评价已完成三臂来选择配方。

### 完整 MRI/独立强度资格：session **74234**

最新实际 **fe39d6** 仍 live：

- **4104/35904** fields，wall2160.9098秒。
- pre error `9.5367431640625e-7`
- shared-post `1.9073486328125e-6`
- isolated/full-chain **`2.86102294921875e-6`**，已接近3e-6，尚未超。
- support `7.771561172376096e-16`
- coordinate `1.1368683772161603e-13`
- rolling MRI6/GT3，失败列表空。**仅部分观察，不是全35904通过。**

目录：

`innovation/resolution_degradation_controls_2026_10_08/full_real_pipeline_attempt01`

脚本：

`qualify_full_real_pipeline.py`

范围5984母几何×两输入×三模式=35904，CPU1/低优先级、wall32400秒、日志1.5MB、整个阶段5MB、RAM/disk各8,000,000,000bytes。

真正 exit0 后，保存完整真实工具返回为 `ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json`，加 `observed_unified_exec_session=74234`，再运行已准备 `audit_full_real_terminal.py`。它只是完成日志/来源/分母审计，不重生成fields。

若 exit1，保存真实terminal和 `failed_field`，先诊断，不放宽门槛、不删患者/轴/patch、不直接训练。**不要修改正在运行脚本或其冻结绑定来源。**

## 本 turn 实际完成

工作仍集中于同目录 `resolution_degradation_controls_2026_10_08`。

1. **三篇已知 MRI 论文公开作者稿渠道核查**
   - 初稿 `follow_public_author_routes.py` 因无 requests，在 import/attempt/网络前 **352291 exit1**；保留。
   - V2 urllib：**ccc872 exit1**，Jiang/Hsu exact DOI 200、closed，仅DOI/PubMed位置无pdf；Gou429共享IP免费日额度不足。原响应gzip保存，不重试/key。
   - arXiv三条预定标题查询各200、0命中；session10166 **896872 exit0**、10.6817371秒。
   - 未取得正文，**新增maintext/摘要核读/作者执行均0**。不证明全网无作者稿。
   - Jiang OpenAlex末作者名与旧MED firstName字段有差异，不按名字自动匹配正文。
   - 相关脚本/protocol及两个 attempt 目录已保存。

2. **确认患者分母的纯数学审计**
   - `audit_confirmation_inference_limits.py` **81095b exit0**。
   - n0..12全部91组exact sign，Fraction组合尾概率与SciPy binomtest差0；n1..8另枚举全部二元向量。
   - n8无ties：6/7/8正差 p分别 `.2890625 / .0703125 / .0078125`。
   - all8正差的95%双侧CP获益方向概率下界 `.6305833524`。
   - 使用sign+Bonferroni m7时最小校正p `.0546875`，只限制该方法组合，不能取消强控制或声称其他合法连续/联合分析无效。
   - 12series不是12独立患者；没有开确认GT/像素。
   - `confirmation_inference_limits_attempt01/receipt.json` 保存。

3. **实际存储预检及透明压缩**
   - 完成臂每last约 **5,622,337bytes**。
   - 六同架构last权重33,734,022，atomic临时5,622,337，六日志按最大完成history估10,805,280。
   - 严格LOPO两输入22个task last仅权重 **123,691,414bytes**，未含QC/收益模型/标签生成。
   - 当时扣8GB储备只有约17MB。
   - `fsutil fsinfo volumeinfo D:` **d0189b Access denied**，是命令自身权限错误，**非自动审批拒绝**。
   - 新8192byte probe **9bbd20 exit0**：原逻辑字节/SHA相同，GetCompressedFileSizeW8192→4096，compressed属性成立。
   - `compress_completed_text_evidence.py` **4e8996 exit0**：
     - 压缩冻结链内29份已完成离线文本，逻辑28,116,603bytes。
     - **原路径、逻辑字节和冻结SHA全部不变**；改变NTFS物理表示/compressed属性。
     - 无MRI/GT/model/live文件处理，无旧内容删除/移动/编辑，无PID操作。
     - API存储口径减少 **15,144,571bytes**。
     - workspace free `8,017,158,144 → 8,032,362,496`，另受同期写入影响。
     - 储备之上约32MB仍不足完整LOPO/六臂全部训练文件，不能据此启动新训练或降低储备。
   - 计划gzip及逐文件receipt在 `completed_text_compression_attempt01`。新stage文件不在压缩目标里。

## 科研判断

“预测相对收益选择有限动作”已经被真正读过的 cost-sensitive/defer/SafeRestore 覆盖，不能仅“收益头”称算法创新。

仍待证伪的 MRI 机制/应用问题：充分任务能力后，合法采集可见性是否能预测具体动作真实病灶损害差及全费用，并超过同信息/容量/监督/预算的强QC/error-cost/defer/static/random/去采集控制。

全11GT训练的19998 parent **不能冒充严格患者折外初始化**。原任务能力、实际动作余量、全费用、严格折外模型及8未见独立确认均尚缺。

## 文件与归档：下一步明确待办

旧主归档已完成 **6376**，不得改写/重跑：

- `APPEND_INDEX.json` SHA  
  `b22589f518e68e358a46bf9bca3893e6fa470b5cca34b0e95152f6c9fa8fd69b`
- `APPEND_PROOF.json` SHA  
  `0e3c52f5381745417e0ecec9c2c2dcc33d4a14a5655ce0504ef7359cf5583777`

**刚创建但尚未执行**：

`archive_continuation_turn29.py`

它接6376，重新核全部旧逻辑SHA（包括透明压缩后的29文件），归档新辅助证据；原训练/完整MRI rolling仍排除，只有frozen_config允许。输出预定：

- `APPEND_CONTINUATION_INDEX_TURN29.json`
- `APPEND_CONTINUATION_PROOF_TURN29.json`

采用opaque旧indices和计数式绑定核验，避免重复大清单。它也纳入turn28后附文件。

本次新报告已创建：

- `RESULTS_CONTINUATION_TURN29.md`
- `VISIBLE_DIALOGUE_TURN29.md`

真实工具记录：

`ACTUAL_TOOL_OBSERVATIONS_TURN29.json.gz`

17个store返回，原111246bytes→32557bytes，SHA：

`4e6a1e510e6ea219898693392cf5df3bc9a785d4a795d8803c5f6c11ce26eab1`

首次把大JSON塞进shell命令因Windows CreateProcess206长度限制，在执行前失败；改apply_patch临时文件→短Python无损gzip，**273470 exit0**，只删除新建临时buffer。**不要再把大正文放shell参数。**

尚未保存本 turn 最终公开回复、最终后附交接及archive之后工具观察。不要覆盖已冻结文件，另后附保存，下一delta纳入。

## 接续顺序

1. **先真实poll74234、29823**；可能有新失败或第四臂进度。
2. Fresh资源与5MB容量检查后执行 `archive_continuation_turn29.py`，观察真实terminal；阶段容量已约3.1MB，须保留full journal到1.5MB、audit150KB、后附100KB，别新增大文件。
3. 保存归档真实返回、最新运行状态、公开对话后附与最终交接。
4. 原训练整个exit0则医学评价优先；完整MRI exit0才其独立audit。
5. 目标保持active，不把辅助数学/存储/数值资格当可发表医学claim。

根hash最近 **19d364** 实核不变：

- `.gitignore` `7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524`
- `environment.yml` `dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257`

functions.store仍可 `load()` 本turn keys，尤其：

`turn29_gate_status_before_records`、`turn29_compress_evidence_start`、`turn29_observations_compressed`、`turn29_three_poll`。
