# Folio CSS 验证记录

## 2.2.0 · 展示入口与最终样刊收尾（2026-10-23）

- 原网站继续承载完整目录：26 组原子、21 个布局、36 个组件、8 个变奏，共 91 项、353 个公开类。新增 [完整页码索引](specimen-index.md)，由同一目录自动生成。
- 详情真正读取 `specimen-map.js`，显示页码；全景链接从不存在的 `#panorama` 修正为 `#panorama-1`。新增回归逐项核对全部 91 个锚点。
- 网页字体子集复用 `family.find_source` 的源字体缓存查找，不再要求仓库内有 `dev/fonts`，不下载依赖。README 澄清固定预览与自包含离线 HTML 的区别，完整 PDF 由本地 export 生成。
- 第 95 页填图字在 PDF 边缘有照片细线：局部配方遮边，并明确只适用纯色色面。共享 CSS 与运行时未改变。
- 最终构建 `0bdda986d0b9`：100 页，render / measure / postflight / raster / coverage 全 pass，blocking 0。契约 0 错、1 条 `style.custom` 提示；确认 13 个自定义类只承担样刊说明/索引/页脚/示例摆位。
- 视觉复核：整册缩略 + 第 95 页阅读尺度；其余 99 页与已审构建 `7b049e159e72` 的栅格逐页字节一致，继承其既有判断。不是独立评测，也未声称本轮逐字重读全部 100 页。[复核记录](../samples/native/folio-swiss/.qa/0bdda986d0b9/visual-review.md)与[100 页哈希](../samples/native/folio-swiss/.qa/0bdda986d0b9/raster-comparison.json)。
- 浏览器回归：`family-css` 9 + `family-css-extended` 4 + `family-css-swiss` 7 = **20/20 pass**。本轮只读审查另确认 91 项映射一致、无阻塞问题。
- 导出：`out/folio-swiss-v2.2/` 已刷新；正式 PDF 与验收哈希一致，可编辑 PDF 无 Type 3 且字体完整嵌入、离线 HTML 无外部请求，源包在干净目录重建为同构建；三种派生产物均逐页栅格一致，交付文件哈希全部复核。
- 快速自检：`bash dev/tests/selftest.sh --quick` PASS，36 份活跃文档链接、语法与 31 项 Python 测试通过；证据目录 `hb-native-selftest.HdaFiO`。浏览器与样刊另由上述实跑覆盖。
- 实际环境：Node 24.9.0 / Python 3.13.3 / Playwright 1.64.1 / 已安装 Chromium 149.0.7827.55；无新增依赖。

---

## 2.2.0 · Swiss 底座调试轮（2026-10-23）

承接 Swiss 底座融合，本轮把「样册必须真的过契约」跑通：91 个目录项 → 100 页 A4 样刊。

| 项目 | 实际结果 |
|---|---|
| 生成一致性 | `python3 dev/build-folio-css.py --check` pass；`design.css`、`catalog.js`、`api-coverage.json` 与源模块一致。 |
| 契约 | `python3 hb/core/validate.py dev/samples/native/folio-swiss` 通过（0 错 0 警）。 |
| 浏览器回归 | `family-css` 8 + `family-css-extended` 4 + `family-css-swiss` 7 = **19/19 pass**；含展示页筛选、源码、结构视图与 390px 宽度。 |
| 度量回归 | `node --test dev/tests/core/measure.test.mjs` **21/21 pass**；18 个反例（含文字重叠、压图、对比度、出血）仍全部命中。 |
| Python | `python3 -m unittest discover -s dev/tests/core -p 'test_*.py'` **31 项全 pass**（含新增 `test_adherence.py` 13 项）。 |
| 样式一致性 | `validate` 新增 `style.token / style.offladder / style.brand / style.decor / style.custom`；节奏 token 覆写与越阶字号为硬项。样册为 0 错误；模拟漂移册（覆写 4 个节奏 token、52/34px、3 渐变 8 圆角 2 阴影）被判不通过。 |
| 样册技术验收 | 构建 `7b049e159e72`，100 页：render / measure / postflight / raster / coverage 全 pass，硬项 fail 0、blocking 0；11 条提示（悬挂列表伪元素 ×4、旋转内容 ×7）已目检。 |
| 视觉审稿 | 整册缩略、93–100 页逐页阅读尺度（四轮）、13 页其他单页、3 组真实面对页；结论「可交付」（作者自评，不评优秀、不计 S12）。记录见 [样册审稿](../samples/native/folio-swiss/.qa/visual-review.md)。 |
| 流程前置 | `workflows/new.md` 第 4 步写清 design.css / book.css 分工与「非必要不新增」；第 5 步为「三页小样，最多三轮」，结论落 `style-lock.md`。`validate` 新增 `process.style-lock`：≥12 页且无锁定记录时提示。 |
| 字体供给 | `hb/core/fonts.py status / install / install --system`：只下载可再分发的 OFL 字面，校验字形表并写 SHA256SUMS 与许可；Tahoma 等专有字体只报告「需自备」。本机已装 Inter / Noto Sans SC / Noto Serif SC 到 `~/Library/Fonts`。 |
| 导出 | `out/folio-swiss-v2.2/`；正式 PDF 与验收哈希一致、可编辑 PDF 字体完整嵌入且逐页一致、离线 HTML 无外部请求且打印一致、源包干净重建为同构建同栅格。 |

本轮修掉的实际缺陷（都不是放宽检查换来的通过）：

- **契约硬错**：生成器在无图页面写出 `data-overlap=""`，`validate` 直接拒绝。改为只在确有图片时声明。
- **检查器误报**：Chrome 的 Range 矩形是字体内容盒（ascent+descent），紧行距（`leading-tight/display/hero`）时高于 CSS `line-height`，导致 15 处「文字重叠」与 1 处反白色带「1:1 对比度」的假失败。叠放与对比度改用 CSS 行框判断，越界与安全区仍用字形盒；18 个反例不受影响。
- **公开配方缺声明**：`a-scrim`（标签落在未压暗一侧，实测 1.97:1）、`a-page`、`bleed-top/full/outer` 缺少 `data-overlap` / `data-bleed`，照抄即违反契约。已补，并按遮罩方向重排 scrim 标签。
- **角色映射**：生成器把 `.fl-size-aux` 示例标成 body，11px 低于 14px 下限；`annotate()` 补上 `fl-size-aux → aux`。
- **版面**：原子索引续页只剩 2 条（整页 85% 空白）改为均分；短页示例在剩余空间内垂直居中；`a-sizing` 标题改显式断行；`x-edge` 色面页改纵向居中。
- **去掉 Tahoma**：`family.json` 只剩 Noto Serif SC / Noto Sans SC / Inter 三个 OFL 家族；数字与正文同族（Inter），不再有数字专用字重（bold 900 / light 200 跟随字号档位）。`family.py` 的 Tahoma 分支、`fonts.py` 的系统回退、`tahoma-system-font-note.txt` 与全部文档表述一并移除；两份 CSS 测试改为断言 Inter 与阶梯字重。
- **变奏章按主张落版**：先写 [philosophy-variations.md](../samples/native/folio-swiss/philosophy-variations.md)（受控变量 · Controlled Variance），主张只管判断、不定模数。八页的数值只用系统已有的：字号 11–280 字阶（裁字/填图字取 2×280），高度取 28 的倍数（196 / 112 / 84 / 588），间距 0/7/14/28/42/56，内边距走 `fl-p-3` 等原子。中途试过把八页塞进统一的 600px 图版 + 署名带，因压小手势、与页脚说明重复、把 100 页由整页降级成短图版而撤回。
- **变奏 8 页重做**（93–100）：原稿是「小样 + 大留白」的说明卡，同构且分量不足；改为每页一个构图主张——五条通栏字带按比例分配高度、640px 巨字被右侧纸边切断并用纸面板保留完整名称、320px 粗字重填图字、2:3 竖幅原色/乘色并置、银河照片上的乘色块与不透明纸面对照、6 轨 24 单元的程序图形、三条通栏导视牌、两面 196px 色面向左右纸边展开。修掉四个真问题：display 带里的 13px 编号低于下限、纸面说明压白字 2.99:1、multiply 图层把白字一起混掉、站名被 space-between 推到中间。

未覆盖：纸样、其他浏览器、Node 22 / Python 3.10 实跑、Acrobat 内改字、独立人工校准。

---

## 1.1.0 · 16 页编辑样刊与企业册

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
