# 原生页面作者指南

先读 [contract](contract.md)，再按 [composition](composition.md) 组织页面。所有例子都是写法提示，页面结构按内容决定。

## 最小页面

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>手册</title></head>
<body>
<section class="page" data-page-id="p-intro">
  <div class="intro-area">
    <h1 data-role="display" data-source-id="intro-title">读懂这趟旅程</h1>
    <p data-source-id="intro-body">这里放原文。</p>
  </div>
</section>
</body>
</html>
```

CSS 放在 `project.json.styles` 列出的文件中，字体只在 project.json 声明；不要在作者 HTML 写 `<style>`、样式表 link 或脚本。普通内联 style 可用，重复构图优先写 book.css。

每个 `.page` 是 body 的直接子元素，一页一张物理页；页面 ID 不随重排变化。打印尺寸和边界变量来自 project.json，禁止作者重复 `@page` 或 `@font-face`。`.page` 必须保持成品+出血的媒体尺寸，具体变量见契约和生成的打印 CSS。

## 内容与原生 CSS

文字承载元素写稳定 `data-source-id`，不在内部嵌套另一个内容节点；强调、链接、换行等按契约白名单。图片写 `data-edit-id` 和 `data-asset`。角色 `body/key/aux/display/deco` 决定物理可读性检查，不能把正文标装饰逃避检查。

```css
.intro-area {
  position: absolute;
  inset: 24mm 20mm;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 8mm;
  align-content: start;
}
.intro-area h1 { grid-column: 1 / -1; }
```

尺寸是可审阅的作者决定，不被引擎吸附到固定栏/行。连续正文注意阅读行长与换行；标签/数值/时间地点保持成组。页面专属类可以直接写，不必新增 Python 布局函数。

## 溢出、叠放与多语言

先调整分组、栏宽、构图或分页，避免牺牲正文可读性。不要用 `overflow:hidden` 掩盖漏文。局部合法叠放用 `data-overlap` 解释，图片出血用 `data-bleed`，两者不构成整页豁免。复杂变换/图片背景对比度无法自动证明时保留 unverified 并实际审稿；硬项未验证仍阻止正式导出。

默认语言写 HTML，其他语言格式为 `{"contract":1,"lang":"en","strings":{"intro-title":"…","intro-body":"…"}}`，放 `copy/en.json`。语言 CSS 在 `lang/en.css`，无需手动加入 styles。缺译和多余译文都会报错。长文见 [blocks](blocks.md)。

可读真实源文件位于 `dev/samples/native/product-brochure/` 与 `dev/samples/native/nature-camp/`；新项目的统一原子与可选布局见 [Folio CSS](../families/folio/README.md)，实际组合与源码见 [展示页](../dev/folio-css/index.html)。不要把例子的页坐标当通用模板。
