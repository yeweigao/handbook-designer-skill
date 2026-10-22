# Folio 数据图表

CSS 负责字体、颜色、间距；`hb/core/charts.py` 负责数值、坐标与 SVG。使用 Python 标准库，生成时和阅读时均不需要安装图表库。独立 SVG 文字保留为 `<text>`。嵌入本项目作者源时使用 `render_figure(spec)`：SVG 只负责图形，所有标签成为同坐标的普通 HTML 文本，可接受现有字体、对比度、碰撞和内容覆盖审计。不要截图后当图片插入。

```sh
python3 hb/core/charts.py input.json -o chart.svg
python3 dev/tests/core/test_charts.py
python3 dev/build-folio-css.py
```

最后一条从 `chart-examples.json` 生成展示中的图形与标签；JSON 是数据源，不手改生成结果。项目内同时保留原始 JSON。导入 API：`render_chart(spec: dict) -> str`（独立SVG）与 `render_figure(spec: dict) -> str`（原生作者源，固定尺寸）。

共同字段：`type`、唯一 `id`、`title`、`width`（默认640，至少600）、`height`（默认340，至少280）、`precision`（0–4）。宽高以 CSS px 计，输出默认14px标签；排版时缩小 SVG 会同时缩小字，必须以最终 PDF 字号检查为准。

| 类型 | 数据字段 | 检查 |
|---|---|---|
| `bar` | `labels`, `values`, 可选 `highlight` 索引 | 等长、有限数、共同零轴、负数向另一侧延伸；最多9条且有足够行高 |
| `line` | `labels`, `series: [{name,values}]`；可选 `range:[min,max]` | 至少2期、最多8期/3条序列；默认含零；显式范围需包含全部值 |
| `stacked` | `labels`, `series`；`percent` 默认true | 非负；比例模式每组必须合计100，不自动归一化；过窄标签报错，改用表格或显式合并分类 |
| `waterfall` | `start`, `start_label`, `changes:[{label,value}]`, `end_label`，可选 `expected_total` | 每项从前一累计值出发，末值自动计算；指定总计不闭合则失败，支持跨零与负终值 |

```json
{
  "type": "waterfall",
  "id": "profit-bridge",
  "title": "利润桥接 / 示例数据",
  "start": 25,
  "start_label": "上年利润",
  "changes": [{"label": "收入贡献", "value": 12}, {"label": "新增成本", "value": -5}],
  "end_label": "本年利润",
  "expected_total": 32
}
```

每张图必须配一个可见的说明：单位、期间、来源、实际/预测/示例状态，以及必要的口径限制。`title` 是可访问名称，不代替可见结论标题。相邻 SVG 使用不同 `id`；展示脚本会为重复卡片预览分配独立标题 ID。

长标签、多条末值相邻或复杂数据分布仍需要人工编排；生成器不自动缩字或旋转标签。请使用全宽图、缩短已定义的标签、拆图或改成数据表，再跑可读性与碰撞检查。企业样册是实际 PDF 回归，不能证明任意输入都美观。

瀑布图的累计计算与连接关系参考官方 [Vega-Lite waterfall example](https://vega.github.io/vega-lite/examples/waterfall_chart.html)；本项目未引入 Vega 依赖。
