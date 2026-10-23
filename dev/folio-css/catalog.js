// Generated from catalog.json. Plain script also works when opened as a local file.
window.FOLIO_CATALOG = {
  "version": "2.2.0",
  "layouts": [
    {
      "id": "flow",
      "title": "行间与段间",
      "category": "reading",
      "description": "同一组间距控制段落推进与短信息并列，适合开篇、说明和页内元信息。",
      "grammar": "stack 纵向排列；cluster 依内容宽度换行。原子可覆盖 gap，而文字本身自然增高。",
      "classes": [
        "fl-l-stack",
        "fl-l-cluster",
        "fl-gap-2",
        "fl-gap-4"
      ],
      "limits": "cluster 适合短标签与元信息；长正文保留独立阅读路径。它们不限制高度，也不自动截断内容。",
      "html": "<article class=\"fl-l-stack fl-gap-4\">\n  <header class=\"fl-l-stack fl-gap-2\"><p class=\"fl-kicker\">FIELD NOTES / 观察笔记</p><h2 class=\"fl-h2\">先看见，再命名。</h2></header>\n  <p class=\"fl-lead\">同一页中，标题、引言和正文有不同的停顿。</p>\n  <p class=\"fl-body fl-measure\">先写下眼前的形状、颜色和方向。暂时不急着下结论，让一个细节带来下一个问题。</p>\n  <footer class=\"fl-l-cluster fl-key fl-text-muted\"><span>观察</span><span>记录</span><span>回看</span></footer>\n</article>",
      "specimenPage": {
        "id": "flow",
        "label": "行间与段间"
      }
    },
    {
      "id": "split",
      "title": "双栏阅读",
      "category": "reading",
      "description": "把相关但独立的两段阅读放在相同的栏宽里，形成安静、稳定的节拍。",
      "grammar": "六轨各占三轨；列间共享 --fl-gutter；fl-l-full 可穿越两栏。",
      "classes": [
        "fl-l-split",
        "fl-l-full"
      ],
      "limits": "双栏不是自动多栏排文；按 DOM 先左后右阅读。续接长文需人工确定段落分界，不把完整句子切在两栏之间。",
      "html": "<article class=\"fl-l-split\">\n  <h2 class=\"fl-l-full fl-h2\">一处地方，两次观察。</h2>\n  <div class=\"fl-prose fl-body\"><h3 class=\"fl-h3 fl-mb-2\">第一次：看整体</h3><p>从远处确认地形与路径。光线落在哪里，人或植物集中在哪里？先建立一张粗略的空间印象。</p><p>记录最先吸引你的东西，也写下尚未理解的部分。</p></div>\n  <div class=\"fl-prose fl-body\"><h3 class=\"fl-h3 fl-mb-2\">第二次：看细节</h3><p>靠近一个具体对象，观察边缘、纹理与相邻关系。让描述比判断先发生。</p><p>把两次记录并排放在一起，变化本身也可以成为线索。</p></div>\n</article>",
      "specimenPage": {
        "id": "split",
        "label": "双栏阅读"
      }
    },
    {
      "id": "sidebar-offset",
      "title": "主文与侧栏",
      "category": "reading",
      "description": "让正文承担完整论述，短旁注提供词义、来源或另一种观察角度；左右可以交换。",
      "grammar": "sidebar=主文四轨＋旁注两轨；offset=旁注两轨＋主文四轨。两者沿同一六轨线。",
      "classes": [
        "fl-l-sidebar",
        "fl-l-offset",
        "fl-l-main",
        "fl-l-aside",
        "fl-l-full"
      ],
      "limits": "旁注应是短的辅助阅读，不是把装不下的正文塞进窄栏。相同页面内可交换主次位置，但保持明确读序。",
      "html": "<div class=\"fl-l-stack fl-gap-5\">\n  <article class=\"fl-l-sidebar\"><div class=\"fl-l-main fl-prose\"><h3 class=\"fl-h3 fl-mb-2\">主文先说清楚</h3><p class=\"fl-body\">记录一次观察，不只是列出物体的名称。我们也可以描述它与环境的关系：朝向、距离，以及随着时间发生的变化。</p></div><aside class=\"fl-l-aside fl-key fl-text-muted\"><p class=\"fl-kicker fl-mb-2\">旁注</p><p>将一个术语或一个来源放在这里，正文仍能独立读完。</p></aside></article>\n  <article class=\"fl-l-offset\"><aside class=\"fl-l-aside fl-key fl-text-muted\">另一种起笔：先给一个短问题。</aside><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-2\">哪些变化值得回来再看？</h3><p class=\"fl-body\">让问题占据较窄的位置，把展开它的论述留在宽栏中。</p></div></article>\n</div>",
      "specimenPage": {
        "id": "sidebar-offset",
        "label": "主文与侧栏"
      }
    },
    {
      "id": "marginalia",
      "title": "贴近段落的旁注",
      "category": "reading",
      "description": "注释和它解释的段落成对排布，读者不用在整页中寻找关联。",
      "grammar": "每个 fl-l-pair 独立成行；左侧 1 份为短注，右侧 3 份为主文；以首行基线对齐。",
      "classes": [
        "fl-l-marginalia",
        "fl-l-pair",
        "fl-l-main",
        "fl-l-aside"
      ],
      "limits": "1:3 是旁注自身的局部比例，不宣称沿六轨 2+4。每条旁注只对应同一 pair 的正文；长注应移到正文或页末。",
      "html": "<article class=\"fl-l-marginalia\">\n  <section class=\"fl-l-pair\"><aside class=\"fl-l-aside fl-aux fl-text-muted\">01 / 位置<br>先有参照，再谈变化。</aside><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-2\">找到共同的起点</h3><p class=\"fl-body\">每次观察都从同一个位置开始。这样回看记录时，我们更容易判断变化来自对象，还是来自观察角度。</p></div></section>\n  <section class=\"fl-l-pair\"><aside class=\"fl-l-aside fl-aux fl-text-muted\">02 / 时间<br>记下日期与光线。</aside><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-2\">给记录一个时间坐标</h3><p class=\"fl-body\">同一处景物在不同时间有不同面貌。把观察发生的时间放在描述附近，让后来的比较有依据。</p></div></section>\n</article>",
      "specimenPage": {
        "id": "marginalia",
        "label": "贴近段落的旁注"
      }
    },
    {
      "id": "hanging",
      "title": "悬挂编号",
      "category": "information",
      "description": "编号在正文之外建立稳定入口，正文保持完整的左对齐边。",
      "grammar": "max-content 标签＋可伸展正文；首行基线对齐。标签宽度由真实内容决定。",
      "classes": [
        "fl-l-hanging",
        "fl-l-label",
        "fl-l-main"
      ],
      "limits": "标签宜短；长标题放入正文。这里的编号表示顺序，大小和间距不表示数量。",
      "html": "<div class=\"fl-l-stack fl-gap-4\">\n  <section class=\"fl-l-hanging\"><span class=\"fl-l-label fl-number fl-size-h2\">01</span><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-2\">选定一个对象</h3><p class=\"fl-body\">从一片叶、一块石头或一道水流开始，给观察一个清楚的范围。</p></div></section>\n  <section class=\"fl-l-hanging\"><span class=\"fl-l-label fl-number fl-size-h2\">02</span><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-2\">留下可比较的描述</h3><p class=\"fl-body\">写下位置、尺度和可见细节，让下一次观察可以接续这一次。</p></div></section>\n</div>",
      "specimenPage": {
        "id": "hanging",
        "label": "悬挂编号"
      }
    },
    {
      "id": "comparison",
      "title": "同行对照",
      "category": "information",
      "description": "把同一维度的两个观察放在真实的同一行，长内容增高时仍保持对照关系。",
      "grammar": "六轨 3+3；fl-l-pair 横跨全宽，再以 subgrid 继承列轴；每对内容共同决定行高。",
      "classes": [
        "fl-l-comparison",
        "fl-l-pair"
      ],
      "limits": "每一行比较相同问题。未知值明确标示，不为了对称编造信息；这不是面积或长度图表。",
      "html": "<article class=\"fl-l-comparison\">\n  <h3 class=\"fl-h3\">远看</h3><h3 class=\"fl-h3\">近看</h3>\n  <div class=\"fl-l-pair fl-rule fl-pt-2\"><p class=\"fl-body\">确认整体轮廓与环境。</p><p class=\"fl-body\">观察边缘、纹理与细小差异。</p></div>\n  <div class=\"fl-l-pair fl-rule fl-pt-2\"><p class=\"fl-body\">记录对象之间的距离和方向。</p><p class=\"fl-body\">记录同一对象内部的形状与结构。</p></div>\n  <div class=\"fl-l-pair fl-rule fl-pt-2\"><p class=\"fl-body\">适合提出一个范围较大的问题。</p><p class=\"fl-body\">适合为问题寻找一个具体的线索。</p></div>\n</article>",
      "specimenPage": {
        "id": "comparison",
        "label": "同行对照"
      }
    },
    {
      "id": "chronology",
      "title": "时间与事件",
      "category": "information",
      "description": "让短时间标签形成查阅入口，解释内容自然展开，不让段落长短打乱两列关系。",
      "grammar": "每个 fl-l-item 是标签＋正文的一行；统一 --fl-label-width，默认 5.5em。",
      "classes": [
        "fl-l-chronology",
        "fl-l-item",
        "fl-l-label",
        "fl-l-main"
      ],
      "limits": "这是按序排列的文字，不是按比例绘制的时间轴。标签较长时增宽列或改用表格，不缩小正文。",
      "html": "<div class=\"fl-l-chronology\" style=\"--fl-label-width:6em\">\n  <section class=\"fl-l-item\"><p class=\"fl-l-label fl-number fl-size-lead\">抵达时</p><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-1\">建立地点印象</h3><p class=\"fl-body\">记下方位、地形与天气，画一个简单的观察位置图。</p></div></section>\n  <section class=\"fl-l-item\"><p class=\"fl-l-label fl-number fl-size-lead\">观察中</p><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-1\">跟随一个细节</h3><p class=\"fl-body\">记录具体的形状、行为或变化，并区分看到的事实与自己的解释。</p></div></section>\n  <section class=\"fl-l-item\"><p class=\"fl-l-label fl-number fl-size-lead\">离开前</p><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-1\">留下下次的问题</h3><p class=\"fl-body\">回看记录，写下一件仍想确认的事。</p></div></section>\n</div>",
      "specimenPage": {
        "id": "chronology",
        "label": "时间与事件"
      }
    },
    {
      "id": "photo-pair",
      "title": "并置的两张照片",
      "category": "photography",
      "description": "用同等宽度并置两个视角，靠照片内容与图注建立关系。",
      "grammar": "六轨各占三轨；比例由图框原子决定，照片不被拉伸。",
      "classes": [
        "fl-l-photo-pair",
        "fl-frame",
        "fl-ratio-portrait",
        "fl-l-full"
      ],
      "limits": "同宽不等于同地点或同时间。若作事实比较，图注必须交代可比条件。每张图独立选择焦点。",
      "html": "<div class=\"fl-l-photo-pair\">\n  <figure><figure class=\"fl-frame fl-ratio-portrait\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" alt=\"树木与林地\" loading=\"lazy\"></figure><figcaption class=\"fl-caption fl-mt-2\">01 / 林地的层次</figcaption></figure>\n  <figure><figure class=\"fl-frame fl-ratio-portrait\"><img src=\"../samples/native/nature-camp/assets/images/clear-stream.jpg\" alt=\"清澈水流\" loading=\"lazy\"></figure><figcaption class=\"fl-caption fl-mt-2\">02 / 水面与石头</figcaption></figure>\n  <p class=\"fl-l-full fl-key fl-text-muted\">不同地点的素材，用于展示观察尺度；并置不表示同一次活动。</p>\n</div>",
      "specimenPage": {
        "id": "photo-pair",
        "label": "并置的两张照片"
      }
    },
    {
      "id": "photo-essay",
      "title": "主图与两个细节",
      "category": "photography",
      "description": "让一张主图建立场景，再用两张较小的照片补充不同观察尺度。",
      "grammar": "主图占四轨，辅助图组占两轨；两张辅图沿同一列边排列，共享沟槽。",
      "classes": [
        "fl-l-photo-essay",
        "fl-l-main",
        "fl-l-aside",
        "fl-l-full"
      ],
      "limits": "主图必须有叙事任务。辅助图不能只是为了填满空位；比例和焦点需随素材调整。",
      "html": "<div class=\"fl-l-photo-essay\">\n  <figure class=\"fl-l-main fl-frame fl-ratio-portrait\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" alt=\"作为主图的林地场景\" loading=\"lazy\"></figure>\n  <div class=\"fl-l-aside\"><figure class=\"fl-frame fl-ratio-square\"><img src=\"../samples/native/nature-camp/assets/images/autumn-leaves.jpg\" alt=\"叶片细节\" loading=\"lazy\"></figure><figure class=\"fl-frame fl-ratio-square\"><img src=\"../samples/native/nature-camp/assets/images/waterfall-moss.jpg\" alt=\"苔藓与水流\" loading=\"lazy\"></figure></div>\n  <div class=\"fl-l-full\"><h3 class=\"fl-h3 fl-mb-2\">从场景，到纹理。</h3><p class=\"fl-caption\">主图建立环境，两张辅助照片展示形状与质地。本组为不同地点的示例素材。</p></div>\n</div>",
      "specimenPage": {
        "id": "photo-essay",
        "label": "主图与两个细节"
      }
    },
    {
      "id": "contact",
      "title": "六图接触印样",
      "category": "photography",
      "description": "以重复的框和间距方便扫描六个视角，让图像差异成为内容。",
      "grammar": "三列两行；每幅图使用相同比例，图注与图片处于同一个 figure。",
      "classes": [
        "fl-l-contact",
        "fl-frame",
        "fl-ratio-photo",
        "fl-l-full"
      ],
      "limits": "按 DOM 从左到右、从上到下阅读。编号只标识图像；若需要先后顺序，在图注明确，不让版位暗示未证实的时间关系。",
      "html": "<div class=\"fl-l-contact\">\n  <figure><figure class=\"fl-frame fl-ratio-photo\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" alt=\"林地\" loading=\"lazy\"></figure><figcaption class=\"fl-caption fl-mt-1\">01 / 林地</figcaption></figure>\n  <figure><figure class=\"fl-frame fl-ratio-photo\"><img src=\"../samples/native/nature-camp/assets/images/clear-stream.jpg\" alt=\"水流\" loading=\"lazy\"></figure><figcaption class=\"fl-caption fl-mt-1\">02 / 水流</figcaption></figure>\n  <figure><figure class=\"fl-frame fl-ratio-photo\"><img src=\"../samples/native/nature-camp/assets/images/autumn-leaves.jpg\" alt=\"叶片\" loading=\"lazy\"></figure><figcaption class=\"fl-caption fl-mt-1\">03 / 叶片</figcaption></figure>\n  <figure><figure class=\"fl-frame fl-ratio-photo\"><img src=\"../samples/native/nature-camp/assets/images/waterfall-moss.jpg\" alt=\"苔藓\" loading=\"lazy\"></figure><figcaption class=\"fl-caption fl-mt-1\">04 / 苔藓</figcaption></figure>\n  <figure><figure class=\"fl-frame fl-ratio-photo\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" alt=\"海岸\" loading=\"lazy\"></figure><figcaption class=\"fl-caption fl-mt-1\">05 / 海岸</figcaption></figure>\n  <figure><figure class=\"fl-frame fl-ratio-photo\"><img src=\"../samples/native/nature-camp/assets/images/milky-way-arch.jpg\" alt=\"星空\" loading=\"lazy\"></figure><figcaption class=\"fl-caption fl-mt-1\">06 / 星空</figcaption></figure>\n  <p class=\"fl-l-full fl-key fl-text-muted\">六个不同地点的观察主题。图像来源沿用样册素材记录。</p>\n</div>",
      "specimenPage": {
        "id": "contact",
        "label": "六图接触印样"
      }
    },
    {
      "id": "masonry",
      "title": "有边界的组图",
      "category": "photography",
      "description": "固定列边、沟槽和共同底线，按照片内容人工安排高低关系。",
      "grammar": "三列共用 --fl-masonry-height；每列 --fl-masonry-rows 明确两张照片的高度比例。",
      "classes": [
        "fl-l-masonry",
        "fl-l-column",
        "fl-frame",
        "fl-l-full"
      ],
      "limits": "这里不使用自动最短列填充。每列必须有两张图片，图注放在有界图像场之外；仅图框裁切图片，不裁文字。",
      "html": "<div class=\"fl-l-masonry\" style=\"--fl-masonry-height:105mm\">\n  <div class=\"fl-l-column\" style=\"--fl-masonry-rows:minmax(0,1fr) minmax(0,1.35fr)\"><figure class=\"fl-frame\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" alt=\"上部林地\" loading=\"lazy\"></figure><figure class=\"fl-frame\"><img src=\"../samples/native/nature-camp/assets/images/autumn-leaves.jpg\" alt=\"下部叶片\" loading=\"lazy\"></figure></div>\n  <div class=\"fl-l-column\" style=\"--fl-masonry-rows:minmax(0,1.7fr) minmax(0,1fr)\"><figure class=\"fl-frame\"><img src=\"../samples/native/nature-camp/assets/images/waterfall-moss.jpg\" alt=\"上部苔藓水流\" loading=\"lazy\"></figure><figure class=\"fl-frame\"><img src=\"../samples/native/nature-camp/assets/images/clear-stream.jpg\" alt=\"下部清澈溪流\" loading=\"lazy\"></figure></div>\n  <div class=\"fl-l-column\" style=\"--fl-masonry-rows:minmax(0,1fr) minmax(0,1.8fr)\"><figure class=\"fl-frame\"><img src=\"../samples/native/nature-camp/assets/images/milky-way-arch.jpg\" alt=\"上部星空\" loading=\"lazy\"></figure><figure class=\"fl-frame\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" alt=\"下部海岸\" loading=\"lazy\"></figure></div>\n  <div class=\"fl-l-full\"><h3 class=\"fl-h3 fl-mb-2\">共同的边，不同的节拍。</h3><p class=\"fl-caption\">按列从上到下：林地／叶片，水流／溪流，星空／海岸。来自不同地点，示范裁切与图组节奏。</p></div>\n</div>",
      "specimenPage": {
        "id": "masonry",
        "label": "有边界的组图"
      }
    },
    {
      "id": "stagger",
      "title": "错位的图像叙事",
      "category": "photography",
      "description": "让相邻照片从不同高度进入视线，图注给读者一条明确路径。",
      "grammar": "两列；偶数项下移 --fl-stagger-step；每项占据正常文流，不相互遮盖。",
      "classes": [
        "fl-l-stagger",
        "fl-l-item",
        "fl-l-full"
      ],
      "limits": "错位不能代替读序。保持 DOM 顺序、编号与图注一致，勿把不同地点的素材写成真实连续行程。",
      "html": "<div class=\"fl-l-stagger\">\n  <figure class=\"fl-l-item\"><figure class=\"fl-frame fl-ratio-portrait\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" alt=\"林地远景\" loading=\"lazy\"></figure><figcaption class=\"fl-caption fl-mt-2\">01 / 先看环境的层次</figcaption></figure>\n  <figure class=\"fl-l-item\"><figure class=\"fl-frame fl-ratio-portrait\"><img src=\"../samples/native/nature-camp/assets/images/autumn-leaves.jpg\" alt=\"叶片细节\" loading=\"lazy\"></figure><figcaption class=\"fl-caption fl-mt-2\">02 / 再靠近一种纹理</figcaption></figure>\n  <p class=\"fl-l-full fl-body\">这是从整体到局部的阅读顺序。两张素材不代表同一地点。</p>\n</div>",
      "specimenPage": {
        "id": "stagger",
        "label": "错位的图像叙事"
      }
    },
    {
      "id": "edge-photo",
      "title": "照片走到页边",
      "category": "photography",
      "description": "阅读区和照片各有完整空间，让照片触及裁切边形成页面的尺度感。",
      "grammar": "bleed-bottom 用 --fl-image-height 保留下部图像场；bleed-side 用 --fl-image-width 保留右侧图像场。文字使用 fl-area 安全边距。",
      "classes": [
        "fl-l-bleed-bottom",
        "fl-l-bleed-side",
        "fl-l-photo",
        "fl-l-copy",
        "fl-area"
      ],
      "limits": "放在 runtime .page 内。照片和底层容器需要准确 data-bleed；不要把文本放入图框。下方示范 A5 几何，真实成品尺寸由项目控制；切换侧图时将图片出血声明改为 top right bottom。",
      "html": "<section class=\"page\" data-side=\"right\" style=\"--trim-w:148mm;--trim-h:210mm;--bleed:0mm;--media-w:148mm;--media-h:210mm;position:relative;width:var(--media-w);height:var(--media-h)\">\n  <div class=\"fl-l-bleed-bottom\" style=\"--fl-image-height:44%\">\n    <figure class=\"fl-l-photo fl-frame\" data-bleed=\"left right bottom\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" alt=\"林地场景\" data-bleed=\"left right bottom\"></figure>\n    <div class=\"fl-l-copy fl-area fl-l-stack fl-gap-3\"><p class=\"fl-kicker\">FIELD NOTES</p><h2 class=\"fl-h1\">让阅读<br>走向风景。</h2><p class=\"fl-body\">上半页展开一个简短的想法，下半页把它带回具体的环境。文字保有稳定的行长，照片获得完整的宽度。</p></div>\n  </div>\n</section>",
      "previewHeight": 800,
      "specimenPage": {
        "id": "edge-photo",
        "label": "照片走到页边"
      }
    },
    {
      "id": "overlay",
      "title": "图文跨过边界",
      "category": "photography",
      "description": "标题跨越白边与图像边界，让两种材料产生联系，仍保持独立可编辑。",
      "grammar": "六轨中图片占第二至第六轨；标题占第一至第五轨，位于较高层。布局不自动添加遮罩或底色。",
      "classes": [
        "fl-l-overlay",
        "fl-l-photo",
        "fl-l-copy",
        "fl-l-caption"
      ],
      "limits": "对比处理必须针对真实照片；可选表面原子只用于所需文字区域。标题保持简短，不将长段落直接压在复杂图像上。",
      "html": "<article class=\"fl-l-overlay\" style=\"--fl-overlay-min:100mm\">\n  <figure class=\"fl-l-photo fl-frame\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" alt=\"林地照片，作为可独立替换的图层\" loading=\"lazy\"></figure>\n  <div class=\"fl-l-copy\"><h2 class=\"fl-h1 fl-leading-display\"><span class=\"fl-surface-paper fl-px-2\">走近一点，</span><br><span class=\"fl-surface-paper fl-px-2\">再看一次。</span></h2></div>\n  <p class=\"fl-l-caption fl-caption\">照片、文字及局部阅读底各自独立；这里主动使用纸色原子保证字后对比，布局本身不带底框。</p>\n</article>",
      "specimenPage": {
        "id": "overlay",
        "label": "图文跨过边界"
      }
    },
    {
      "id": "panorama",
      "title": "同一场景的面对页",
      "category": "photography",
      "description": "一幅照片跨越真正相邻的左右页，共用裁切坐标，让风景连续经过书脊。",
      "grammar": "完整图像场宽 2×trim-w＋2×bleed；左页位移 0，右页位移 −trim-w。两页同源、同高、同焦点，先共同裁切再分开观察。",
      "classes": [
        "fl-l-panorama",
        "fl-l-panorama-image",
        "fl-area"
      ],
      "limits": "正式书序必须偶数左页＋下一奇数右页；data-side 声明不替代页序验证。两页的 top/height/src/focus 必须一致，关键主体避开中缝。下方是零出血的 A5 并置演示；生产时保留 runtime bleed，检查裁切后拼合，不能直接把含出血的两张页面边缘相接。",
      "html": "<div class=\"fl-flex\" style=\"--trim-w:148mm;--trim-h:210mm;--bleed:0mm;--media-w:148mm;--media-h:210mm;--fl-panorama-top:0mm;--fl-panorama-height:133mm;--fl-focus-x:50%;--fl-focus-y:50%;width:calc(2 * var(--media-w))\">\n  <section class=\"page fl-shrink-0\" data-side=\"left\" data-spread=\"forest\" style=\"position:relative;width:var(--media-w);height:var(--media-h)\">\n    <figure class=\"fl-l-panorama\" data-side=\"left\" data-bleed=\"left right top\"><img class=\"fl-l-panorama-image\" src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" alt=\"同一林地场景的左半页\" data-bleed=\"left right top\"></figure>\n    <div class=\"fl-area\" style=\"top:145mm\"><p class=\"fl-kicker fl-mb-2\">一幅景观 / 左页</p><h2 class=\"fl-h2\">让目光<br>继续向前。</h2></div>\n  </section>\n  <section class=\"page fl-shrink-0\" data-side=\"right\" data-spread=\"forest\" style=\"position:relative;width:var(--media-w);height:var(--media-h)\">\n    <figure class=\"fl-l-panorama\" data-side=\"right\" data-bleed=\"left right top\"><img class=\"fl-l-panorama-image\" src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" alt=\"同一林地场景的右半页\" data-bleed=\"left right top\"></figure>\n    <div class=\"fl-area\" style=\"top:145mm\"><p class=\"fl-body\">两张页面共享同一个图像场。翻开的书页在中间相遇，照片的尺度与位置始终保持一致。</p><p class=\"fl-caption fl-mt-2\">照片：SpessiG，CC0 1.0。</p></div>\n  </section>\n</div>",
      "previewHeight": 800,
      "ratio": "296 / 210",
      "specimenPage": {
        "id": "panorama",
        "label": "同一场景的面对页"
      }
    },
    {
      "id": "typographic",
      "title": "文字的停顿",
      "category": "reading",
      "description": "用短句的尺度、偏置的小声部与留白，让一页成为阅读中的停顿。",
      "grammar": "标题横跨六轨；下部两轨短声部＋四轨主文；纵向停顿使用 space token。字体与字号由原子决定。",
      "classes": [
        "fl-l-typographic",
        "fl-l-title",
        "fl-l-aside",
        "fl-l-main"
      ],
      "limits": "大字只承载短思想，不是长文章容器。中文词组和英文专名保持完整；若标题过长就换尺度或换布局，而非隐藏溢出。",
      "html": "<article class=\"fl-l-typographic\">\n  <h2 class=\"fl-l-title fl-display fl-leading-display fl-balance\">慢一点。<br>看得更多。</h2>\n  <p class=\"fl-l-aside fl-key fl-text-muted\">留白不是<br>尚未填满。</p>\n  <div class=\"fl-l-main fl-prose fl-body\"><p>当一个想法足够重要，可以给它一个更慢的入口。</p><p>让标题先发生，再让较小的声音接住它。共同的对齐关系让页面仍然完整。</p></div>\n</article>",
      "specimenPage": {
        "id": "typographic",
        "label": "文字的停顿"
      }
    },
    {
      "id": "bleed-top",
      "title": "顶部通栏摄影",
      "category": "photography",
      "classes": [
        "fl-l-bleed-top",
        "fl-l-photo",
        "fl-l-copy",
        "fl-area"
      ],
      "description": "摄影与版心共用一张纸。出血抵达纸边，阅读信息仍守安全边界。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "真实输出由project.json提供纸张尺寸；摄影裁切按主体检查，图上文字单独检查对比度。",
      "html": "<section class=\"page fl-relative\" style=\"width:568px;height:760px;--bleed:0px;--fl-margin-top:42px;--fl-margin-bottom:42px;--fl-margin-inner:42px;--fl-margin-outer:42px\"><div class=\"fl-l-bleed-top\"><figure class=\"fl-l-photo fl-frame\" data-bleed=\"all\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\" data-bleed=\"all\"></figure><div class=\"fl-l-copy fl-area\"><p class=\"fl-h1\">沿着光线，<br>理解现场。</p><p class=\"fl-key fl-mt-3\">照片提供事实，文字建立阅读方向。</p></div></div></section>",
      "specimenPage": {
        "id": "bleed-top",
        "label": "顶部通栏摄影"
      }
    },
    {
      "id": "bleed-full",
      "title": "满版摄影",
      "category": "photography",
      "classes": [
        "fl-l-bleed-full",
        "fl-l-photo",
        "fl-l-copy",
        "fl-area"
      ],
      "description": "摄影与版心共用一张纸。出血抵达纸边，阅读信息仍守安全边界。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "真实输出由project.json提供纸张尺寸；摄影裁切按主体检查，图上文字单独检查对比度。",
      "html": "<section class=\"page fl-relative\" style=\"width:568px;height:760px;--bleed:0px;--fl-margin-top:42px;--fl-margin-bottom:42px;--fl-margin-inner:42px;--fl-margin-outer:42px\"><div class=\"fl-l-bleed-full\"><figure class=\"fl-l-photo fl-frame\" data-bleed=\"all\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\" data-bleed=\"all\"></figure><div class=\"fl-l-copy fl-area\"><div class=\"fl-surface-paper fl-p-3\" style=\"max-width:300px\"><p class=\"fl-h1\">沿着光线，<br>理解现场。</p><p class=\"fl-key fl-mt-3\">照片提供事实，文字建立阅读方向。</p></div></div></div></section>",
      "specimenPage": {
        "id": "bleed-full",
        "label": "满版摄影"
      }
    },
    {
      "id": "bleed-outer",
      "title": "外侧出血摄影",
      "category": "photography",
      "classes": [
        "fl-l-bleed-outer",
        "fl-l-photo",
        "fl-l-copy",
        "fl-area"
      ],
      "description": "摄影与版心共用一张纸。出血抵达纸边，阅读信息仍守安全边界。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "真实输出由project.json提供纸张尺寸；摄影裁切按主体检查，图上文字单独检查对比度。",
      "html": "<section class=\"page fl-relative\" style=\"width:568px;height:760px;--bleed:0px;--fl-margin-top:42px;--fl-margin-bottom:42px;--fl-margin-inner:42px;--fl-margin-outer:42px\"><div class=\"fl-l-bleed-outer\"><figure class=\"fl-l-photo fl-frame\" data-bleed=\"all\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\" data-bleed=\"all\"></figure><div class=\"fl-l-copy fl-area\"><p class=\"fl-h1\">沿着光线，<br>理解现场。</p><p class=\"fl-key fl-mt-3\">照片提供事实，文字建立阅读方向。</p></div></div></section>",
      "specimenPage": {
        "id": "bleed-outer",
        "label": "外侧出血摄影"
      }
    },
    {
      "id": "timeline-grid",
      "title": "同一轴线的时间",
      "category": "information",
      "classes": [
        "fl-l-timeline",
        "fl-l-item",
        "fl-l-full"
      ],
      "description": "明确列数形成共享轨道，通栏说明仍属于同一阅读单元。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-timeline fl-axis\" style=\"--fl-timeline-count:4\"><section class=\"fl-l-item\"><p class=\"fl-font-number fl-size-h2\">09:00</p><p class=\"fl-h3\">集合</p></section><section class=\"fl-l-item\"><p class=\"fl-font-number fl-size-h2\">10:00</p><p class=\"fl-h3\">观察</p></section><section class=\"fl-l-item\"><p class=\"fl-font-number fl-size-h2\">13:00</p><p class=\"fl-h3\">讨论</p></section><section class=\"fl-l-item\"><p class=\"fl-font-number fl-size-h2\">15:00</p><p class=\"fl-h3\">复盘</p></section><p class=\"fl-l-full fl-key fl-mt-4\">示例行程 / 节点按时间排序；需按真实安排核对时长。</p></div>",
      "specimenPage": {
        "id": "timeline-grid",
        "label": "同一轴线的时间"
      }
    },
    {
      "id": "stair-grid",
      "title": "递进与阶梯",
      "category": "reading",
      "classes": [
        "fl-l-stair"
      ],
      "description": "每一步移动一条共同轨道，文字按DOM顺序自然向下阅读。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-stair\"><p class=\"fl-h1\">观察，</p><p class=\"fl-h1\">理解，</p><p class=\"fl-h1\">判断，</p><p class=\"fl-h1\">行动。</p></div>",
      "specimenPage": {
        "id": "stair-grid",
        "label": "递进与阶梯"
      }
    }
  ],
  "components": [
    {
      "id": "opening",
      "title": "眉题、标题、导语",
      "category": "reading",
      "description": "三个不同阅读速度组成一个开篇：定位、命题、展开。",
      "grammar": "stack＋角色字级＋固定段间距；字号、字重和颜色均可独立替换。",
      "classes": [
        "fl-l-stack",
        "fl-kicker",
        "fl-h1",
        "fl-lead",
        "fl-gap-2"
      ],
      "limits": "眉题提供语境，不重复标题。导语宜短；长论述进入正文，不持续放大字号。",
      "html": "<header class=\"fl-l-stack fl-gap-2\">\n  <p class=\"fl-kicker fl-text-muted\">观察练习 / 第一章</p>\n  <h2 class=\"fl-h1 fl-balance\">从熟悉的地方<br>发现一个新问题。</h2>\n  <p class=\"fl-lead fl-mt-2\">给第一次看见的细节留一个位置，也给尚未理解的事留一点时间。</p>\n</header>",
      "specimenPage": {
        "id": "opening",
        "label": "眉题、标题、导语"
      }
    },
    {
      "id": "quotation",
      "title": "引文与署名",
      "category": "reading",
      "description": "引文通过独立字级和留白获得第二种阅读速度，署名紧跟其后。",
      "grammar": "blockquote 内使用 stack；引文 display 字体＋lead 尺度，署名为 key 角色。",
      "classes": [
        "fl-l-stack",
        "fl-font-display",
        "fl-size-h3",
        "fl-leading-lead",
        "fl-key"
      ],
      "limits": "引用真实作者时保留原文、署名和出处。下方文字为本库编排示例，不借用人物名义。",
      "html": "<blockquote class=\"fl-l-stack fl-gap-3 fl-py-3\">\n  <p class=\"fl-font-display fl-size-h3 fl-leading-lead\">“给一个细节足够的空间，<br>它会带来下一个问题。”</p>\n  <footer class=\"fl-key fl-text-muted\">Folio 编排示例 · 原创示例文案</footer>\n</blockquote>",
      "specimenPage": {
        "id": "quotation",
        "label": "引文与署名"
      }
    },
    {
      "id": "caption",
      "title": "图片与分层图注",
      "category": "photography",
      "description": "图片、说明和来源各自清楚，却作为一个完整单元移动。",
      "grammar": "figure 包含 frame、正文图注和较轻的来源行；全由原子与 stack 构成。",
      "classes": [
        "fl-frame",
        "fl-ratio-wide",
        "fl-caption",
        "fl-aux",
        "fl-l-stack"
      ],
      "limits": "说明写可见内容；来源保持可追溯。不要将图库照片说成项目现场。该例来源链接来自现有素材记录。",
      "html": "<figure class=\"fl-l-stack fl-gap-2\">\n  <figure class=\"fl-frame fl-ratio-wide\"><img src=\"../samples/native/nature-camp/assets/images/forest-cc0.jpg\" alt=\"树木与林地\" loading=\"lazy\"></figure>\n  <figcaption class=\"fl-l-stack fl-gap-1\"><p class=\"fl-caption\">林地的远近层次。画面用于展示图注与照片的对应关系。</p><p class=\"fl-aux fl-text-muted\">SpessiG · Landscape of a wild forest · CC0 1.0<br><a href=\"https://commons.wikimedia.org/wiki/File:Landscape_of_a_wild_forest.jpg\">Wikimedia Commons 素材来源</a></p></figcaption>\n</figure>",
      "specimenPage": {
        "id": "caption",
        "label": "图片与分层图注"
      }
    },
    {
      "id": "number-unit",
      "title": "数字、单位与解释",
      "category": "information",
      "description": "让关键数字成为入口，同时把单位和限定保留在旁边。",
      "grammar": "baseline cluster 将大数字与单位对齐；下方短说明保持自然阅读尺度。",
      "classes": [
        "fl-l-cluster",
        "fl-items-baseline",
        "fl-number",
        "fl-size-hero",
        "fl-tabular",
        "fl-key"
      ],
      "limits": "数字必须有真实来源与单位。示例 6 指本库网格的轨数，不是装饰性的业务指标。",
      "html": "<div class=\"fl-l-stack fl-gap-2\">\n  <div class=\"fl-l-cluster fl-gap-2 fl-items-baseline\"><strong class=\"fl-number fl-size-hero fl-leading-display fl-tabular\">6</strong><span class=\"fl-key\">条对齐轨道</span></div>\n  <p class=\"fl-body\">可以组成 3＋3 双栏、4＋2 主文旁注，或完整的通栏。</p>\n  <p class=\"fl-caption fl-text-muted\">轨道定义对齐关系；正文实际行长由内容与字级决定。</p>\n</div>",
      "specimenPage": {
        "id": "number-unit",
        "label": "数字、单位与解释"
      }
    },
    {
      "id": "contents",
      "title": "目录条目",
      "category": "information",
      "description": "章节号、标题和页码保持稳定关系，读者能快速寻找目标。",
      "grammar": "hanging 外置编号；正文内部 flex 将标题与页码分开，下方放简短说明。",
      "classes": [
        "fl-l-stack",
        "fl-l-hanging",
        "fl-l-label",
        "fl-l-main",
        "fl-flex",
        "fl-justify-between"
      ],
      "limits": "目录页码在成册后核对；示例页码只演示关系。标题长度变动时允许换行，不用省略号掩盖内容。",
      "html": "<nav aria-label=\"示例目录\" class=\"fl-l-stack fl-gap-4\">\n  <div class=\"fl-l-hanging\"><span class=\"fl-l-label fl-number fl-size-lead\">01</span><div class=\"fl-l-main\"><div class=\"fl-flex fl-justify-between fl-gap-3 fl-items-baseline\"><span class=\"fl-h3\">走进现场</span><span class=\"fl-number fl-key\">04</span></div><p class=\"fl-key fl-text-muted fl-mt-1\">认识环境，找到观察的起点。</p></div></div>\n  <div class=\"fl-l-hanging\"><span class=\"fl-l-label fl-number fl-size-lead\">02</span><div class=\"fl-l-main\"><div class=\"fl-flex fl-justify-between fl-gap-3 fl-items-baseline\"><span class=\"fl-h3\">留下记录</span><span class=\"fl-number fl-key\">12</span></div><p class=\"fl-key fl-text-muted fl-mt-1\">从描述出发，再组织自己的解释。</p></div></div>\n</nav>",
      "specimenPage": {
        "id": "contents",
        "label": "目录条目"
      }
    },
    {
      "id": "question-answer",
      "title": "问答条目",
      "category": "reading",
      "description": "问题成为明确入口，回答保有连续段落，不用每条套一个提示框。",
      "grammar": "两个 hanging 行；Q/A 使用相同标签位置，回答维持正文尺度。",
      "classes": [
        "fl-l-stack",
        "fl-l-hanging",
        "fl-l-label",
        "fl-l-main",
        "fl-h3",
        "fl-body"
      ],
      "limits": "真实问答应完整回应问题。回答较长时可以继续自然段或续页，不固定条目高度。",
      "html": "<article class=\"fl-l-stack fl-gap-3\">\n  <div class=\"fl-l-hanging\"><span class=\"fl-l-label fl-key fl-text-muted\">Q</span><h3 class=\"fl-l-main fl-h3\">一定要先知道名称，才能开始观察吗？</h3></div>\n  <div class=\"fl-l-hanging\"><span class=\"fl-l-label fl-key fl-text-muted\">A</span><div class=\"fl-l-main fl-prose fl-body\"><p>可以先描述你看见的东西。形状、位置、颜色和变化，都是有效的记录。</p><p>找到名称之后，再回看原来的描述。比较两者，会帮助你发现哪些细节最有区分力。</p></div></div>\n</article>",
      "specimenPage": {
        "id": "question-answer",
        "label": "问答条目"
      }
    },
    {
      "id": "checklist",
      "title": "可勾选清单",
      "category": "information",
      "description": "让勾选标记承担实际记录用途，条目之间用行距组织。",
      "grammar": "stack＋hanging；fl-check 是固定大小的功能标记，正文仍自然换行。",
      "classes": [
        "fl-l-stack",
        "fl-l-hanging",
        "fl-check",
        "fl-body"
      ],
      "limits": "清单是打印记录，不是浏览器交互表单。需要线上输入时应换成原生 input，并单独处理可访问名称。",
      "html": "<section class=\"fl-l-stack fl-gap-3\">\n  <h3 class=\"fl-h3\">离开前，回看记录。</h3>\n  <div class=\"fl-l-hanging\"><span class=\"fl-l-label fl-check\" aria-hidden=\"true\"></span><p class=\"fl-l-main fl-body\">写下观察的位置与时间。</p></div>\n  <div class=\"fl-l-hanging\"><span class=\"fl-l-label fl-check\" aria-hidden=\"true\"></span><p class=\"fl-l-main fl-body\">区分看到的事实与自己的解释。</p></div>\n  <div class=\"fl-l-hanging\"><span class=\"fl-l-label fl-check\" aria-hidden=\"true\"></span><p class=\"fl-l-main fl-body\">留下一个下次想确认的问题。</p></div>\n</section>",
      "specimenPage": {
        "id": "checklist",
        "label": "可勾选清单"
      }
    },
    {
      "id": "open-table",
      "title": "开放式表格",
      "category": "information",
      "description": "通过列对齐和水平分隔呈现查阅信息，让完整数据保持可读。",
      "grammar": "原生 table＋width 原子＋表头字重；横线加在行上，单元格使用相同 padding。",
      "classes": [
        "fl-w-full",
        "fl-rule",
        "fl-rule-strong",
        "fl-key",
        "fl-weight-strong",
        "fl-py-2",
        "fl-px-2"
      ],
      "limits": "真实表格保留全部行、单位与来源。不要把每行变成独立卡片；长表需要按实际内容分页并重复表头。",
      "html": "<table class=\"fl-w-full fl-key\">\n  <caption class=\"fl-h3 fl-text-left fl-mb-3\">观察记录的三个维度</caption>\n  <thead><tr class=\"fl-rule-strong\"><th scope=\"col\" class=\"fl-py-2 fl-px-2 fl-weight-strong\">维度</th><th scope=\"col\" class=\"fl-py-2 fl-px-2 fl-weight-strong\">记录什么</th><th scope=\"col\" class=\"fl-py-2 fl-px-2 fl-weight-strong\">回看时的问题</th></tr></thead>\n  <tbody><tr class=\"fl-rule\"><th scope=\"row\" class=\"fl-py-2 fl-px-2 fl-weight-regular\">位置</th><td class=\"fl-py-2 fl-px-2\">方向与相邻关系</td><td class=\"fl-py-2 fl-px-2\">观察角度是否一致？</td></tr><tr class=\"fl-rule\"><th scope=\"row\" class=\"fl-py-2 fl-px-2 fl-weight-regular\">时间</th><td class=\"fl-py-2 fl-px-2\">日期与光照条件</td><td class=\"fl-py-2 fl-px-2\">变化可能来自什么？</td></tr><tr class=\"fl-rule\"><th scope=\"row\" class=\"fl-py-2 fl-px-2 fl-weight-regular\">细节</th><td class=\"fl-py-2 fl-px-2\">形状、颜色与质地</td><td class=\"fl-py-2 fl-px-2\">哪些差异值得再看？</td></tr></tbody>\n</table>",
      "specimenPage": {
        "id": "open-table",
        "label": "开放式表格"
      }
    },
    {
      "id": "itinerary-days",
      "title": "多日行程 · 张弛安排",
      "category": "itinerary",
      "description": "到达、深入、收束各有节奏；每天明确核心体验与休息时段。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-cols-3",
        "fl-grid",
        "fl-h3",
        "fl-key",
        "fl-kicker",
        "fl-mb-2"
      ],
      "limits": "等宽列表示天数，不表示每项持续时长。示例行程未核验交通、场地或天气，不可直接用于出行承诺。",
      "html": "<div class=\"fl-grid fl-cols-3\"><section><p class=\"fl-kicker fl-mb-2\">DAY 01 · 适应</p><h3 class=\"fl-h3 fl-mb-2\">抵达与定向</h3><p class=\"fl-key\">上午｜集合与交通<br>下午｜林地定向 · 低强度<br>晚上｜整理问题 · 早休息</p></section><section><p class=\"fl-kicker fl-mb-2\">DAY 02 · 深入</p><h3 class=\"fl-h3 fl-mb-2\">完整现场观察</h3><p class=\"fl-key\">上午｜溪流样方 · 中强度<br>下午｜自由记录 · 弹性休息<br>晚上｜星空观察 · 天气备选</p></section><section><p class=\"fl-kicker fl-mb-2\">DAY 03 · 收束</p><h3 class=\"fl-h3 fl-mb-2\">交换发现与返程</h3><p class=\"fl-key\">上午｜小组交流 · 低强度<br>中午｜午餐与整理<br>下午｜返程 · 预留缓冲</p></section></div>",
      "specimenPage": {
        "id": "itinerary-days",
        "label": "多日行程 · 张弛安排"
      }
    },
    {
      "id": "timeline-vertical",
      "title": "纵向 timeline · 当日时刻",
      "category": "itinerary",
      "description": "让时间、活动、转场和休息沿同一条阅读路径展开。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-h3",
        "fl-key",
        "fl-l-chronology",
        "fl-l-item",
        "fl-l-label",
        "fl-l-main",
        "fl-mb-2",
        "fl-tabular"
      ],
      "limits": "这是按事件顺序排列的定性 timeline；行高随文字增长，不代表时间长度。需要时长比例时使用节奏时间带。",
      "html": "<ol class=\"fl-l-chronology\"><li class=\"fl-l-item\"><time class=\"fl-l-label fl-key fl-tabular\">09:00</time><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-2\">集合与安全说明</h3><p class=\"fl-key\">30 分钟｜确认身体状态、路线与退出点。</p></div></li><li class=\"fl-l-item\"><time class=\"fl-l-label fl-key fl-tabular\">09:30</time><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-2\">林缘慢行</h3><p class=\"fl-key\">60 分钟｜小组轮换记录；坡段不安排讲解。</p></div></li><li class=\"fl-l-item\"><time class=\"fl-l-label fl-key fl-tabular\">10:30</time><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-2\">饮水与休息</h3><p class=\"fl-key\">30 分钟｜留出自主休息，不把缓冲当作活动。</p></div></li><li class=\"fl-l-item\"><time class=\"fl-l-label fl-key fl-tabular\">11:00</time><div class=\"fl-l-main\"><h3 class=\"fl-h3 fl-mb-2\">整理观察</h3><p class=\"fl-key\">45 分钟｜比较记录；11:45 集合返程。</p></div></li></ol>",
      "specimenPage": {
        "id": "timeline-vertical",
        "label": "纵向 timeline · 当日时刻"
      }
    },
    {
      "id": "rhythm-band",
      "title": "节奏时间带 · 按时长比例",
      "category": "itinerary",
      "description": "以 15 分钟为一格，活动时长与色段宽度严格对应。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-caption",
        "fl-cols-12",
        "fl-cols-3",
        "fl-gap-0",
        "fl-gap-2",
        "fl-grid",
        "fl-key",
        "fl-l-stack",
        "fl-span-1",
        "fl-span-2",
        "fl-span-3",
        "fl-span-4",
        "fl-surface-accent",
        "fl-surface-dark",
        "fl-surface-soft",
        "fl-weight-strong"
      ],
      "limits": "每轨必须对应相同时间单位；此例 12×15 分钟。色带不是活动强度曲线，短时段标签置于色带外。",
      "html": "<div class=\"fl-l-stack fl-gap-2\"><p class=\"fl-key fl-weight-strong\">09:00—12:00 · 共 180 分钟</p><div class=\"fl-grid fl-cols-12 fl-gap-0\" style=\"height:42px\" aria-label=\"30分钟集合，60分钟观察，30分钟休息，45分钟整理，15分钟缓冲\"><div class=\"fl-span-2 fl-surface-dark\"></div><div class=\"fl-span-4 fl-surface-accent\"></div><div class=\"fl-span-2 fl-surface-soft\"></div><div class=\"fl-span-3 fl-surface-dark\"></div><div class=\"fl-span-1 fl-surface-soft\"></div></div><div class=\"fl-grid fl-cols-12 fl-gap-0\"><p class=\"fl-key fl-span-2\">集合<br>30 min</p><p class=\"fl-key fl-span-4\">观察<br>60 min</p><p class=\"fl-key fl-span-2\">休息<br>30 min</p><p class=\"fl-key fl-span-3\">整理<br>45 min</p><p class=\"fl-key fl-span-1\">缓冲<br>15 min</p></div><p class=\"fl-caption\">色段与下方标签逐项对齐；浅色代表休息或缓冲。</p></div>",
      "specimenPage": {
        "id": "rhythm-band",
        "label": "节奏时间带 · 按时长比例"
      }
    },
    {
      "id": "milestones",
      "title": "横向 timeline · 阶段里程碑",
      "category": "itinerary",
      "description": "阶段、交付与判断标准一起展示，让读者知道下一步何时发生。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-cols-3",
        "fl-grid",
        "fl-h3",
        "fl-key",
        "fl-kicker",
        "fl-mb-2"
      ],
      "limits": "等距节点表示阶段顺序，不暗示等长时间；若有日期，将实际日期写入标签。",
      "html": "<div class=\"fl-grid fl-cols-3\"><section><p class=\"fl-kicker fl-mb-2\">01 / 定义</p><h3 class=\"fl-h3 fl-mb-2\">确认问题</h3><p class=\"fl-key\">交付：观察清单<br>进入条件：范围与责任人已确认</p></section><section><p class=\"fl-kicker fl-mb-2\">02 / 试行</p><h3 class=\"fl-h3 fl-mb-2\">验证方法</h3><p class=\"fl-key\">交付：试点记录<br>进入条件：关键假设得到证据</p></section><section><p class=\"fl-kicker fl-mb-2\">03 / 推进</p><h3 class=\"fl-h3 fl-mb-2\">形成常规</h3><p class=\"fl-key\">交付：执行手册<br>进入条件：资源与复盘机制就绪</p></section></div>",
      "specimenPage": {
        "id": "milestones",
        "label": "横向 timeline · 阶段里程碑"
      }
    },
    {
      "id": "swimlane",
      "title": "并行泳道 · 谁在何时做什么",
      "category": "itinerary",
      "description": "三条任务线共享时间列，呈现并行、交接与协同。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-key",
        "fl-py-2",
        "fl-rule"
      ],
      "limits": "使用真实表头，按行读取仍有意义。列代表阶段，不是按日历比例绘制的甘特图；依赖关系另加文字说明。",
      "html": "<table class=\"fl-key\" style=\"width:100%;border-collapse:collapse;text-align:left\"><thead><tr><th class=\"fl-py-2 fl-rule\">工作线</th><th class=\"fl-py-2 fl-rule\">准备期</th><th class=\"fl-py-2 fl-rule\">现场期</th><th class=\"fl-py-2 fl-rule\">复盘期</th></tr></thead><tbody><tr><th class=\"fl-py-2 fl-rule\">内容</th><td class=\"fl-py-2 fl-rule\">确定问题</td><td class=\"fl-py-2 fl-rule\">采集记录</td><td class=\"fl-py-2 fl-rule\">校核结论</td></tr><tr><th class=\"fl-py-2 fl-rule\">运营</th><td class=\"fl-py-2 fl-rule\">确认资源</td><td class=\"fl-py-2 fl-rule\">协调现场</td><td class=\"fl-py-2 fl-rule\">归档反馈</td></tr><tr><th class=\"fl-py-2 fl-rule\">设计</th><td class=\"fl-py-2 fl-rule\">建立结构</td><td class=\"fl-py-2 fl-rule\">整理素材</td><td class=\"fl-py-2 fl-rule\">出版交付</td></tr></tbody></table>",
      "specimenPage": {
        "id": "swimlane",
        "label": "并行泳道 · 谁在何时做什么"
      }
    },
    {
      "id": "kpi-evidence",
      "title": "关键指标 · 数字与口径",
      "category": "business",
      "description": "数字旁边同时给出单位、时期、比较基准与来源。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-caption",
        "fl-cols-3",
        "fl-grid",
        "fl-h3",
        "fl-key",
        "fl-kicker",
        "fl-mb-2",
        "fl-mt-3"
      ],
      "limits": "指标必须可追溯；比例需写分子分母。实际业务口径（如税前/税后）需补齐后再用于宣传。",
      "html": "<div class=\"fl-grid fl-cols-3\"><section><p class=\"fl-kicker fl-mb-2\">2025 · 示例</p><h3 class=\"fl-h3 fl-mb-2\">128 百万元</h3><p class=\"fl-key\">年度收入<br>较上年 +28%；基准 100</p></section><section><p class=\"fl-kicker fl-mb-2\">2025 · 示例</p><h3 class=\"fl-h3 fl-mb-2\">32 百万元</h3><p class=\"fl-key\">年度利润<br>较上年 +7；基准 25</p></section><section><p class=\"fl-kicker fl-mb-2\">2025 · 示例</p><h3 class=\"fl-h3 fl-mb-2\">25.0%</h3><p class=\"fl-key\">利润 / 收入<br>32 ÷ 128；同比持平</p></section></div><p class=\"fl-caption fl-mt-3\">来源：本页自拟演示数据；并非某家公司的实际经营业绩。</p>",
      "specimenPage": {
        "id": "kpi-evidence",
        "label": "关键指标 · 数字与口径"
      }
    },
    {
      "id": "target-actual",
      "title": "目标与实际 · 差距可见",
      "category": "business",
      "description": "目标、实际和差额共同呈现，避免只挑选好看的百分比。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-caption",
        "fl-key",
        "fl-mt-2",
        "fl-py-2",
        "fl-rule",
        "fl-tabular"
      ],
      "limits": "不同单位的指标不共用长度比例；差额的正负不自动等同于好坏，例如成本应按业务目标解读。",
      "html": "<table class=\"fl-key\" style=\"width:100%;border-collapse:collapse;text-align:left\"><thead><tr><th class=\"fl-py-2 fl-rule\">项目</th><th class=\"fl-py-2 fl-rule\">目标</th><th class=\"fl-py-2 fl-rule\">实际</th><th class=\"fl-py-2 fl-rule\">差额</th></tr></thead><tbody><tr><td class=\"fl-py-2 fl-rule fl-tabular\">收入 / 百万元</td><td class=\"fl-py-2 fl-rule fl-tabular\">130</td><td class=\"fl-py-2 fl-rule fl-tabular\">128</td><td class=\"fl-py-2 fl-rule fl-tabular\">−2</td></tr><tr><td class=\"fl-py-2 fl-rule fl-tabular\">利润 / 百万元</td><td class=\"fl-py-2 fl-rule fl-tabular\">30</td><td class=\"fl-py-2 fl-rule fl-tabular\">32</td><td class=\"fl-py-2 fl-rule fl-tabular\">+2</td></tr><tr><td class=\"fl-py-2 fl-rule fl-tabular\">交付项目 / 个</td><td class=\"fl-py-2 fl-rule fl-tabular\">50</td><td class=\"fl-py-2 fl-rule fl-tabular\">48</td><td class=\"fl-py-2 fl-rule fl-tabular\">−2</td></tr></tbody></table><p class=\"fl-caption fl-mt-2\">2025 年度；差额 = 实际 − 目标。自拟演示数据。</p>",
      "specimenPage": {
        "id": "target-actual",
        "label": "目标与实际 · 差距可见"
      }
    },
    {
      "id": "five-forces",
      "title": "波特五力 · 行业结构",
      "category": "analysis",
      "description": "把五种竞争压力与判断依据对应，避免把框架误写成企业能力雷达。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-caption",
        "fl-cols-3",
        "fl-gap-3",
        "fl-grid",
        "fl-h3",
        "fl-key",
        "fl-mb-2",
        "fl-mt-3",
        "fl-p-3",
        "fl-row-start-2",
        "fl-row-start-3",
        "fl-start-1",
        "fl-start-2",
        "fl-surface-dark"
      ],
      "limits": "五力用于行业竞争结构；应注明行业、地区、时间与证据。定性强弱须写依据，不凭装饰性分数宣称精确。",
      "html": "<div class=\"fl-grid fl-cols-3 fl-gap-3\"><section class=\"fl-start-2\"><h3 class=\"fl-h3 fl-mb-2\">潜在进入者</h3><p class=\"fl-key\">技术门槛与渠道准入；需核验进入成本。</p></section><section class=\"fl-start-1 fl-row-start-2\"><h3 class=\"fl-h3 fl-mb-2\">供应商议价</h3><p class=\"fl-key\">关键原料集中度、替代来源和切换成本。</p></section><section class=\"fl-row-start-2 fl-surface-dark fl-p-3\"><h3 class=\"fl-h3 fl-mb-2\">现有竞争者</h3><p class=\"fl-key\">行业增长、差异化与退出成本。</p></section><section class=\"fl-row-start-2\"><h3 class=\"fl-h3 fl-mb-2\">购买者议价</h3><p class=\"fl-key\">采购集中度、价格敏感度与转换选择。</p></section><section class=\"fl-start-2 fl-row-start-3\"><h3 class=\"fl-h3 fl-mb-2\">替代品威胁</h3><p class=\"fl-key\">满足同一需求的其他方案及性价比。</p></section></div><p class=\"fl-caption fl-mt-3\">方法框架：Michael E. Porter / HBS Institute for Strategy and Competitiveness；此页仅列分析问题，尚无行业结论。</p>",
      "specimenPage": {
        "id": "five-forces",
        "label": "波特五力 · 行业结构"
      }
    },
    {
      "id": "decision-matrix",
      "title": "二维决策矩阵 · 取舍有轴",
      "category": "analysis",
      "description": "用明确的两个维度组织判断，并写出象限的行动含义。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-caption",
        "fl-cols-2",
        "fl-gap-0",
        "fl-gap-2",
        "fl-grid",
        "fl-h3",
        "fl-key",
        "fl-l-stack",
        "fl-mb-2",
        "fl-p-3",
        "fl-rule",
        "fl-surface-soft",
        "fl-weight-strong"
      ],
      "limits": "明确轴、阈值与评估时期；定性四象限不是数据散点图。不要给无依据的精确坐标。",
      "html": "<div class=\"fl-l-stack fl-gap-2\"><p class=\"fl-key fl-weight-strong\">纵轴：预期影响 ↑ 横轴：实施难度 →</p><div class=\"fl-grid fl-cols-2 fl-gap-0\"><section class=\"fl-p-3 fl-rule fl-surface-soft\"><h3 class=\"fl-h3 fl-mb-2\">优先试行</h3><p class=\"fl-key\">高影响 / 低难度<br>先做小范围验证，确认收益可复现。</p></section><section class=\"fl-p-3 fl-rule \"><h3 class=\"fl-h3 fl-mb-2\">分阶段投入</h3><p class=\"fl-key\">高影响 / 高难度<br>先解依赖，设置里程碑与退出条件。</p></section><section class=\"fl-p-3 fl-rule \"><h3 class=\"fl-h3 fl-mb-2\">顺手改进</h3><p class=\"fl-key\">低影响 / 低难度<br>控制投入，避免占用核心资源。</p></section><section class=\"fl-p-3 fl-rule fl-surface-soft\"><h3 class=\"fl-h3 fl-mb-2\">谨慎延后</h3><p class=\"fl-key\">低影响 / 高难度<br>记录暂缓理由与重新评估的触发条件。</p></section></div><p class=\"fl-caption\">定性示意；“高 / 低”需在项目中预先约定阈值。本例没有量化项目落点。</p></div>",
      "specimenPage": {
        "id": "decision-matrix",
        "label": "二维决策矩阵 · 取舍有轴"
      }
    },
    {
      "id": "value-chain",
      "title": "价值链 · 从能力到结果",
      "category": "analysis",
      "description": "连接投入、关键活动、交付结果，并暴露每一步的验证依据。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-caption",
        "fl-cols-3",
        "fl-grid",
        "fl-h3",
        "fl-key",
        "fl-kicker",
        "fl-mb-2",
        "fl-mt-3"
      ],
      "limits": "箭头表示逻辑顺序，不证明因果。企业宣传中的能力描述需有可核验证据支撑。",
      "html": "<div class=\"fl-grid fl-cols-3\"><section><p class=\"fl-kicker fl-mb-2\">输入 →</p><h3 class=\"fl-h3 fl-mb-2\">真实问题</h3><p class=\"fl-key\">用户访谈与既有资料<br>依据：需求记录</p></section><section><p class=\"fl-kicker fl-mb-2\">活动 →</p><h3 class=\"fl-h3 fl-mb-2\">可重复方法</h3><p class=\"fl-key\">小规模试验与过程复核<br>依据：验证日志</p></section><section><p class=\"fl-kicker fl-mb-2\">输出</p><h3 class=\"fl-h3 fl-mb-2\">可核验结果</h3><p class=\"fl-key\">交付、采用与持续改进<br>依据：验收与使用记录</p></section></div><p class=\"fl-caption fl-mt-3\">简化的价值创造路径；如分析完整产业链，应补齐采购、生产、分销及支持活动。</p>",
      "specimenPage": {
        "id": "value-chain",
        "label": "价值链 · 从能力到结果"
      }
    },
    {
      "id": "capability-table",
      "title": "能力对照 · 可核验的主张",
      "category": "business",
      "description": "每项能力都对应证据、范围和限制。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-caption",
        "fl-key",
        "fl-mt-2",
        "fl-py-2",
        "fl-rule"
      ],
      "limits": "竞品对照需同口径、有日期与来源；未经证实的勾选和“领先”结论不能用图表造型代替。",
      "html": "<table class=\"fl-key\" style=\"width:100%;border-collapse:collapse;text-align:left\"><thead><tr><th class=\"fl-py-2 fl-rule\">能力主张</th><th class=\"fl-py-2 fl-rule\">证据</th><th class=\"fl-py-2 fl-rule\">适用范围</th></tr></thead><tbody><tr><td class=\"fl-py-2 fl-rule\">稳定交付</td><td class=\"fl-py-2 fl-rule\">项目验收记录</td><td class=\"fl-py-2 fl-rule\">明确的产品与地区</td></tr><tr><td class=\"fl-py-2 fl-rule\">一致质量</td><td class=\"fl-py-2 fl-rule\">抽样方法与缺陷率</td><td class=\"fl-py-2 fl-rule\">标注样本量与期间</td></tr><tr><td class=\"fl-py-2 fl-rule\">持续改进</td><td class=\"fl-py-2 fl-rule\">同口径前后对照</td><td class=\"fl-py-2 fl-rule\">说明外部因素</td></tr></tbody></table><p class=\"fl-caption fl-mt-2\">示例是证据清单，尚未构成任何公司的已验证业绩。</p>",
      "specimenPage": {
        "id": "capability-table",
        "label": "能力对照 · 可核验的主张"
      }
    },
    {
      "id": "claim-evidence",
      "title": "结论与证据 · 咨询式图文组",
      "category": "business",
      "description": "先给可验证结论，再给证据，最后说明局限与下一步。",
      "grammar": "共享六轨 / 字阶 / 间距；语义 HTML 保留阅读顺序。",
      "classes": [
        "fl-body",
        "fl-h3",
        "fl-key",
        "fl-kicker",
        "fl-l-aside",
        "fl-l-main",
        "fl-l-sidebar",
        "fl-mb-2",
        "fl-weight-strong"
      ],
      "limits": "标题须由数据支持；相关性不能写成因果。没有证据时展示待验证假设，不写成既定结论。",
      "html": "<article class=\"fl-l-sidebar\"><div class=\"fl-l-main\"><p class=\"fl-kicker fl-mb-2\">判断</p><h3 class=\"fl-h3 fl-mb-2\">增量来自哪里，比增幅本身更重要。</h3><p class=\"fl-body\">把起点、增减项和终点放在同一张桥接图上，读者可以核对结论如何成立。</p></div><aside class=\"fl-l-aside\"><p class=\"fl-key fl-weight-strong\">核验清单</p><p class=\"fl-key\">期间一致<br>单位一致<br>各项不重复<br>合计可闭合<br>来源可回溯</p></aside></article>",
      "specimenPage": {
        "id": "claim-evidence",
        "label": "结论与证据 · 咨询式图文组"
      }
    },
    {
      "id": "swiss-furniture",
      "title": "页眉与页脚 · 阅读坐标",
      "category": "information",
      "description": "系列、主题与页码建立阅读位置，细线用于分隔元信息。",
      "grammar": "fl-meta 六轨页眉；fl-foot 以共同的首轨宽度对齐内容。",
      "classes": [
        "fl-foot",
        "fl-foot-end",
        "fl-gap-5",
        "fl-h1",
        "fl-key",
        "fl-l-aside",
        "fl-l-main",
        "fl-l-sidebar",
        "fl-l-stack",
        "fl-meta",
        "fl-pt-4",
        "fl-text-muted"
      ],
      "limits": "元信息保持简短；页码须由实际页序核对。页眉与页脚放入安全区，不能当作出血元素。",
      "html": "<article class=\"fl-l-stack fl-gap-5\">\n  <header class=\"fl-meta\"><span>FOLIO</span><span>方法与现场</span><span>第二章</span><span>08 / 24</span></header>\n  <div class=\"fl-l-sidebar\"><h2 class=\"fl-l-main fl-h1\">为阅读<br>建立坐标。</h2><p class=\"fl-l-aside fl-key fl-text-muted fl-pt-4\">系列与页码回答“我在哪里”，正文获得自己的空间。</p></div>\n  <footer class=\"fl-foot\"><span>第二章</span><span>从观察开始</span><span class=\"fl-foot-end\">08</span></footer>\n</article>",
      "specimenPage": {
        "id": "swiss-furniture",
        "label": "页眉与页脚 · 阅读坐标"
      }
    },
    {
      "id": "swiss-index",
      "title": "目录与索引 · 编号先行",
      "category": "information",
      "description": "编号、条目与终点各占一列，长标题自然换行。",
      "grammar": "fl-index + fl-index-n + fl-index-end；序号与正文同族，可加 fl-font-number 保持等宽数字。",
      "classes": [
        "fl-body",
        "fl-gap-4",
        "fl-h1",
        "fl-index",
        "fl-index-end",
        "fl-index-n",
        "fl-l-stack"
      ],
      "limits": "页码和日期是作者提供的数据。目录顺序须与书页一致；行线只分隔条目，不充当装饰边框。",
      "html": "<section class=\"fl-l-stack fl-gap-4\"><h2 class=\"fl-h1\">阅读路径</h2><ol class=\"fl-index fl-body\">\n  <li><span class=\"fl-index-n\">01</span><span>一个地方，一组问题</span><span class=\"fl-index-end\">04</span></li>\n  <li><span class=\"fl-index-n\">02</span><span>把细节放回整体</span><span class=\"fl-index-end\">12</span></li>\n  <li><span class=\"fl-index-n\">03</span><span>让证据支持判断</span><span class=\"fl-index-end\">20</span></li>\n  <li><span class=\"fl-index-n\">04</span><span>材料、方法与来源</span><span class=\"fl-index-end\">28</span></li>\n</ol></section>",
      "specimenPage": {
        "id": "swiss-index",
        "label": "目录与索引 · 编号先行"
      }
    },
    {
      "id": "swiss-term",
      "title": "双语术语 · 同一语义层级",
      "category": "reading",
      "description": "中文标题与外文术语形成相邻关系，定义独立展开。",
      "grammar": "fl-term 使用当前标题字族；正文回到 fl-body。",
      "classes": [
        "fl-body",
        "fl-display",
        "fl-gap-2",
        "fl-key",
        "fl-l-aside",
        "fl-l-main",
        "fl-l-offset",
        "fl-l-stack",
        "fl-mt-4",
        "fl-term",
        "fl-text-muted"
      ],
      "limits": "翻译须经校对。外文术语提供对应概念，不能仅为装饰。切换 bold/light 时，两种语言的标题一同切换。",
      "html": "<section class=\"fl-l-stack fl-gap-2\"><p class=\"fl-key fl-text-muted\">方法词典 / 03</p><h2 class=\"fl-display\">观察</h2><p class=\"fl-term\" lang=\"en\">Observation</p><div class=\"fl-l-offset fl-mt-4\"><p class=\"fl-l-aside fl-key fl-text-muted\">先描述，<br>再解释。</p><p class=\"fl-l-main fl-body\">把可见的形态、位置和变化记录下来。一个判断成立之前，应当能指出支撑它的具体细节。</p></div></section>",
      "specimenPage": {
        "id": "swiss-term",
        "label": "双语术语 · 同一语义层级"
      }
    },
    {
      "id": "swiss-legend",
      "title": "照片图注 · 编号、说明与来源",
      "category": "photography",
      "description": "照片保留主场，图注按六轨组织可检索信息。",
      "grammar": "fl-frame + fl-ratio-wide；fl-legend 的编号、四轨说明与来源各就各位。",
      "classes": [
        "fl-frame",
        "fl-gap-2",
        "fl-l-stack",
        "fl-legend",
        "fl-ratio-wide"
      ],
      "limits": "图注只描述看得见或有来源支持的事实。AI 生成图须明确标为非实拍，素材授权单独登记。",
      "html": "<figure class=\"fl-l-stack fl-gap-2\"><div class=\"fl-frame fl-ratio-wide\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" alt=\"礁岩、潮池与远处海岬上的灯塔\"></div><figcaption class=\"fl-legend\"><span>图 03</span><span>礁岩与潮池构成前景，灯塔位于远处海岬。图注接续照片的阅读方向。</span><span>Folio<br>素材登记</span></figcaption></figure>",
      "specimenPage": {
        "id": "swiss-legend",
        "label": "照片图注 · 编号、说明与来源"
      }
    },
    {
      "id": "swiss-dimensions",
      "title": "尺寸标注 · 观察与测量",
      "category": "information",
      "description": "水平与垂直标线把测量值留为真实文字。",
      "grammar": "fl-dim / fl-dim-v 由容器决定测量线长度；数字内容由作者填写。",
      "classes": [
        "fl-abb",
        "fl-caption",
        "fl-dim",
        "fl-dim-v",
        "fl-frame",
        "fl-gap-3",
        "fl-grid",
        "fl-h2",
        "fl-l-stack",
        "fl-ratio-wide"
      ],
      "limits": "标线不会读取物体尺寸。用于产品或工程资料时，必须以实测值替换示例，并注明单位与测量条件。",
      "html": "<section class=\"fl-l-stack fl-gap-3\"><h2 class=\"fl-h2\">对象与尺度</h2><div class=\"fl-grid\" style=\"grid-template-columns:42px minmax(0,1fr)\"><div></div><div class=\"fl-dim\"><span>横向实测值 / 单位</span></div><div class=\"fl-dim-v\"><span>纵向实测值 / 单位</span></div><figure class=\"fl-frame fl-ratio-wide\"><img src=\"../samples/native/nature-camp/assets/images/waterfall-moss.jpg\" alt=\"瀑布与岩石，尺寸组件的排版示意\"></figure></div><p class=\"fl-caption\"><span class=\"fl-abb\">图 04</span>标注结构演示；本图未提供实测尺寸。</p></section>",
      "specimenPage": {
        "id": "swiss-dimensions",
        "label": "尺寸标注 · 观察与测量"
      }
    },
    {
      "id": "swiss-statistics",
      "title": "关键数字 · 数值与口径",
      "category": "business",
      "description": "数值、单位、指标名和统计口径放在同一阅读单元里。",
      "grammar": "fl-stat + fl-number + fl-unit；三列共用顶端轴线。",
      "classes": [
        "fl-caption",
        "fl-cols-3",
        "fl-gap-4",
        "fl-grid",
        "fl-h2",
        "fl-key",
        "fl-l-stack",
        "fl-mb-2",
        "fl-number",
        "fl-stat",
        "fl-text-muted",
        "fl-unit"
      ],
      "limits": "示例为虚构数据。百分比须写明分母和时间，增幅须说明比较基期；数字大小不代表图表比例。",
      "html": "<section class=\"fl-l-stack fl-gap-4\"><header><p class=\"fl-key fl-text-muted fl-mb-2\">经营概览 / 示例数据</p><h2 class=\"fl-h2\">数字之后，保留依据。</h2></header><div class=\"fl-grid fl-cols-3\">\n<div class=\"fl-stat\"><p class=\"fl-number\">24<span class=\"fl-unit\">项</span></p><h3 class=\"fl-key\">已交付项目</h3><p class=\"fl-caption\">2025 全年；含验收记录</p></div>\n<div class=\"fl-stat\"><p class=\"fl-number\">92<span class=\"fl-unit\">%</span></p><h3 class=\"fl-key\">按期交付率</h3><p class=\"fl-caption\">22 / 24 项，四舍五入</p></div>\n<div class=\"fl-stat\"><p class=\"fl-number\">8<span class=\"fl-unit\">年</span></p><h3 class=\"fl-key\">连续服务</h3><p class=\"fl-caption\">2018—2025，含首尾年</p></div></div></section>",
      "specimenPage": {
        "id": "swiss-statistics",
        "label": "关键数字 · 数值与口径"
      }
    },
    {
      "id": "swiss-data-table",
      "title": "经营表格 · 文字左齐，数字右齐",
      "category": "business",
      "description": "取消单元格底色，让行线、列宽与数值对齐承担阅读任务。",
      "grammar": "fl-table 提供分隔；fl-num 统一数字字族与 tabular figures。",
      "classes": [
        "fl-caption",
        "fl-gap-3",
        "fl-h2",
        "fl-key",
        "fl-l-stack",
        "fl-mb-2",
        "fl-num",
        "fl-table",
        "fl-text-left"
      ],
      "limits": "保持表头、单位、时间与来源完整。表格数据是自拟示例；小数位同列一致，不用颜色替代正负号。",
      "html": "<section class=\"fl-l-stack fl-gap-3\"><h2 class=\"fl-h2\">项目组合</h2><table class=\"fl-table fl-key\"><caption class=\"fl-caption fl-text-left fl-mb-2\">2025 年度示例 · 单位：万元</caption><thead><tr><th scope=\"col\">业务类别</th><th scope=\"col\" class=\"fl-num\">收入</th><th scope=\"col\" class=\"fl-num\">成本</th><th scope=\"col\" class=\"fl-num\">结余</th></tr></thead><tbody><tr><th scope=\"row\">研究与咨询</th><td class=\"fl-num\">640.0</td><td class=\"fl-num\">420.0</td><td class=\"fl-num\">220.0</td></tr><tr><th scope=\"row\">内容与出版</th><td class=\"fl-num\">380.0</td><td class=\"fl-num\">290.0</td><td class=\"fl-num\">90.0</td></tr><tr><th scope=\"row\">培训与活动</th><td class=\"fl-num\">260.0</td><td class=\"fl-num\">210.0</td><td class=\"fl-num\">50.0</td></tr></tbody><tfoot><tr><th scope=\"row\">合计</th><td class=\"fl-num\">1,280.0</td><td class=\"fl-num\">920.0</td><td class=\"fl-num\">360.0</td></tr></tfoot></table><p class=\"fl-caption\">数据为结构演示；结余 = 收入 − 成本，未计税费。</p></section>",
      "specimenPage": {
        "id": "swiss-data-table",
        "label": "经营表格 · 文字左齐，数字右齐"
      }
    },
    {
      "id": "swiss-hanging-list",
      "title": "悬挂列表 · 保持左边界",
      "category": "reading",
      "description": "短横占据悬挂区，续行仍与文字左边界对齐。",
      "grammar": "fl-list 提供语义列表与悬挂符号；fl-l-offset 分配标题和内容。",
      "classes": [
        "fl-body",
        "fl-h2",
        "fl-key",
        "fl-l-aside",
        "fl-l-main",
        "fl-l-offset",
        "fl-list",
        "fl-mb-2",
        "fl-text-muted"
      ],
      "limits": "条目应属于同一分类。顺序重要时使用有编号的索引或步骤，不能只用装饰短横暗示先后。",
      "html": "<section class=\"fl-l-offset\"><header class=\"fl-l-aside\"><p class=\"fl-key fl-text-muted fl-mb-2\">出发之前</p><h2 class=\"fl-h2\">把准备<br>说清楚。</h2></header><ul class=\"fl-l-main fl-list fl-body\"><li>确认集合地点、联系人与返回时间。</li><li>根据当天活动选择便于行走的衣物，携带个人饮水。</li><li>将观察工具与记录纸放在随手可取的位置。</li><li>记录身体状态；需要协助时及时告知带队人员。</li></ul></section>",
      "specimenPage": {
        "id": "swiss-hanging-list",
        "label": "悬挂列表 · 保持左边界"
      }
    },
    {
      "id": "swiss-event-axis",
      "title": "时间轴 · 节点与当前阶段",
      "category": "itinerary",
      "description": "一条连续轴线连接事件，当前节点用信号色明确定位。",
      "grammar": "fl-l-timeline 决定等宽节点；fl-axis 提供轴线，fl-axis-now 标记当前。",
      "classes": [
        "fl-axis",
        "fl-axis-now",
        "fl-font-number",
        "fl-gap-4",
        "fl-h2",
        "fl-h3",
        "fl-key",
        "fl-l-item",
        "fl-l-stack",
        "fl-l-timeline"
      ],
      "limits": "等宽列表示事件顺序，不表示时间长度。持续时长的真实比例使用节奏时间带；日期与现场安排须另行核验。",
      "html": "<section class=\"fl-l-stack fl-gap-4\"><h2 class=\"fl-h2\">一次现场工作的节奏</h2><ol class=\"fl-l-timeline fl-axis\" style=\"list-style:none;padding:0;margin:0\"><li class=\"fl-l-item\"><time class=\"fl-key fl-font-number\">09:00</time><h3 class=\"fl-h3\">定向</h3><p class=\"fl-key\">确认路径<br>说明分工</p></li><li class=\"fl-l-item fl-axis-now\"><time class=\"fl-key fl-font-number\">09:30</time><h3 class=\"fl-h3\">观察</h3><p class=\"fl-key\">记录整体<br>进入细节</p></li><li class=\"fl-l-item\"><time class=\"fl-key fl-font-number\">11:00</time><h3 class=\"fl-h3\">交流</h3><p class=\"fl-key\">交换记录<br>核对问题</p></li><li class=\"fl-l-item\"><time class=\"fl-key fl-font-number\">11:45</time><h3 class=\"fl-h3\">收束</h3><p class=\"fl-key\">整理材料<br>检查返程</p></li></ol></section>",
      "specimenPage": {
        "id": "swiss-event-axis",
        "label": "时间轴 · 节点与当前阶段"
      }
    },
    {
      "id": "swiss-stair-heading",
      "title": "阶梯标题 · 按阅读顺序递进",
      "category": "reading",
      "description": "每一行向右推进一轨，以几何关系表达句子的推进。",
      "grammar": "fl-l-stair 控制逐行缩进；标题使用共享 fl-h1 字阶。",
      "classes": [
        "fl-gap-4",
        "fl-h1",
        "fl-key",
        "fl-l-stack",
        "fl-l-stair",
        "fl-mt-3",
        "fl-text-muted"
      ],
      "limits": "每次右移都会减少可用行宽。控制短句长度；全文保持 DOM 顺序，不旋转或裁切承载信息的文字。",
      "html": "<header class=\"fl-l-stack fl-gap-4\"><p class=\"fl-key fl-text-muted\">从问题到行动 / 一条思考路径</p><h2 class=\"fl-l-stair fl-h1\"><span>先看见，</span><span>再理解，</span><span>然后</span><span>行动。</span></h2><p class=\"fl-key fl-text-muted fl-mt-3\">右移来自共同的网格；句意决定每次停顿。</p></header>",
      "specimenPage": {
        "id": "swiss-stair-heading",
        "label": "阶梯标题 · 按阅读顺序递进"
      }
    },
    {
      "id": "swiss-negative-space",
      "title": "留白构图 · 空轨也有作用",
      "category": "reading",
      "description": "一个短标题与一段定义分处不同网格位置，以空白建立张力。",
      "grammar": "fl-grid + fl-cols-6 + span/start；间距使用 space-7。",
      "classes": [
        "fl-body",
        "fl-cols-6",
        "fl-foot",
        "fl-grid",
        "fl-h1",
        "fl-key",
        "fl-lead",
        "fl-mb-2",
        "fl-mt-3",
        "fl-mt-4",
        "fl-mt-7",
        "fl-span-4",
        "fl-span-full",
        "fl-start-3",
        "fl-text-muted"
      ],
      "limits": "空白是有意保留的阅读停顿。信息量增长时重排内容，不能通过减小正文来维持同一轮廓。",
      "html": "<section class=\"fl-grid fl-cols-6\"><header class=\"fl-span-4\"><p class=\"fl-key fl-text-muted fl-mb-2\">观察方法 / 01</p><h2 class=\"fl-h1\">给一个细节<br>足够的空间。</h2></header><div class=\"fl-start-3 fl-span-4 fl-mt-7\"><p class=\"fl-lead\">空白并非等待被填满。</p><p class=\"fl-body fl-mt-3\">它让相邻的信息分开，让重要的线索变得清晰，也让读者在翻页前拥有一次停顿。</p></div><footer class=\"fl-span-full fl-foot fl-mt-4\"><span>方法</span><span>先确定阅读顺序，再决定留白的位置。</span></footer></section>",
      "specimenPage": {
        "id": "swiss-negative-space",
        "label": "留白构图 · 空轨也有作用"
      }
    },
    {
      "id": "swiss-type-image",
      "title": "字即构图 · 巨字与真实标题",
      "category": "reading",
      "description": "一个巨字作为视觉锚点，真实标题与说明保持独立、可阅读。",
      "grammar": "fl-size-giant 扩展既定标题阶梯；几何关系由六轨网格承担。",
      "classes": [
        "fl-cols-6",
        "fl-font-display",
        "fl-grid",
        "fl-h2",
        "fl-items-end",
        "fl-key",
        "fl-leading-display",
        "fl-mark",
        "fl-mt-3",
        "fl-size-giant",
        "fl-span-3"
      ],
      "limits": "巨字只是视觉强调，信息必须在真实标题中完整出现。禁止为了塞入画面缩小正文字号，字形不可越出安全区。",
      "html": "<section class=\"fl-grid fl-cols-6 fl-items-end\"><p class=\"fl-span-3 fl-font-display fl-size-giant fl-leading-display\" aria-hidden=\"true\" data-role=\"deco\">形</p><div class=\"fl-span-3\"><span class=\"fl-mark\" aria-hidden=\"true\"></span><h2 class=\"fl-h2 fl-mt-3\">从形态<br>读出关系。</h2><p class=\"fl-key fl-mt-3\">边缘、方向、疏密与比例。字形和摄影一样，可以成为一页的视觉重心。</p></div></section>",
      "specimenPage": {
        "id": "swiss-type-image",
        "label": "字即构图 · 巨字与真实标题"
      }
    },
    {
      "id": "chart-bar",
      "title": "排名比较 · 直接标值",
      "category": "charts",
      "description": "同一零轴比较，不用截断坐标夸大差距。",
      "grammar": "Python 标准库计算几何 → SVG 图形与可编辑 HTML 标签；Folio 颜色与字体变量控制视觉。",
      "classes": [
        "fl-caption",
        "fl-mt-2"
      ],
      "limits": "默认 640px 宽；缩小时重新生成并检查最终字号。数据、单位、时期、来源必须齐全。示例值不能当作真实业绩。",
      "data": {
        "type": "bar",
        "labels": [
          "服务 A",
          "服务 B",
          "服务 C",
          "服务 D"
        ],
        "values": [
          48,
          35,
          28,
          17
        ],
        "id": "chart-bar",
        "title": "排名比较 · 直接标值",
        "width": 640,
        "height": 340
      },
      "html": "<figure><div style=\"position:relative;width:640px;height:340px;font-family:var(--fl-font-body);font-weight:400\"><svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 340\" width=\"640\" height=\"340\" style=\"display:block;max-width:100%;height:auto;font-family:var(--fl-font-body, sans-serif);font-size:14px\" aria-hidden=\"true\">\n<line x1=\"128.000\" y1=\"14.000\" x2=\"128.000\" y2=\"307.000\" stroke=\"var(--fl-text-muted,#56616A)\" stroke-width=\"1\" />\n<rect x=\"128.000\" y=\"26.000\" width=\"444.000\" height=\"45.540\" fill=\"var(--fl-text-accent,#164BE8)\" data-value=\"48\" data-zero=\"128\" />\n<rect x=\"128.000\" y=\"95.000\" width=\"323.750\" height=\"45.540\" fill=\"var(--fl-text-muted,#56616A)\" data-value=\"35\" data-zero=\"128\" />\n<rect x=\"128.000\" y=\"164.000\" width=\"259.000\" height=\"45.540\" fill=\"var(--fl-text-muted,#56616A)\" data-value=\"28\" data-zero=\"128\" />\n<rect x=\"128.000\" y=\"233.000\" width=\"157.250\" height=\"45.540\" fill=\"var(--fl-text-muted,#56616A)\" data-value=\"17\" data-zero=\"128\" />\n</svg><p data-role=\"key\" style=\"position:absolute;left:0.000px;top:43.88px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">服务 A</p><p data-role=\"key\" style=\"position:absolute;left:580.000px;top:43.88px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">48</p><p data-role=\"key\" style=\"position:absolute;left:0.000px;top:112.88px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">服务 B</p><p data-role=\"key\" style=\"position:absolute;left:459.750px;top:112.88px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">35</p><p data-role=\"key\" style=\"position:absolute;left:0.000px;top:181.88px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">服务 C</p><p data-role=\"key\" style=\"position:absolute;left:395.000px;top:181.88px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">28</p><p data-role=\"key\" style=\"position:absolute;left:0.000px;top:250.88px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">服务 D</p><p data-role=\"key\" style=\"position:absolute;left:293.250px;top:250.88px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">17</p><p data-role=\"key\" style=\"position:absolute;left:128.000px;top:316px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text-muted,#56616A)\">0</p></div><figcaption class=\"fl-caption fl-mt-2\">2025 年收入 / 百万元；四类合计 128。自拟演示数据。</figcaption></figure>",
      "specimenPage": {
        "id": "chart-bar",
        "label": "排名比较 · 直接标值"
      }
    },
    {
      "id": "chart-line",
      "title": "经营趋势 · 连续期间",
      "category": "charts",
      "description": "时间轴等距，标出末值与单位；不把预测混同已实现。",
      "grammar": "Python 标准库计算几何 → SVG 图形与可编辑 HTML 标签；Folio 颜色与字体变量控制视觉。",
      "classes": [
        "fl-caption",
        "fl-mt-2"
      ],
      "limits": "默认 640px 宽；缩小时重新生成并检查最终字号。数据、单位、时期、来源必须齐全。示例值不能当作真实业绩。",
      "data": {
        "type": "line",
        "labels": [
          "2022",
          "2023",
          "2024",
          "2025"
        ],
        "series": [
          {
            "name": "收入 / 百万元",
            "values": [
              72,
              86,
              100,
              128
            ]
          }
        ],
        "id": "chart-line",
        "title": "经营趋势 · 连续期间",
        "width": 640,
        "height": 340
      },
      "html": "<figure><div style=\"position:relative;width:640px;height:340px;font-family:var(--fl-font-body);font-weight:400\"><svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 340\" width=\"640\" height=\"340\" style=\"display:block;max-width:100%;height:auto;font-family:var(--fl-font-body, sans-serif);font-size:14px\" aria-hidden=\"true\">\n<line x1=\"58.000\" y1=\"288.000\" x2=\"566.000\" y2=\"288.000\" stroke=\"var(--fl-stroke,#B7BEC6)\" stroke-width=\"1\" />\n<line x1=\"58.000\" y1=\"171.500\" x2=\"566.000\" y2=\"171.500\" stroke=\"var(--fl-stroke,#B7BEC6)\" stroke-width=\"1\" />\n<line x1=\"58.000\" y1=\"55.000\" x2=\"566.000\" y2=\"55.000\" stroke=\"var(--fl-stroke,#B7BEC6)\" stroke-width=\"1\" />\n<polyline points=\"58.000,156.938 227.333,131.453 396.667,105.969 566.000,55.000\" fill=\"none\" stroke=\"var(--fl-text-accent,#164BE8)\" stroke-width=\"2.5\" />\n<circle cx=\"58.000\" cy=\"156.938\" r=\"3.5\" fill=\"var(--fl-text-accent,#164BE8)\" />\n<circle cx=\"227.333\" cy=\"131.453\" r=\"3.5\" fill=\"var(--fl-text-accent,#164BE8)\" />\n<circle cx=\"396.667\" cy=\"105.969\" r=\"3.5\" fill=\"var(--fl-text-accent,#164BE8)\" />\n<circle cx=\"566.000\" cy=\"55.000\" r=\"3.5\" fill=\"var(--fl-text-accent,#164BE8)\" />\n</svg><p data-role=\"key\" style=\"position:absolute;left:48.000px;top:277px;transform:translateX(-100%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text-muted,#56616A)\">0</p><p data-role=\"key\" style=\"position:absolute;left:48.000px;top:160.5px;transform:translateX(-100%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text-muted,#56616A)\">64</p><p data-role=\"key\" style=\"position:absolute;left:48.000px;top:44px;transform:translateX(-100%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text-muted,#56616A)\">128</p><p data-role=\"key\" style=\"position:absolute;left:58.000px;top:305px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text-muted,#56616A)\">2022</p><p data-role=\"key\" style=\"position:absolute;left:227.333px;top:305px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text-muted,#56616A)\">2023</p><p data-role=\"key\" style=\"position:absolute;left:396.667px;top:305px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text-muted,#56616A)\">2024</p><p data-role=\"key\" style=\"position:absolute;left:566.000px;top:305px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text-muted,#56616A)\">2025</p><p data-role=\"key\" style=\"position:absolute;left:58.000px;top:5px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:700;color:var(--fl-text-accent,#164BE8)\">收入 / 百万元</p><p data-role=\"key\" style=\"position:absolute;left:575.000px;top:44px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text-accent,#164BE8)\">128</p></div><figcaption class=\"fl-caption fl-mt-2\">2022—2025 年；同口径年度收入。自拟演示数据。</figcaption></figure>",
      "specimenPage": {
        "id": "chart-line",
        "label": "经营趋势 · 连续期间"
      }
    },
    {
      "id": "chart-stacked",
      "title": "构成比较 · 每组共 100%",
      "category": "charts",
      "description": "直接标注各部分数值，比例输入必须闭合到 100%。",
      "grammar": "Python 标准库计算几何 → SVG 图形与可编辑 HTML 标签；Folio 颜色与字体变量控制视觉。",
      "classes": [
        "fl-caption",
        "fl-mt-2"
      ],
      "limits": "默认 640px 宽；缩小时重新生成并检查最终字号。数据、单位、时期、来源必须齐全。示例值不能当作真实业绩。",
      "data": {
        "type": "stacked",
        "labels": [
          "2024",
          "2025"
        ],
        "series": [
          {
            "name": "订阅",
            "values": [
              45,
              55
            ]
          },
          {
            "name": "项目",
            "values": [
              35,
              30
            ]
          },
          {
            "name": "其他",
            "values": [
              20,
              15
            ]
          }
        ],
        "id": "chart-stacked",
        "title": "构成比较 · 每组共 100%",
        "width": 640,
        "height": 340
      },
      "html": "<figure><div style=\"position:relative;width:640px;height:340px;font-family:var(--fl-font-body);font-weight:400\"><svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 340\" width=\"640\" height=\"340\" style=\"display:block;max-width:100%;height:auto;font-family:var(--fl-font-body, sans-serif);font-size:14px\" aria-hidden=\"true\">\n<rect x=\"90.000\" y=\"55.000\" width=\"214.200\" height=\"29.000\" fill=\"var(--fl-text-accent,#164BE8)\" data-value=\"45\" />\n<rect x=\"304.200\" y=\"55.000\" width=\"166.600\" height=\"29.000\" fill=\"var(--fl-text-muted,#56616A)\" data-value=\"35\" />\n<rect x=\"470.800\" y=\"55.000\" width=\"95.200\" height=\"29.000\" fill=\"var(--fl-text,#202B32)\" data-value=\"20\" />\n<rect x=\"90.000\" y=\"171.500\" width=\"261.800\" height=\"29.000\" fill=\"var(--fl-text-accent,#164BE8)\" data-value=\"55\" />\n<rect x=\"351.800\" y=\"171.500\" width=\"142.800\" height=\"29.000\" fill=\"var(--fl-text-muted,#56616A)\" data-value=\"30\" />\n<rect x=\"494.600\" y=\"171.500\" width=\"71.400\" height=\"29.000\" fill=\"var(--fl-text,#202B32)\" data-value=\"15\" />\n</svg><p data-role=\"key\" style=\"position:absolute;left:90.000px;top:4px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:700;color:var(--fl-text-accent,#164BE8)\">订阅</p><p data-role=\"key\" style=\"position:absolute;left:260.000px;top:4px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:700;color:var(--fl-text-muted,#56616A)\">项目</p><p data-role=\"key\" style=\"position:absolute;left:430.000px;top:4px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:700;color:var(--fl-text,#202B32)\">其他</p><p data-role=\"key\" style=\"position:absolute;left:0.000px;top:62px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">2024</p><p data-role=\"key\" style=\"position:absolute;left:197.100px;top:86px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">45%</p><p data-role=\"key\" style=\"position:absolute;left:387.500px;top:86px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">35%</p><p data-role=\"key\" style=\"position:absolute;left:518.400px;top:86px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">20%</p><p data-role=\"key\" style=\"position:absolute;left:576.000px;top:62px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">100%</p><p data-role=\"key\" style=\"position:absolute;left:0.000px;top:178.5px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">2025</p><p data-role=\"key\" style=\"position:absolute;left:220.900px;top:202.5px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">55%</p><p data-role=\"key\" style=\"position:absolute;left:423.200px;top:202.5px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">30%</p><p data-role=\"key\" style=\"position:absolute;left:530.300px;top:202.5px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">15%</p><p data-role=\"key\" style=\"position:absolute;left:576.000px;top:178.5px;transform:translateX(0);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">100%</p></div><figcaption class=\"fl-caption fl-mt-2\">收入结构 / %；每年合计 100%。自拟演示数据。</figcaption></figure>",
      "specimenPage": {
        "id": "chart-stacked",
        "label": "构成比较 · 每组共 100%"
      }
    },
    {
      "id": "chart-waterfall",
      "title": "瀑布图 · 解释增减",
      "category": "charts",
      "description": "累计桥接起点与终点，正负变化和总计明确区分。",
      "grammar": "Python 标准库计算几何 → SVG 图形与可编辑 HTML 标签；Folio 颜色与字体变量控制视觉。",
      "classes": [
        "fl-caption",
        "fl-mt-2"
      ],
      "limits": "默认 640px 宽；缩小时重新生成并检查最终字号。数据、单位、时期、来源必须齐全。示例值不能当作真实业绩。",
      "data": {
        "type": "waterfall",
        "start": 25,
        "start_label": "上年利润",
        "changes": [
          {
            "label": "收入贡献",
            "value": 12
          },
          {
            "label": "效率改善",
            "value": 4
          },
          {
            "label": "研发投入",
            "value": -6
          },
          {
            "label": "其他成本",
            "value": -3
          }
        ],
        "end_label": "本年利润",
        "expected_total": 32,
        "id": "chart-waterfall",
        "title": "瀑布图 · 解释增减",
        "width": 640,
        "height": 340
      },
      "html": "<figure><div style=\"position:relative;width:640px;height:340px;font-family:var(--fl-font-body);font-weight:400\"><svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 340\" width=\"640\" height=\"340\" style=\"display:block;max-width:100%;height:auto;font-family:var(--fl-font-body, sans-serif);font-size:14px\" aria-hidden=\"true\">\n<line x1=\"38.000\" y1=\"289.000\" x2=\"618.000\" y2=\"289.000\" stroke=\"var(--fl-text-muted,#56616A)\" stroke-width=\"1\" />\n<rect x=\"48.000\" y=\"137.171\" width=\"54.150\" height=\"151.829\" fill=\"var(--fl-text,#202B32)\" data-start=\"0\" data-end=\"25\" data-value=\"25\" />\n<line x1=\"102.150\" y1=\"137.171\" x2=\"143.000\" y2=\"137.171\" stroke=\"var(--fl-stroke,#B7BEC6)\" stroke-width=\"1\" stroke-dasharray=\"4 4\" />\n<rect x=\"143.000\" y=\"64.293\" width=\"54.150\" height=\"72.878\" fill=\"var(--fl-text-accent,#164BE8)\" data-start=\"25\" data-end=\"37\" data-value=\"12\" />\n<line x1=\"197.150\" y1=\"64.293\" x2=\"238.000\" y2=\"64.293\" stroke=\"var(--fl-stroke,#B7BEC6)\" stroke-width=\"1\" stroke-dasharray=\"4 4\" />\n<rect x=\"238.000\" y=\"40.000\" width=\"54.150\" height=\"24.293\" fill=\"var(--fl-text-accent,#164BE8)\" data-start=\"37\" data-end=\"41\" data-value=\"4\" />\n<line x1=\"292.150\" y1=\"40.000\" x2=\"333.000\" y2=\"40.000\" stroke=\"var(--fl-stroke,#B7BEC6)\" stroke-width=\"1\" stroke-dasharray=\"4 4\" />\n<rect x=\"333.000\" y=\"40.000\" width=\"54.150\" height=\"36.439\" fill=\"var(--fl-text-muted,#56616A)\" data-start=\"41\" data-end=\"35\" data-value=\"-6\" />\n<line x1=\"387.150\" y1=\"76.439\" x2=\"428.000\" y2=\"76.439\" stroke=\"var(--fl-stroke,#B7BEC6)\" stroke-width=\"1\" stroke-dasharray=\"4 4\" />\n<rect x=\"428.000\" y=\"76.439\" width=\"54.150\" height=\"18.220\" fill=\"var(--fl-text-muted,#56616A)\" data-start=\"35\" data-end=\"32\" data-value=\"-3\" />\n<line x1=\"482.150\" y1=\"94.659\" x2=\"523.000\" y2=\"94.659\" stroke=\"var(--fl-stroke,#B7BEC6)\" stroke-width=\"1\" stroke-dasharray=\"4 4\" />\n<rect x=\"523.000\" y=\"94.659\" width=\"54.150\" height=\"194.341\" fill=\"var(--fl-text,#202B32)\" data-start=\"0\" data-end=\"32\" data-value=\"32\" />\n</svg><p data-role=\"key\" style=\"position:absolute;left:33.000px;top:278px;transform:translateX(-100%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text-muted,#56616A)\">0</p><p data-role=\"key\" style=\"position:absolute;left:75.075px;top:111.171px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:700;color:var(--fl-text,#202B32)\">25</p><p data-role=\"key\" style=\"position:absolute;left:75.075px;top:305px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">上年利润</p><p data-role=\"key\" style=\"position:absolute;left:170.075px;top:38.293px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">+12</p><p data-role=\"key\" style=\"position:absolute;left:170.075px;top:305px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">收入贡献</p><p data-role=\"key\" style=\"position:absolute;left:265.075px;top:14px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">+4</p><p data-role=\"key\" style=\"position:absolute;left:265.075px;top:305px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">效率改善</p><p data-role=\"key\" style=\"position:absolute;left:360.075px;top:14px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">-6</p><p data-role=\"key\" style=\"position:absolute;left:360.075px;top:305px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">研发投入</p><p data-role=\"key\" style=\"position:absolute;left:455.075px;top:50.439px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">-3</p><p data-role=\"key\" style=\"position:absolute;left:455.075px;top:305px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">其他成本</p><p data-role=\"key\" style=\"position:absolute;left:550.075px;top:68.659px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:700;color:var(--fl-text,#202B32)\">32</p><p data-role=\"key\" style=\"position:absolute;left:550.075px;top:305px;transform:translateX(-50%);margin:0;white-space:nowrap;font-size:14px;line-height:22px;font-weight:400;color:var(--fl-text,#202B32)\">本年利润</p></div><figcaption class=\"fl-caption fl-mt-2\">2024→2025 年利润桥接 / 百万元；25 + 12 + 4 − 6 − 3 = 32。自拟演示数据；变动项按不重叠口径分解。</figcaption></figure>",
      "specimenPage": {
        "id": "chart-waterfall",
        "label": "瀑布图 · 解释增减"
      }
    }
  ],
  "atoms": [
    {
      "id": "a-surface",
      "title": "表面与前景角色",
      "category": "颜色",
      "classes": [
        "fl-surface-paper",
        "fl-surface-soft",
        "fl-surface-dark",
        "fl-surface-accent",
        "fl-text-main",
        "fl-text-muted",
        "fl-text-accent",
        "fl-tone-inverse"
      ],
      "description": "表面同时绑定背景、正文、次要字、强调字和线条。强调色服务阅读主次。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-grid fl-cols-2\"><section class=\"fl-surface-paper fl-p-3\"><p class=\"fl-h2\">白纸</p><p class=\"fl-key fl-text-muted\">次要说明 / 来源</p><p class=\"fl-key fl-text-accent\">一个明确的重点</p></section><section class=\"fl-surface-soft fl-p-3\"><p class=\"fl-h2\">软纸</p><p class=\"fl-key fl-text-muted\">次要说明 / 来源</p><p class=\"fl-key fl-text-accent\">一个明确的重点</p></section><section class=\"fl-surface-dark fl-p-3\"><p class=\"fl-h2\">深墨</p><p class=\"fl-key fl-text-muted\">次要说明 / 来源</p><p class=\"fl-key fl-text-accent\">一个明确的重点</p></section><section class=\"fl-surface-accent fl-p-3\"><p class=\"fl-h2\">信号</p><p class=\"fl-key fl-text-muted\">次要说明 / 来源</p><p class=\"fl-key fl-text-accent\">一个明确的重点</p></section></div>",
      "specimenPage": {
        "id": "a-surface",
        "label": "表面与前景角色"
      }
    },
    {
      "id": "a-profiles",
      "title": "两种标题结构",
      "category": "排印",
      "classes": [
        "fl-type-bold",
        "fl-type-light"
      ],
      "description": "bold用衬线标题，light用无衬线标题；大字更轻的阶梯属于light。数字与正文同族，跟随字号档位。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-grid fl-cols-2\"><section class=\"fl-type-bold\"><p class=\"fl-kicker\">BOLD</p><p class=\"fl-display\">有序，<br>自由。</p><p class=\"fl-body fl-mt-3\">同一网格与字号，不同的字体与分量。</p><p class=\"fl-number fl-mt-3\">2026</p></section><section class=\"fl-type-light\"><p class=\"fl-kicker\">LIGHT</p><p class=\"fl-display\">有序，<br>自由。</p><p class=\"fl-body fl-mt-3\">同一网格与字号，不同的字体与分量。</p><p class=\"fl-number fl-mt-3\">2026</p></section></div>",
      "specimenPage": {
        "id": "a-profiles",
        "label": "两种标题结构"
      }
    },
    {
      "id": "a-roles",
      "title": "文字的阅读任务",
      "category": "排印",
      "classes": [
        "fl-display",
        "fl-h1",
        "fl-h2",
        "fl-h3",
        "fl-lead",
        "fl-body",
        "fl-key",
        "fl-aux",
        "fl-caption",
        "fl-kicker",
        "fl-number"
      ],
      "description": "语义样式不代替内容角色；正文、关键信息和图注仍需要正确data-role。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-stack fl-gap-3\"><p class=\"fl-display\">主张</p><p class=\"fl-h1\">专题标题</p><p class=\"fl-h2\">章节标题</p><p class=\"fl-h3\">栏目标题</p><p class=\"fl-lead\">引言引导读者进入正文。</p><p class=\"fl-body\">正文按自然阅读速度展开，保持字行与空间的关系。</p><p class=\"fl-key\">关键事实与提示</p><p class=\"fl-caption\">图 01 / 观察说明</p><p class=\"fl-aux\">来源 · 日期 · 页码</p><p class=\"fl-kicker\">FOLIO / FIELD NOTES</p><p class=\"fl-number\">128</p></div>",
      "specimenPage": {
        "id": "a-roles",
        "label": "文字的阅读任务"
      }
    },
    {
      "id": "a-font",
      "title": "字体与真实字重",
      "category": "排印",
      "classes": [
        "fl-font-display",
        "fl-font-reading",
        "fl-font-body",
        "fl-font-label",
        "fl-font-number",
        "fl-weight-regular",
        "fl-weight-strong"
      ],
      "description": "字体、字号、字重可独立组合。常规与强调请求已有静态字面，不合成伪粗体。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-stack fl-gap-3\"><p class=\"fl-font-display fl-size-h2\">标题 / Display</p><p class=\"fl-font-reading fl-size-h2\">阅读 / Reading</p><p class=\"fl-font-body fl-size-h2\">正文 / Body</p><p class=\"fl-font-label fl-size-h2\">LABEL / 元信息</p><p class=\"fl-font-number fl-size-h2\">0123456789</p><p class=\"fl-body\">常规 <strong>强调文字</strong></p><p class=\"fl-font-body fl-weight-strong\">显式选择强调</p></div>",
      "specimenPage": {
        "id": "a-font",
        "label": "字体与真实字重"
      }
    },
    {
      "id": "a-scale",
      "title": "从图注到标题的字阶",
      "category": "排印",
      "classes": [
        "fl-size-aux",
        "fl-size-key",
        "fl-size-small",
        "fl-size-body",
        "fl-size-lead",
        "fl-size-h3",
        "fl-size-h2",
        "fl-size-h1",
        "fl-size-display"
      ],
      "description": "尺寸是物理CSS px；字号原子同时应用当前模式对应字重。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-stack fl-gap-3\"><div class=\"fl-flex fl-items-baseline fl-gap-3\"><p class=\"fl-font-number fl-size-key\">11px</p><span class=\"fl-font-display fl-size-aux\">尺度之间</span></div><div class=\"fl-flex fl-items-baseline fl-gap-3\"><p class=\"fl-font-number fl-size-key\">13px</p><span class=\"fl-font-display fl-size-key\">尺度之间</span></div><div class=\"fl-flex fl-items-baseline fl-gap-3\"><p class=\"fl-font-number fl-size-key\">14px</p><span class=\"fl-font-display fl-size-small\">尺度之间</span></div><div class=\"fl-flex fl-items-baseline fl-gap-3\"><p class=\"fl-font-number fl-size-key\">16px</p><span class=\"fl-font-display fl-size-body\">尺度之间</span></div><div class=\"fl-flex fl-items-baseline fl-gap-3\"><p class=\"fl-font-number fl-size-key\">20px</p><span class=\"fl-font-display fl-size-lead\">尺度之间</span></div><div class=\"fl-flex fl-items-baseline fl-gap-3\"><p class=\"fl-font-number fl-size-key\">24px</p><span class=\"fl-font-display fl-size-h3\">尺度之间</span></div><div class=\"fl-flex fl-items-baseline fl-gap-3\"><p class=\"fl-font-number fl-size-key\">32px</p><span class=\"fl-font-display fl-size-h2\">尺度之间</span></div><div class=\"fl-flex fl-items-baseline fl-gap-3\"><p class=\"fl-font-number fl-size-key\">46px</p><span class=\"fl-font-display fl-size-h1\">尺度之间</span></div><div class=\"fl-flex fl-items-baseline fl-gap-3\"><p class=\"fl-font-number fl-size-key\">64px</p><span class=\"fl-font-display fl-size-display\">尺度之间</span></div></div>",
      "specimenPage": {
        "id": "a-scale",
        "label": "从图注到标题的字阶"
      }
    },
    {
      "id": "a-large",
      "title": "大字作为画面",
      "category": "排印",
      "classes": [
        "fl-size-hero",
        "fl-size-giant",
        "fl-size-colossal"
      ],
      "description": "巨字、图像与空白共享视觉分量。完整标题仍参与内容审计。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "大字需要足够行高与留白。正文不能裁切，只有重复装饰字可以越界。",
      "html": "<div class=\"fl-type-light\"><p class=\"fl-display fl-size-colossal fl-leading-hero\">Aa</p><div class=\"fl-flex fl-items-baseline fl-gap-3\"><p class=\"fl-display fl-size-giant fl-leading-hero\">字</p><p class=\"fl-number fl-size-hero\">112</p></div><p class=\"fl-caption\">280 / 196 / 112 px，字号不会随页面缩小。</p></div>",
      "specimenPage": {
        "id": "a-large",
        "label": "大字作为画面"
      }
    },
    {
      "id": "a-leading",
      "title": "行距与字距",
      "category": "排印",
      "classes": [
        "fl-leading-body",
        "fl-leading-reading",
        "fl-leading-lead",
        "fl-leading-tight",
        "fl-leading-display",
        "fl-leading-hero",
        "fl-tracking-tighter",
        "fl-tracking-tight",
        "fl-tracking-normal",
        "fl-tracking-wide"
      ],
      "description": "行距控制上下关系，字距控制同一行的密度；小字号不靠紧排来补容量。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-grid fl-cols-2\"><section><p class=\"fl-caption\">body</p><p class=\"fl-body fl-leading-body\">空间组织阅读。<br>阅读需要停顿。</p></section><section><p class=\"fl-caption\">reading</p><p class=\"fl-body fl-leading-reading\">空间组织阅读。<br>阅读需要停顿。</p></section><section><p class=\"fl-caption\">lead</p><p class=\"fl-body fl-leading-lead\">空间组织阅读。<br>阅读需要停顿。</p></section><section><p class=\"fl-caption\">tight</p><p class=\"fl-body fl-leading-tight\">空间组织阅读。<br>阅读需要停顿。</p></section><section><p class=\"fl-caption\">display</p><p class=\"fl-body fl-leading-display\">空间组织阅读。<br>阅读需要停顿。</p></section><section><p class=\"fl-caption\">hero</p><p class=\"fl-body fl-leading-hero\">空间组织阅读。<br>阅读需要停顿。</p></section></div><div class=\"fl-mt-4\"><p class=\"fl-font-label fl-size-h3 fl-tracking-tighter\">FOLIO / tighter</p><p class=\"fl-font-label fl-size-h3 fl-tracking-tight\">FOLIO / tight</p><p class=\"fl-font-label fl-size-h3 fl-tracking-normal\">FOLIO / normal</p><p class=\"fl-font-label fl-size-h3 fl-tracking-wide\">FOLIO / wide</p></div>",
      "specimenPage": {
        "id": "a-leading",
        "label": "行距与字距"
      }
    },
    {
      "id": "a-alignment",
      "title": "对齐、标点与数字",
      "category": "排印",
      "classes": [
        "fl-text-start",
        "fl-text-end",
        "fl-text-left",
        "fl-text-center",
        "fl-text-right",
        "fl-tabular",
        "fl-proportional",
        "fl-balance",
        "fl-caps",
        "fl-hang",
        "fl-optical"
      ],
      "description": "默认左齐右松；居中、右齐用于有明确轴线的内容，数字表列独立对齐。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-stack fl-gap-3\"><p class=\"fl-h3 fl-text-start\">左侧是一条共同的轴线。</p><p class=\"fl-h3 fl-text-center\">这是信息的中轴</p><p class=\"fl-h3 fl-text-end\">终点清晰可见</p><p class=\"fl-body fl-hang\">“开头标点可以悬挂，文字仍保持完整。</p><p class=\"fl-font-label fl-caps\">Folio / field notes</p><p class=\"fl-font-number fl-tabular fl-text-right\">1,280.50<br>9,042.00</p><p class=\"fl-h1 fl-balance fl-optical\">有序的留白</p></div>",
      "specimenPage": {
        "id": "a-alignment",
        "label": "对齐、标点与数字"
      }
    },
    {
      "id": "a-prose",
      "title": "连续文流与行长",
      "category": "排印",
      "classes": [
        "fl-measure",
        "fl-prose",
        "fl-prose-columns-2",
        "fl-prose-indent"
      ],
      "description": "连续双栏依DOM顺序流动，缩进与段距二选一；版面不隐藏溢出。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-prose fl-prose-columns-2 fl-font-reading fl-leading-reading\"><p>版面不是容器的堆叠。一个段落从哪里开始、在哪里结束，与相邻照片隔开多少距离，都会影响阅读顺序。</p><p>先保留完整内容，再决定分组。行长、行距和段距共同控制阅读速度；长文应增加页数，而不是压缩字形。</p><p>同一套规则可以接纳文字、摄影与数据。变化来自关系，而不是换一套模板。</p><p>留白不是剩余空间。它让主题获得分量，也为翻页设置停顿。</p></div><div class=\"fl-prose-indent fl-measure fl-mt-5\"><p>短段落可以保持齐头。</p><p>连续叙述也可以选择缩进方式，并贯穿同一篇文章。</p></div>",
      "specimenPage": {
        "id": "a-prose",
        "label": "连续文流与行长"
      }
    },
    {
      "id": "a-grid",
      "title": "共同的横向网格",
      "category": "网格",
      "classes": [
        "fl-grid",
        "fl-cols-1",
        "fl-cols-2",
        "fl-cols-3",
        "fl-cols-4",
        "fl-cols-6",
        "fl-cols-12"
      ],
      "description": "轨道是对齐坐标，不要求把正文塞成十二条窄栏。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-stack fl-gap-3\"><div><p class=\"fl-caption\">1 轨，共用栏距</p><div class=\"fl-grid fl-cols-1 fl-gap-y-0\"><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div></div></div><div><p class=\"fl-caption\">2 轨，共用栏距</p><div class=\"fl-grid fl-cols-2 fl-gap-y-0\"><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div></div></div><div><p class=\"fl-caption\">3 轨，共用栏距</p><div class=\"fl-grid fl-cols-3 fl-gap-y-0\"><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div></div></div><div><p class=\"fl-caption\">4 轨，共用栏距</p><div class=\"fl-grid fl-cols-4 fl-gap-y-0\"><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div></div></div><div><p class=\"fl-caption\">6 轨，共用栏距</p><div class=\"fl-grid fl-cols-6 fl-gap-y-0\"><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div></div></div><div><p class=\"fl-caption\">12 轨，共用栏距</p><div class=\"fl-grid fl-cols-12 fl-gap-y-0\"><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div><div class=\"fl-fill-accent\" style=\"height:28px\" aria-hidden=\"true\"></div></div></div></div>",
      "specimenPage": {
        "id": "a-grid",
        "label": "共同的横向网格"
      }
    },
    {
      "id": "a-span",
      "title": "横向跨度与起点",
      "category": "网格",
      "classes": [
        "fl-span-1",
        "fl-span-2",
        "fl-span-3",
        "fl-span-4",
        "fl-span-5",
        "fl-span-6",
        "fl-span-7",
        "fl-span-8",
        "fl-span-9",
        "fl-span-10",
        "fl-span-11",
        "fl-span-12",
        "fl-span-full",
        "fl-start-1",
        "fl-start-2",
        "fl-start-3",
        "fl-start-4",
        "fl-start-5",
        "fl-start-6",
        "fl-start-7",
        "fl-start-8",
        "fl-start-9",
        "fl-start-10",
        "fl-start-11",
        "fl-start-12"
      ],
      "description": "跨度负责大小，起栏负责位置。二者组合后必须仍落在显式网格内。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-stack fl-gap-3\"><div class=\"fl-grid fl-cols-12 fl-gap-y-1\"><div class=\"fl-start-1 fl-span-1 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨1轨\"></div><div class=\"fl-start-1 fl-span-2 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨2轨\"></div><div class=\"fl-start-1 fl-span-3 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨3轨\"></div><div class=\"fl-start-1 fl-span-4 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨4轨\"></div><div class=\"fl-start-1 fl-span-5 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨5轨\"></div><div class=\"fl-start-1 fl-span-6 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨6轨\"></div><div class=\"fl-start-1 fl-span-7 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨7轨\"></div><div class=\"fl-start-1 fl-span-8 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨8轨\"></div><div class=\"fl-start-1 fl-span-9 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨9轨\"></div><div class=\"fl-start-1 fl-span-10 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨10轨\"></div><div class=\"fl-start-1 fl-span-11 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨11轨\"></div><div class=\"fl-start-1 fl-span-12 fl-fill-accent\" style=\"height:14px\" aria-label=\"跨12轨\"></div></div><div class=\"fl-grid fl-cols-12 fl-gap-y-1\"><div class=\"fl-start-1 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第1轨开始\"></div><div class=\"fl-start-2 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第2轨开始\"></div><div class=\"fl-start-3 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第3轨开始\"></div><div class=\"fl-start-4 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第4轨开始\"></div><div class=\"fl-start-5 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第5轨开始\"></div><div class=\"fl-start-6 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第6轨开始\"></div><div class=\"fl-start-7 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第7轨开始\"></div><div class=\"fl-start-8 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第8轨开始\"></div><div class=\"fl-start-9 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第9轨开始\"></div><div class=\"fl-start-10 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第10轨开始\"></div><div class=\"fl-start-11 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第11轨开始\"></div><div class=\"fl-start-12 fl-span-1 fl-fill-ink\" style=\"height:14px\" aria-label=\"从第12轨开始\"></div></div></div>",
      "specimenPage": {
        "id": "a-span",
        "label": "横向跨度与起点"
      }
    },
    {
      "id": "a-rows",
      "title": "二维模块网格",
      "category": "网格",
      "classes": [
        "fl-rows-2",
        "fl-rows-3",
        "fl-rows-4",
        "fl-rows-6",
        "fl-row-start-1",
        "fl-row-start-2",
        "fl-row-start-3",
        "fl-row-start-4",
        "fl-row-start-5",
        "fl-row-start-6",
        "fl-row-span-1",
        "fl-row-span-2",
        "fl-row-span-3",
        "fl-row-span-4",
        "fl-row-span-5",
        "fl-row-span-6",
        "fl-row-span-full"
      ],
      "description": "有界模块网格先定义高度，再跨行；文字溢出仍可见并接受检查。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-grid fl-cols-2\"><div class=\"fl-grid fl-cols-2 fl-rows-2 fl-gap-1\" style=\"height:180px\"><div class=\"fl-row-span-full fl-fill-accent\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div></div><div class=\"fl-grid fl-cols-2 fl-rows-3 fl-gap-1\" style=\"height:180px\"><div class=\"fl-row-span-full fl-fill-accent\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div></div><div class=\"fl-grid fl-cols-2 fl-rows-4 fl-gap-1\" style=\"height:180px\"><div class=\"fl-row-span-full fl-fill-accent\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div></div><div class=\"fl-grid fl-cols-2 fl-rows-6 fl-gap-1\" style=\"height:180px\"><div class=\"fl-row-span-full fl-fill-accent\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div><div class=\"fl-fill-soft\"></div></div></div><p class=\"fl-caption fl-mt-2\">2 / 3 / 4 / 6 行，照片或内容可以跨行。</p>",
      "specimenPage": {
        "id": "a-rows",
        "label": "二维模块网格"
      }
    },
    {
      "id": "a-flex",
      "title": "流动分组",
      "category": "网格",
      "classes": [
        "fl-flex",
        "fl-flex-col",
        "fl-wrap",
        "fl-grow",
        "fl-shrink-0"
      ],
      "description": "弹性布局连接同层级的短信息，不把所有内容都包装成卡片。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-flex fl-flex-col fl-gap-4\"><div class=\"fl-flex fl-wrap fl-gap-2\"><p class=\"fl-key fl-surface-soft fl-p-2\">观察</p><p class=\"fl-key fl-surface-soft fl-p-2\">记录</p><p class=\"fl-key fl-surface-soft fl-p-2\">比较</p><p class=\"fl-key fl-surface-soft fl-p-2\">提问</p><p class=\"fl-key fl-surface-soft fl-p-2\">复盘</p></div><div class=\"fl-flex fl-gap-3\"><p class=\"fl-number fl-shrink-0\">01</p><p class=\"fl-body fl-grow\">短标签可随空间换行，长正文在其阅读路径中展开。</p></div></div>",
      "specimenPage": {
        "id": "a-flex",
        "label": "流动分组"
      }
    },
    {
      "id": "a-align-items",
      "title": "内容的对齐轴",
      "category": "网格",
      "classes": [
        "fl-items-start",
        "fl-items-center",
        "fl-items-end",
        "fl-items-baseline",
        "fl-items-stretch",
        "fl-self-start",
        "fl-self-center",
        "fl-self-end",
        "fl-self-stretch",
        "fl-justify-start",
        "fl-justify-center",
        "fl-justify-end",
        "fl-justify-between",
        "fl-justify-self-start",
        "fl-justify-self-center",
        "fl-justify-self-end",
        "fl-justify-self-stretch",
        "fl-content-start",
        "fl-content-center",
        "fl-content-end",
        "fl-content-between"
      ],
      "description": "先选Grid/Flex，再选择子项、单项或多轨内容的对齐；align与justify不是同一个轴。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-stack fl-gap-3\"><div class=\"fl-flex fl-items-start fl-justify-between fl-rule fl-pt-2\" style=\"height:84px\"><p class=\"fl-key\">start</p><p class=\"fl-h1\">Aa</p><p class=\"fl-font-number fl-size-h3\">012</p></div><div class=\"fl-flex fl-items-center fl-justify-between fl-rule fl-pt-2\" style=\"height:84px\"><p class=\"fl-key\">center</p><p class=\"fl-h1\">Aa</p><p class=\"fl-font-number fl-size-h3\">012</p></div><div class=\"fl-flex fl-items-end fl-justify-between fl-rule fl-pt-2\" style=\"height:84px\"><p class=\"fl-key\">end</p><p class=\"fl-h1\">Aa</p><p class=\"fl-font-number fl-size-h3\">012</p></div><div class=\"fl-flex fl-items-baseline fl-justify-between fl-rule fl-pt-2\" style=\"height:84px\"><p class=\"fl-key\">baseline</p><p class=\"fl-h1\">Aa</p><p class=\"fl-font-number fl-size-h3\">012</p></div><div class=\"fl-flex fl-items-stretch fl-justify-between fl-rule fl-pt-2\" style=\"height:84px\"><p class=\"fl-key\">stretch</p><p class=\"fl-h1\">Aa</p><p class=\"fl-font-number fl-size-h3\">012</p></div></div>",
      "specimenPage": {
        "id": "a-align-items",
        "label": "内容的对齐轴"
      }
    },
    {
      "id": "a-grid-guide",
      "title": "可见的结构辅助线",
      "category": "网格",
      "classes": [
        "fl-show-columns",
        "fl-show-columns-12",
        "fl-show-baseline"
      ],
      "description": "六/十二轨与基线可以叠加；嵌套辅助层不会把外层网格重复继承。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-show-columns fl-show-baseline\" style=\"height:224px\"><p class=\"fl-h1 fl-span-4\">先建立关系。</p></div><div class=\"fl-show-columns-12 fl-mt-3\" style=\"height:112px\"></div>",
      "specimenPage": {
        "id": "a-grid-guide",
        "label": "可见的结构辅助线"
      }
    },
    {
      "id": "a-gaps",
      "title": "元素间距",
      "category": "节奏",
      "classes": [
        "fl-gap-0",
        "fl-gap-1",
        "fl-gap-2",
        "fl-gap-3",
        "fl-gap-4",
        "fl-gap-5",
        "fl-gap-6",
        "fl-gap-7",
        "fl-gap-8",
        "fl-gap-x-0",
        "fl-gap-x-1",
        "fl-gap-x-2",
        "fl-gap-x-3",
        "fl-gap-x-4",
        "fl-gap-x-5",
        "fl-gap-x-6",
        "fl-gap-x-7",
        "fl-gap-x-8",
        "fl-gap-y-0",
        "fl-gap-y-1",
        "fl-gap-y-2",
        "fl-gap-y-3",
        "fl-gap-y-4",
        "fl-gap-y-5",
        "fl-gap-y-6",
        "fl-gap-y-7",
        "fl-gap-y-8"
      ],
      "description": "gap控制整体间距，x/y分别控制列与行；值来自共同基线。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<table class=\"fl-table\"><thead><tr><th>刻度</th><th>物理尺寸</th><th>相对关系</th></tr></thead><tbody><tr><td class=\"fl-num\">0</td><td class=\"fl-num\">0px</td><td><div class=\"fl-fill-accent\" style=\"width:1px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">1</td><td class=\"fl-num\">7px</td><td><div class=\"fl-fill-accent\" style=\"width:7px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">2</td><td class=\"fl-num\">14px</td><td><div class=\"fl-fill-accent\" style=\"width:14px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">3</td><td class=\"fl-num\">28px</td><td><div class=\"fl-fill-accent\" style=\"width:28px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">4</td><td class=\"fl-num\">42px</td><td><div class=\"fl-fill-accent\" style=\"width:42px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">5</td><td class=\"fl-num\">56px</td><td><div class=\"fl-fill-accent\" style=\"width:56px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">6</td><td class=\"fl-num\">84px</td><td><div class=\"fl-fill-accent\" style=\"width:84px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">7</td><td class=\"fl-num\">112px</td><td><div class=\"fl-fill-accent\" style=\"width:112px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">8</td><td class=\"fl-num\">168px</td><td><div class=\"fl-fill-accent\" style=\"width:168px;height:7px\" aria-hidden=\"true\"></div></td></tr></tbody></table><div class=\"fl-grid fl-cols-2 fl-gap-3 fl-mt-3\"><p class=\"fl-h3\">共同刻度</p><p class=\"fl-body\">在同一套节奏中安排内容。</p></div>",
      "specimenPage": {
        "id": "a-gaps",
        "label": "元素间距"
      }
    },
    {
      "id": "a-padding",
      "title": "容器内留白",
      "category": "节奏",
      "classes": [
        "fl-p-0",
        "fl-p-1",
        "fl-p-2",
        "fl-p-3",
        "fl-p-4",
        "fl-p-5",
        "fl-p-6",
        "fl-p-7",
        "fl-p-8",
        "fl-px-0",
        "fl-px-1",
        "fl-px-2",
        "fl-px-3",
        "fl-px-4",
        "fl-px-5",
        "fl-px-6",
        "fl-px-7",
        "fl-px-8",
        "fl-py-0",
        "fl-py-1",
        "fl-py-2",
        "fl-py-3",
        "fl-py-4",
        "fl-py-5",
        "fl-py-6",
        "fl-py-7",
        "fl-py-8",
        "fl-pt-0",
        "fl-pt-1",
        "fl-pt-2",
        "fl-pt-3",
        "fl-pt-4",
        "fl-pt-5",
        "fl-pt-6",
        "fl-pt-7",
        "fl-pt-8",
        "fl-pb-0",
        "fl-pb-1",
        "fl-pb-2",
        "fl-pb-3",
        "fl-pb-4",
        "fl-pb-5",
        "fl-pb-6",
        "fl-pb-7",
        "fl-pb-8"
      ],
      "description": "内边距用来组织内容与边界的关系，不为每段自动加底色。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<table class=\"fl-table\"><thead><tr><th>刻度</th><th>物理尺寸</th><th>相对关系</th></tr></thead><tbody><tr><td class=\"fl-num\">0</td><td class=\"fl-num\">0px</td><td><div class=\"fl-fill-accent\" style=\"width:1px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">1</td><td class=\"fl-num\">7px</td><td><div class=\"fl-fill-accent\" style=\"width:7px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">2</td><td class=\"fl-num\">14px</td><td><div class=\"fl-fill-accent\" style=\"width:14px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">3</td><td class=\"fl-num\">28px</td><td><div class=\"fl-fill-accent\" style=\"width:28px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">4</td><td class=\"fl-num\">42px</td><td><div class=\"fl-fill-accent\" style=\"width:42px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">5</td><td class=\"fl-num\">56px</td><td><div class=\"fl-fill-accent\" style=\"width:56px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">6</td><td class=\"fl-num\">84px</td><td><div class=\"fl-fill-accent\" style=\"width:84px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">7</td><td class=\"fl-num\">112px</td><td><div class=\"fl-fill-accent\" style=\"width:112px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">8</td><td class=\"fl-num\">168px</td><td><div class=\"fl-fill-accent\" style=\"width:168px;height:7px\" aria-hidden=\"true\"></div></td></tr></tbody></table><div class=\"fl-p-3 fl-surface-soft fl-mt-3\"><p class=\"fl-body\">一条基线的内边距</p></div>",
      "specimenPage": {
        "id": "a-padding",
        "label": "容器内留白"
      }
    },
    {
      "id": "a-margin",
      "title": "段落与章节停顿",
      "category": "节奏",
      "classes": [
        "fl-mt-0",
        "fl-mt-1",
        "fl-mt-2",
        "fl-mt-3",
        "fl-mt-4",
        "fl-mt-5",
        "fl-mt-6",
        "fl-mt-7",
        "fl-mt-8",
        "fl-mb-0",
        "fl-mb-1",
        "fl-mb-2",
        "fl-mb-3",
        "fl-mb-4",
        "fl-mb-5",
        "fl-mb-6",
        "fl-mb-7",
        "fl-mb-8",
        "fl-mt-auto"
      ],
      "description": "上下外边距划分段落与章节，auto用于有剩余高度的纵向布局。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<table class=\"fl-table\"><thead><tr><th>刻度</th><th>物理尺寸</th><th>相对关系</th></tr></thead><tbody><tr><td class=\"fl-num\">0</td><td class=\"fl-num\">0px</td><td><div class=\"fl-fill-accent\" style=\"width:1px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">1</td><td class=\"fl-num\">7px</td><td><div class=\"fl-fill-accent\" style=\"width:7px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">2</td><td class=\"fl-num\">14px</td><td><div class=\"fl-fill-accent\" style=\"width:14px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">3</td><td class=\"fl-num\">28px</td><td><div class=\"fl-fill-accent\" style=\"width:28px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">4</td><td class=\"fl-num\">42px</td><td><div class=\"fl-fill-accent\" style=\"width:42px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">5</td><td class=\"fl-num\">56px</td><td><div class=\"fl-fill-accent\" style=\"width:56px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">6</td><td class=\"fl-num\">84px</td><td><div class=\"fl-fill-accent\" style=\"width:84px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">7</td><td class=\"fl-num\">112px</td><td><div class=\"fl-fill-accent\" style=\"width:112px;height:7px\" aria-hidden=\"true\"></div></td></tr><tr><td class=\"fl-num\">8</td><td class=\"fl-num\">168px</td><td><div class=\"fl-fill-accent\" style=\"width:168px;height:7px\" aria-hidden=\"true\"></div></td></tr></tbody></table><div class=\"fl-flex fl-flex-col fl-mt-3\" style=\"height:112px\"><p class=\"fl-key\">组内紧密</p><p class=\"fl-key fl-mt-auto\">下一组在共同边界结束</p></div>",
      "specimenPage": {
        "id": "a-margin",
        "label": "段落与章节停顿"
      }
    },
    {
      "id": "a-sizing",
      "title": "内容尺寸与剩余空间",
      "category": "版面",
      "classes": [
        "fl-w-full",
        "fl-h-full",
        "fl-min-w-0"
      ],
      "description": "width/height填充已知容器，min-width:0允许Grid/Flex合理收缩；不等于允许裁文字。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-grid fl-cols-2\" style=\"height:280px\"><figure class=\"fl-frame fl-frame-fill fl-w-full fl-h-full\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\"></figure><div class=\"fl-min-w-0 fl-h-full fl-flex fl-flex-col\"><p class=\"fl-h2\">尺寸有边界，<br>内容保持完整。</p><p class=\"fl-body fl-mt-auto\">先定义容器，再填满。长句不能靠隐藏溢出来变短。</p></div></div>",
      "specimenPage": {
        "id": "a-sizing",
        "label": "内容尺寸与剩余空间"
      }
    },
    {
      "id": "a-image",
      "title": "图像比例与原始尺寸",
      "category": "摄影",
      "classes": [
        "fl-image",
        "fl-image-fill",
        "fl-frame",
        "fl-frame-fill",
        "fl-ratio-square",
        "fl-ratio-photo",
        "fl-ratio-wide",
        "fl-ratio-portrait",
        "fl-ratio-tall",
        "fl-ratio-landscape"
      ],
      "description": "图框选择比例；原图不被修改。充满有界图框与保持原始比例是两种任务。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-grid fl-cols-3 fl-items-start\"><figure><div class=\"fl-frame fl-ratio-square\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\"></div><p class=\"fl-caption fl-mt-1\">square</p></figure><figure><div class=\"fl-frame fl-ratio-photo\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\"></div><p class=\"fl-caption fl-mt-1\">photo</p></figure><figure><div class=\"fl-frame fl-ratio-wide\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\"></div><p class=\"fl-caption fl-mt-1\">wide</p></figure><figure><div class=\"fl-frame fl-ratio-portrait\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\"></div><p class=\"fl-caption fl-mt-1\">portrait</p></figure><figure><div class=\"fl-frame fl-ratio-tall\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\"></div><p class=\"fl-caption fl-mt-1\">tall</p></figure><figure><div class=\"fl-frame fl-ratio-landscape\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\"></div><p class=\"fl-caption fl-mt-1\">landscape</p></figure></div>",
      "specimenPage": {
        "id": "a-image",
        "label": "图像比例与原始尺寸"
      }
    },
    {
      "id": "a-crop",
      "title": "裁切焦点与容纳",
      "category": "摄影",
      "classes": [
        "fl-focus-top",
        "fl-focus-bottom",
        "fl-focus-left",
        "fl-focus-right",
        "fl-focus-center",
        "fl-fit-cover",
        "fl-fit-contain",
        "fl-mono"
      ],
      "description": "焦点先看主体位置；contain保全画面，cover填满图框，灰度是显式选择。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-grid fl-cols-3 fl-items-start\"><figure><div class=\"fl-frame fl-ratio-square fl-focus-left\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\"></div><p class=\"fl-caption fl-mt-1\">left</p></figure><figure><div class=\"fl-frame fl-ratio-square fl-focus-center\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\"></div><p class=\"fl-caption fl-mt-1\">center</p></figure><figure><div class=\"fl-frame fl-ratio-square fl-focus-right\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\"></div><p class=\"fl-caption fl-mt-1\">right</p></figure></div><div class=\"fl-grid fl-cols-2 fl-mt-4\"><figure class=\"fl-frame fl-ratio-wide\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"fl-fit-contain\" alt=\"项目已登记授权的自然景观，作排版示意\"></figure><figure class=\"fl-frame fl-ratio-wide\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"fl-fit-cover fl-mono\" alt=\"项目已登记授权的自然景观，作排版示意\"></figure></div>",
      "specimenPage": {
        "id": "a-crop",
        "label": "裁切焦点与容纳"
      }
    },
    {
      "id": "a-scrim",
      "title": "图上文字的对比层",
      "category": "摄影",
      "classes": [
        "fl-scrim-top",
        "fl-scrim-bottom",
        "fl-scrim-start",
        "fl-scrim-end"
      ],
      "description": "遮罩可以帮助局部对比，实际文字必须放在合适区域并检查最终照片。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "遮罩不能自动保证任意照片上的可读性。没有必要时保留客观摄影，文字移出图框。",
      "html": "<div class=\"fl-grid fl-cols-2\"><figure class=\"fl-frame fl-ratio-square fl-relative\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\" data-edit-id=\"scrim-1\"><div class=\"fl-bleed fl-scrim-top\" aria-hidden=\"true\"></div><figcaption class=\"fl-absolute fl-tone-inverse fl-z-1 fl-key\" style=\"left:14px;top:14px\" data-overlap=\"scrim-1\">top</figcaption></figure><figure class=\"fl-frame fl-ratio-square fl-relative\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\" data-edit-id=\"scrim-2\"><div class=\"fl-bleed fl-scrim-bottom\" aria-hidden=\"true\"></div><figcaption class=\"fl-absolute fl-tone-inverse fl-z-1 fl-key\" style=\"left:14px;bottom:14px\" data-overlap=\"scrim-2\">bottom</figcaption></figure><figure class=\"fl-frame fl-ratio-square fl-relative\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\" data-edit-id=\"scrim-3\"><div class=\"fl-bleed fl-scrim-start\" aria-hidden=\"true\"></div><figcaption class=\"fl-absolute fl-tone-inverse fl-z-1 fl-key\" style=\"left:14px;top:14px\" data-overlap=\"scrim-3\">start</figcaption></figure><figure class=\"fl-frame fl-ratio-square fl-relative\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"\" alt=\"项目已登记授权的自然景观，作排版示意\" data-edit-id=\"scrim-4\"><div class=\"fl-bleed fl-scrim-end\" aria-hidden=\"true\"></div><figcaption class=\"fl-absolute fl-tone-inverse fl-z-1 fl-key\" style=\"right:14px;top:14px\" data-overlap=\"scrim-4\">end</figcaption></figure></div>",
      "specimenPage": {
        "id": "a-scrim",
        "label": "图上文字的对比层"
      }
    },
    {
      "id": "a-rules",
      "title": "线与色块的分量",
      "category": "颜色",
      "classes": [
        "fl-rule",
        "fl-rule-strong",
        "fl-rule-heavy",
        "fl-rule-accent",
        "fl-rule-bottom",
        "fl-rule-none",
        "fl-fill-accent",
        "fl-fill-ink",
        "fl-fill-soft"
      ],
      "description": "线用于轴线、分组和计量；色块用于层级与节奏。空色块不是正文容器。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-stack fl-gap-3\"><div class=\"fl-rule fl-pt-2\"><p class=\"fl-key\">fl-rule</p></div><div class=\"fl-rule-strong fl-pt-2\"><p class=\"fl-key\">fl-rule-strong</p></div><div class=\"fl-rule-heavy fl-pt-2\"><p class=\"fl-key\">fl-rule-heavy</p></div><div class=\"fl-rule-accent fl-pt-2\"><p class=\"fl-key\">fl-rule-accent</p></div><div class=\"fl-grid fl-cols-3\"><div class=\"fl-fill-accent\" style=\"height:84px\"></div><div class=\"fl-fill-ink\" style=\"height:84px\"></div><div class=\"fl-fill-soft\" style=\"height:84px\"></div></div></div>",
      "specimenPage": {
        "id": "a-rules",
        "label": "线与色块的分量"
      }
    },
    {
      "id": "a-marks",
      "title": "查阅与书写",
      "category": "版面",
      "classes": [
        "fl-fill-lines",
        "fl-check",
        "fl-running",
        "fl-folio"
      ],
      "description": "书写区与勾选空间服务真实任务；页眉页脚属于阅读定位，不挤压正文。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-l-stack fl-gap-3\"><p class=\"fl-h2\">观察记录</p><p class=\"fl-body\"><span class=\"fl-check\" aria-hidden=\"true\"></span> 已记录可见的形态与位置</p><p class=\"fl-body\"><span class=\"fl-check\" aria-hidden=\"true\"></span> 已为判断注明来源</p><div class=\"fl-fill-lines\" style=\"height:168px\"></div><p class=\"fl-caption\">页眉与页码由fl-running / fl-folio放在物理安全区，页码使用页面计数器。</p></div>",
      "specimenPage": {
        "id": "a-marks",
        "label": "查阅与书写"
      }
    },
    {
      "id": "a-page",
      "title": "页面几何与图层",
      "category": "版面",
      "classes": [
        "fl-scope",
        "fl-area",
        "fl-relative",
        "fl-absolute",
        "fl-bleed",
        "fl-z-0",
        "fl-z-1",
        "fl-z-2"
      ],
      "description": "fl-area负责物理版心；fl-scope限定片段。z类仅在定位/网格堆叠上下文中生效。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "这里是局部图层示意。真实页面几何由运行时生成，不能用示例容器代替@page与安全区。",
      "html": "<div class=\"fl-relative fl-surface-soft\" style=\"height:336px\"><figure class=\"fl-absolute fl-z-0\" style=\"inset:0 42% 0 0\"><img src=\"../samples/native/nature-camp/assets/images/coast-lighthouse.jpg\" class=\"fl-image-fill\" alt=\"项目已登记授权的自然景观，作排版示意\" data-edit-id=\"page-photo\"></figure><div class=\"fl-absolute fl-z-1 fl-surface-paper fl-p-3\" style=\"left:40%;right:28px;top:56px\" data-overlap=\"page-photo\"><p class=\"fl-h2\">图层是关系</p><p class=\"fl-body fl-mt-2\">照片与文字分别组织；重叠须是作者明确的选择。</p></div></div>",
      "specimenPage": {
        "id": "a-page",
        "label": "页面几何与图层"
      }
    },
    {
      "id": "a-direction",
      "title": "竖排与侧向阅读",
      "category": "排印",
      "classes": [
        "fl-vertical",
        "fl-sideways"
      ],
      "description": "明确改变书写方向，仍保留真实文字与DOM顺序。检查字体方向及页面可读性。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-flex fl-gap-5\" style=\"height:336px\"><p class=\"fl-h1 fl-vertical\">秩序与自由</p><p class=\"fl-font-label fl-size-h3 fl-sideways\">FOLIO / FIELD NOTES</p><div class=\"fl-self-end\"><p class=\"fl-body\">方向变化服务书脊、边栏与特定阅读节奏。</p></div></div>",
      "specimenPage": {
        "id": "a-direction",
        "label": "竖排与侧向阅读"
      }
    }
  ],
  "expressions": [
    {
      "id": "x-band",
      "title": "硬边字带与反白",
      "category": "字形",
      "classes": [
        "fl-band",
        "fl-surface-dark",
        "fl-surface-accent",
        "fl-surface-soft"
      ],
      "description": "完整文字落在纯色面上，字带和空间建立强弱关系。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-flex fl-flex-col\"><p class=\"fl-band fl-surface-dark fl-display fl-size-hero fl-w-full fl-flex fl-items-end\" style=\"height:196px\">FOLIO</p><p class=\"fl-band fl-surface-accent fl-h1 fl-w-full fl-flex fl-items-center\" style=\"height:112px\">有序的自由</p><p class=\"fl-band fl-surface-soft fl-h2 fl-w-full fl-flex fl-items-center\" style=\"height:84px\">形体越鲜明</p><p class=\"fl-band fl-surface-dark fl-body fl-w-full fl-flex fl-items-center\" style=\"height:112px\">色带贴住文字本身，只负责分隔与识别，不负责装饰。</p><p class=\"fl-band fl-surface-accent fl-key fl-w-full fl-flex fl-items-center fl-justify-between\" style=\"height:84px\"><span>反白也适用于注释</span><span class=\"fl-font-number\">2.2</span></p></div>",
      "specimenPage": {
        "id": "x-band",
        "label": "硬边字带与反白"
      }
    },
    {
      "id": "x-crop",
      "title": "裁字与页边",
      "category": "字形",
      "classes": [
        "fl-crop",
        "fl-crop-top",
        "fl-crop-bottom",
        "fl-crop-left",
        "fl-crop-right",
        "fl-bleed-right"
      ],
      "description": "裁字只作为重复的图形语言。完整名称保留在可读区域。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "内容标题不能通过裁切、deco或隐藏绕过内容审计。这里的裁框是明确的图形区域。",
      "html": "<div class=\"fl-relative fl-bleed-right fl-surface-accent\" style=\"height:588px;overflow:clip\" data-bleed=\"right\"><div class=\"fl-crop fl-crop-right fl-crop-bottom fl-size-colossal\" style=\"font-size:560px;bottom:-.1em;color:var(--fl-ink)\" data-role=\"deco\" aria-hidden=\"true\">Aa</div><div class=\"fl-surface-paper fl-p-3\" style=\"position:absolute;left:28px;top:28px;max-width:280px\"><p class=\"fl-key\">FOLIO / 形体研究</p><p class=\"fl-caption fl-mt-1\">被切断的字只做重复的图形；完整名称留在这里。</p></div></div>",
      "specimenPage": {
        "id": "x-crop",
        "label": "裁字与页边"
      }
    },
    {
      "id": "x-photo-type",
      "title": "照片进入字形",
      "category": "字形",
      "classes": [
        "fl-type-photo"
      ],
      "description": "文字可以成为图形，但不能让唯一内容丢失可读性。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "填图字仅用于重复装饰。此例用当前纯色色面遮住打印边缘杂线；照片或渐变背景不能照搬该遮边。检查最终PDF与可读副本。",
      "html": "<div class=\"fl-type-bold fl-type-photo fl-size-colossal fl-tracking-tighter\" style=\"background-image:url(../samples/native/nature-camp/assets/images/waterfall-moss.jpg);outline:2px solid var(--fl-bg);outline-offset:-1px\" data-role=\"deco\" aria-hidden=\"true\">山海</div><p class=\"fl-h1 fl-mt-4\">山海 / 字与图像的交汇</p><p class=\"fl-body fl-mt-2 fl-measure\">照片只当字形的材质。可读的标题另写在下方，字形本身不承载唯一信息。</p>",
      "specimenPage": {
        "id": "x-photo-type",
        "label": "照片进入字形"
      }
    },
    {
      "id": "x-duotone",
      "title": "双色摄影与原色",
      "category": "摄影",
      "classes": [
        "fl-duotone",
        "fl-frame-fill"
      ],
      "description": "同一张照片可以表达客观信息，也可以经过明确的色调处理进入视觉叙事。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "CSS乘色是浏览器外观模拟，不是专色分色或印刷叠印参数。",
      "html": "<div class=\"fl-grid fl-cols-2 fl-gap-2\" style=\"height:588px;grid-template-rows:auto 1fr\"><p class=\"fl-key\">原色记录</p><p class=\"fl-key\">双色 / 灰度乘色</p><figure class=\"fl-frame fl-frame-fill\"><img src=\"../samples/native/nature-camp/assets/images/fire-lookout.jpg\" alt=\"已登记的公有领域照片，作排版示意\" data-edit-id=\"duotone-a\"></figure><figure class=\"fl-frame fl-frame-fill fl-duotone\"><img src=\"../samples/native/nature-camp/assets/images/fire-lookout.jpg\" alt=\"已登记的公有领域照片，作排版示意\" data-edit-id=\"duotone-b\"></figure></div>",
      "specimenPage": {
        "id": "x-duotone",
        "label": "双色摄影与原色"
      }
    },
    {
      "id": "x-overprint",
      "title": "交叠与方向",
      "category": "图形",
      "classes": [
        "fl-overprint",
        "fl-rotate-6",
        "fl-rotate-n6",
        "fl-surface-accent"
      ],
      "description": "少量方向变化建立张力；正文与关键信息保持稳定。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "混色不是实际印刷叠印设置。旋转内容可能触发几何unverified，须完成契约要求的审查。",
      "html": "<div class=\"fl-relative\" style=\"height:588px;overflow:clip\"><figure class=\"fl-frame fl-frame-fill\" style=\"position:absolute;inset:0\"><img src=\"../samples/native/nature-camp/assets/images/milky-way-arch.jpg\" alt=\"已登记的公有领域照片，作排版示意\" data-edit-id=\"op-photo\"></figure><div class=\"fl-absolute fl-surface-accent fl-overprint fl-rotate-6\" style=\"left:56px;top:84px;width:56%;height:30%\" data-overlap=\"op-photo\" aria-hidden=\"true\"></div><div class=\"fl-absolute fl-rotate-6 fl-p-3\" style=\"left:56px;top:84px;width:56%\" data-overlap=\"op-photo\"><p class=\"fl-h1 fl-tone-inverse\">偏离轴线，<br>仍然有理由。</p></div><div class=\"fl-absolute fl-surface-paper fl-rotate-n6 fl-p-2\" style=\"left:60%;top:53%;width:36%\" data-overlap=\"op-photo\"><p class=\"fl-key\">不透明色面</p><p class=\"fl-caption fl-mt-1\">同样的角度，不同的材质。</p></div></div>",
      "specimenPage": {
        "id": "x-overprint",
        "label": "交叠与方向"
      }
    },
    {
      "id": "x-programme",
      "title": "规则生成的图形",
      "category": "图形",
      "classes": [
        "fl-programme"
      ],
      "description": "设计生成关系，使图形随规则变化。它表达节奏，不假装是业务数据。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "类清单覆盖该功能组的公开选项；示例展示典型组合。按真实内容、版心与安全区检查，不自动缩字。",
      "html": "<div class=\"fl-programme\" style=\"--fl-programme-cols:6;--fl-programme-gap:7px\" aria-hidden=\"true\" data-role=\"deco\"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div><p class=\"fl-caption fl-mt-3\">30 个单元 / 6 轨：颜色与形状按固定周期变化。它表达节奏，不是数据图。</p>",
      "specimenPage": {
        "id": "x-programme",
        "label": "规则生成的图形"
      }
    },
    {
      "id": "x-sign",
      "title": "导向与路线标识",
      "category": "导向",
      "classes": [
        "fl-sign",
        "fl-bullet"
      ],
      "description": "路线同时使用文字、编号与方向。颜色是帮助识别的线索。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "距离与方向为结构示例。实际导向须核对现场，颜色不能是唯一信息载体。",
      "html": "<div class=\"fl-flex fl-flex-col fl-gap-2\"><div class=\"fl-sign fl-surface-dark\" style=\"height:168px\"><span class=\"fl-bullet fl-font-number fl-size-h2\">1</span><p class=\"fl-display\" style=\"margin-left:28px\">观察站</p><p class=\"fl-key\" style=\"margin-left:auto\">向前 200 m →</p></div><div class=\"fl-sign fl-surface-accent\" style=\"height:168px\"><span class=\"fl-bullet fl-font-number fl-size-h2\">2</span><p class=\"fl-display\" style=\"margin-left:28px\">集合点</p><p class=\"fl-key\" style=\"margin-left:auto\">左转 ←</p></div><div class=\"fl-sign fl-surface-soft\" style=\"height:168px\"><span class=\"fl-bullet fl-font-number fl-size-h2\">3</span><p class=\"fl-display\" style=\"margin-left:28px\">水源</p><p class=\"fl-key\" style=\"margin-left:auto\">直行 80 m ↑</p></div></div><p class=\"fl-caption fl-mt-3\">编号、文字与方向同时出现；颜色只是辅助线索。距离为结构示例，实际导视须核对现场。</p>",
      "specimenPage": {
        "id": "x-sign",
        "label": "导向与路线标识"
      }
    },
    {
      "id": "x-edge",
      "title": "色面抵达纸边",
      "category": "图形",
      "classes": [
        "fl-bleed-left",
        "fl-bleed-right"
      ],
      "description": "延展色面与内部补偿留白同时存在，纸边不等于文字起点。",
      "grammar": "共享 CSS 与普通语义 HTML 组合，数值来自 Folio tokens。",
      "limits": "仅在版心边缘使用，明确data-bleed并检查装订侧；其他padding原子可能覆盖补偿，需要重新检查。",
      "html": "<section class=\"page fl-relative\" style=\"width:568px;height:620px;--bleed:0px;--fl-margin-top:56px;--fl-margin-bottom:56px;--fl-margin-inner:56px;--fl-margin-outer:56px\"><div class=\"fl-area fl-flex fl-flex-col fl-justify-center\" style=\"gap:28px\"><div class=\"fl-bleed-left fl-surface-accent fl-flex fl-items-center fl-py-3\" style=\"height:196px\" data-bleed=\"left\"><p class=\"fl-display\">开放的边界</p></div><p class=\"fl-body\">内容守在版心，色面向外展开；纸边不等于文字起点。</p><div class=\"fl-bleed-right fl-surface-dark fl-flex fl-items-center fl-py-3\" style=\"height:196px;padding-left:28px\" data-bleed=\"right\"><p class=\"fl-display\">完整的内容</p></div></div></section>",
      "specimenPage": {
        "id": "x-edge",
        "label": "色面抵达纸边"
      }
    }
  ],
  "coverage": {
    "classes": 353,
    "entries": 91
  }
};
