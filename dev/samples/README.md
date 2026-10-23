# dev/samples — 样册源码（二进制资产不入库）

这个目录保留**可读的源码**：`book.html`、`book.css`、`design.css`、`project.json`、
`brief.md`、`page-plan.md`、`sources/`（原稿与逐张署名）。照片、字体与导出包都不进 git。

理由很直接：仓库是给人读和给 agent 读的，不是素材盘。474MB 的图片与字体会让
`Download ZIP` 和 `clone` 变得没法用，而它们都是可以按记录重新取回的。

## 克隆之后要重建样册

```sh
python3 hb/core/fonts.py install                                # 三个 OFL 字面（Noto Serif SC / Noto Sans SC / Inter）
python3 dev/samples/fetch-assets.py --status                    # 看每册缺什么
python3 dev/samples/fetch-assets.py --all                       # 按 sources/assets.json 取回照片
node hb/core/cli.mjs check dev/samples/native/folio-swiss       # 正常走验收
```

`fetch-assets.py` 只处理 `sources/assets.json` 里记了 Wikimedia Commons 链接的条目；
没有链接的（如 `folio-business`、`product-brochure` 的历史素材）只报告"需自备"，不猜。

## 要看成品，不需要重建

`<册>/preview.html` 是固定构建的阅读预览，当前 Swiss 样册仍引用本册 `assets/`，需先恢复素材与字体。
三本 Folio 样册的 `preview.html` 都保留在仓库；`<册>/out/` 一律不入库。
导出包中的 `*.html` 才是图片、字体全部内联的自包含离线成品，和正式 PDF 一起保存在本地。

## 各册

| 册 | 页数 | 说明 | 照片 |
|---|---|---|---|
| `native/folio-swiss/` | 100 | 当前 Folio CSS 2.2 底座样册，展示页的"翻看完整样刊"指向它 | 7 张，Commons 公有领域 |
| `native/folio-system/` | 16 | Folio 1.1 冻结样册（系统/分析类） | 6 张，Commons 公有领域 |
| `native/folio-business/` | 9 | Folio 1.1 冻结样册（商务/咨询类） | 历史素材，需自备 |
| `native/nature-camp/` | 16 中英 | Campus 1.1 摄影册 | 9 张，Commons 公有领域 |
| `native/product-brochure/` | 12 | Campus 1.0 纯文字册（历史文稿） | 无 |

## 一个诚实的差异

`fetch-assets.py` 取回的是 Commons 上的**原图**；当初入库的可能是裁切或压缩过的版本。
所以恢复后重建，画面构图一致，但逐页栅格的 SHA256 不一定与 `dev/folio-css/verification.md`
里记录的构建完全相同。要逐像素复现，请以各册 `out/` 里的交付包为准。
