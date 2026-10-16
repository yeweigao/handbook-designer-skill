"""视觉风格（book.style）。借鉴 ppt-master 的分层：风格只管“长什么样”（形状语言、装饰、留白、质感、字体性格），
配色（book.colors）与字体（book.fonts）是独立的旋钮——风格给默认值，用户可以分别覆盖。

photo 是默认的“国家地理式”照片风格；其余 7 种是无图模式：照片位置换成按风格生成的底图（art.py），
也可以和真实照片混用（写了 image 的页仍用照片）。
tone：底图明暗。dark → 底图上用白字；light → 底图上用深色字。
edge：底图与纸面的交界。hard = 画面自己决定边界、纸面完全不透明（平面图形风格，避免半透明混出脏色）；soft = 照片式渐隐（照片、水墨的雾、弥散渐变）。
css：该风格的装饰语法，{G}{INK}… 会替换成配色。
"""
STYLES = {
  'photo': dict(edge='soft',
    zh='纪实摄影杂志（默认）：满版照片 + 图上压字 + 半透明纸面',
    tone='dark', fonts='magazine', colors={},
    css=''),
  'editorial': dict(edge='hard',
    zh='杂志排版：深色纸底 + 发丝分栏线，衬线大标题、首字下沉、小标签上方细线。适合家长手册、年度回顾、报告式手册',
    tone='dark', fonts='magazine',
    colors=dict(G='#1F3A5F', OCH='#8A5A12', GOLD='#F2C14E', INK='#16202B', MUT='#3E4A56', PAPER='#FBFAF7'),
    css=('.ink .kk,.ink .k{border-top:.8px solid {INK};padding-top:7px;width:100%}'
         '.ink .hd0 .sf{padding-bottom:10px;border-bottom:.8px solid {INK}}'
         '.ink .lt p:first-child::first-letter{float:left;font-family:var(--f-title);font-weight:900;font-size:3.1em;line-height:.92;margin:4px 8px 0 0;color:{G}}'
         '.ln,.fd i,.rl{border-bottom-width:.6px}')),
  'swiss': dict(edge='hard',
    zh='瑞士网格：大色块 + 巨型几何形，无衬线、强对比、零装饰。适合入职手册、会议指南、机构介绍',
    tone='dark', fonts='sans',
    colors=dict(G='#C8102E', OCH='#141414', GOLD='#FFFFFF', INK='#141414', MUT='#4A4A4A', PAPER='#FFFFFF'),
    css=('.nu{font-style:normal;font-weight:900}.ink .kk{font-weight:800;color:{INK}}'
         '.ink .hd0 .sf{letter-spacing:.02em}.bx{border:1.4px solid {INK}}.ln,.fd i,.rl{border-bottom:1px solid {INK}}'
         '.ink .kk::before{content:"";display:inline-block;width:10px;height:10px;background:{G};margin-right:9px;vertical-align:-1px}')),
  'notebook': dict(edge='soft',
    zh='手账笔记：点阵纸 + 马卡龙色块 + 手绘涂鸦，手写字体、虚线书写行、荧光笔小标签。适合学生任务册、营地手册、亲子手册',
    tone='light', fonts='hand',
    colors=dict(G='#2E6E8E', OCH='#B5562B', GOLD='#F2B84B', INK='#2B2B2B', MUT='#555555', PAPER='#FFFDF6'),
    css=('.page.paper{background-image:linear-gradient({G}21 1px,transparent 1px),linear-gradient(90deg,{G}21 1px,transparent 1px),linear-gradient({G}1F 1px,transparent 1px),linear-gradient(90deg,{G}1F 1px,transparent 1px);background-size:20px 20px,20px 20px,100px 100px,100px 100px;background-position:-1px -1px}'
         '.ln,.fd i{border-bottom:1.2px dashed #9AA5AB}.rl{border-bottom:1.2px dashed #9AA5AB}'
         '.bx{border:1.6px solid {INK};border-radius:12px}'
         '.ink .kk{background:linear-gradient(transparent 52%,{GOLD}99 52%,{GOLD}99 92%,transparent 92%);width:fit-content;padding:0 6px;color:{INK}}'
         '.nu{font-weight:700}')),
  'inkwash': dict(edge='soft',
    zh='新中式水墨：宣纸底 + 层叠远山 + 一方朱印，毛笔标题、细线、印章红点缀。适合传统文化研学、国学、非遗、书院',
    tone='light', fonts={'preset': 'serif', 'title': ['eb-garamond', 'ma-shan-zheng', 'noto-serif-sc'], 'css': {'title_w': 400}},
    colors=dict(G='#2F3B36', OCH='#9E2A2B', GOLD='#9E2A2B', INK='#1E1E1E', MUT='#5A5A55', PAPER='#F6F1E7'),
    css=('.ink .kk{color:{OCH}}.ink .kk::before{content:"";display:inline-block;width:8px;height:8px;background:{OCH};margin-right:9px;vertical-align:0}'
         '.ln,.fd i,.rl{border-bottom:.6px solid #B9B2A3}.bx{border:.6px solid #9C9585}'
         '.nu{font-style:normal}')),
  'papercut': dict(edge='hard',
    zh='剪纸拼贴：层叠波浪纸片 + 纸太阳 + 柔和投影，圆角卡片、胶囊标签、童趣标题。适合幼儿园、亲子活动、节日、低年级',
    tone='light', fonts={'preset': 'hand', 'title': ['caveat', 'lxgw-marker-gothic', 'lxgw-wenkai']},
    colors=dict(G='#245A4E', OCH='#A3441D', GOLD='#F4B942', INK='#24302C', MUT='#4E5A55', PAPER='#FFF9F0'),
    css=('.bx{border:none;background:#FFFFFF;border-radius:16px;box-shadow:0 1px 0 rgba(0,0,0,.05),0 6px 16px rgba(60,40,10,.12)}'
         '.ink .kk{background:{G};color:#FFFFFF;border-radius:99px;padding:3px 12px 2px;width:fit-content}'
         '.ln,.fd i,.rl{border-bottom:1.2px solid #D9CBB5}')),
  'riso': dict(edge='hard',
    zh='复古印刷（Risograph）：暖纸 + 半调网点 + 色带 + 套色错位，海报式粗标题、盖章式标签。适合营地、文创、社团活动、展览',
    tone='light', fonts={'preset': 'sans', 'title': ['oswald', 'smiley-sans', 'noto-sans-sc']},
    colors=dict(G='#1F4E9C', OCH='#A32E1A', GOLD='#F7B32B', INK='#1C1C1C', MUT='#4A4A4A', PAPER='#F6F0E3'),
    css=('.ink .disp,.ink .hd0 .sf{text-shadow:2px 2px 0 {GOLD}B3}'
         '.ink .kk{border:1.4px solid currentColor;padding:2px 7px 1px;width:fit-content;color:{OCH}}'
         '.bx{border:1.4px solid {INK}}.ln,.fd i,.rl{border-bottom:1px solid #8C8579}.nu{font-style:normal}')),
  'aurora': dict(edge='soft',
    zh='弥散玻璃（Aurora / Glassmorphism）：柔和弥散渐变 + 柔光 + 磨砂玻璃卡片与胶囊标签，细白描边、当代无衬线。适合科技/互联网公司入职手册、产品与活动指南、设计营、年轻化品牌',
    tone='light', fonts={'preset': 'sans', 'title': ['geist', 'noto-sans-sc'], 'body': ['geist', 'lxgw-neo-xihei', 'noto-sans-sc'],
                         'label': ['geist', 'lxgw-neo-xihei', 'noto-sans-sc'], 'accent': ['geist', 'noto-sans-sc'],
                         'css': {'title_w': 500, 'accent_w': 500, 'label_track': '.16em'}},
    colors=dict(G='#0B5CAD', OCH='#8A4B0F', GOLD='#FFE0AE', INK='#111827', MUT='#4B5563', PAPER='#F3F7FF'),
    css=('.page.paper{background-image:radial-gradient(75% 45% at 92% 0%,{GOLD}AA,transparent 70%),radial-gradient(85% 55% at 0% 100%,{G}26,transparent 70%)}'
         '.bx{border:1px solid rgba(255,255,255,.95);background:rgba(255,255,255,.55);border-radius:18px;box-shadow:0 10px 28px rgba(30,60,110,.08),inset 0 1px 0 #FFFFFF}'
         '.ink .kk{background:rgba(255,255,255,.66);border:1px solid rgba(255,255,255,.98);border-radius:99px;padding:3px 12px 2px;width:fit-content;color:{G};box-shadow:0 4px 12px rgba(30,60,110,.08)}'
         '.ln,.fd i,.rl{border-bottom:1px solid rgba(17,24,39,.2)}.nu{font-style:normal;font-weight:500}')),
  'nebula': dict(edge='hard',
    zh='深色星云（科技品牌）：深墨夜色 + 紫色弥散光 + 粒子星点 + 细轨道环；纸面是淡色弥散光。玻璃卡片、渐变小标签、圆润几何西文。适合 AI / 科技公司产品手册、发布会、投资人材料',
    tone='dark', fonts={'preset': 'sans', 'title': ['comfortaa', 'lxgw-neo-xihei', 'noto-sans-sc'], 'body': ['comfortaa', 'lxgw-neo-xihei', 'noto-sans-sc'],
                        'label': ['comfortaa', 'lxgw-neo-xihei', 'noto-sans-sc'], 'accent': ['comfortaa', 'lxgw-neo-xihei', 'noto-sans-sc'],
                        'css': {'title_w': 400, 'accent_w': 500, 'accent_style': 'normal', 'label_case': 'none', 'label_track': '.12em', 'label_scale': 1.05}},
    colors=dict(G='#4B3BFF', OCH='#7A2FE0', GOLD='#C6B8FF', INK='#1A1040', MUT='#4B4372', PAPER='#F4F1FF'),
    css=('.page.paper{background-image:radial-gradient(70% 45% at 100% 0%,{OCH}1F,transparent 70%),radial-gradient(60% 40% at 0% 100%,{G}17,transparent 70%)}'
         '.kk{display:flex;align-items:center;gap:8px}.kk::before{content:"";flex:0 0 18px;height:1.5px;background:linear-gradient(90deg,{G},{OCH})}'
         '.ph .kk{color:{GOLD}!important}.ph .kk::before{background:linear-gradient(90deg,{GOLD},#fff)}'
         '.cd{border-top:none;background:#fff;border:1px solid {G}14;border-radius:16px;padding:15px 17px;box-shadow:0 10px 28px {G}12}'
         '.cdt{color:{INK}!important;font-weight:400!important;font-size:16px}.cdn{background:linear-gradient(90deg,{G},{OCH});-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:{G}!important}'
         '.ph .cdn{background:linear-gradient(90deg,{GOLD},#fff);-webkit-background-clip:text;background-clip:text;color:{GOLD}!important}'
         '.ph .cd{background:rgba(14,8,40,.42);border:1px solid rgba(255,255,255,.16);box-shadow:none}.ph .cdt{color:#fff!important}.ph .cdx{color:rgba(255,255,255,.82)}'
         '.st{border-top:1px solid {G}26}.stn{font-family:var(--f-accent);font-weight:400}.ph .st{border-color:rgba(255,255,255,.22)}.ph .stn{color:#fff!important}'
         '.fgi{border-radius:16px}.bx{border:1px solid {G}26;border-radius:16px}.ln,.fd i,.rl{border-bottom:1px solid {G}26}'
         '.nu{font-style:normal}.qm{font-family:var(--f-accent)}')),
}

# 新内容块（figure / stats / quote / cards）在各风格里的样子：同一套语言的延伸
for _k, _c in {
    'swiss': '.cd{border-top:4px solid {G}}.stn{font-weight:900}.st{border-top:2px solid {INK}}',
    'notebook': '.fgi{border:7px solid #fff;box-shadow:0 3px 10px rgba(40,40,40,.14)}.cd{border-top:1.6px dashed {G}}.st{border-top:1.6px dashed {G}}',
    'inkwash': '.cd,.st{border-top:.6px solid {INK}}.fgi{border:.6px solid #B9B2A3;padding:5px;background:#FBF8F1}',
    'papercut': '.cd{border-top:none;background:#fff;border-radius:16px;padding:14px 16px;box-shadow:0 1px 0 rgba(0,0,0,.04),0 6px 16px rgba(60,40,10,.10)}.fgi{border-radius:16px}',
    'riso': '.cd{border-top:3px solid {OCH}}.st{border-top:1.4px solid {INK}}',
    'aurora': '.cd{border-top:none;background:rgba(255,255,255,.55);border:1px solid rgba(255,255,255,.95);border-radius:16px;padding:14px 16px;box-shadow:0 10px 26px rgba(30,60,110,.07)}'
              '.fgi{border-radius:18px}.st{border-top-color:{G}33}',
}.items(): STYLES[_k]['css'] += _c
