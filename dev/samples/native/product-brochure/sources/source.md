HANDBOOK DESIGNER SKILL · A4 EDITORIAL GRID ENGINE

一套六轨网格，

支撑千面出版级手册。

Three-Layer Editorial Architecture — Theme × Layout × Font

抛弃呆板的整页色块与拼贴套路。我们将杂志艺术总监的版面判断力拆解为纯粹的三层正交架构：Theme 管色彩与纸感气质，Layout 用 HTML 6 轨 CSS Grid 管空间秩序与阅读节奏，Font 管共享字重阶梯与按需字体。

4

大核心视觉主题

24

种 A4 社论版式原型

6×32

黄金基线对齐网格

100%

原文与事实门禁核验

CONTENTS & SPECIFICATIONS · 目录与规格

全册阅读路径与引擎基准参数

全书按「三层正交架构 → 6 轨 CSS Grid 版式家族 → 四大主题与共享排印 → 五步闭环门禁」展开，所有章节页码自动采集生成。

Theme × Layout × Font

三层正交解耦

Orthogonal Separation of Atmosphere, Structure, and Typography

从阅读、信息到影像：

三大版式家族全览

Reading Rhythms, Information Structures, and Edge-to-Edge Photography

共享字重阶梯、

按需字体与零幻觉门禁

Shared Weight Ladders, Non-Blocking Fonts, and Automated Gates

794×1123

A4 物理像素画布（1:√2）

16px/28px

默认正文（12pt 小四）与基线行距

3+3 / 4+2

六轨对齐轴上的黄金分栏组合

MANIFESTO · 为什么重构版式层

版式是阅读的呼吸，

不是给每页涂满颜色的填空题。

借鉴经典社论期刊（National Geographic、The Economist、Monocle）的编辑传统，真正高级的画册依靠栏宽比例、发丝横线、留白尺度与图文出血建立秩序。

稳定的是版心边缘、栏间与文字层级；可变的是跨几栏、从哪里开始、何时停顿。黑白缩略图仍能分清主次，才说明结构在工作。

— A4 Editorial Rhythm 设计准则

过去许多自动化排版工具为了掩盖版面结构的单调，习惯在每一页轮换刺眼的大面积彩色底块，或塞入毫无信息意义的巨型装饰数字。结果不仅破坏了长文阅读的宁静感，也让手册沦为廉价的传单。

我们在 HTML 引擎中完整引入 A4 Editorial 的 24 种六轨结构原型：默认保持温润干净的阅读纸面，利用 CSS Grid 原生的轨道跨越（3+3 双栏、4+2 主文与旁注、2+4 导语与年表、2+2+2 组图与瀑布流）让文字自然流动，让摄影延伸至裁切边。

01

CHAPTER ONE · THREE-LAYER ARCHITECTURE

Theme × Layout × Font

三层正交解耦

Orthogonal Separation of Atmosphere, Structure, and Typography

把视觉主题、空间结构与排印字重彻底解耦：修改任意一层配置，其余两层的几何对齐与阅读流向均保持严丝合缝。

LAYER BREAKDOWN · 职责边界与锚定旁注

三层各司其职，互不越界覆盖

每一本手册都由 Theme、Layout、Font 三个正交旋钮共同决定。主文阐述核心机制，右侧 2 轨旁注固定贴合对应段落。

第一层 · Theme（视觉主题与色彩角色）

Theme 只管纸张底色（background）、墨字（body_text）、主色（primary）、强调色（accent）、横线粗细与影像色调处理。当前精选维护 Photo（纪实摄影）、Swiss Minimal（瑞士极简）、Editorial（书卷社论）、Stijl（风格派构成）四大主题。

THEME 边界准则

主题绝不篡改页面的栏宽或制造随机坐标补丁；切换主题时，六轨网格的列宽与对齐轴完全不变。

结构管阅读顺序与视线入口，主题管光影与纸墨质感，排印管字重与呼吸。

Handbook Designer 引擎架构规范

第二层 · Layout（6 轨 HTML CSS Grid 结构）

Layout 拥有 A4 画布的六条垂直对齐轨（每轨 80px、栏间 32px）与 32 条水平基线（行距 28px）。无论是双栏阅读、锚定旁注、开放横线表还是六图瀑布流，均由 CSS Grid 自然撑开行高，拒绝硬编码像素框。

LAYOUT 边界准则

HTML CSS Grid 比静态 SVG 更适合手册排版：中英文长短变化时，同行旁注与主文自动同步推进，绝不错位。

EDITORIAL RHYTHM · 三个尺度的阅读节拍

在整册、单页与组件三个尺度建立呼吸感

好的手册不是把同一种图文框重复十二遍，而是像谱曲一样安排重拍、密集阅读与安静停顿。

在「整册尺度」上，翻页时应当看得见任务的变化：用满版出血摄影或大尺度宣言打开章节，随后进入安静的 3+3 双栏或 4+2 旁注深读页，再以开放式横线表或四步路径承接查阅信息，避免连续多页高密度文字带来的视觉疲劳。

当你把页面缩成黑白缩略图时，依然能一眼看清第一眼入口、主阅读区与停顿点，版式才算真正成立。

Editorial Rhythm 审稿铁律

在「单页尺度」上，固定版心外沿与六轨对齐轴，同时有目的地改变跨栏宽度与起点高度。例如本页采用 2+4 偏置导语起笔，中段以跨栏引语打断阅读速度，下段再转为错位 3+3 双栏收束。

在「组件尺度」上，眉标（Kicker）、发丝横线（Hairline）、悬挂编号、旁注顶线与图注各自保持稳定的视觉语法。重复教会读者每个组件的含义，克制的例外则用来标示真正的重点。

02

CHAPTER TWO · THE A4 EDITORIAL LAYOUT REPERTOIRE

从阅读、信息到影像：

三大版式家族全览

Reading Rhythms, Information Structures, and Edge-to-Edge Photography

全面吸收 ppt-master-themes 的 24 个 A4 社论结构原型，并针对 HTML CSS Grid 流式排版完成原生重构。

LAYOUT FAMILIES · 六轨网格上的多元组合

三大版式家族，覆盖手册全部叙事场景

不再靠更换底色区分页面，而是根据内容本身的信息关系选择最贴切的六轨网格结构。

FAMILY 01 · 深度阅读

01

DUAL 双栏与 SIDEBAR 旁注

3+3 双栏（DUAL）适合连贯论述与并行短文；4+2 主文加侧栏（SIDEBAR）让正文保持顺畅，将方法提示或背景数据收进右侧两轨。

FAMILY 02 · 节奏变奏

02

RHYTHM 节奏与 MARGINALIA

RHYTHM 通过 2+4 起笔与错位双栏制造阅读变速；MARGINALIA 让每条旁注严格锚定在对应段落右侧，段落再长也不会串位。

FAMILY 03 · 文字焦点

03

READING 续读与 TYPOGRAPHIC

READING 采用 2+4 侧栏篇名加四轨长文，支持多页无缝续读；TYPOGRAPHIC 以大尺度短标题配双声部底栏，适合观点转折页。

FAMILY 04 · 信息查阅

04

TABLE 横线表与 STEPS 路径

TABLE 摒弃封闭网格框，仅用轻重横线与列对齐呈现日程与费用；STEPS 以连续竖脊串联四个复合阶段，逻辑一目了然。

FAMILY 05 · 结构对照

05

INDEX 索引与 COMPARISON

INDEX 将出血窄图或章节大字与三行横线导航结合；COMPARISON 采用 3+3 同基线平行对照，让读者沿行比较差异。

FAMILY 06 · 影像叙事

06

MASONRY 瀑布流与 OVERLAY

涵盖满版封面、底部/侧边出血、双页连续全景、六图有界瀑布流（MASONRY）、接触印样（CONTACT）与跨边界标题板（OVERLAY）。

ARCHITECTURAL COMPARISON · 架构演进对照

告别廉价色块堆砌，回归出版级网格秩序

通过 3+3 平行对照，直观对比旧版排版逻辑与全新「Theme × Layout × Font」六轨 CSS Grid 架构的核心差异。

旧版排版模式（已废弃）

新版 A4 Editorial HTML Grid 架构

纸面与色彩

机械轮换整页 A/B 大色块与巨型水印数

每页强制在深色块、浅色块与 480px 装饰大数字之间交替，容易压迫正文并产生浓重的模板廉价感。

纸面与色彩

默认安静纸面 + 轻重横线与克制强调色

阅读页默认保持纯净纸面（暖白或米白），仅用 2px 主线、1px 分隔线与 3px 短强调线建立清晰层级。

定位与流向

绝对定位文字栈 + 顶部/底部硬钉死

页头钉在顶边、正文钉在底边，内容少时中间裂开巨大空洞，内容多时相互挤压报错。

定位与流向

原生 6 轨 CSS Grid 自然流动与同行对齐

依托 .cn-ed-grid 六轨容器从上往下自然排布，4+2 旁注、3+3 对照与多图网格自动等高对齐。

架构耦合度

主题、版式与字体混写，牵一发而动全身

换一个主题往往连带改变盒模型与装饰位置，难以在保持版式不变的前提下自由切换视觉气质。

架构耦合度

Theme × Layout × Font 三层彻底正交

四大主题、24 种六轨版式与两套字重阶梯（Bold / Light）可任意正交组合，几何坐标零漂移。

架构基准对照：基于 dev/tests/ 下的编辑网格回归、共享排印回归与出血摄影像素验证。

03

CHAPTER THREE · TYPOGRAPHY & QUALITY GATES

共享字重阶梯、

按需字体与零幻觉门禁

Shared Weight Ladders, Non-Blocking Fonts, and Automated Gates

四大主题共享 Bold / Light 两套字重阶梯；系统字体秒级先行顶上，后台静默缓存开源字体，配合五道门禁保障交付品质。

WORKFLOW & GATES · 五步工程化流水线

从原始文稿到可印刷 PDF 的闭环路径

沿左侧连续序列脊线依次推进，每一步都有明确的产物文件与自动化门禁脚本把关。

STEP 01

素材盘点与决策锁定（plan.py + lock.py）

自动抽取原稿段落编号（copy_map.md）与图片分辨率分档，在 brief.md 中锁定 style、typography 与 colors，防止中途偏离确认方向。

STEP 02

编辑顾问审稿与逐页方案（page-plan.md）

先规划整册翻页节奏（锚点页、密集阅读页、呼吸转场页），明确每页第一眼入口与六轨跨栏方案，再映射为声明式 book.yaml。

STEP 03

零阻塞字体回退与六轨编译（hb.py + fonts.py）

首次构建直接复用本机系统衬线/无衬线字体秒级渲染，同时后台异步拉起进程静默下载思源宋体/黑体并按书裁切真实静态字重子集。

STEP 04

浏览器网格测量与三重门禁（fill.js + check_copy.py + facts.py）

自动检测文字越界、重叠与字重阶梯合规性；逐句比对原文（MISSING 0 / EXTRA 0），逐项核查每个数字的事实出处。

GET STARTED · 立即体验三层架构

Theme 赋气质，Layout 定骨架，

Font 立层级。

Ready for Print, Standalone HTML, and Online Collaborative Editing

无论你需要制作研学任务册、招生简章、品牌画册还是技术白皮书，只需声明一份简洁的 book.yaml，即可一键导出印刷级 PDF 与单文件画册。

QUICK COMMANDS · 常用命令

三行命令启动构建与主题试排

bash hb/new_project.sh <项目目录> <原文路径>

python3 hb/directions.py <项目目录> 生成三方向对比样张

bash hb/run.sh <项目目录> && bash hb/export.sh <项目目录>

FOUR THEMES · 四大核心主题

同一份六轨版式，四种鲜明出版气质

photo：纪实摄影杂志（柔边纸面过渡 + 宋体标题）

swiss：瑞士极简（中性纸面 + 单强调色 + 200/100 轻盈字重）

editorial：经典书卷社论（暖米白纸面 + 宋体阅读 + 发丝细线）

stijl：风格派构成（classic 三原色 / tone 深浅灰 / beat 节拍列）
