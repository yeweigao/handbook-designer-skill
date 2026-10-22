# 长文、表格、任务区与跨页

这些是原生 HTML/CSS 的内容组织方法，不是引擎块枚举。作者约定及完整属性表见 [contract](contract.md)。

## 可续排文字

给固定高度容器写同一个 `data-flow`，按 DOM 顺序形成内容流。内容节点保持稳定 ID；标题默认随下文，其他要绑定下一块的内容写 `data-flow-keep="next"`。

```html
<section class="page" data-page-id="p-reading">
  <article class="reading-frame" data-flow="story">
    <h2 data-source-id="story-title" data-flow-keep="next">原文标题</h2>
    <p data-source-id="story-01">原文长段落……</p>
  </article>
</section>
```

```css
.reading-frame { position: absolute; inset: 24mm 22mm; }
```

```bash
node "$HB/core/cli.mjs" paginate "$P" --flow story
# 审 .qa/paginate/book.html.diff 与 report.json，再 check 所有语言
```

工具合并旧片段后重排，按框容量移动/拆分内容；必要时克隆最后一个框所在页作为续页并写回作者源。`data-fragment` 连续编号，生成页带 `data-flow-generated`；不手改这些生成页，需固定页面时去掉生成标记。工具只移动内容，不改字号、行距、间距或删内容。

标题随下文，片段首尾至少两行，图、表和列表整体移动；过高的整体块会报错。表格不拆行，超长表格须作者拆成多个表；没有固定高度的框不能续排。续页会复制页眉等结构，需不同版式时先自行提供多个框。插页使后续跨页错位时只报错，不擅加空白页。

其他语言在渲染快照里合并、注入并重新续排，不写回默认语言作者源。长双语回归是 `dev/fixtures/flow/long-bilingual/`（未分页状态，先复制到临时目录再 paginate）。目录和页内指代必须按各语言实际页数核对。

## 表格与填写区域

用真实 `<table>` 表达标签与数值，长名单按分组及标题组织；不能用缩字号通过溢出。填写区是功能：按书写动作确定空间，行距可从 8mm 试作，画图/对照/选择题用对应形状的区域，并按实际打印尺度复核；引擎不会自动删线或收紧填写区。

## 联合跨页

两张相邻 `.page` 写相同 `data-spread`，依 first_page 核左右位置。图像可分别裁切同一原图，使用相同缩放和连续坐标；声明局部出血，关键文字/人脸避中缝。CSS 的盒子合法无法证明照片主体与图文指代正确，审最终 PDF 面对页。[images](images.md) 说明分辨率与裁切。[delivery](delivery.md) 说明装订。
