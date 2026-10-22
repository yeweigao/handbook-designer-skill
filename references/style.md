# CSS 基因、字体与品牌

家族给作品共同语言，作者决定页面构图。当前原生家族为 Campus（学院墨蓝，v1.1）；家族清单以 `python3 hb/core/family.py list` 为准。历史画廊的主题名称不表示当前存在同名可用家族。

## 冻结与分工

- `families/<家族>/design.css` 是创建项目的来源，family.json 提供版本、画布与字体角色。
- 项目 `design.css` 是本项目的权威基因：颜色角色、字体角色、字号/行距阶梯、线条/间距与低层原语。创建时复制并在 project.json 记录 name/version/sha256。
- `book.css` 是本书的整页构图；`lang/<lang>.css` 解决语言长度、断行及局部差异；Folio 规则暂存 edits.css，审阅后可并入本书 CSS。

家族更新不会静默改旧项目。项目改变基因时记原因与影响范围并审全册，主动更新来源记录。整页封面、双栏页或卡片页作为作品示例存在，不变成家族必选类。

## 字体资源

字体角色用实际本地静态文件。每个需要的字重/斜体在 project.json.fonts 声明；可变字体先用 `font_static.py` 或 `family.py fonts` 实例化。字体准备与正式 render 分开，不后台下载、不先用系统字后下轮换样。补新文字后查字形与实际使用字体，必要时显式重建项目字体。

Campus 使用 Noto Serif SC / Noto Sans SC / Inter，源码字体按 family.json.source 的文件名放到 `HB_FONT_DIR` 或已有缓存。项目源包保留实际静态文件与授权文本，不依赖作者机器的缓存。准备细节见 [delivery](delivery.md)。

## 用色与图形

按纸面、正文、标题、强调、辅助与反白角色选组合，不用品牌色绕过对比度。照片处理、字重和行长根据读者任务决定；栏目、序号、主标题不因原稿字号大就混成同一层。

品牌标志完整、正确用色且有权使用。需要延展时，用独立 SVG/CSS 从源形提炼章节锚点或背景，记录与内容的关系；不替代正式 logo，不要求每页都有。示例 [Acme](../brands/acme/README.md) 仅用于展示资源组织。

可读性硬下限只有 [contract](contract.md) 定义；家族可以提高，不能降低。最终逐页判断见 [review](review.md)。
