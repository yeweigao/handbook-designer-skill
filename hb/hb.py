#!/usr/bin/env python3
"""hb.py — 数据驱动的手册排版器。  用法:  python3 hb.py <project_dir>
读 <project_dir>/book.yaml → 烘焙图片(纸面 wash) → 写 book.html + map.json + plan.txt。
你（agent）只需要写 book.yaml；坐标、遮罩、跨页拼接、页码都由本程序计算。
画布由 book.canvas 决定（a4 / a5 / xhs，网格与字号档见 canon.CANVAS）；默认 A4 竖版 794×1123 CSS px。
"""
import math, sys, os, re, json, shutil, html as _h, yaml
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import wash, art, fonts as FONTS_
from styles import STYLES
import palettes as PAL
W,H=794,1123
ERR=[]; WARN=[]
SAFE=re.compile(r'&lt;(/?)(b|strong|i|em|u|br|sup|sub|small)\s*/?&gt;',re.I)
def esc(s):   # 文案一律 HTML 转义，只放行不带属性的 <b> <strong> <i> <em> <u> <br> <sup> <sub> <small>；需要任意 HTML 用 {html: ...} 块
    return SAFE.sub(lambda m:f'<{m.group(1)}{m.group(2).lower()}>',_h.escape(str(s)))
DECO=' data-deco="1"'   # 标记“允许新增的装饰/提示文字”（页眉、页脚、图注、小标签、填写提示），原文核对的 EXTRA 会跳过它们
# ---------------------------------------------------------------- config
PROJ=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else '.')
try: SPEC=yaml.safe_load(open(os.path.join(PROJ,'book.yaml'),encoding='utf-8'))
except yaml.YAMLError as e:
    m=getattr(e,'problem_mark',None); tip=''
    if m is not None:
        try: ln=open(os.path.join(PROJ,'book.yaml'),encoding='utf-8').read().splitlines()[m.line]
        except (OSError,IndexError): ln=''
        if "'" in re.sub(r"'[^']*'",'',ln):   # 去掉完整的 '…' 串后还有单引号 → 撇号写在了单引号串里（如 Thailand's）
            tip="\n  这一行有单引号字符串里带撇号 → 单引号内的撇号要双写 '' 或改用双引号"
    sys.exit(f"ERROR: book.yaml 语法错误{f'（第 {m.line+1} 行第 {m.column+1} 列附近）' if m else ''}：{getattr(e,'problem',e)}\n"
             "  常见原因：花括号 {...} 里的文字含有 : , ? # [ ] { } 或以引号开头 → 给整段文字加单引号，如 {p: '时间：上午 9:00'}"+tip)
_LG={'zh','zh-hans','zh-hant','zh-tw','zh-hk','en','ja','ko','fr','de','es','it','pt','ru','th','vi','ms','ar'}
def _multi(o): return isinstance(o,dict) and o and all(str(k).lower() in _LG for k in o)
def _pick(o,l):   # 多语言写法 {zh: …, en: …}：直接跑 hb.py 时取 book.lang（或第一种）；run.sh 会先拆成各语言子项目
    if _multi(o): return _pick(next((v for k,v in o.items() if str(k).lower()==l.lower()),next(iter(o.values()))),l)
    if isinstance(o,dict): return {k:_pick(v,l) for k,v in o.items()}
    if isinstance(o,list): return [_pick(v,l) for v in o]
    return o
_b=SPEC.get('book') or {}
_l=str(_b.get('lang') or (_b.get('langs') or ['zh'])[0]); SPEC=_pick(SPEC,_l); SPEC.setdefault('book',{})['lang']=_l
import brand as BRAND_
BK,BRAND=BRAND_.apply(SPEC.get('book',{})); SPEC['book']=BK   # book.brand：品牌包的配色、字体、页脚、logo 作为默认值
if SPEC.get('pages') and len(SPEC['pages'])>3 and SPEC['pages'][-1].get('layout') in ('FULL','POSTER'): SPEC['pages'][-1]=dict(SPEC['pages'][-1],_last=True)   # 封底（品牌包在这里放 logo + 联系方式）
import canon as CN
CANVAS=str(BK.get('canvas','a4')); W,H=CN.setup(CANVAS,int(BK['body']) if str(BK.get('body','')).isdigit() else BK.get('body'))   # 画布：a4（默认）/ a5 / xhs（小红书 3:4）；非 A4 只能用 8 个内容版式
SRC=os.path.join(PROJ,BK.get('photos','photos'))
STYLE=str(BK.get('style','photo'))
PURPOSE=str(BK.get('purpose','workbook'))   # workbook 任务册（有书写区）/ guide 指南须知（以阅读为主）/ brochure 宣传册（不要书写区）
if PURPOSE not in ('workbook','guide','brochure'): sys.exit(f'ERROR: book.purpose 可选 workbook / guide / brochure，当前 {PURPOSE}')
if STYLE not in STYLES: sys.exit(f'ERROR: 未知 style {STYLE}，可选 {list(STYLES)}')
SD=STYLES[STYLE]
TH_=dict(INK='#17211C',G='#1D5A43',MUT='#3F4A44',GOLD='#F2C14E',OCH='#7E560E',PAPER='#FBFAF7'); TH_.update(SD['colors']); TH_=PAL.resolve(BK.get('colors') or (None if SD['colors'] else PAL.DEFAULT),TH_)   # 没写配色、风格也没自带配色 → 默认 klein（克莱因蓝 × 拿坡里黄）
TH_['A'],TH_['B']=PAL.pair(TH_)   # 内容版式的两块撞色（角色：主色 primary、强调色 accent）
COLOR_MODE,MODE_WHY=PAL.mode(TH_,BK.get('color_mode') if BK.get('color_mode') not in (None,'auto') else SD.get('mode'))   # 用色档位：clash 撞色 / accent 点缀 / mono 单色；没写时用风格的默认档（swiss → mono），再没有就按两色的色相差和对比度自动判断
if SD.get('mode') and BK.get('color_mode') in (None,'auto'): MODE_WHY=f'{STYLE} 风格默认 {COLOR_MODE}（单页主题色纸面写 surface: A；整册撞色写 color_mode: clash）'
if STYLE=='swiss' and COLOR_MODE=='clash' and not BK.get('colors'):   # 瑞士撞色档没写配色 → 用默认撞色方案（风格自带的红 + 白撑不起撞色）
    TH_=PAL.resolve(PAL.DEFAULT,dict(INK='#17211C',G='#1D5A43',MUT='#3F4A44',GOLD='#F2C14E',OCH='#7E560E',PAPER='#FBFAF7')); TH_['A'],TH_['B']=PAL.pair(TH_)
if STYLE=='stijl' and str(BK.get('look','classic')).lower()=='tone': TH_['A']=TH_['INK']   # 风格派无线：强调用墨色
if STYLE=='stijl' and str(BK.get('look','classic')).lower()!='tone': TH_['TINT']=TH_['PAPER']   # 风格派：次级背景就是纸色，分区靠粗线
if COLOR_MODE=='mono' and not TH_.get('TINT'): TH_['TINT']=PAL.mix(TH_['PAPER'],TH_['INK'],.055)   # 单色：次级背景是中性浅灰
if COLOR_MODE!='clash' and not TH_.get('TINT'): TH_['TINT']=PAL.mix(TH_['PAPER'],TH_['A'],.07)
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
IMGS={}; LOCAL=[]; CLIP={}; FLAT=[]; USE=[]   # USE：每张照片用在哪页、印出来约多少 dpi（images.py → images.yaml）
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
BAKE_USED=set()   # 本轮构建用到的烘焙缓存键（.art/bake_*.jpg；构建末尾清掉不再用的）
def _mask_id(mask,w,H):
    """掩膜标识：在一小片采样网格上量它的值（同一函数每次结果一致；换了掩膜或参数，缓存即失效）"""
    import hashlib
    try:
        import numpy as _np
        gx,gy=_np.meshgrid(_np.linspace(-2,w+2,11),_np.linspace(-1,H+1,11))
        return hashlib.md5(_np.asarray(mask(gx,gy),_np.float32).tobytes()).hexdigest()[:8]
    except Exception:
        c=getattr(mask,'__code__',None)
        return hashlib.md5(repr((c and c.co_code,c and c.co_consts,c and c.co_names,bool(getattr(mask,'__closure__',None)))).encode()).hexdigest()[:8]
def _bkey(s,w,H,focus,target,zoom,mask,kind,box):
    """照片烘焙缓存键：源文件（mtime+size）+ 目标 w/H + focus/target/zoom + 掩膜标识 + kind + 纸面倍率/不透明度。
    都没变就命中 .art/bake_<键>.jpg，跳过重烤（改一字看效果的循环不再每次全量重算）。"""
    import hashlib
    try: mt,sz=os.path.getmtime(s),os.path.getsize(s)
    except OSError: mt,sz=0,0
    r4=lambda vs: tuple(round(float(v),4) for v in vs)
    return hashlib.md5(repr((os.path.abspath(s),mt,sz,round(w),round(H),r4(focus),r4(target),round(float(zoom),4),
                             _mask_id(mask,w,H),kind,r4(box),round(wash.A,4),wash.S,wash.PAPERC.tolist())).encode()).hexdigest()[:12]
def bake(n,name,f,w,mask,focus,target,zoom,kind,local,box=(0,0,1,1)):
    if str(f).startswith('ai:'):   # AI 配图位：有成图就当照片用，没有就画占位
        fn=ai_file(f); AISLOTS.append(dict(id=str(f)[3:].strip(),page=n,where='版式图片',img=name,css=[w,H],box=list(box),done=fn))
        if fn: f=fn
    s=plate(n,f,w,box) if is_art(f) else src(n,f)
    if not s: return
    if not is_art(f):   # 清晰度：按铺满后的缩放估算印出来的 dpi
        from PIL import Image as _I
        iw,ih=_I.open(s).size; dpi=96/(max((w*(box[2]-box[0])+4)/iw,(H*(box[3]-box[1])+2)/ih)*zoom); USE.append(dict(page=n,file=str(f),dpi=round(dpi),img=name))
        if dpi<96: WARN.append(f'第{n}页：{f} 只有 {iw}×{ih}px，放在这里约 {dpi:.0f}dpi，满版会糊 → 换更大的原图，或放进 figure 插图块')
        elif dpi<130: WARN.append(f'第{n}页：{f}（{iw}×{ih}px）放在这里约 {dpi:.0f}dpi：电子版没问题，印刷会偏软')
    if is_art(f):   # 底图按 box 精确构图：不缩放、不裁切
        zoom,focus,target=1.0,(.5,.5),(w/2,H/2)
        if SD.get('edge')=='hard':   # 平面风格：纸面完全不透明、硬边（在原淡出带的末端切开），不和画面半透明混色
            m0=mask; mask=lambda X,Y,m0=m0: wash.ss(.966,.974,m0(X,Y)/max(wash.A,1e-6)); FLAT.append(name)
    out=os.path.join(PROJ,'img',name.replace('.jpg','_base.jpg'))
    ckey=_bkey(s,w,H,focus,target,zoom,mask,kind,(0,0,1,1) if is_art(f) else box)
    cdir=os.path.join(PROJ,'.art'); os.makedirs(cdir,exist_ok=True); cfile=os.path.join(cdir,f'bake_{ckey}.jpg')
    BAKE_USED.add(ckey)
    if os.path.exists(cfile):   # 命中缓存：源图、尺寸、focus、掩膜都没变 → 跳过重烤
        shutil.copy(cfile,out)
    else:
        wash.bake2(s,out,w,H,tuple(focus),tuple(target),zoom,mask,box if not is_art(f) else (0,0,1,1))
        shutil.copy(out,cfile)
    IMGS[name]=kind
    if local: LOCAL.append(name)
def IMGTAG(name,x=-2,w=W+4): return f'<img class="a" alt="" src="img/{name}" style="left:{x}px;top:-1px;width:{w}px;height:{H+2}px">'
# ---------------------------------------------------------------- blocks  (每个 block 是一个 dict，第一个已知键决定类型)
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
        name='fig_'+hashlib.md5((str(f)+str(os.path.getmtime(s))).encode()).hexdigest()[:10]+'.svg'; shutil.copy(s,os.path.join(PROJ,'img',name)); USE.append(dict(page=CURN,file=str(f),dpi=None,img=name)); return 'img/'+name
    im=_I.open(s); iw,ih=im.size; USE.append(dict(page=CURN,file=str(f),dpi=round(96*iw/max(1,need/1.5)),img=None))
    if iw<need*1.0: WARN.append(f'第{CURN}页：插图 {f} 只有 {iw}px 宽，显示约 {need:.0f}px 宽，印出来约 {96*iw/need:.0f}dpi（偏软）')
    png=im.mode in ('RGBA','LA','P') or str(f).lower().endswith('.png')
    name='fig_'+hashlib.md5((str(f)+str(os.path.getmtime(s))).encode()).hexdigest()[:10]+('.png' if png else '.jpg'); out=os.path.join(PROJ,'img',name); USE[-1]['img']=name
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
# 内容块（title、p、cards、figure …）由 flow.py 按 canon 的字号档和整行间距排（canon.blocks / flow.R）
# ---------------------------------------------------------------- layouts
PP=[]; MAP={}; CHAPTERS=[]; BRAND_GRAPHICS={}
def page(n,html,img,side,bg,cls='',chapter=None):
    ch = f' data-chapter="{esc(str(chapter))}"' if chapter is not None else ''
    if chapter is not None: CHAPTERS.append(str(chapter))
    PP.append(f'<section class="page{cls}" id="p{n}" style="background:{bg}" data-n="{n}"{ch}>{html}</section>')   # id：目录、PDF 里的页内链接跳到这里
    if img: MAP[len(PP)-1]=dict(img=img,side=side)
# 照片版式（POSTER / T / B / SL / SR / HOLE / PAPER / 跨页）也排在 6 栏网格上：见 flow.py

# ---------------------------------------------------------------- 内容版式库（recipes）
# 和上面“照片放在哪”的版式不同，这里每个版式回答“内容怎么排”：单栏 ONE · 双栏 TWO · 卡片 CARDS · 错位 STAGGER ·
# 全屏 FULL · 拼贴 COLLAGE · 网格 GRID · 组合 MIX。yaml 里只写固定的几个空位（title / intro / cards / items / images …），
# 不写尺寸：全部排在 canon.py 的 6 栏网格上（A4 默认 32 行 × 28px，book.body: 14 为 38 行 × 24px）——文字栈钉在版心上下沿，照片和色块吸收长短（中文、英文同一套版式），
# fill.js 在浏览器里把每条边补齐到行线并自检（出版心 / 出色块 / 互压 / 照片被挤小）。相邻两页同版式时自动换镜像变体。
RECIPE_PREV=[None,0]   # 上一页的内容版式、连用次数（用来轮换变体）
SURF_HIST=[]           # 每页的主底色（plan.txt 里写出来）
PCUR=[{}]
def LIMIT(name,xs,lo,hi,what):
    if len(xs)<lo: ERR.append(f'第{CURN}页 {name}：{what}至少 {lo} 个（现在 {len(xs)}）→ 换别的版式，或和相邻内容合并')
    if len(xs)>hi: ERR.append(f'第{CURN}页 {name}：{what}最多 {hi} 个（现在 {len(xs)}）→ 拆成两页：前 {(len(xs)+1)//2} 个一页、后 {len(xs)//2} 个一页（两页用同一版式，引擎会自动换变体）')
def BUDGET(p,keys,share=1.0):   # 粗估字数是否放得下（中文按字、西文按 2 字符≈1 字）
    def cnt(v):
        if isinstance(v,dict): return sum(cnt(x) for k,x in v.items() if k not in ('img','focus','src'))
        if isinstance(v,(list,tuple)): return sum(cnt(x) for x in v)
        s=str(v) if v is not None else ''; return sum(1 if ord(ch)>0x2e80 else .5 for ch in s)
    c=sum(cnt(p.get(k)) for k in keys); cap=1200*share*(1 if CJK else 1.1)*(14/CN.BS)**2   # 1200 字是 14px 网格的量；16px 约 920 字
    if c>cap: WARN.append(f'第{CURN}页 {p["layout"]}：正文约 {c:.0f} 字，这个版式大约放 {cap:.0f} 字 → 很可能溢出，建议拆成两页或换 GRID / TWO')
def VAR(name,k):   # 变体轮换：页上写 mirror: true/false 优先；否则相邻同版式自动换
    m=PCUR[0].get('mirror')
    return (1 if m else 0) if m is not None else RECIPE_PREV[1]%k
import canon as CN
CN.init(globals())
RECIPES=CN.RECIPES
import flow
LAY=dict(flow.LAYOUTS)   # 照片版式（flow.py）和 8 个内容版式（canon.py）共用一个网格、一套字号
LAY.update({k:(f,1) for k,f in RECIPES.items()})
# ---------------------------------------------------------------- build
n=1; prev=None; plan=[]; PIDX=[]   # PIDX：yaml 里第 i 个页面 → 成品第几页（在线编辑、图片清单用）
for i,p in enumerate(SPEC['pages']):
    lay=p.get('layout')
    if lay not in LAY: ERR.append(f'第{i+1}个页面: 未知 layout {lay}，可选 {list(LAY)}'); continue
    if CANVAS!='a4' and lay not in RECIPES: ERR.append(f'第{i+1}个页面: {lay} 是 A4 专用的照片版式；canvas: {CANVAS} 只能用内容版式 {list(RECIPES)}'); continue
    if CANVAS=='xhs' and LAY[lay][1]==2: ERR.append(f'第{i+1}个页面: 小红书画布是单页，不能用跨页 {lay}'); continue
    fn,span=LAY[lay]; PIDX.append([i,n,span])
    if lay=='PAPER' or (lay in RECIPES and lay!='FULL'): pass
    elif not p.get('image') and STYLE=='photo' and lay not in ('FULL','POSTER'): ERR.append(f'第{n}页 {lay}: 缺少 image（没照片时写 image: placeholder 先占位，或换无图风格 book.style，或用 layout: PAPER）'); n+=span; prev=lay; continue
    if span==2 and n%2==1: ERR.append(f'{lay} 从第{n}页开始，跨页左页必须是偶数页 → 在它前面增/减一页，或把前面的内容挪动')
    RECIPE_PREV[1]=RECIPE_PREV[1]+1 if lay==RECIPE_PREV[0] else 0; RECIPE_PREV[0]=lay; PCUR[0]=p
    if lay==prev and span==1 and lay in ('ONE','TWO','CARDS','STAGGER','COLLAGE','MIX'): print(f'提示：第{n}页与上一页同为 {lay}，已自动换镜像变体（不想要就写 mirror: false）')
    elif lay==prev and span==1 and lay not in ('POSTER','FULL'): print(f'提示：第{n}页与上一页版式相同（{lay}），建议换一种')
    if STYLE=='photo' and str(p.get('image','')).startswith('placeholder'): print(f'提示：第{n}页用的是占位底图（{p["image"]}），拿到照片后把 image 换成文件名即可')
    CURN=n
    try: fn(n,p)
    except Exception as e:
        ERR.append(f'第{n}页 {lay}: {type(e).__name__}: {e}')
        if os.environ.get('HB_DEBUG'): import traceback; traceback.print_exc()
    if lay not in RECIPES: SURF_HIST.append('image' if lay in ('POSTER','SPREAD_P','SPREAD_OPENER') else 'paper'); CN.used(SURF_HIST[-1])
    elif len(SURF_HIST)<len(plan)+1: SURF_HIST.append('paper')
    SN={'A':'A 色块','B':'B 色块','paper':'纸色','image':'照片'}
    plan.append(f'{n:02d}{"-%02d"%(n+1) if span==2 else "   "} {lay:14s} {"（内容版式 · 主底 "+SN.get(SURF_HIST[-1],SURF_HIST[-1])+"）" if lay in RECIPES else p.get("image","") or ("" if lay=="PAPER" else "（"+STYLE+" 底图）")}  {p.get("note","")}')
    n+=span; prev=lay
total=n-1
import brand_graphic
ERR.extend(brand_graphic.validate_spreads(BRAND_GRAPHICS, W))
if BK.get('binding') not in (None, 'saddle'): ERR.append('book.binding 目前支持 saddle（骑马钉）；其他装订方式不写此项')
if BK.get('binding')=='saddle' and total%4 and not os.environ.get('HB_PROOF'): ERR.append(f'骑马钉总页数须为4的倍数（含封面封底），当前{total}页 → 先统筹合页/拆页，不自动塞空白')
declared_chapters = [str(k) for k in BK.get('series', {}).get('chapters', {}).get('items', {})]
if declared_chapters and CHAPTERS != declared_chapters and not os.environ.get('HB_PROOF'): ERR.append(f'章节顺序不完整：登记{declared_chapters}，实际{CHAPTERS} → 检查合页后的chapter与可见章标')
CSS=open(os.path.join(HERE,'style.css'), encoding='utf-8').read()+open(os.path.join(HERE,'canon.css'), encoding='utf-8').read()+SD['css']+SD.get('ccss','')
if not CJK: CSS+='.op,.lt p{text-align:left}.fo span:first-child{letter-spacing:.18em}.cn-tx{text-align:left}.cn-tx:not(.cn-t20):not(.cn-t28):not(.cn-t40) p{text-wrap:pretty}.cn-disp{letter-spacing:-.015em}'   # 西文：左对齐（两端对齐会撑出大空格）；不自动断词（窄栏要断用 <wbr> / 软连字符）；正文段落 text-wrap:pretty 收过短末行（Chromium 117+；导语 cn-t20 与大字号 display 不加）
for k,v in dict(W=W,H=H-1,G=G,INK=INK,MUT=MUT,GOLD=GOLD,OCH=OCH,PAPER=PAPER).items(): CSS=CSS.replace('{'+k+'}',str(v))
# 字体：按本书实际用到的字裁切嵌入（见 fonts.py）
TEXT=_h.unescape(re.sub(r'<[^>]+>','',''.join(PP)))+str(BK.get('title',''))
FCSS,FROLES,FMISS=FONTS_.build_css(BK.get('fonts',SD['fonts']),TEXT,PROJ,CJK)
CSS=FCSS+CSS
JS=open(os.path.join(HERE,'fill.js'), encoding='utf-8').read()
TYPESETTING=BK.get('typesetting', 'grid')
if TYPESETTING not in ('grid', 'editorial') or (TYPESETTING == 'editorial' and CJK):
    raise SystemExit('ERROR: book.typesetting 可选 grid（默认）或 editorial（西文编辑式排印）')
open(os.path.join(PROJ,'book.html'),'w',encoding='utf-8').write(f'<!doctype html><html lang="{LANG}"><head><meta charset="utf-8"><title>{esc(BK.get("title","Handbook"))}</title><style>{CSS}</style></head><body class="st-{STYLE} m-{COLOR_MODE} ty-{TYPESETTING}" style="--bs:{CN.BS}px;--lh:{CN.LH}px;--gut:{CN.GUT}px;--s:{CN.S:.4f}" data-grid="{CN.TOP},{CN.LH},{CN.y(CN.LAST)},{W},{H},{CN.COL},{CN.GUT},{CN.LAST},{CN.IN},{CN.OUT}" data-canvas="{CANVAS}">{"".join(PP)}{JS}</body></html>')
os.makedirs(os.path.join(PROJ,'.qa'),exist_ok=True); json.dump(dict(slots=AISLOTS,scale=wash.S,colors=TH_,style=STYLE),open(os.path.join(PROJ,'.qa','ai_slots.json'),'w', encoding='utf-8'),ensure_ascii=False)
json.dump(dict(map=MAP,imgs=IMGS,local=LOCAL,clip=CLIP,paper=PAPER,flat=FLAT,use=USE,pidx=PIDX,W=W,H=H,canvas=CANVAS,color_mode=COLOR_MODE),open(os.path.join(PROJ,'map.json'),'w', encoding='utf-8'))
_used=set(re.findall(r'img/(slot_[0-9a-f]+\.jpg)',''.join(PP)))
for _f in os.listdir(os.path.join(PROJ,'img')):   # 删掉不再用到的旧图位缓存，免得源文件 zip 越来越大
    if _f.startswith('slot_') and _f not in _used: os.remove(os.path.join(PROJ,'img',_f))
_ad=os.path.join(PROJ,'.art')
if os.path.isdir(_ad):
    for _f in os.listdir(_ad):   # 删掉不再用的照片烘焙缓存（plate / slot 缓存各有自己的清理，只动 bake_*）
        if _f.startswith('bake_') and _f not in {f'bake_{k}.jpg' for k in BAKE_USED}: os.remove(os.path.join(_ad,_f))
for nm in IMGS: shutil.copy(os.path.join(PROJ,'img',nm.replace('.jpg','_base.jpg')),os.path.join(PROJ,'img',nm))
open(os.path.join(PROJ,'plan.txt'),'w', encoding='utf-8').write('\n'.join(plan)+'\n')
print('\n'.join(plan)); print(f'用色 {COLOR_MODE}：{MODE_WHY}'); print(f'风格 {STYLE} · 字体 ' + ' / '.join(f'{r}:{"+".join(v)}' for r,v in FROLES.items()))
print(f'== {total} 页', '（骑马钉需 4 的倍数，当前余 %d）'%(total%4) if total%4 else '（4 的倍数 ✓）')
if WARN:
    _w = list(dict.fromkeys(WARN)); print('\n'.join('注意：' + w for w in _w))
    open(os.path.join(PROJ, '.qa', 'warn.txt'), 'w', encoding='utf-8').write('\n'.join(_w) + '\n')   # 进 QA 报告（doctor 作为提示输出，不算失败）
if ERR: print('\n'.join('ERROR: '+e for e in ERR)); sys.exit(1)
