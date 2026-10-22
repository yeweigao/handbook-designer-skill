# Folio CSS 1.1.0 验证记录

2026-10-23。16组布局、24个组件：基础8组 + 行程/经营/分析12组 + 数据图表4组。共40个预览。

| 项目 | 实际结果 |
|---|---|
| CSS与目录生成 | `python3 dev/build-folio-css.py --check` pass；标准库拼接，无新增依赖。 |
| 浏览器回归 | `node --test dev/tests/core/family-css.test.mjs dev/tests/core/family-css-extended.test.mjs` 11/11 pass；新增二维图框、镜像与底部出血、真实400宋体、透明反白。 |
| 图表数值 | `python3 dev/tests/core/test_charts.py` 11/11 pass；正负零轴、百分比闭合、瀑布累计/终点、跨零、非有限值与溢出、转义、HTML标签等价。 |
| 展示实测 | 40张预览无横向内容溢出；全部图片解码成功；1440px及390px正常；图表筛选、详情、原始JSON、结构视图和源码入口可用。图表预览为640px内容另留60px边距，避免裁掉末值。 |
| 编辑样刊 | `66661d362fca`，16页，render/measure/postflight/raster/coverage全pass，硬项fail/unverified=0。 |
| 企业与行程 | `4a143ad5c0c7`，9页，同上全部pass；书页图表标签用普通HTML，接受完整文字审计。 |
| 视觉审稿 | 两册25页及11对内页面对页全部复核；修改页重新看，最后构建与已审栅格逐页字节一致。作者结论可交付，不评优秀、不计S12。 |
| 导出 | 两册正式PDF与验收哈希一致；可编辑PDF字体完整嵌入且逐页一致；离线HTML无外部请求、打印一致；源包干净重建为同构建同栅格。 |
| quick自检 | pass，34份活跃文档链接、15个Python测试及语法检查；证据`hb-native-selftest.ThPVWq`。 |

导出目录：`dev/samples/native/folio-system/out/folio-system-v1.1/` 和 `folio-business/out/folio-business-v1.1/`；不将大体积交付包入库。绑定证据在各册最终 `.qa/<build>/`，入口为 `.qa/visual-review.md`。

实际环境仍为Node24.9.0/Python3.13.3/Playwright1.64.1/显式Chromium149.0.7827.55，复用已有字体和照片。本轮未安装依赖。Node22/Python3.10运行、其他浏览器、纸样与独立用户审美校准仍unverified。

本轮还修复了通用图框position/width覆盖出血槽位、低对比度第三系列文字、连续正文中途换字、目录次序、取景焦点及时间带标签错位。覆盖边界见[coverage.md](coverage.md)，逐页能力映射见[specimen-map.md](specimen-map.md)。

---

以下保留首版历史记录；八页样册不再代表当前展示。

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
