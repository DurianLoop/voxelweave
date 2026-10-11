# 本轮IDE与用户环境可见上下文

第一条IDE上下文：Active file .gitignore；Open tabs .gitignore、environment.yml。用户要求批量读论文、按既有MRI工作找创新，能验证就探索，不能验证记录准备，所有本轮内容放D:\MRI\innovation。

后续IDE上下文：Open tabs .gitignore；用户更新“可以用gpu”。该授权持续有效，不重复请求许可。

用户提供的环境块：

```xml
<environment_context>
  <cwd>D:\MRI</cwd>
  <shell>powershell</shell>
  <current_date>2026-10-09</current_date>
  <timezone>Asia/Shanghai</timezone>
  <filesystem><workspace_roots><root>D:\MRI</root></workspace_roots><permission_profile type="managed"><file_system type="restricted"><entry access="read"><special>:root</special></entry><entry access="write"><path>D:\MRI</path></entry><entry access="write"><special>:slash_tmp</special></entry><entry access="write"><special>:tmpdir</special></entry><entry access="read"><path>D:\MRI\.git</path></entry><entry access="read"><path>D:\MRI\.agents</path></entry><entry access="read"><path>D:\MRI\.codex</path></entry><entry access="read"><path>D:\MRI\.aws</path></entry></file_system></permission_profile></filesystem>
  <subagents>
    <agent name="/root/diffusion_prior_art" />
    <agent name="/root/prior_art_interpolation" />
    <agent name="/root/project_evidence" />
  </subagents>
</environment_context>
```
