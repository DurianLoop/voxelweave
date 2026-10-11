# 不配对数学字符：改用独立PDFium提取

本地严格UTF-16提取ce125f / exit1：仅第1页通过，第2页存在illegal UTF-16 surrogate。不能声称原始数学字符全部是合法成对surrogate；attempt04的完整receipt和两页raw JSON保留，严格失败不修写。

attempt05另用PDFium读取同一个实际SHA PDF，保存每页完整text；pypdf原始字符串逐页另存ASCII JSON，确保包括不合法代码单元也完整保留。PDFium文字不冒充原始pypdf的逐字等价修复，不声称UTF-16代码单元恒等。数学公式、路由函数和表格仍以实际PDF页渲染视觉核对，不能仅由坏编码猜符号。该fallback无联网、无再次下载、无PDF重导出、无环境修改。
