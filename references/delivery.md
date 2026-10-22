# 环境、构建与交付

## 依赖与实际成本

先检查已有工具再安装缺少的部分，不默认重复装一整套。下表说明**当前实现**，按需路径是能力边界，不表示所有模块已做成可选插件。

| 用途 | 当前所需 |
|---|---|
| 静态契约校验 | Python 标准库；fontTools 用于字体信息检查 |
| HTML/CSS 渲染与测量 | Node（参考环境 22）、hb/package-lock.json 锁定的 Playwright 1.64.1、可用 Chromium |
| 最终 PDF 检查/预览 | Python + pikepdf、Poppler（pdfinfo/pdffonts/pdftotext/pdftoppm）、Pillow |
| 家族字体准备/可编辑 PDF | fontTools、brotli、pikepdf、家族指定源字体；已在项目内的字体无需重下 |
| Office/PDF 原稿提取 | 按输入格式使用现有 markitdown/pandoc/python-docx、python-pptx、Poppler；图像提取模块当前还会加载 numpy/Pillow |

`hb/requirements.lock` 保留既有参考环境精确版本；`requirements.txt` 是历史沿用的宽范围清单，含新链路未使用的组件。**不要因做一份纯文字册就无条件安装清单全部内容。** 按实际命令缺失项准备；新依赖/版本变动记录在交接中。依赖分层与轻量默认路径尚需后续运行时改造，不能在文档里宣称已实现。

```bash
# 仅首次且缺少浏览器环境时使用；会 npm ci 并下载对应 Chromium
bash "$HB/core/setup_env.sh"
```

锁定浏览器用于减少换行、字体与 PDF 的版本漂移。当前运行时默认用 Playwright 配套 Chromium，启动失败给出错误，**不会静默寻找系统 Chrome**。已有浏览器可以通过 `HB_CHROMIUM=/绝对路径/浏览器可执行文件` 显式指定；构建清单记录实际版本和这个选择，构建 ID 随之变化。使用已有版本可避免下载，结果须在该版本下重新检查，不能冒称与参考环境完全一致。精确版本基准测试要用对应环境；一般项目应报告自己实际用的环境。

资源先本地化，render 不联网。Campus 源字体文件名见 family.json（NotoSansSC-VF.ttf、NotoSerifSC-VF.ttf、Inter-VF.ttf），从已有 `HB_FONT_DIR`、用户缓存或开发字体目录查找。分发包不含开发字库时，自行提供已授权文件；`family.py init/fonts` 将所需字库实例化为项目静态文件并复制许可文本。手工项目可用 `font_static.py`，不会构建时后台下载或切换系统字体。

## 生产参数

只改 project.json 的 canvas、binding、first_page；打印 CSS 由渲染器生成。成品框/出血/媒体框/安全区及可读性下限以 [contract](contract.md) 为准。电子版/散页不强制四的倍数，骑马钉与胶装分别检查其页数条件。换小画布必须重新排版并审实际物理字号。

多语言共用作者源、各自渲染与验收。续页造成页数不同，人工复核各语言目录与页内指代；冻结逐页对应不是自动检查承诺。PDF 书签取 `data-outline`，无显式标记时取每页首个 h1/h2，细节以当前契约为准。书签不能代替可点击目录的实际测试。

## 验收与正式输出

`check` = render → measure → postflight → 最终 PDF 栅格 → 原文/素材覆盖。缺依赖按 fail/unverified 报告，任何硬项未通过就阻止正式交付。`verify` 核当前输入、工具与 PDF 哈希，`review` 绑定实际视觉结论。命令见 [SKILL](../SKILL.md)。

正式 `export` 先验技术和视觉记录，在 `out/.staging-<构建ID>/` 实测全部产物，成功才发布 `out/<文件名>/`。每种语言有普通 PDF、`.editable.pdf`、离线 `.html`、`.sheet.png`、`.spreads.png`；另有 source.zip、credits.md、delivery.json（检查与文件哈希）。逐页 PDF 栅格保存在 `.qa/<构建ID>/<语言>/raster/`，需要时一并提供。

- 普通 PDF 复制自已验收最终文件。
- 可编辑 PDF 直接扩充嵌入字库，当前支持 Chromium 导出且使用静态 TrueType 的路径，扩充到 GB2312 常用字、拉丁及本书字符；验证与普通版文字层及逐页栅格一致。**尚未在 Acrobat 等编辑器中实测改字，不承诺任意编辑器或任意新字符可无损编辑。** SVG 栅格化、编辑器能力等须按实际项目说明。
- 离线 HTML 内嵌资源，实测资源就绪、无外部请求及打印与最终 PDF 栅格一致；不缩图，大照片册文件可能很大。
- 源包含全部输入、sources、许可与 REBUILD.md，在新临时目录解包后重建、比较指纹与逐页输出。离线构建拒绝外部请求；系统级关闭网卡未自动测试。
- `export --draft` 只生成带“草稿 DRAFT”水印 PDF，状态清楚，不作为正式版。

浏览器 RGB PDF 不自动满足印厂 PDF/X、CMYK、专色或拼版要求。有具体印厂规格时逐项确认支持与实测，做不到的说明范围。用户编辑见 [Folio](../workflows/edit-online.md)，修改后旧验收失效，必须重建和审稿。
