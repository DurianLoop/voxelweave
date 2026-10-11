# 首次静态归档检查：DOI大小写修正

第一次总归档真实完成28个历史stage write/read-only检查，全部通过；第29个（当前5正文/实验阶段的write检查）返回exit1，错误 `Primary DOI identity differs`。原[首总审计](SESSION_ARCHIVE_VERIFICATION_ORDER_RISK_AND_PHASE_2026-10-03.json)保持不覆盖。

实际来源核读：形态学论文XML的DOI为 `10.1162/IMAG.a.997`，已登记DOI为 `10.1162/imag.a.997`。两者是大小写形式差异，原获取脚本已采用casefold身份核对，静态检查器却使用区分大小写字符串比较。修正静态检查为strip/casefold，并在错误文字注明paper key；没有更换论文、患者、标签、数组、结果或合同。

修改前检查器原字节以及首次阶段manifest保存在 `literature/source_cache/order_risk_and_phase_entry_snapshot_2026-10-03/`。首次失败仍有实际stdout/returncode；修正版只继续余下的当前两个stage和全局write/read-only，共6个检查，不重复已通过的28个历史检查或科学实验。

修正版验收保存在[第二次剩余审计](SESSION_ARCHIVE_VERIFICATION_ORDER_RISK_AND_PHASE_2026-10-03_attempt_02.json)。归档成功不意味着科学claim达成。
