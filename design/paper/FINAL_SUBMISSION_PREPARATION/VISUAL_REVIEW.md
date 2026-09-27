# 最终视觉与内容保留审阅

最终LaTeX状态：主文8页（正文7页、参考文献1页），补充33页；pdflatex/bibtex均成功，无Overfull、undefined reference或LaTeX Error。页面按95dpi渲染，主图另有200dpi预览和嵌入字体的PDF输出。最终渲染目录 `final_page_renders_v4/`；它是本轮实际查看的页面集合，不用旧页数残留代替检查。

## 主文逐页

| 页 | 审阅内容 | 结果 |
|---|---|---|
| 1 | 新题名、四段逻辑摘要、首段贡献 | 题名居中完整；摘要保持边界，未列密集结果清单；匿名模板原状态保留 |
| 2 | 真实图1、物理锚、GT/error/disagreement共享色标 | 全图无裁切，目标和A固定，两行锚身份明确；显示值由数组断言 |
| 3 | Algorithm1、能量分解、Proposition1、有限响应定义 | 公式与文本无溢出；报告卡字段明示NA和条件适用 |
| 4 | acquired-only计算合同、模型/数据、统计单位和回顾性说明 | 权重、合同与数据真实性边界清楚；删去重复wrapper细节以避免结论孤页 |
| 5 | 新图2、表1、influence和support/geometry段 | 图2统一local estimand；表1具有配对O和ΔO区间；8/6镜像警告可见 |
| 6 | 新图3三面板、表2、固定局部模型与失败评分 | 能量变化为signed coupled−independent；HAT/SwinIR全部四幅度可见；caption保留126.4%边界；原始完整scatter另在补充 |
| 7 | 全部40个队列×有向模型对图4、7行报告卡、局限与结论 | 完整矩阵、统一色标、NA字段无填零；报告卡为紧凑7pt表，矢量PDF可放大；结论完整留在正文页内 |
| 8 | 参考文献 | 新增HAT/SwinIR/brain来源引文正常，IXI无虚构出版年份，引用无未定义项 |

主文v4八页PNG与已审阅v3逐字节一致，见 `outputs/main_render_equivalence.json`；主图2/3还分别查看过200dpi独立预览。

## 补充材料完整审阅

查看全部contact sheets，对最后复现页和主报告卡页单独放大核对。内容覆盖：

- 第1–5页：研究史、协议修订、数据/伦理缺口、理论、输入合同、随机定性例和坐标纠正。
- 第6–18页：完整主要观察、两队列所有有向模型对/各端点、influence稳定性、全部Proposition样本、历史模型库与local/ranking的区分、旧ranking和stable-wrong保留。
- 第19–24页：旧影响量、fixed-count膝关节混合结果、当前误差条件分析、全baseline/budget及缺失项NA。小单列表改成兼容双栏浮动后，消除了原单表独占页。
- 第25–27页：支持区域、residue与mirror的全20对表、家族依赖性摘要。负镜像差和零交叉区间完整，fastMRI严格几何NA在方法和完整CSV说明。
- 第28–32页：guard失败、有限响应稳定性失败、外部MRA的方向反例、单位和bright-weighting代价，未按正结果筛选。
- 第33页：精简后的复现/证据地图，详细本地路径转入REPRODUCIBILITY，不再出现末页仅少量路径文字的孤页。

后半部修改前后渲染对应记录在 `outputs/supplement_render_equivalence.json`。主文与补充仍有表格密集页，这是保留完整审计证据的明确取舍，不以删掉负结果换取短页数。

## 机器检查与实际修复

`outputs/historical_retention.json`验证原可达40个表格正文均仍在新可达47个表格中，11个未重绘历史图文件hash保持一致。五张重生成主图/理论图另由数组数值和视觉核验，不强求带PDF创建元数据的二进制hash相同。这个检查验证原表未消失，不把新增表算作独立实验。

初次文件依赖检查漏识别LaTeX的 `graphicspath{figures/}`，因此报找不到framework图；已修正解析路径，再运行通过。此技术错误没有改动图或数字。最终打包也使用修正后的可达文件解析器。

仍需作者完成的内容：CVPR目标年份/author kit、提交ID、真实数据使用和图像许可、NingXia伦理/同意/去标识资料。本轮保留明确待核实措辞；本报告不把视觉合格等同于可立即正式投稿。
