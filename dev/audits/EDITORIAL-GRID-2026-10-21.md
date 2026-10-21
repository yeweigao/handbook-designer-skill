# 编辑网格第一轮 · 2026-10-21

## 结论与证据

HTML 路线保留。值得从本地 `ppt-master-themes` 学习的是统一网格上的编辑变奏、图文关系和阅读节奏；它们适合用 CSS Grid、自然文字流和 SVG 内容插图组合实现。SVG 整页输出不是这些设计能力的前提。

比较依据：该库 `framework/EDITORIAL_RHYTHM.md`、`layouts/a4-editorial/workspace/templates/design_spec.layout.a4-editorial.md`，及实际 rhythm、marginalia、typographic、geometry、evidence、多图/跨页样张。参考版本 `2031b27`。当前 handbook 基线 `d816613` 已有六栏网格，问题不是“没有网格”，而是已有组合偏固定、正文/旁注组织不足，部分主题装饰仍针对旧 DOM。

方案采用 Grid / Layout / Theme / Brand / Project 分工：网格提供对齐，布局组织阅读，主题提供排印与视觉语言，品牌保存身份约束，项目决定内容和页序。沿用现有 `style / colors / fonts / brand` API，不另增同义 theme 参数。详细规则唯一入口为 [composition.md](../../references/composition.md)。

## 已落地的范围

- `RHYTHM`：2＋4 导语/论述、跨栏摘句、完整段落的错位续读。
- `MARGINALIA`：4＋2 主文/旁注，一组由两侧较高者决定下一组起点。
- `PLATE`：保全主体的图版与编号解读；实际素材必需，默认保留原色。
- `SEQUENCE`：一张主图与两张补充图，大小和错位表达主次，图注跟图。
- 四者共用 `canon.editorial_grid()` 和原有文字栈/测量门禁；正文不因放不下而偷偷缩小。固定页面超量仍需拆页，尚无自动文章续页。
- editorial / notebook / riso 的细线、标签、旁注等接入现行 `.cn-*` DOM；主题不自建另一套坐标。
- 可见旁注贯通翻译提取/应用、在线编辑和原文核对；页级内部 note 仍为元数据，图片路径与 surface 标识不进入翻译。
- SVG 图版可原样嵌入单文件 HTML；已有 `ai:编号` 成图可以使用，缺图不会退化成随机底纹。

不采用的做法：整页文本转 SVG；为每个主题复制一套布局；强制每三页插一张照片；用随机背景代替内容插图；给所有内容加同等醒目的卡片。普通查阅区允许重复稳定结构。

## 可复核样张

| 证据 | 范围 |
|---|---|
| [同文案前后对照](../gallery/editorial_same_copy.jpg) | 原 ONE/TWO 与 RHYTHM/MARGINALIA；文字字符多重集一致，阅读顺序和强调方式变化。文案为原创演示，不冒充用户真实手册改版 |
| [编辑网格](../gallery/editorial_grid.jpg) | 阅读、旁注、图版和暗色停顿页；来自实际 PDF 栅格 |
| [三主题对照](../archive/retired-styles/editorial_themes.jpg) | 同一内容同一布局换主题；字体自然换行可变，结构关系保持 |
| [模板预览](../previews/book.editorial.zh.preview.jpg) | `book.editorial.zh.yaml` 的八页合成素材回归 |

本地完整样册在忽略目录 `dev/proofs/editorial-v1/`，含 YAML、照片来源清单、页面计划、HTML、八页 A4 PDF 及逐页 PDF 栅格。跟踪入库的预览仅含原创文字、原创叶片 SVG 或合成素材。摄影样册使用 sibling 库已有照片，文件散列与该库来源清单相符；本轮没有重新联网核验许可。

实际 PDF 全八页经过主执行者查看；独立视觉复核覆盖 2–5、7 页及 notebook/riso 样张。旁注归属、叶片三处编号、多图主次、图注归属成立；摄影分别展示环境、远景和水流，没有声称来自同一地点。

## 验证与已知问题

- 新布局浏览器/PDF 回归检查：长旁注配对、固定字体下三主题几何一致、正文 16px、打印保留三张图、缺图及错误数量拒绝、A5/小红书短文布局、超量文字报溢出。
- 内容回归检查：旁注可翻译/可编辑，原文核对能发现旁注缺失和额外内容；页级 note 不变成印刷文案。
- 导出回归检查：SVG 内嵌字节不变并可离线加载，功能图默认不双色调而显式 duo 仍有效，已存在 AI 成图可解析。
- 完整 selftest 已执行，不能宣称全通过。旧 `book.layouts` 英文 STAGGER 第三项多出 21px，已在未经修改的 `d816613` 副本复现。风格矩阵另有对比度、nebula 容量及 `images.py` 读取内联 grid 样式异常，尚未关闭。
- 首次完整测试还暴露本机缺 qrcode 与临时测试探针找不到 Playwright：qrcode 与 PDF 书签所需 pikepdf 装在临时独立依赖目录；selftest 改为与 run.sh 共用 env.sh，避免子进程解析环境不一致。没有修改系统 Python。
- 通用 skill `quick_validate.py` 仍拒绝仓库要求的 `agent_created` 元数据；这是既有管理契约兼容问题，不删字段掩盖。

最终命令结果与本机日志见本节末尾的验收记录。完整回归的失败保留，不通过缩短原有测试文案或放宽检查阈值来制造全绿。

## 下一轮的完成条件

1. 从真实手册选择长中文、双语长文和密集资料页，验证容量、拆页及续读；短篇样册不能替代这项验收。
2. 补照片开场、正文开场或横向标题的变化，解决四种新布局顶部结构相似的问题；同一整册不得连续只用“大标题＋正文”。
3. 摄影采用确有联系的环境/动作/细节组，验证叙事，而不只验证三张图都能排进去。
4. 地图、流程、证据图分别建立内容模型与样张；本轮只提供“外部插图＋解读布局”，未实现这些图的自动生成。
5. 旧模板矩阵问题按原输入修复，保留基线与修后证据；更多主题的当前 DOM 语法需单独视觉评测。

第一轮的完成标准是可复用的四类布局、可看见的对照与真实导出闭环，不代表所有手册的视觉质量已经解决。

## 本地验收记录

- `bash dev/tests/selftest.sh --quick`：PASS，46 个 Python 文件编译，文档链接及元数据检查通过。
- `test_editorial_layout.py`：PASS，包含实际浏览器与 PDF；新增 SVG/保色/AI 素材及错误数量覆盖，图片清单 DPI 与实际跨栏图框一致。
- `test_editorial_content.py`：PASS，包含 extract/apply、在线编辑和原文核对；故意为图片路径/底色提供译文也不改变标识。
- 最终样册单文件 HTML 在断网浏览器中：8 页、4 张图片全部加载、溢出列表为空；图版截图已看。
- `git diff --check`：PASS。
- 完整 `selftest.sh`：FAIL，保留以下范围划分。图片打印、品牌图形、适配、新编辑网格和旁注内容链路均 PASS；brochure/editorial/family-handbook/nophoto/study-trip 模板、swiss/notebook/inkwash/papercut/stijl beat、A5/xhs 构建均 PASS。`book.layouts`、acme 品牌、stijl/geo/editorial/riso/aurora/nebula 的旧模板组合未通过，具体溢出与对比度记录保留。
- 完整矩阵最终日志和基线复现归档到本地 `dev/proofs/verification/`，该目录不随 Skill 分发。

样册文件散列：PDF `89ed3675094ffc717efd25f2a8fc86956332f6367c81ab1305026e861477ce41`；单文件 HTML `053b1f37fc2ef3e983598c1ec0f0eafee540095e9655e35bbe2ffceb7cd54938`。
