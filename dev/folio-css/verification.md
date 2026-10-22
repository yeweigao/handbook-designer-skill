# Folio CSS 1.0.0 验证记录

2026-10-22。统一的 Folio CSS：文字、信息与摄影共用规则；16 个布局目录项、8 个组件配方。

| 范围 | 结果与证据 |
|---|---|
| 单文件分发 | `python3 dev/build-folio-css.py --check` pass；CSS 与目录生成文件一致；不含外部 import 或字体下载。 |
| 实际组合回归 | `node --test dev/tests/core/family-css.test.mjs` **7/7 pass**：嵌套色面对比、镜像安全区、六轨布局及原子覆盖、真实角色字重、比例/焦点/有界组图、非零出血跨页坐标、展示交互及手机宽度。 |
| 展示页 | file:// 与本机 HTTP 均正常；24 张预览、摄影筛选8项、结构视图、详情、Escape关闭、网格与裁切控件正常；1440px / 390px 没有横向溢出，图片全部加载，无页面JS错误。另实测复制按钮写入的剪贴板内容与配方HTML相同。 |
| 初始化 | `family.py init folio /tmp/folio-css-init-verification` 成功；5个本地字体文件、家族名/版本/CSS哈希与分发文件一致，validate通过。 |
| 快速自检 | `bash dev/tests/selftest.sh --quick` pass；34份活跃文档链接、语法、4个Python契约测试、生成文件检查。日志目录 `hb-native-selftest.1EhV1u`。本轮不声称重跑全部既有core浏览器测试。 |
| 真实样册 | 构建 `bebe29aa0866`，中文8页，render/measure/postflight/raster/coverage全部pass，硬项无fail/unverified。见[逐页审稿](../samples/native/folio-system/.qa/bebe29aa0866/visual-review.md)。 |
| 视觉审稿 | 全部8张最终PDF栅格、3对连续面对页、封面封底已复核；作者结论可交付，不计独立人工校准。 |
| 导出 | 普通PDF哈希一致；可编辑PDF扩充字体后无Type3且逐页栅格一致；离线HTML无外部请求且打印一致；源包在干净目录重建同构建同栅格。产物在样册 `out/folio-css-specimen/`，报告为 `delivery.json`。 |

实际环境：Node 24.9.0、Python 3.13.3、Playwright 1.64.1、显式复用 Chromium 149.0.7827.55，Python依赖复用 `/tmp/hb-editorial-test-deps`。本轮没有安装依赖，也没有联网获取素材。

集成中修复了三个实际问题：布局槽位优先级过高导致原子不能覆盖；figure显式左右侧不能覆盖page推导；有界图片列被内在比例撑宽。以上均有浏览器回归。

纸样、其他浏览器、Node22/Python3.10运行环境与Acrobat内实际改字未实测。这里的单册视觉复核与组件验证不替代S11全量视觉资产审计或S12独立创作评测。
