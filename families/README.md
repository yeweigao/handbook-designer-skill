# Folio CSS

新项目使用 [Folio CSS](folio/README.md)：统一的排印、颜色、网格、节奏和图像原子，配合可选布局与 HTML 组件配方。摄影与纯文字使用同一系统。

- [交互展示：规则 → 布局 → 组件 → 样册](../dev/folio-css/index.html)
- [分发 CSS](folio/design.css)（复制到项目，无运行时依赖）
- [设计决定与边界](../docs/plans/folio-css.md)
- [Campus 历史方案](campus/README.md)（供已有项目复现）

```sh
python3 hb/core/family.py init folio /tmp/my-book --title '我的手册'
```

开发源在 `folio/tokens.css` 与 `core/*.css`。更新后运行：

```sh
python3 dev/build-folio-css.py
python3 dev/build-folio-css.py --check
```

类名表达样式与结构，内容追溯和印刷要求仍使用既有 `data-*` 契约。项目创建时冻结 CSS 版本与哈希，后续更新仓库不会静默改变项目。
