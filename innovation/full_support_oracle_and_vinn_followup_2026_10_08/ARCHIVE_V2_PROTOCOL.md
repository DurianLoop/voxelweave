# 原失败公开响应不是JSON，完整保存后归档

归档V1真实d9b932 exit1；6164旧hash核验完成，尚未写APPEND_INDEX/PROOF。错误是早先BioC的lesion_ensemble_bioc.json扩展名虽为.json，正文却是`[Error] : No result can be found` HTML/文本，json parser不能读。其HTTP200不能算有效原文，本轮已从新PMC HTML取得论文；原失败响应和V1脚本完整保留。

V2只允许这个**固定已知路径、固定SHA256 478f38e0765ee9c406831bb2fc27e8019ac5227c20c6b28ca0de582d8449354a**跳过JSON内部binding解析，仍逐bytes哈希纳入evidence list。任何其他JSON解析失败必须仍报错，不放宽全档案完整性。V2来源绑定同时纳入V1和本失败记录，接原6164，rolling训练仍排除。
