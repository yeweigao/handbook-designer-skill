# Folio CSS

新项目使用 [Folio](folio/README.md)：统一排印、颜色、网格、节奏和图像的印刷主题。文字、摄影、行程与图表共用一个系统。

- [正式分发 folio.css](folio/folio.css)：单文件复制到项目，无运行时构建依赖。
- [配方索引](folio/recipe-index.md)：按任务取原子、布局与组件组合。
- [主题与补丁](../references/style.md)：`book.css` 默认可空，必要扩展的边界。
- [Campus 历史方案](campus/README.md)：仅供已有项目复现。

```sh
python3 hb/core/family.py init folio /tmp/my-book --title '我的手册'
```

项目创建时冻结 CSS 版本与哈希；后续更新 Skill 不会静默改变项目。家族元数据的 `css` 指定分发文件；旧家族缺此字段时使用 `design.css`。内容追溯和印刷要求仍使用项目的 `data-*` 契约。
