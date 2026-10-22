"""当前维护四种视觉风格。布局共用 canon / flow，字体角色与字重策略由同一引擎实现。"""
STYLES = {
    'photo': dict(
        zh='Photo · 国家地理纪实杂志：满版出血摄影、渐融纸面过渡、传奇黄框眉标、高对比衬线标题与黑体正文',
        edge='soft', tone='dark', fonts='magazine', mode='accent',
        colors=dict(G='#22306E', OCH='#3F7062', GOLD='#F2C14E', INK='#151B2E', MUT='#5A6275', PAPER='#F4F1EA'),
        css='',
        ccss=('.st-photo .cn-qt{font-style:italic}'
              '.st-photo .cn-h{font-weight:700}'
              '.st-photo .cn-lab{letter-spacing:.22em;display:inline-flex;align-items:center;gap:8px}'
              '.st-photo .cn-lab::before{content:"";display:inline-block;width:9px;height:14px;border:2.5px solid #F2C14E;flex-shrink:0}'
              '.st-photo .cn-ed-rule-strong{height:3px;background:linear-gradient(90deg,#F2C14E 0 72px,var(--hd) 72px 100%)}'
              '.st-photo .cn-ed-rule-accent{height:4px;width:72px;background:#F2C14E}'
              '.st-photo .cn-ed-note{background:linear-gradient(#F2C14E,#F2C14E) top left/48px 3px no-repeat;padding-top:calc(.75 * var(--lh))}'
              '.st-photo .cn-q{border-left:4px solid #F2C14E;padding-left:20px}'
              '.st-photo .cn-fo{border-top:1px solid var(--line);padding-top:4px}'
              '.st-photo .page.sf-image::after{content:"";position:absolute;left:50px;top:0;width:56px;height:6px;background:#F2C14E;z-index:5;pointer-events:none}')),
    'swiss': dict(
        zh='Swiss Minimal · 瑞士极简：中性纸面、一个强调色、无衬线、大字轻小字稳',
        edge='hard', tone='dark', fonts='swiss', mode='mono',
        colors=dict(G='#A32F25', OCH='#A32F25', GOLD='#FFFFFF', INK='#151515', MUT='#50504D', PAPER='#FAFAF8', TINT='#F0F0EE'),
        css='',
        ccss=('.st-swiss .cn-tx{text-align:left}.st-swiss .cn-lab{letter-spacing:.12em}'
              '.st-swiss .cn-disp,.st-swiss .cn-num{font-weight:200;letter-spacing:-.025em}'
              '.st-swiss .cn-h,.st-swiss .cn-sub,.st-swiss .cn-qt{font-weight:300;font-style:normal}'
              '.st-swiss .cn-cap,.st-swiss .cn-fo{font-family:var(--f-label);letter-spacing:.06em}'
              '.st-swiss .cn-top2{background:linear-gradient(var(--rule),var(--rule)) top/100% 1px no-repeat}'
              '.st-swiss .cn-fo{background:linear-gradient(var(--line),var(--line)) top/100% 1px no-repeat}'
              '.st-swiss .page{font-synthesis:none}')),
    'editorial': dict(
        zh='Editorial · 克制的书卷感：宋体标题与正文、黑体功能标签、短简报三栏、细线与中小幅图片',
        edge='hard', tone='dark', fonts='serif', mode='accent',
        colors=dict(G='#292720', OCH='#625B4D', GOLD='#D8D0BA', INK='#292720', MUT='#514E46', PAPER='#FDFCF3'),
        css='',
        ccss=('.st-editorial .cn-lab{letter-spacing:.12em}'
              '.st-editorial .cn-top2{background:linear-gradient(var(--rule),var(--rule)) top/100% 1px no-repeat}'
              '.st-editorial .cn-fo{background:linear-gradient(var(--line),var(--line)) top/100% 1px no-repeat}'
              '.st-editorial .cn-q{border-left-width:1px}.st-editorial .cn-ed-note{background-size:100% 1px}'
              '.st-editorial .cn-h{font-weight:600}.st-editorial .cn-h.cn-ttl{font-weight:700}')),
}

# 保留有明确图形语法的风格派；与 Swiss Minimal 分别维护。
STYLES.update({'stijl': {'edge': 'hard',
           'zh': '风格派（蒙德里安）：先分空间、再放内容、最后上颜色。线有层级——主结构（标题区、图与字、页脚）一两条粗线、条目之间细线、其余靠对齐；颜色就是粗线围出的格子，按角色：红 = '
                 '主角区、蓝 = 图片区 / 窄条、黄 = 页码日期小格。封面、封底、章节页是一整幅构成，阅读页只有两三条主线和几小格颜色。三种画法 book.look：classic 粗黑线 + '
                 '三原色大格子 / tone 无线（细线 + 深浅灰）/ beat 节奏（Grid + '
                 'Rhythm：线细，大色块缩成小色块，切口页边一列跟着条目走的节拍）。照片转黑白。适合展览、品牌画册、机构介绍、年度回顾',
           'tone': 'light',
           'fonts': 'magazine',
           'mode': 'mono',
           'colors': {'G': '#D7261E',
                      'GOLD': '#F2C318',
                      'OCH': '#1F4C9C',
                      'C': '#1F4C9C',
                      'INK': '#141414',
                      'MUT': '#55524C',
                      'PAPER': '#F3EFE6'},
           'ccss': '.st-stijl .cn-tx{text-align:left}.st-stijl .cn-lab{letter-spacing:.2em}.st-stijl '
                   '.cn-top2{background:linear-gradient(var(--rule),var(--rule)) top/100% 1px '
                   'no-repeat}.st-stijl .cn-ino{position:relative}.st-stijl '
                   '.cn-ino::after{content:"";position:absolute;left:0;bottom:0;width:40px;height:5px;background:var(--bar,transparent)}.sj-blk,.sj-line,.sj-tick,.sj-rail{position:absolute;display:block;pointer-events:none}.sj-blk{z-index:1}.sj-line{z-index:3}.sj-tick{z-index:4}.sj-rail{z-index:3}.sj-rule{z-index:3}.sj-railbox{pointer-events:none}.sj-pn{position:absolute;z-index:4;display:flex;align-items:center;justify-content:center;font-family:var(--f-title);font-weight:700;font-size:calc(20px '
                   '* var(--s));font-feature-settings:"lnum" '
                   '1;color:var(--ink,#141414)}.sj-pn.sj-pnb{font-size:calc(34px * '
                   'var(--s));letter-spacing:.01em}.st-stijl '
                   '.sj-ix{font-size:260px;line-height:.86;margin:12px 0 '
                   '28px;letter-spacing:-.02em}.st-stijl .cn-field{z-index:0}.st-stijl '
                   '.cn-st{z-index:2}.st-stijl .cn-fo{z-index:2}',
           'css': ''}})
