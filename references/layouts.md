# 原生页面作者指南

先读 [contract](contract.md)，再按 [瑞士主义底座](swiss.md) 与 [composition](composition.md) 组织页面。所有例子都是写法提示，页面结构按内容决定。

## 最小页面

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>手册</title></head>
<body>
<section class="page" data-page-id="p-intro">
  <div class="fl-area fl-l-stack fl-gap-3">
    <h1 class="fl-h1" data-role="display" data-source-id="intro-title">读懂这趟旅程</h1>
    <p class="fl-body fl-measure" data-source-id="intro-body">这里放原文。</p>
  </div>
</section>
</body>
</html>
```

CSS 放在 `project.json.styles` 列出的文件中，字体只在 project.json 声明；不要在作者 HTML 写 `<style>`、样式表 link 或脚本。结构和样式优先用 Folio 类组合；内联与本书 CSS 同样遵循 [主题与补丁](style.md)。

每个 `.page` 是 body 的直接子元素，一页一张物理页；页面 ID 不随重排变化。打印尺寸和边界变量来自 project.json，禁止作者重复 `@page` 或 `@font-face`。`.page` 必须保持成品+出血的媒体尺寸，具体变量见契约和生成的打印 CSS。

## 内容与原生 CSS

文字承载元素写稳定 `data-source-id`，不在内部嵌套另一个内容节点；强调、链接、换行等按契约白名单。图片写 `data-edit-id` 和 `data-asset`。角色 `body/key/aux/display/deco` 决定物理可读性检查，不能把正文标装饰逃避检查。

上面的页面不需要新增 CSS：版心、段落间距、标题和正文直接来自主题。需要双栏时组合 `fl-grid` 与 `fl-span-*`，需要图文关系时从 [正式配方](../families/folio/recipe-index.md) 取布局。只有具体关系确实超出现有组合时才写局部 CSS，记录缺口并沿用主题 token；不为每本书重写 reset、全局标题、正文或卡片样式。

Folio 的安全版心、网格与布局可以组合，也能单独使用。选择顺序是：先定页面任务与阅读起点，再定栏跨度和图文比例，最后加入需要的索引、图注、数据或时间轴组件。`fl-type-bold` / `fl-type-light` 控制排印模式，不改变布局；摄影与纯文字共用这些结构。整页满版背景和出血图置于版心之外，正文与功能信息仍遵守安全边距。

默认依靠对齐、留白和比例分组，需要明确边界时再加线条或色面。不要因为展示配方有页眉线、术语栏、序号或底色，就把这些元素带进每张页面；组件可以拆解，现有网格与排布原子优先；扩展仍需满足补丁边界。

## 溢出、叠放与多语言

先调整分组、栏宽、构图或分页，避免牺牲正文可读性。不要用 `overflow:hidden` 掩盖漏文。局部合法叠放用 `data-overlap` 解释，图片出血用 `data-bleed`，两者不构成整页豁免。复杂变换/图片背景对比度无法自动证明时保留 unverified 并实际审稿；硬项未验证仍阻止正式导出。

默认语言写 HTML，其他语言格式为 `{"contract":1,"lang":"en","strings":{"intro-title":"…","intro-body":"…"}}`，放 `copy/en.json`。语言 CSS 在 `lang/en.css`，无需手动加入 styles。缺译和多余译文都会报错。长文见 [blocks](blocks.md)。

统一原子、布局与功能组件见 [Folio API](../families/folio/README.md) 与 [正式配方](../families/folio/recipe-index.md)。不要把例子的页坐标当通用模板。
