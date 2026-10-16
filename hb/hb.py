#!/usr/bin/env python3
"""hb.py — 数据驱动的手册排版器。  用法:  python3 hb.py <project_dir>
读 <project_dir>/book.yaml → 烘焙图片(纸面 wash) → 写 book.html + map.json + plan.txt。
你（agent）只需要写 book.yaml；坐标、遮罩、跨页拼接、页码都由本程序计算。
页面固定为 A4 竖版（794×1123 CSS px）。
"""
import math, sys, os, re, json, shutil, html as _h, yaml
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import wash, art, fonts as FONTS_
from styles import STYLES
import palettes as PAL
MX=56   # 页边距（出血图片用）
W,H=794,1123; M0=56; LH=32
ERR=[]; WARN=[]
SAFE=re.compile(r'&lt;(/?)(b|strong|i|em|u|br|sup|sub|small)\s*/?&gt;',re.I)
def esc(s):   # 文案一律 HTML 转义，只放行不带属性的 <b> <strong> <i> <em> <u> <br> <sup> <sub> <small>；需要任意 HTML 用 {html: ...} 块
    return SAFE.sub(lambda m:f'<{m.group(1)}{m.group(2).lower()}>',_h.escape(str(s)))
DECO=' data-deco="1"'   # 标记“允许新增的装饰/提示文字”（页眉、页脚、图注、小标签、填写提示），原文核对的 EXTRA 会跳过它们
# ---------------------------------------------------------------- config
PROJ=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else '.')
try: SPEC=yaml.safe_load(open(os.path.join(PROJ,'book.yaml'),encoding='utf-8'))
except yaml.YAMLError as e:
    m=getattr(e,'problem_mark',None)
    sys.exit(f"ERROR: book.yaml 语法错误{f'（第 {m.line+1} 行第 {m.column+1} 列附近）' if m else ''}：{getattr(e,'problem',e)}\n"
             "  常见原因：花括号 {...} 里的文字含有 : , ? # [ ] { } 或以引号开头 → 给整段文字加单引号，如 {p: '时间：上午 9:00'}")
BK=SPEC.get('book',{})
SRC=os.path.join(PROJ,BK.get('photos','photos'))
STYLE=str(BK.get('style','photo'))
PURPOSE=str(BK.get('purpose','workbook'))   # workbook 任务册（有书写区）/ guide 指南须知（以阅读为主）/ brochure 宣传册（不要书写区）
if PURPOSE not in ('workbook','guide','brochure'): sys.exit(f'ERROR: book.purpose 可选 workbook / guide / brochure，当前 {PURPOSE}')
if STYLE not in STYLES: sys.exit(f'ERROR: 未知 style {STYLE}，可选 {list(STYLES)}')
SD=STYLES[STYLE]
TH_=dict(INK='#17211C',G='#1D5A43',MUT='#3F4A44',GOLD='#F2C14E',OCH='#7E560E',PAPER='#FBFAF7'); TH_.update(SD['colors']); TH_=PAL.resolve(BK.get('colors'),TH_)
INK,G,MUT,GOLD,OCH,PAPER=[TH_[k] for k in ('INK','G','MUT','GOLD','OCH','PAPER')]
FOLIO=BK.get('folio',BK.get('title',''))
wash.PAPERC=wash.np.array([int(PAPER.lstrip('#')[i:i+2],16) for i in (0,2,4)],wash.np.float32)   # 照片融合色 = 纸色
os.makedirs(os.path.join(PROJ,'img'),exist_ok=True)
wash.A=BK.get('paper',0.9)   # 纸面不透明度：0.86 通透 … 0.94 更易读（照片繁杂时调高）
wash.S=BK.get('scale',2)     # 图片烘焙倍率：2≈190dpi（屏幕/打样），3≈290dpi（交印刷厂）
LANG=str(BK.get('lang','zh')); CJK=LANG.split('-')[0].lower() in ('zh','ja','ko')
FROLES_PRE=FONTS_.resolve(BK.get('fonts',SD['fonts']),CJK)[0]   # 描边大字转路径时要用到标题字体
def sp(v): return v if CJK else round(float(v)*0.15,3)   # 西文不需要中文那样的宽字距
COLON='：' if CJK else ': '
def lab(s): return esc(str(s).rstrip('：: '))+COLON   # 标签后自动加冒号（原文已带冒号也不会重复）
# ---------------------------------------------------------------- image baking
IMGS={}; LOCAL=[]; CLIP={}; FLAT=[]
def src(p,f):
    s=os.path.join(SRC,f)
    if not os.path.exists(s): ERR.append(f'p{p}: 找不到图片 {s}'); return None
    return s
def is_art(f): return f in (None,'','art') or str(f).startswith(('placeholder','ai:'))
# ---- AI 配图位：image / figure 写 ai:编号；photos/ai_编号.(png|jpg|webp) 出现后自动替换。构建后 brief.py 按实际尺寸与文字落点生成 image_brief.md
AISLOTS=[]
def ai_file(f):
    k=str(f)[3:].strip()
    for e in ('png','jpg','jpeg','webp'):
        if os.path.exists(os.path.join(SRC,f'ai_{k}.{e}')): return f'ai_{k}.{e}'
    return None
def ai_font(px):
    from PIL import ImageFont
    p=FONTS_.path_of('lxgw-neo-xihei') or FONTS_.path_of('noto-sans-sc')
    try: return ImageFont.truetype(p,px) if p else ImageFont.load_default()
    except Exception: return ImageFont.load_default()
def ai_label(im,k,box,size_txt):
    """在占位图上画虚线框 + 图位编号 + 需要的尺寸（只出现在占位阶段）"""
    from PIL import ImageDraw
    d=ImageDraw.Draw(im); W_,H_=im.size; x0,y0,x1,y1=[int(v) for v in (box[0]*W_+24,box[1]*H_+24,box[2]*W_-24,box[3]*H_-24)]
    for i in range(x0,x1,28): d.line([(i,y0),(min(i+14,x1),y0)],fill=(255,255,255),width=3); d.line([(i,y1),(min(i+14,x1),y1)],fill=(255,255,255),width=3)
    for j in range(y0,y1,28): d.line([(x0,j),(x0,min(j+14,y1))],fill=(255,255,255),width=3); d.line([(x1,j),(x1,min(j+14,y1))],fill=(255,255,255),width=3)
    f1,f2=ai_font(max(28,W_//40)),ai_font(max(20,W_//60)); tx,ty=(x0+x1)//2,(y0+y1)//2
    d.text((tx,ty),f'AI 配图 · {k}',fill=(255,255,255),font=f1,anchor='mm'); d.text((tx,ty+max(40,W_//30)),size_txt,fill=(235,235,255),font=f2,anchor='mm')
    return im
def plate(n,f,w,box=(0,0,1,1)):
    """无图模式：按风格生成底图（photo 风格下 = 深色占位图）。同一页同一尺寸只生成一次。"""
    import hashlib
    key=hashlib.md5(repr((STYLE,sorted(TH_.items()),box,os.path.getmtime(art.__file__),str(f) if str(f).startswith('ai:') else '')).encode()).hexdigest()[:8]
    d=os.path.join(PROJ,'.art'); os.makedirs(d,exist_ok=True); out=os.path.join(d,f'{STYLE}_{n:02d}_{w}_{key}.jpg')
    if not os.path.exists(out):
        for old in os.listdir(d):
            if old.startswith(f'{STYLE}_{n:02d}_{w}_'): os.remove(os.path.join(d,old))
        im=art.make(STYLE,w*2,H*2,n*7+3,TH_,box)
        if str(f).startswith('ai:'): im=ai_label(im,str(f)[3:],box,f'电子版 ≥ {w*2}×{H*2}px · 印刷 ≥ {round(w*3.125)}×{round(H*3.125)}px')
        im.save(out,quality=92)
    return out
def placeholder(n,f,w):
    """没有照片时的占位底图：主题色的深色渐变 + 一团柔光（GOLD）+ 细噪点。版式、压暗、QA 照常工作，之后换成照片即可。"""
    import numpy as np
    from PIL import Image
    d=os.path.join(PROJ,'.placeholder'); os.makedirs(d,exist_ok=True); out=os.path.join(d,f'{f}_{n}_{w}.jpg')
    if os.path.exists(out): return out
    hx=lambda c:np.array([int(c.lstrip('#')[i:i+2],16) for i in (0,2,4)],np.float32)
    rng=np.random.default_rng(n*7+len(f)); PW,PH=w*2,H*2
    y,x=np.mgrid[0:PH,0:PW].astype(np.float32); base=hx(G)*0.45; top=hx(G)*0.75+hx(INK)*0.1
    t=(y/PH)[...,None]; img=top*(1-t)+base*t
    cx,cy=rng.uniform(.25,.75)*PW,rng.uniform(.3,.7)*PH; r=np.exp(-(((x-cx)/(PW*.35))**2+((y-cy)/(PH*.3))**2))[...,None]
    img=img*(1-.35*r)+hx(GOLD)*.35*r
    img+=rng.normal(0,4,img.shape[:2])[...,None]
    Image.fromarray(img.clip(0,255).astype(np.uint8)).save(out,quality=90); return out
def bake(n,name,f,w,mask,focus,target,zoom,kind,local,box=(0,0,1,1)):
    if str(f).startswith('ai:'):   # AI 配图位：有成图就当照片用，没有就画占位
        fn=ai_file(f); AISLOTS.append(dict(id=str(f)[3:].strip(),page=n,where='版式图片',img=name,css=[w,H],box=list(box),done=fn))
        if fn: f=fn
    s=plate(n,f,w,box) if is_art(f) else src(n,f)
    if not s: return
    if not is_art(f):   # 清晰度：按铺满后的缩放估算印出来的 dpi
        from PIL import Image as _I
        iw,ih=_I.open(s).size; dpi=96/(max((w+4)/iw,(H+2)/ih)*zoom)
        if dpi<96: WARN.append(f'第{n}页：{f} 只有 {iw}×{ih}px，放在这里约 {dpi:.0f}dpi，满版会糊 → 换更大的原图，或放进 figure 插图块')
        elif dpi<130: WARN.append(f'第{n}页：{f}（{iw}×{ih}px）放在这里约 {dpi:.0f}dpi：电子版没问题，印刷会偏软')
    if is_art(f):   # 底图按 box 精确构图：不缩放、不裁切
        zoom,focus,target=1.0,(.5,.5),(w/2,H/2)
        if SD.get('edge')=='hard':   # 平面风格：纸面完全不透明、硬边（在原淡出带的末端切开），不和画面半透明混色
            m0=mask; mask=lambda X,Y,m0=m0: wash.ss(.966,.974,m0(X,Y)/max(wash.A,1e-6)); FLAT.append(name)
    wash.bake2(s,os.path.join(PROJ,'img',name.replace('.jpg','_base.jpg')),w,H,tuple(focus),tuple(target),zoom,mask)
    IMGS[name]=kind
    if local: LOCAL.append(name)
def IMGTAG(name,x=-2,w=W+4): return f'<img class="a" alt="" src="img/{name}" style="left:{x}px;top:-1px;width:{w}px;height:{H+2}px">'
# ---------------------------------------------------------------- blocks  (每个 block 是一个 dict，第一个已知键决定类型)
def num(i,c=None,s=20): return f'<span class="nu" style="font-size:{s}px;color:{c or G}">{int(i):02d}</span>' if str(i).isdigit() else f'<span class="nu" style="font-size:{s}px;color:{c or G}">{i}</span>'
def LN(n): return '<div class="ln"></div>'*int(n)
def FD(l,size=None):
    st=f' style="font-size:{size}px"' if size else ''
    return f'<div class="fd"{st}><span{DECO}>{esc(l)}</span><i></i></div>'
def ROW(items,cols=None): return f'<div class="row" style="grid-template-columns:{cols or " ".join(["1fr"]*len(items))}">{"".join(items)}</div>'
def GT(b,ph,html):   # 渐变标题（可选）：块里 gradient 优先；否则用 book.gradient（只用在适合的底色上）
    spec=b.get('gradient',None)
    if spec is None:
        spec=BK.get('gradient')
        if isinstance(spec,str) and spec in PAL.GRADIENTS and (PAL.GRADIENTS[spec]['on']=='dark')!=bool(ph): spec=None
    r=PAL.gradient(spec,TH_,bool(ph))
    if not r: return html
    return f'<span class="gt" style="background-image:{r[0]};-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;-webkit-box-decoration-break:clone;box-decoration-break:clone;text-shadow:none;color:{r[1]}">{html}</span>'
CURN=1
def FIGIMG(f,need):
    """插图：从 photos 复制到 img/（超过 2400px 的缩小；PNG 透明保留），并按显示宽度检查清晰度。"""
    import hashlib
    from PIL import Image as _I
    s=os.path.join(SRC,str(f))
    if not os.path.exists(s): ERR.append(f'第{CURN}页: 找不到图片 {s}'); return ''
    if str(f).lower().endswith('.svg'):   # 矢量（logo 等）原样嵌入，PDF 里仍是矢量
        name='fig_'+hashlib.md5((str(f)+str(os.path.getmtime(s))).encode()).hexdigest()[:10]+'.svg'; shutil.copy(s,os.path.join(PROJ,'img',name)); return 'img/'+name
    im=_I.open(s); iw,ih=im.size
    if iw<need*1.0: WARN.append(f'第{CURN}页：插图 {f} 只有 {iw}px 宽，显示约 {need:.0f}px 宽，印出来约 {96*iw/need:.0f}dpi（偏软）')
    png=im.mode in ('RGBA','LA','P') or str(f).lower().endswith('.png')
    name='fig_'+hashlib.md5((str(f)+str(os.path.getmtime(s))).encode()).hexdigest()[:10]+('.png' if png else '.jpg'); out=os.path.join(PROJ,'img',name)
    if not os.path.exists(out):
        im=im.convert('RGBA' if png else 'RGB')
        if max(iw,ih)>2400: im.thumbnail((2400,2400),_I.LANCZOS)
        im.save(out,**({} if png else {'quality':90}))
    return 'img/'+name
def AIFIG(f,wcss,hcss,where):
    """插图位的 AI 配图：有成图返回文件名；没有就生成带标注的占位图（风格色渐变 + 虚线框）。"""
    k=str(f)[3:].strip(); fn=ai_file(f)
    AISLOTS.append(dict(id=k,page=CURN,where=where,css=[round(wcss),round(hcss)],done=fn))
    if fn: return fn
    from PIL import Image as _I
    import numpy as np
    W2,H2=max(200,round(wcss*2)),max(120,round(hcss*2)); y,x=np.mgrid[0:H2,0:W2].astype(np.float32)
    c=lambda h:np.array([int(h.lstrip('#')[i:i+2],16) for i in (0,2,4)],np.float32)
    t=((x/W2+y/H2)/2)[...,None]; img=c(G)*(1-t)+c(OCH)*t; img=img*.55+255*.45
    im=_I.fromarray(img.clip(0,255).astype(np.uint8)); im=ai_label(im,k,(0,0,1,1),f'{W2}×{H2}px 起（印刷 {round(wcss*3.125)}×{round(hcss*3.125)}）')
    d=os.path.join(SRC,'.ai_placeholder'); os.makedirs(d,exist_ok=True); im.save(os.path.join(d,f'{k}.png'))
    return os.path.join('.ai_placeholder',f'{k}.png')
def FIG(f,h,b,need,cap=None):
    g=lambda k,d=None:b.get(k,d); fx,fy=g('focus',[.5,.5]); fit=g('fit','cover'); fr=' fr' if g('frame') else ''
    if str(f).startswith('ai:'): f=AIFIG(f,need,h,'插图')
    p=FIGIMG(f,need*1.5)
    c=f'<div class="fcap"{DECO}>{esc(cap)}</div>' if cap else ''
    return f'<figure class="fg{fr}"><div class="fgi" style="height:{h}px"><img alt="" src="{p}" style="object-fit:{fit};object-position:{fx*100:.0f}% {fy*100:.0f}%"></div>{c}</figure>'
_OLF={}
def OUTLINE(text,size,stroke,color,track=0):
    """把一行字转成 SVG 描边路径（用标题字体；按字取第一个有这个字的字体）"""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    ids=[x for x in FROLES_PRE['title'] if FONTS_.path_of(x)]
    fonts=[]
    for fid in ids:
        if fid not in _OLF:
            t=TTFont(FONTS_.path_of(fid)); loc={'wght':400} if 'fvar' in t else None
            _OLF[fid]=(t,t.getGlyphSet(location=loc) if loc else t.getGlyphSet(),t.getBestCmap(),t['head'].unitsPerEm,t['hhea'].ascent)
        fonts.append(_OLF[fid])
    x=0; paths=[]; asc=max(f[4]/f[3] for f in fonts) if fonts else .9
    for ch in text:
        f=next((f for f in fonts if ord(ch) in f[2]),None)
        if not f: x+=size*.5; continue
        t,gs,cm,upm,_=f; gn=cm[ord(ch)]; sc=size/upm
        pen=SVGPathPen(gs); gs[gn].draw(TransformPen(pen,(sc,0,0,-sc,x,asc*size)))
        d=pen.getCommands()
        if d: paths.append(d)
        x+=gs[gn].width*sc+size*float(track)
    h=size*1.18
    return (f'<svg width="{x+stroke*2:.1f}" height="{h:.1f}" viewBox="{-stroke:.1f} {-stroke:.1f} {x+stroke*2:.1f} {h:.1f}" style="overflow:visible;display:block">'
            f'<path d="{" ".join(paths)}" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linejoin="round"/></svg>')
def B(b,ph):
    if isinstance(b,str): b={'p':b}
    g=lambda k,d=None:b.get(k,d)
    gold=GOLD if ph else G
    if 'display' in b:   # 海报大字
        c={'gold':GOLD if ph else OCH,'white':'#fff' if ph else INK,'ink':INK}.get(g('color','white'),g('color'))
        if g('stroke'):   # 描边空心大字（章节号、L1–L4）：转成矢量路径——Chrome 会把描边文字写成 Type 3 字体
            return f'<div class="disp" aria-label="{esc(str(b["display"]))}" style="margin-top:{g("mt",6)}px;line-height:0">{OUTLINE(str(b["display"]),g("size",48),g("stroke"),c,g("spacing",0))}</div>'
        ol=f'color:{c};'
        return f'<div class="disp" style="font-size:{g("size",48)}px;letter-spacing:{sp(g("spacing",.14))}em;line-height:{g("lh",1.15)};{ol}margin-top:{g("mt",6)}px">{GT(b,ph,esc(b["display"]))}</div>'
    if 'title' in b:
        k=f'<div class="k"{DECO}>{esc(g("kicker"))}</div>' if g('kicker') else ''
        t=f'<div class="sf" style="font-size:{g("size",34)}px;font-weight:var(--title-w);letter-spacing:{sp(.12)}em;margin-top:8px;line-height:1.3">{GT(b,ph,esc(b["title"]))}</div>'
        s=f'<div class="sub"{DECO}>{esc(g("sub"))}</div>' if g('sub') else ''
        return f'<div class="hd0">{k}{t}{s}</div>'
    if 'en' in b:   # 英文斜体副标题
        return f'<div{DECO} style="font-family:var(--f-accent);font-style:var(--accent-style);font-weight:600;font-size:{g("size",17)}px;color:{GOLD if ph else OCH};margin-top:{g("mt",8)}px">{esc(b["en"])}</div>'
    if 'kicker' in b: return f'<div class="kk"{DECO} style="margin-top:{g("mt",14)}px">{esc(b["kicker"])}</div>'
    if 'worksheet' in b: return f'<div class="kk"{DECO} style="margin-top:18px;color:{"#fff" if ph else MUT}">Worksheet · {esc(b["worksheet"])}</div>'
    if 'task' in b:
        return (f'<div class="hd0"><div style="display:flex;align-items:baseline;gap:14px"><span style="font-family:var(--f-accent);font-style:var(--accent-style);font-weight:800;font-size:58px;line-height:1;color:{GOLD if ph else OCH}">{esc(b["task"])}</span>'
                f'<span class="sf" style="font-size:{g("size",25)}px;font-weight:var(--title-w);letter-spacing:{sp(.04)}em">{esc(g("name",""))}</span></div>'
                +(f'<div class="sf" style="font-size:14.5px;font-weight:700;margin:6px 0 4px;letter-spacing:.06em">{esc(g("sub"))}</div>' if g('sub') else '')+'</div>')
    if 'p' in b:
        lead=f'<b>{esc(g("lead"))}</b>' if g('lead') else ''
        st=f'font-size:{g("size")}px;' if g('size') else ''
        if g('weight'): st+=f'font-weight:{g("weight")};'
        if g('mt') is not None: st+=f'margin-top:{g("mt")}px;'
        return f'<p class="op" style="{st}">{lead}{esc(b["p"])}</p>'
    if 'letter' in b:   # 书信体段落（海报页）
        return '<div class="lt">'+''.join(f'<p>{esc(x)}</p>' for x in b['letter'])+'</div>'
    if 'items' in b:
        if g('style')=='big':
            s=g('size',16); return (f'<div class="kk" style="margin-top:8px">{esc(g("heading"))}</div>' if g('heading') else '')+''.join(f'<div class="big" style="grid-template-columns:{int(s*3.2)}px 1fr">{num(i,gold,int(s*1.8))}<div class="sf" style="font-size:{s}px;font-weight:{g("weight",700)};line-height:1.6">{esc(t)}</div></div>' for i,t in enumerate(b['items'],1))
        return f'<div class="ob2">'+(f'<div class="kk">{esc(g("heading"))}</div>' if g('heading') else '')+''.join(f'<div class="oi"><span class="nu" style="font-size:13px;color:{"#fff" if ph else G}">{i}</span><span>{esc(t)}</span></div>' for i,t in enumerate(b['items'],1))+'</div>'
    if 'kv' in b:   # 键值行：行程表、时间表
        kw=g('kw',90); return ''.join(f'<div style="display:grid;grid-template-columns:{kw}px 1fr;margin-top:{g("gap",10)}px;align-items:baseline"><span class="sf" style="font-size:{g("ksize",15)}px;font-weight:800;color:{gold}">{esc(k)}</span><span style="font-size:{g("vsize",14)}px;font-weight:{g("weight",600)};line-height:1.6">{esc(v)}</span></div>' for k,v in b['kv'])
    if 'step' in b:   # 编号任务 + 书写区
        t=f'<b style="color:{gold}">{lab(g("lead"))}</b>{esc(g("text",""))}' if g('lead') else esc(g('text',''))
        grow=';flex:1 1 auto' if g('grow') else ''
        return f'<div class="tk" style="{grow}"><div class="tr">{num(b["step"],gold)}<div class="tt">{t}</div></div><div class="tb">{R(g("write",[]),ph)}</div></div>'
    if 'q' in b:
        return f'<div class="tk" style="flex:1 1 auto;display:flex;flex-direction:column"><div class="tr"><span class="qn">Q{esc(b["q"])}</span><div class="tt">{esc(g("text",""))}</div></div><div class="tb">{R(g("write",[{"fill":64}]),ph)}</div></div>'
    # 多栏 / 表格放在 field、lines 之前判断：它们自己也可能带 cols、lines 参数
    if isinstance(b.get('cols'),list):   # 多栏：cols: [[blocks],[blocks]]（fields/boxes 的 cols 是列宽字符串，不算）
        return f'<div class="row" style="grid-template-columns:{g("widths"," ".join(["1fr"]*len(b["cols"])))};column-gap:{g("gap",36)}px">'+''.join(f'<div>{R(c,ph)}</div>' for c in b['cols'])+'</div>'
    if 'table' in b:
        cols=b['table']; n=g('lines',1); hd=''.join(f'<div class="thd"{DECO}>{esc(c)}</div>' for c in cols)
        for r in g('rows',[]): hd+=f'<div class="rl" style="height:{LH*n}px">{esc(r)}</div>'+''.join(f'<div>{LN(n)}</div>' for _ in cols[1:])
        return f'<div class="tbl" style="grid-template-columns:{g("widths"," ".join(["1fr"]*len(cols)))}">{hd}</div>'
    if 'field' in b: return FD(b['field'],g('size'))
    if 'fields' in b: return ROW([FD(x,g('size')) for x in b['fields']],g('cols'))
    if 'lines' in b: return LN(b['lines'])
    if 'fill' in b: return f'<div class="fill" style="flex:1 1 0;min-height:{b["fill"]}px"></div>'
    if 'box' in b: return f'<div class="bx" style="height:{g("h",140)}px"><span class="bl"{DECO} style="top:7px">{esc(b["box"])}</span></div>'
    if 'boxes' in b: return ROW([f'<div class="bx" style="height:{g("h",140)}px"><span class="bl"{DECO} style="top:7px">{esc(x)}</span></div>' for x in b['boxes']],g('cols'))
    if 'choice' in b: return f'<div class="ch"><span class="cl">{esc(b["choice"])}</span>'+''.join(f'<span class="co">{esc(o)}</span>' for o in g('options',[]))+'</div>'
    if 'blanks' in b:   # 封面/签名：姓名____ 班级____
        return '<div class="bl2" style="font-size:%spx;margin-top:%spx">'%(g('size',15),g('mt',20))+''.join(f'<span>{lab(l)}</span><i style="width:{g("w",180)}px"></i><span style="width:26px"></span>' for l in b['blanks'])+'</div>'
    if 'sign' in b:
        return f'<div class="bl2" style="font-size:{g("size",17)}px;margin-top:{g("mt",24)}px">{esc(b["sign"])}<span style="width:40px"></span>{lab(g("label","签名" if CJK else "Signature"))}<i style="width:{g("w",240)}px"></i></div>'
    if 'figure' in b:   # 插图：照片、截图、图表、logo（fit: contain 不裁切；frame: true 加细框，适合截图）
        bl=g('bleed'); mg=f'margin-right:-{MX}px;' if bl=='right' else f'margin-left:-{MX}px;' if bl=='left' else f'margin-left:-{MX}px;margin-right:-{MX}px;' if bl=='both' else ''
        return f'<div class="{"bleed " + bl if bl else ""}" style="margin-top:{g("mt",12)}px;{mg}">'+FIG(b['figure'],g('h',220),b,g('w',682),g('caption'))+'</div>'
    if 'gallery' in b:   # 图组：一行几张
        fs=b['gallery']; caps=g('captions',[None]*len(fs)); ws=g('widths',' '.join(['1fr']*len(fs)))
        return f'<div class="row gal" style="grid-template-columns:{ws};column-gap:{g("gap",10)}px;margin-top:{g("mt",12)}px">'+''.join(FIG(f,g('h',160),b,682/len(fs),c) for f,c in zip(fs,caps))+'</div>'
    if 'stats' in b:   # 关键数字：[[数字, 说明], …]
        st=b['stats']; s=g('size',44)
        cells=''.join(f'<div class="st"><div class="stn" style="font-size:{s}px;color:{gold}">{GT(b,ph,re.sub(r'([+＋%])$',r'<sup>\1</sup>',esc(str(x[0]))))}</div><div class="stl">{esc(x[1]) if len(x)>1 else ""}</div></div>' for x in st)
        return f'<div class="sts" style="grid-template-columns:repeat({g("cols",len(st))},1fr);margin-top:{g("mt",16)}px">{cells}</div>'
    if 'quote' in b:   # 引语 / 学员说 / 校长语录（原文自带的引号去掉、“——署名”自动拆成 by）
        qt,by=str(b['quote']).strip(),g('by')
        if not by:
            m_=re.match(r'^(.*?)\s*(?:——|—|--)\s*([^—]{1,30})$',qt,re.S)
            if m_: qt,by=m_.group(1),m_.group(2)
        qt=re.sub(r'^[“「『"]+|[”」』"]+$','',qt.strip())
        return (f'<div class="qt" style="margin-top:{g("mt",16)}px"><div class="qm"{DECO} style="color:{gold}">“</div>'
                f'<div class="qx" style="font-size:{g("size",19)}px">{esc(qt)}</div>'+(f'<div class="qb">{esc(by)}</div>' if by else '')+'</div>')
    if 'cards' in b:   # 亮点卡片：[[标题, 说明], …]；num: true 加编号
        cs=b['cards']; cols=g('cols',2 if len(cs) in (2,4) else min(3,len(cs)))
        def cell(i,c):   # 卡片：[标题, 说明] 或 {k: 眉标, t: 标题, x: 说明, img: 图标}
            if isinstance(c,dict): k_,t_,x_,im_=c.get('k'),c.get('t',''),c.get('x'),c.get('img')
            else: k_,t_,x_,im_=None,c[0],(c[1] if len(c)>1 else None),None
            return (f'<div class="cd">'+(f'<img class="cdi" alt="" src="{FIGIMG(im_,120)}">' if im_ else '')+(f'<div class="cdn" style="color:{gold}">{i:02d}</div>' if g('num') else '')
                    +(f'<div class="cdk">{esc(k_)}</div>' if k_ else '')+f'<div class="cdt" style="color:{gold}">{esc(t_)}</div>'+(f'<div class="cdx">{esc(x_)}</div>' if x_ else '')+'</div>')
        return f'<div class="cds{" line" if g("style")=="line" else ""}" style="grid-template-columns:repeat({cols},1fr);margin-top:{g("mt",14)}px">'+''.join(cell(i,c) for i,c in enumerate(cs,1))+'</div>'
    if 'qr' in b:   # 二维码（矢量）：报名链接、公众号、问卷
        try: import qrcode, qrcode.image.svg
        except ImportError: ERR.append('二维码块需要 qrcode：pip install qrcode（或把二维码图片放进 photos/，用 figure 块）'); return ''
        sv=qrcode.make(str(b['qr']),image_factory=qrcode.image.svg.SvgPathImage,border=0).to_string(encoding='unicode')
        sv=re.sub(r'<\?xml[^>]*>','',sv); sv=re.sub(r'width="[^"]*" height="[^"]*"',f'width="{g("size",104)}" height="{g("size",104)}"',sv,count=1)
        sv=sv.replace('<path ',f'<path fill="{INK}" ')   # 二维码永远深色码 + 白底静区：反色码很多扫码软件认不出
        pad=round(g('size',104)*.12)
        return f'<div class="qr" style="margin-top:{g("mt",14)}px"><div class="qrt" style="padding:{pad}px">{sv}</div>'+(f'<div class="qrc"{DECO}>{esc(g("caption"))}</div>' if g('caption') else '')+'</div>'
    if 'bars' in b:   # 对比条形图：[[指标, 我方, 对照], …]，series 是两组的名字
        sr=g('series',['', '']); un=g('unit','%'); mx=g('max',100)
        rows=''.join(f'<div class="br"><div class="brl">{esc(r[0])}</div><div class="brt"><i class="b1" style="width:{r[1]/mx*100:.1f}%"></i><span class="brv">{esc(r[1])}{esc(un)}</span></div>'
                     f'<div class="brt b2w"><i class="b2" style="width:{r[2]/mx*100:.1f}%"></i><span class="brv2">{esc(sr[1])}{COLON}{esc(r[2])}{esc(un)}</span></div></div>' for r in b['bars'])
        lg=f'<div class="brg"{DECO}><span><i class="b1"></i>{esc(sr[0])}</span><span><i class="b2"></i>{esc(sr[1])}</span></div>' if sr[0] else ''
        return f'<div class="bars" style="margin-top:{g("mt",14)}px">{lg}{rows}</div>'
    if 'product' in b:   # 产品卡：渐变图区 + 标签 + 名称 + 说明
        im_=g('image')
        if im_ and str(im_).startswith('ai:'): im_=AIFIG(im_,g('w',320),g('h',200),'产品卡插图')
        im=FIGIMG(im_,340) if im_ else ''
        pic=f'<div class="pdi" style="height:{g("h",200)}px"><img alt="" src="{im}" style="object-fit:{g("fit","contain")}"></div>' if im else ''
        tag=f'<span class="pdt"{DECO}>{esc(g("tag"))}</span>' if g('tag') else ''
        return (f'<div class="pd" style="margin-top:{g("mt",14)}px">{pic}<div class="pdb">{tag}<div class="pdn" style="font-size:{g("size",20)}px">{esc(b["product"])}</div>'
                +(f'<div class="pdx">{esc(g("text"))}</div>' if g('text') else '')+'</div></div>')
    if 'chips' in b:   # 层级/分类胶囊：on = 当前第几个（从 1 开始）
        return f'<div class="chs"{DECO} style="margin-top:{g("mt",0)}px">'+''.join(f'<span class="ch1{" on" if i==g("on") else ""}">{esc(c)}</span>' for i,c in enumerate(b['chips'],1))+'</div>'
    if 'cycle' in b:   # 循环图（飞轮）：节点沿圆周，中心一句话；节点文字算装饰，说明写在旁边的块里
        ns=b['cycle']; S_=g('size',300); r=S_*.38; c=S_/2; n=len(ns)
        pts=[(c+r*math.sin(2*math.pi*i/n),c-r*math.cos(2*math.pi*i/n)) for i in range(n)]
        arcs=''.join(f'<path d="M{pts[i][0]:.1f},{pts[i][1]:.1f} A{r:.1f},{r:.1f} 0 0 1 {pts[(i+1)%n][0]:.1f},{pts[(i+1)%n][1]:.1f}" fill="none" stroke="url(#cg)" stroke-width="2" marker-end="url(#ca)" opacity=".85"/>' for i in range(n))
        nodes=''.join(f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="{S_*.075:.1f}" class="cyn{" on" if i==0 else ""}"/><text x="{x:.1f}" y="{y+S_*.016:.1f}" class="cyt{" on" if i==0 else ""}" text-anchor="middle">{esc(nd[0])}</text>'
                      +(f'<text x="{x:.1f}" y="{y+S_*.13:.1f}" class="cys" text-anchor="middle">{esc(nd[1])}</text>' if len(nd)>1 else '')+'</g>' for i,(nd,(x,y)) in enumerate(zip(ns,pts)))
        ctr=f'<text x="{c}" y="{c+5}" class="cyc" text-anchor="middle">{esc(g("center",""))}</text>'
        return (f'<div class="cyc0"{DECO} style="margin-top:{g("mt",10)}px"><svg width="{S_}" height="{S_}" viewBox="0 0 {S_} {S_}"><defs><linearGradient id="cg"><stop offset="0" stop-color="{G}"/><stop offset="1" stop-color="{OCH}"/></linearGradient>'
                f'<marker id="ca" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0L10,5L0,10z" fill="{OCH}"/></marker></defs>{arcs}{nodes}{ctr}</svg></div>')
    if 'space' in b: return f'<div style="height:{b["space"]}px;flex-shrink:0"></div>'
    if 'html' in b: return b['html']
    ERR.append(f'未知 block 类型: {list(b)[:3]}'); return ''
def R(bs,ph=False): return ''.join(B(b,ph) for b in (bs or []))
CUR_PH=True   # 当前页“图上文字”用白字（深色照片/深色底图）还是深色字（浅色底图）
def LT(): return '#fff' if CUR_PH else INK
# ---------------------------------------------------------------- regions
def TOP(bs,l,r,t,ph=None):
    ph=CUR_PH if ph is None else ph
    return _TOP(bs,l,r,t,ph)
def _TOP(bs,l,r,t,ph): return f'<div class="a{" ph" if ph else " ink"}" style="left:{l}px;right:{r}px;top:{t}px">{R(bs,ph)}</div>' if bs else ''
def BOT(bs,l,r,b,ph=None):
    ph=CUR_PH if ph is None else ph
    return _BOT(bs,l,r,b,ph)
def _BOT(bs,l,r,b,ph): return f'<div class="a{" ph" if ph else " ink"}" style="left:{l}px;right:{r}px;bottom:{b}px">{R(bs,ph)}</div>' if bs else ''
ALIGN='spread'   # 当前页的纵向排布：spread 撑满（适合书写页）/ top 顶部对齐（适合阅读页）/ bottom
def FLOW(bs,l,r,t,b,ph=False): return f'<div class="a flow{" ph" if ph else " ink"}{"" if ALIGN=="spread" else " "+ALIGN}" style="left:{l}px;right:{r}px;top:{t}px;bottom:{b}px">{R(bs,ph)}</div>' if bs else ''
def head(hd,l=M0,r=M0,col=None):
    if not hd: return ''
    col=col or LT()
    a,b=(hd+[''])[:2] if isinstance(hd,list) else (hd,'')
    return f'<div class="a os rh"{DECO} style="left:{l}px;right:{r}px;color:{col}"><span>{esc(a)}</span><span>{esc(b)}</span></div>'
def folio(n,col=None,l=M0,r=M0): col=col or LT(); return f'<div class="a fo"{DECO} style="left:{l}px;right:{r}px;color:{col}"><span>{esc(FOLIO)}</span><span>{n:02d}</span></div>'
def figc(t,col=None,l=M0): col=col or LT(); return f'<div class="a os fig"{DECO} style="left:{l}px;color:{col}">{esc(t)}</div>' if t else ''
# ---------------------------------------------------------------- layouts
PP=[]; MAP={}
def page(n,html,img,side,bg,cls=''):
    PP.append(f'<section class="page{cls}" style="background:{bg}" data-n="{n}">{html}</section>')
    if img: MAP[len(PP)-1]=dict(img=img,side=side)
def F(p): return tuple(p.get('focus',[.5,.5]))
def L_POSTER(n,p):
    name=f'p{n:02d}.jpg'; bake(n,name,p.get('image'),W,lambda X,Y:0*X,F(p),p.get('target',[W/2,H/2]),p.get('zoom',1.0),'single',False)
    fb=96 if p.get('fig') else 60
    h=IMGTAG(name)+head(p.get('header'))+TOP(p.get('top'),M0,M0,p.get('top_y',78))+BOT(p.get('bottom'),M0,M0,p.get('bottom_y',fb))+figc(p.get('fig'))+(folio(n) if p.get('folio',True) else '')
    page(n,h,name,'S','#0B1410')
def L_T(n,p):   # 照片在上，纸面在下
    sp=p.get('split',330); name=f'p{n:02d}.jpg'
    bake(n,name,p.get('image'),W,wash.M_T(sp-130,sp+10),F(p),p.get('target',[W/2,sp*.45]),p.get('zoom',1.0),'single',True,(0,0,1,sp/H))
    h=IMGTAG(name)+head(p.get('header'))+TOP(p.get('on_photo'),M0,M0,78)+FLOW(p.get('body'),M0,M0,p.get('body_top',sp),60)+folio(n,MUT)
    page(n,h,name,'S',PAPER)
def L_B(n,p):   # 纸面在上，照片在下
    sp=p.get('split',760); name=f'p{n:02d}.jpg'
    bake(n,name,p.get('image'),W,wash.M_B(sp-40,sp+150),F(p),p.get('target',[W/2,(sp+H)/2]),p.get('zoom',1.0),'single',True,(0,sp/H,1,1))
    h=IMGTAG(name)+head(p.get('header'),col=MUT)+FLOW(p.get('body'),M0,M0,64,H-sp+20)+BOT(p.get('on_photo'),M0,M0,70)+folio(n)
    page(n,h,name,'S',PAPER)
def L_SIDE(n,p,right=False):  # SL 照片在左 / SR 照片在右
    st=p.get('strip',270); name=f'p{n:02d}.jpg'
    m=wash.M_SR(W,st-150,st) if right else wash.M_SL(st-150,st)
    bake(n,name,p.get('image'),W,m,F(p),p.get('target',[W-st/2 if right else st/2,H/2]),p.get('zoom',1.6),'single',True,(1-st/W,0,1,1) if right else (0,0,st/W,1))
    l,r=(M0,st-5) if right else (st-5,M0)
    h=IMGTAG(name)+head(p.get('header'),l,r,MUT)+FLOW(p.get('body'),l,r,64,60)+folio(n,MUT,l,r)
    page(n,h,name,'S',PAPER)
def L_PAPER(n,p):  # 纯纸面页（无照片）：规章制度、日程表、通讯录、附录、笔记页
    h=head(p.get('header'),col=MUT)+FLOW(p.get('body'),M0,M0,p.get('body_top',64),60)+folio(n,MUT)
    page(n,h,None,'S',PAPER,' paper')
HOLES={'tr':((600,230),(M0,440,60,560),(580,60)),'tl':((194,230),(440,M0,60,560),(580,60)),
       'br':((600,890),(M0,440,560,60),(60,560)),'bl':((194,890),(440,M0,560,60),(60,560))}
def L_HOLE(n,p):  # 纸面上开窗露出照片
    c,bs,bd=HOLES[p.get('window','tr')]; name=f'p{n:02d}.jpg'
    rx,ry=p.get('size',[300,250])
    bake(n,name,p.get('image'),W,wash.M_HOLE(c[0],c[1],rx,ry,.25,1.1),F(p),p.get('target',list(c)),p.get('zoom',1.4),'single',True,(max(0,(c[0]-rx*.8)/W),max(0,(c[1]-ry*.8)/H),min(1,(c[0]+rx*.8)/W),min(1,(c[1]+ry*.8)/H)))
    h=IMGTAG(name)+FLOW(p.get('beside'),*bs)+FLOW(p.get('body'),M0,M0,*bd)+folio(n,MUT)
    page(n,h,name,'S',PAPER)
SPM={'P':lambda X,Y:0*X,'H':lambda X,Y:0.92*wash.ss(410,530,Y),
     'SL':lambda X,Y:wash.A*wash.ss(W+110,W+260,X),
     'T':lambda X,Y:wash.A*wash.ss(W-50,W+40,X)*wash.ss(130,280,Y)}
def spread_img(n,p,kind,clip=None):
    name=f's{n:02d}.jpg'
    box={'P':(0,0,1,1),'H':(0,0,1,500/H),'SL':(0,0,(W+180)/(2*W),1),'T':(0,0,.5,1)}[kind]
    bake(n,name,p.get('image'),2*W,SPM[kind],F(p),p.get('target',[W,H/2]),p.get('zoom',1.0),'spread',kind!='P',box)
    if clip: CLIP[name]=clip
    return name,IMGTAG(name,-2,2*W+4),IMGTAG(name,-W-2,2*W+4)
def L_SPREAD_P(n,p):   # 双海报跨页
    name,a,b=spread_img(n,p,'P'); L,Rr=p.get('left',{}),p.get('right',{})
    for k,(img,side,q) in enumerate([(a,'L',L),(b,'R',Rr)]):
        fb=96 if q.get('fig') else 60
        page(n+k,img+head(q.get('header'))+TOP(q.get('top'),M0,M0,q.get('top_y',80))+BOT(q.get('bottom'),M0,M0,q.get('bottom_y',fb))+figc(q.get('fig'))+folio(n+k),name,side,'#0B1410')
def L_SPREAD_H(n,p):   # 横向跨页：照片横贯上半部
    name,a,b=spread_img(n,p,'H'); L,Rr=p.get('left',{}),p.get('right',{}); bt=p.get('body_top',548)
    page(n,a+head(L.get('header'))+TOP(L.get('on_photo'),M0-4,M0,66)+FLOW(L.get('body'),M0,M0,bt,60)+folio(n,MUT),name,'L',PAPER)
    page(n+1,b+head(Rr.get('header'))+BOT(Rr.get('on_photo'),M0,M0,H-392)+FLOW(Rr.get('body'),M0,M0,bt,60)+folio(n+1,MUT),name,'R',PAPER)
def L_SPREAD_OPENER(n,p):  # 左页开篇海报，照片延伸到右页并过渡成纸面
    kind=p.get('right_layout','SL'); name,a,b=spread_img(n,p,kind,(-200,W)); L,Rr=p.get('left',{}),p.get('right',{})
    page(n,a+head(L.get('header'))+TOP(L.get('top'),M0,M0,L.get('top_y',78))+BOT(L.get('bottom'),M0,M0,L.get('bottom_y',96 if L.get('fig') else 60))+figc(L.get('fig'))+folio(n),name,'L','#0B1410')
    if kind=='SL': body=FLOW(Rr.get('body'),265,M0,64,60); hd=head(Rr.get('header'),265,M0,MUT); fo=folio(n+1,MUT,265,M0)
    else: body=TOP(Rr.get('on_photo'),M0,M0,70)+FLOW(Rr.get('body'),M0,M0,Rr.get('body_top',300),60); hd=head(Rr.get('header')); fo=folio(n+1,MUT)
    page(n+1,b+hd+body+fo,name,'R',PAPER)
LAY={'PAPER':(L_PAPER,1),'POSTER':(L_POSTER,1),'T':(L_T,1),'B':(L_B,1),'SL':(L_SIDE,1),'SR':(lambda n,p:L_SIDE(n,p,True),1),'HOLE':(L_HOLE,1),
     'SPREAD_P':(L_SPREAD_P,2),'SPREAD_H':(L_SPREAD_H,2),'SPREAD_OPENER':(L_SPREAD_OPENER,2)}
# ---------------------------------------------------------------- build
n=1; prev=None; plan=[]
for i,p in enumerate(SPEC['pages']):
    lay=p.get('layout')
    if lay not in LAY: ERR.append(f'第{i+1}个页面: 未知 layout {lay}，可选 {list(LAY)}'); continue
    fn,span=LAY[lay]
    if lay!='PAPER' and not p.get('image') and STYLE=='photo': ERR.append(f'第{n}页 {lay}: 缺少 image（没照片时写 image: placeholder 先占位，或换无图风格 book.style，或用 layout: PAPER）'); n+=span; prev=lay; continue
    CUR_PH=(SD['tone']=='dark') if is_art(p.get('image')) and not (str(p.get('image','')).startswith('ai:') and ai_file(p.get('image'))) else True
    if p.get('tone') in ('dark','light'): CUR_PH=p['tone']=='dark'   # 图上文字用白字（dark）还是深色字（light）；AI 配图按需求单里写的明暗来
    if span==2 and n%2==1: ERR.append(f'{lay} 从第{n}页开始，跨页左页必须是偶数页 → 在它前面增/减一页，或把前面的内容挪动')
    if lay==prev and span==1 and lay!='POSTER': print(f'提示：第{n}页与上一页版式相同（{lay}），建议换一种')
    ALIGN=p.get('align','top' if lay=='PAPER' or PURPOSE!='workbook' else 'spread')   # 没有书写区的页：内容顶部对齐，不被撑散
    if STYLE=='photo' and str(p.get('image','')).startswith('placeholder'): print(f'提示：第{n}页用的是占位底图（{p["image"]}），拿到照片后把 image 换成文件名即可')
    CURN=n
    try: fn(n,p)
    except Exception as e: ERR.append(f'第{n}页 {lay}: {type(e).__name__}: {e}')
    plan.append(f'{n:02d}{"-%02d"%(n+1) if span==2 else "   "} {lay:14s} {p.get("image","") or ("" if lay=="PAPER" else "（"+STYLE+" 底图）")}  {p.get("note","")}')
    n+=span; prev=lay
total=n-1
CSS=open(os.path.join(HERE,'style.css')).read()+SD['css']
if not CJK: CSS+='.op,.lt p{text-align:left}.fo span:first-child{letter-spacing:.18em}'   # 西文：左对齐（两端对齐会撑出大空格）
for k,v in dict(W=W,H=H-1,G=G,INK=INK,MUT=MUT,GOLD=GOLD,OCH=OCH,PAPER=PAPER).items(): CSS=CSS.replace('{'+k+'}',str(v))
# 字体：按本书实际用到的字裁切嵌入（见 fonts.py）
TEXT=_h.unescape(re.sub(r'<[^>]+>','',''.join(PP)))+str(BK.get('title',''))
FCSS,FROLES,FMISS=FONTS_.build_css(BK.get('fonts',SD['fonts']),TEXT,PROJ,CJK)
CSS=FCSS+CSS
JS=open(os.path.join(HERE,'fill.js')).read()
open(os.path.join(PROJ,'book.html'),'w',encoding='utf-8').write(f'<!doctype html><html lang="{LANG}"><head><meta charset="utf-8"><title>{esc(BK.get("title","Handbook"))}</title><style>{CSS}</style></head><body>{"".join(PP)}{JS}</body></html>')
os.makedirs(os.path.join(PROJ,'.qa'),exist_ok=True); json.dump(dict(slots=AISLOTS,scale=wash.S,colors=TH_,style=STYLE),open(os.path.join(PROJ,'.qa','ai_slots.json'),'w'),ensure_ascii=False)
json.dump(dict(map=MAP,imgs=IMGS,local=LOCAL,clip=CLIP,paper=PAPER,flat=FLAT),open(os.path.join(PROJ,'map.json'),'w'))
for nm in IMGS: shutil.copy(os.path.join(PROJ,'img',nm.replace('.jpg','_base.jpg')),os.path.join(PROJ,'img',nm))
open(os.path.join(PROJ,'plan.txt'),'w').write('\n'.join(plan)+'\n')
print('\n'.join(plan)); print(f'风格 {STYLE} · 字体 ' + ' / '.join(f'{r}:{"+".join(v)}' for r,v in FROLES.items()))
print(f'== {total} 页', '（骑马钉需 4 的倍数，当前余 %d）'%(total%4) if total%4 else '（4 的倍数 ✓）')
if WARN: print('\n'.join('注意：'+w for w in dict.fromkeys(WARN)))
if ERR: print('\n'.join('ERROR: '+e for e in ERR)); sys.exit(1)
