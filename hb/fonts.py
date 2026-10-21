#!/usr/bin/env python3
"""字体系统：系统衬线/无衬线先行顶上 + 后台静默下载推荐字体 + 按书裁切（subset）嵌入。

  python3 hb/fonts.py list                      # 列出所有字体、字体方案与本机状态
  python3 hb/fonts.py prefetch [方案或字体id …] # 后台非阻塞下载推荐字体（立即返回，不卡主流程）
  python3 hb/fonts.py fetch [方案或字体id …]    # 前台同步下载字体到缓存（默认下载全部方案用到的字体）
  python3 hb/fonts.py fetch inter               # 显式扩展无衬线字体

核心策略（零阻塞排版）：
1. 系统字体先行顶上：排版无非是衬线（Serif）、无衬线（Sans）、手写楷体（Hand/Kai）和窄体标签（Condensed）的组合。
   当推荐的开源字体尚未下载完成时，构建不等待网络，直接用本机自带的高质量系统字体（如苹方、宋体、楷体、SF Pro、Georgia、Baskerville、Didot）出图和排版。
2. 后台异步预取：建项目（new_project.sh）或首次构建遇到未缓存字体时，自动在后台拉起独立进程静默下载推荐字体到缓存目录 $HB_FONT_CACHE
   （默认 ~/.cache/handbook-designer/fonts；沙盒受限时回退 /tmp/handbook-designer-fonts），下载完成后下一轮构建自动无缝切换为内嵌子集字体。
3. 只读复用系统已装字体：查找时优先查缓存，其次只读扫描用户系统字体目录（~/Library/Fonts、/Library/Fonts 等），最后扫描 dev/fonts。
"""
import os, sys, io, re, json, time, hashlib, zipfile, shutil, tempfile, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUNDLED = os.path.join(HERE, 'fonts')
DEV_FONTS = os.path.join(ROOT, 'dev', 'fonts')


def _SelectWritableCache():
    """选择可写的独立字体缓存目录：优先 $HB_FONT_CACHE 或 ~/.cache/handbook-designer/fonts；沙盒不可写时回退到 /tmp。"""
    cands = []
    if os.environ.get('HB_FONT_CACHE'):
        cands.append(os.environ['HB_FONT_CACHE'])
    cands.append(os.path.join(os.path.expanduser('~'), '.cache', 'handbook-designer', 'fonts'))
    cands.append(os.path.join(tempfile.gettempdir(), 'handbook-designer-fonts'))
    for d in cands:
        try:
            os.makedirs(d, exist_ok=True)
            test_f = os.path.join(d, '.write_probe')
            open(test_f, 'w', encoding='utf-8').write('ok')
            os.remove(test_f)
            return d
        except OSError:
            continue
    return cands[-1]


CACHE = _SelectWritableCache()

SYS_FONT_DIRS = [
    os.path.join(os.path.expanduser('~'), 'Library', 'Fonts'),
    '/Library/Fonts',
    os.path.join(os.path.expanduser('~'), '.local', 'share', 'fonts'),
    '/usr/local/share/fonts',
    '/usr/share/fonts',
]
READ_DIRS = [CACHE, '/Users/apple/.cache/handbook-designer/fonts', BUNDLED] + SYS_FONT_DIRS + [DEV_FONTS]

GF = 'https://raw.githubusercontent.com/google/fonts/main/ofl/'
GFJ = 'https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/'
WK = 'https://github.com/lxgw/LxgwWenkaiGB/releases/latest/download/'

FONTS = {
  'playfair':        dict(name='Playfair Display', zh='高对比衬线标题', file='PlayfairDisplay-VF.ttf', w=(400, 900), mb=1,
                          urls=[GF + 'playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf', GFJ + 'playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf'],
                          sys=['Playfair Display', 'Didot', 'Bodoni 72', 'Baskerville', 'Georgia', 'Times New Roman']),
  'playfair-italic': dict(name='Playfair Display Italic', zh='衬线斜体', file='PlayfairDisplay-Italic-VF.ttf', w=(400, 900), italic=True, mb=1,
                          urls=[GF + 'playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf', GFJ + 'playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf'],
                          sys=['Playfair Display', 'Didot', 'Bodoni 72', 'Baskerville', 'Georgia', 'Times New Roman']),
  'eb-garamond':     dict(name='EB Garamond', zh='经典 Garamond 正文衬线', file='EBGaramond-VF.ttf', w=(400, 800), mb=1,
                          urls=[GF + 'ebgaramond/EBGaramond%5Bwght%5D.ttf', GFJ + 'ebgaramond/EBGaramond%5Bwght%5D.ttf'],
                          sys=['EB Garamond', 'Garamond', 'Baskerville', 'Palatino', 'Georgia', 'Times New Roman']),
  'eb-garamond-italic': dict(name='EB Garamond Italic', zh='Garamond 斜体', file='EBGaramond-Italic-VF.ttf', w=(400, 800), italic=True, mb=1,
                          urls=[GF + 'ebgaramond/EBGaramond-Italic%5Bwght%5D.ttf', GFJ + 'ebgaramond/EBGaramond-Italic%5Bwght%5D.ttf'],
                          sys=['EB Garamond', 'Garamond', 'Baskerville', 'Palatino', 'Georgia', 'Times New Roman']),
  'inter':           dict(name='Inter', zh='现代无衬线（界面与正文）', file='Inter-VF.ttf', w=(100, 900), mb=1,
                          urls=[GF + 'inter/Inter%5Bopsz,wght%5D.ttf', GFJ + 'inter/Inter%5Bopsz,wght%5D.ttf'],
                          sys=['Inter', '-apple-system', 'BlinkMacSystemFont', 'SF Pro Text', 'SF Pro Display', 'Helvetica Neue', 'Arial']),
  'jetbrains-mono': dict(name='JetBrains Mono', zh='等宽元数据与小标签', file='JetBrainsMono-VF.ttf', w=(100, 800), mb=1,
                          urls=[GF + 'jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf', GFJ + 'jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf'],
                          sys=['JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas']),
  'geist':           dict(name='Geist', zh='当代几何无衬线（Vercel 出品，弥散/科技感标题与正文）', file='Geist-VF.ttf', w=(100, 900), mb=1,
                          urls=[GF + 'geist/Geist%5Bwght%5D.ttf', GFJ + 'geist/Geist%5Bwght%5D.ttf'],
                          sys=['Geist', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'Helvetica Neue', 'Arial']),
  'comfortaa':       dict(name='Comfortaa', zh='圆润几何无衬线（亲和、科技感）', file='Comfortaa-VF.ttf', w=(300, 700), mb=1,
                          urls=[GF + 'comfortaa/Comfortaa%5Bwght%5D.ttf', GFJ + 'comfortaa/Comfortaa%5Bwght%5D.ttf'],
                          sys=['Comfortaa', 'Avenir Next', 'Arial Rounded MT Bold', '-apple-system', 'Helvetica Neue', 'Arial']),
  'oswald':          dict(name='Oswald', zh='窄体无衬线（小标签）', file='Oswald-VF.ttf', w=(200, 700), mb=1,
                          urls=[GF + 'oswald/Oswald%5Bwght%5D.ttf', GFJ + 'oswald/Oswald%5Bwght%5D.ttf'],
                          sys=['Oswald', 'DIN Condensed', 'Avenir Next Condensed', 'Arial Narrow', 'Helvetica Neue', 'Arial']),
  'source-serif-4':  dict(name='Source Serif 4', zh='Adobe 印刷级正文衬线（光学尺寸）', file='SourceSerif4-VF.ttf', w=(200, 900), mb=1,
                          urls=[GF + 'sourceserif4/SourceSerif4%5Bopsz,wght%5D.ttf', GFJ + 'sourceserif4/SourceSerif4%5Bopsz,wght%5D.ttf'],
                          sys=['Source Serif 4', 'Source Serif Pro', 'Charter', 'Baskerville', 'Palatino', 'Georgia', 'Times New Roman']),
  'source-serif-4-italic': dict(name='Source Serif 4 Italic', zh='Source Serif 斜体', file='SourceSerif4-Italic-VF.ttf', w=(200, 900), italic=True, mb=1,
                          urls=[GF + 'sourceserif4/SourceSerif4-Italic%5Bopsz,wght%5D.ttf', GFJ + 'sourceserif4/SourceSerif4-Italic%5Bopsz,wght%5D.ttf'],
                          sys=['Source Serif 4', 'Source Serif Pro', 'Charter', 'Baskerville', 'Palatino', 'Georgia', 'Times New Roman']),
  'libre-baskerville': dict(name='Libre Baskerville', zh='Baskerville 复刻，小字号清晰', file='LibreBaskerville-VF.ttf', w=(400, 700), mb=1,
                          urls=[GF + 'librebaskerville/LibreBaskerville%5Bwght%5D.ttf', GFJ + 'librebaskerville/LibreBaskerville%5Bwght%5D.ttf'],
                          sys=['Libre Baskerville', 'Baskerville', 'Palatino', 'Georgia', 'Times New Roman']),
  'ibm-plex-sans':   dict(name='IBM Plex Sans', zh='IBM 无衬线，理性有个性', file='IBMPlexSans-VF.ttf', w=(100, 700), mb=1,
                          urls=[GF + 'ibmplexsans/IBMPlexSans%5Bwdth,wght%5D.ttf', GFJ + 'ibmplexsans/IBMPlexSans%5Bwdth,wght%5D.ttf'],
                          sys=['IBM Plex Sans', '-apple-system', 'SF Pro Text', 'Helvetica Neue', 'Arial']),
  'caveat':          dict(name='Caveat', zh='自然手写体', file='Caveat-VF.ttf', w=(400, 700), mb=1,
                          urls=[GF + 'caveat/Caveat%5Bwght%5D.ttf', GFJ + 'caveat/Caveat%5Bwght%5D.ttf'],
                          sys=['Caveat', 'Bradley Hand', 'Chalkboard SE', 'Snell Roundhand', 'Comic Sans MS']),
  'noto-serif-sc':   dict(name='思源宋体 Noto Serif SC', zh='中文衬线（宋体）', file='NotoSerifSC-VF.ttf', w=(200, 900), mb=24,
                          urls=[GF + 'notoserifsc/NotoSerifSC%5Bwght%5D.ttf', GFJ + 'notoserifsc/NotoSerifSC%5Bwght%5D.ttf'],
                          sys=['Noto Serif CJK SC', 'Source Han Serif SC', 'Noto Serif SC', 'Songti SC', 'STSong', 'SimSun']),
  'noto-sans-sc':    dict(name='思源黑体 Noto Sans SC', zh='中文无衬线（黑体）', file='NotoSansSC-VF.ttf', w=(100, 900), mb=17,
                          urls=[GF + 'notosanssc/NotoSansSC%5Bwght%5D.ttf', GFJ + 'notosanssc/NotoSansSC%5Bwght%5D.ttf'],
                          sys=['Noto Sans CJK SC', 'Source Han Sans SC', 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans GB', 'Heiti SC', 'Microsoft YaHei']),
  'lxgw-neo-xihei':  dict(name='霞鹜新晰黑 LXGW Neo XiHei', zh='中文黑体，比思源更有书卷味（只有常规体）', file='LXGWNeoXiHei.ttf', w=(1, 599), mb=8, license='IPA',
                          urls=['https://github.com/lxgw/LxgwNeoXiHei/releases/latest/download/LXGWNeoXiHei.ttf'],
                          sys=['LXGW Neo XiHei', '霞鹜新晰黑', 'PingFang SC', 'Hiragino Sans GB', 'Noto Sans CJK SC', 'Source Han Sans SC', 'Microsoft YaHei'], bold='noto-sans-sc'),
  'lxgw-neo-zhisong': dict(name='霞鹜新致宋 LXGW Neo ZhiSong', zh='中文宋体，端正雅致（只有常规体）', file='LXGWNeoZhiSong.ttf', w=(1, 599), mb=11, license='IPA',
                          urls=['https://github.com/lxgw/LxgwNeoZhiSong/releases/latest/download/LXGWNeoZhiSong.ttf'],
                          sys=['LXGW Neo ZhiSong', '霞鹜新致宋', 'Songti SC', 'STSong', 'Noto Serif CJK SC', 'Source Han Serif SC', 'SimSun'], bold='noto-serif-sc'),
  'lxgw-wenkai':     dict(name='霞鹜文楷 GB LXGW WenKai GB', zh='中文手写楷体，大陆规范字形（正文可用）', file='LXGWWenKaiGB-Regular.ttf', w=(1, 499), mb=26,
                          urls=[WK + 'LXGWWenKaiGB-Regular.ttf'], sys=['LXGW WenKai GB', 'LXGW WenKai', '霞鹜文楷', 'Kaiti SC', 'STKaiti', 'KaiTi', 'Songti SC'],
                          pair='lxgw-wenkai-medium'),
  'lxgw-wenkai-medium': dict(name='霞鹜文楷 GB Medium', zh='文楷粗体（标题）', file='LXGWWenKaiGB-Medium.ttf', w=(500, 1000), mb=26,
                          urls=[WK + 'LXGWWenKaiGB-Medium.ttf'], sys=['LXGW WenKai GB Medium', 'LXGW WenKai GB', 'Kaiti SC', 'STKaiti', 'KaiTi', 'Songti SC'], family_of='lxgw-wenkai'),
  'lxgw-marker-gothic': dict(name='霞鹜漫黑 LXGW Marker Gothic', zh='中文马克笔圆头黑体（亲和标题）', file='LXGWMarkerGothic-Regular.ttf', w=(1, 1000), mb=3,
                          urls=[GF + 'lxgwmarkergothic/LXGWMarkerGothic-Regular.ttf', GFJ + 'lxgwmarkergothic/LXGWMarkerGothic-Regular.ttf'],
                          sys=['LXGW Marker Gothic', '霞鹜漫黑', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei']),
  'smiley-sans':     dict(name='得意黑 Smiley Sans', zh='中文海报标题（斜体窄黑）', file='SmileySans-Oblique.ttf', w=(1, 1000), mb=6,
                          urls=['https://github.com/atelier-anchor/smiley-sans/releases/download/v2.0.1/smiley-sans-v2.0.1.zip'],
                          sys=['Smiley Sans', '得意黑', 'PingFang SC', 'Heiti SC', 'Microsoft YaHei']),
  'zcool-kuaile':    dict(name='站酷快乐体 ZCOOL KuaiLe', zh='中文童趣标题（低幼）', file='ZCOOLKuaiLe-Regular.ttf', w=(1, 1000), mb=2,
                          urls=[GF + 'zcoolkuaile/ZCOOLKuaiLe-Regular.ttf', GFJ + 'zcoolkuaile/ZCOOLKuaiLe-Regular.ttf'],
                          sys=['ZCOOL KuaiLe', 'Kaiti SC', 'PingFang SC']),
  'ma-shan-zheng':   dict(name='马善政楷书 Ma Shan Zheng', zh='中文毛笔楷书标题', file='MaShanZheng-Regular.ttf', w=(1, 1000), mb=6,
                          urls=[GF + 'mashanzheng/MaShanZheng-Regular.ttf', GFJ + 'mashanzheng/MaShanZheng-Regular.ttf'],
                          sys=['Ma Shan Zheng', 'Kaiti SC', 'STKaiti', 'KaiTi']),
}

PRESETS = {
  'magazine': dict(zh='思源混排：宋体标题、黑体正文', title=['noto-serif-sc'],
                   body=['noto-sans-sc'], label=['noto-sans-sc'], accent=['noto-serif-sc'],
                   css=dict(title_w=900, body_w=400, accent_style='normal', label_case='uppercase', label_track='.18em', label_scale=1, accent_w=500)),
  'natgeo': dict(zh='国家地理社论：Playfair + 思源宋体标题、Oswald 眉标、黑体正文', title=['playfair', 'noto-serif-sc'],
                 body=['noto-sans-sc'], label=['oswald', 'noto-sans-sc'], accent=['playfair-italic', 'noto-serif-sc'],
                 css=dict(title_w=800, body_w=400, accent_style='italic', label_case='uppercase', label_track='.24em', label_scale=1.05, accent_w=500)),
  'swiss': dict(zh='思源黑体：共享粗细排印', title=['noto-sans-sc'], body=['noto-sans-sc'],
                label=['noto-sans-sc'], accent=['noto-sans-sc'],
                css=dict(title_w=200, body_w=400, accent_style='normal', label_case='uppercase', label_track='.12em', label_scale=1, accent_w=300)),
  'sans': dict(zh='思源黑体', title=['noto-sans-sc'], body=['noto-sans-sc'], label=['noto-sans-sc'], accent=['noto-sans-sc'],
               css=dict(title_w=900, body_w=400, accent_style='normal', label_case='uppercase', label_track='.12em', label_scale=1, accent_w=500)),
  'serif': dict(zh='思源宋体', title=['noto-serif-sc'], body=['noto-serif-sc'], label=['noto-sans-sc'], accent=['noto-serif-sc'],
                css=dict(title_w=900, body_w=400, accent_style='normal', label_case='uppercase', label_track='.12em', label_scale=1, accent_w=500)),
  'wenkai': dict(zh='霞鹜文楷：人文手写楷体配宋体标题', title=['playfair', 'lxgw-wenkai-medium'],
                 body=['lxgw-wenkai'], label=['oswald', 'noto-sans-sc'], accent=['playfair-italic', 'lxgw-wenkai'],
                 css=dict(title_w=700, body_w=400, accent_style='italic', label_case='uppercase', label_track='.16em', label_scale=1, accent_w=500)),
}

ROLES = ('title', 'body', 'label', 'accent')

def typography(style, mode=None):
    mode = mode or ('light' if style == 'swiss' else 'bold')
    if mode not in ('bold', 'light'): raise SystemExit('ERROR: book.typography 可选 bold（厚重型）/ light（轻盈型）')
    return mode

def for_style(spec, style, mode=None, display_weight=None):
    """同一份字体配置用于屏幕、普通 PDF 和可编辑 PDF。"""
    from styles import STYLES
    spec = spec or STYLES[style]['fonts']
    out = dict(preset=spec) if isinstance(spec, str) else dict(spec)
    mode = typography(style, mode)
    weight = 200 if mode == 'light' else 900
    if display_weight is not None:
        if mode != 'light' or str(display_weight) not in ('100', '200'):
            raise SystemExit('ERROR: book.display_weight 可在 typography: light 时选 100 / 200；正文不随之变细')
        weight = int(display_weight)
    out['css'] = dict(out.get('css', {}), weight_scale=mode, display_w=weight, title_w=weight, body_w=400)
    if mode == 'light':
        roles, _ = resolve(out)
        bad = [f for f in roles['title'] if FONTS[f]['w'][0] > weight]
        if bad:
            hint = ('100 可用 noto-sans-sc / inter；思源宋体或 Source Serif 4 最低 200'
                    if weight == 100 else
                    '200 可用 noto-serif-sc / source-serif-4 / noto-sans-sc / inter')
            raise SystemExit(f'ERROR: 标题字体不支持真实{weight}字重：{", ".join(bad)} → {hint}')
    return out


def path_of(fid):
    f = FONTS[fid]
    for d in READ_DIRS:
        if not d or not os.path.isdir(d):
            continue
        p = os.path.join(d, f['file'])
        if os.path.exists(p) and os.path.getsize(p) > 10000:
            return p
    return None


def _is_fetching(fid):
    lk = os.path.join(CACHE, f'.{fid}.fetching')
    if os.path.exists(lk):
        try:
            if time.time() - os.path.getmtime(lk) < 600:
                return True
            os.remove(lk)
        except OSError:
            pass
    return False


def fetch(fid, quiet=False, timeout=180):
    f = FONTS[fid]
    if path_of(fid): return path_of(fid)
    os.makedirs(CACHE, exist_ok=True); dst = os.path.join(CACHE, f['file'])
    lk = os.path.join(CACHE, f'.{fid}.fetching')
    if _is_fetching(fid):
        return None
    try:
        open(lk, 'w', encoding='utf-8').write(str(os.getpid()))
    except OSError:
        pass
    try:
        for url in f.get('urls', []):
            try:
                if not quiet: print(f'  下载 {f["name"]}（约 {f.get("mb", "?")}MB）← {url.split("/")[2]}', flush=True)
                req = urllib.request.Request(url, headers={'User-Agent': 'handbook-designer'})
                data = urllib.request.urlopen(req, timeout=timeout).read()
                if url.endswith('.zip'):
                    z = zipfile.ZipFile(io.BytesIO(data)); data = z.read(next(n for n in z.namelist() if n.endswith(f['file'])))
                if data[:4] not in (b'\x00\x01\x00\x00', b'OTTO', b'true'): raise ValueError('不是字体文件')
                open(dst + '.part', 'wb').write(data); os.replace(dst + '.part', dst); return dst
            except Exception as e:
                if not quiet: print(f'    失败：{type(e).__name__} {str(e)[:80]}')
        return None
    finally:
        try:
            if os.path.exists(lk): os.remove(lk)
        except OSError:
            pass


def prefetch_bg(want=None):
    if os.environ.get('HB_NO_FETCH'):
        return []
    want = want or list(PRESETS)
    ids = []
    for w in want:
        if w in PRESETS:
            ids += [x for r in ROLES for x in PRESETS[w][r]]
        elif w in FONTS:
            ids.append(w)
    ids = list(dict.fromkeys(
        i for x in ids for i in (
            [x]
            + ([FONTS[x]['pair']] if FONTS[x].get('pair') else [])
            + ([FONTS[x]['bold']] if FONTS[x].get('bold') else [])
        )
    ))
    todo = [i for i in ids if not path_of(i) and not _is_fetching(i)]
    if not todo:
        return []
    try:
        subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), 'fetch', '--quiet'] + todo,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass
    return todo


def resolve(spec, cjk=True):
    spec = spec or 'magazine'
    if isinstance(spec, str): spec = {'preset': spec}
    pre = PRESETS.get(spec.get('preset', 'magazine'))
    if pre is None: raise SystemExit(f"ERROR: 未知字体方案 {spec.get('preset')}，可选 {list(PRESETS)}")
    roles = {r: list(pre[r]) for r in ROLES}
    for r in ROLES:
        if r in spec:
            v = spec[r]; v = [v] if isinstance(v, str) else list(v)
            bad = [x for x in v if x not in FONTS]
            if bad: raise SystemExit(f'ERROR: 未知字体 {bad}，可选 {list(FONTS)}')
            roles[r] = v
    for r, ids in roles.items():
        for x in list(ids):
            if FONTS[x].get('pair') and FONTS[x]['pair'] not in ids: ids.insert(ids.index(x) + 1, FONTS[x]['pair'])
    return roles, dict(pre['css'], **spec.get('css', {}))

WEIGHTS = (100, 200, 250, 300, 400, 500, 600, 700, 800, 900)


def _subset(src, outs, text, fid, flavor=None):
    from fontTools import subset
    from fontTools.ttLib import TTFont
    opt = subset.Options(); opt.name_IDs = ['*']; opt.notdef_outline = True
    opt.layout_features += ['palt', 'halt', 'pwid']
    opt.drop_tables += ['DSIG']
    f = TTFont(src, lazy=False)
    s = subset.Subsetter(opt); s.populate(text=text); s.subset(f)
    nm = 'HB Subset ' + fid
    def rename(t, suffix=''):
        for rec in t['name'].names:
            if rec.nameID in (1, 3, 4, 6, 16, 17, 21, 22):
                rec.string = ((nm + suffix).replace(' ', '') if rec.nameID == 6 else nm + suffix)
    if flavor is None:
        flavor = 'woff2'
        try: import brotli  # noqa
        except ImportError: flavor = 'woff'
    if flavor == 'ttf': flavor = None
    if 'fvar' not in f:
        rename(f); f.flavor = flavor; f.save(outs[None]); return
    from fontTools.varLib import instancer
    import copy
    axes = {a.axisTag: a.defaultValue for a in f['fvar'].axes}
    for w, out in outs.items():
        loc = dict(axes, wght=w)
        g = instancer.instantiateVariableFont(copy.deepcopy(f), loc, updateFontNames=False)
        if 'OS/2' in g: g['OS/2'].usWeightClass = int(w)
        rename(g, f' {w}'); g.flavor = flavor; g.save(out)


def build_css(spec, text, proj, cjk=True, log=print, fmt=None, only=None):
    roles, css = resolve(spec, cjk)
    od = os.path.join(proj, 'fonts'); os.makedirs(od, exist_ok=True)
    text = ''.join(sorted(set(text + ''.join(chr(c) for c in range(32, 127)) + '·—–“”‘’…、，。：；！？（）《》「」『』【】0123456789')))
    key = hashlib.md5((text + 'v3-' + str(css.get('weight_scale', 'standard')) + ('-100' if css.get('display_w') == 100 else '')).encode()).hexdigest()[:10]
    faces = []; files = {}; missing = []
    want = list(dict.fromkeys(f for ids in roles.values() for f in ids))
    want += [FONTS[f]['bold'] for f in want if FONTS[f].get('bold') and FONTS[f]['bold'] not in want]
    try:
        import fontTools  # noqa
        has_ft = True
    except ImportError:
        has_ft = False
    try: import brotli; ext = 'woff2'  # noqa
    except ImportError: ext = 'woff'
    if fmt == 'ttf' or not has_ft: ext = 'ttf'
    for fid in want:
        src = path_of(fid)
        if not src and os.environ.get('HB_SYNC_FETCH') and not os.environ.get('HB_NO_FETCH'):
            src = fetch(fid, quiet=False, timeout=60)
        if not src:
            missing.append(fid)
            continue
        lo, hi = FONTS[fid]['w']
        if not has_ft:
            out_p = os.path.join(od, f'hb-{fid}-x-{key}.ttf')
            if not os.path.exists(out_p):
                for old in os.listdir(od):
                    if old.startswith(f'hb-{fid}-'): os.remove(os.path.join(od, old))
                shutil.copy(src, out_p)
            files[fid] = {None: os.path.basename(out_p)}
            continue
        from fontTools.ttLib import TTFont
        var = 'fvar' in TTFont(src, lazy=True)
        ws = [w for w in WEIGHTS if lo <= w <= hi and (w >= 400 or css.get('weight_scale') == 'light' and (w >= 200 or css.get('display_w') == 100))] if var else [None]
        if var and not ws: ws = [lo]
        if var and only is not None: ws = [w for w in ws if w in only.get(fid, set())] or ws[:1]
        outs = {w: os.path.join(od, f'hb-{fid}-{w or "x"}-{key}.{ext}') for w in ws}
        if not all(os.path.exists(o) for o in outs.values()):
            for old in os.listdir(od):
                if old.startswith(f'hb-{fid}-'): os.remove(os.path.join(od, old))
            _subset(src, outs, text, fid, 'ttf' if fmt == 'ttf' else None)
        files[fid] = {w: os.path.basename(o) for w, o in outs.items()}
    if missing and not os.environ.get('HB_NO_FETCH'):
        prefetch_bg(missing)
    def face(fam, fn, lo, hi, italic=False):
        return (f"@font-face{{font-family:'{fam}';src:url(fonts/{fn}) format('{'truetype' if ext == 'ttf' else ext}');"
                f"font-weight:{lo}{'' if hi is None else ' ' + str(hi)};font-style:{'italic' if italic else 'normal'};font-display:block}}")
    for fid, fw in files.items():
        f = FONTS[fid]; lo, hi = f['w']; fam = 'HB-' + f.get('family_of', fid)
        for w, fn in fw.items():
            faces.append(face(fam, fn, lo, hi, f.get('italic')) if w is None else face(fam, fn, w, None, f.get('italic')))
        if f.get('bold') and f['bold'] in files:
            for w, fn in files[f['bold']].items():
                if w is None: faces.append(face('HB-' + fid, fn, 600, 1000))
                elif w >= 600: faces.append(face('HB-' + fid, fn, w, None))
    lic = ['本目录的字体文件是按本书用字裁切的子集（内部名称已改为 HB Subset …），仅供本书显示与打印使用。', '']
    for fid in files:
        f = FONTS[fid]
        if f.get('license') == 'IPA':
            lic.append(f"- {f['name']}：IPA Font License 1.0（https://opensource.org/licenses/IPA）。衍生自 IPA 字体，"
                       "原始字体可从 https://moji.or.jp/ipafont/ipafontdownload/ 获取并替换。")
        else:
            lic.append(f"- {f['name']}：SIL Open Font License 1.1（https://openfontlicense.org）")
    open(os.path.join(od, 'LICENSES.txt'), 'w', encoding='utf-8').write('\n'.join(lic) + '\n')
    if missing:
        log('提示：当前先用系统自带衬线/无衬线字体顶上，后台正在静默下载推荐字体：' + '、'.join(FONTS[m]['name'] for m in missing)
            + f'\n      （如需等待下载完成再导出：python3 {os.path.join(HERE, "fonts.py")} fetch ' + ' '.join(sorted(set(FONTS[m].get('family_of', m) for m in missing))) + '）')
    def stack(ids, generic):
        out = []
        for fid in ids:
            fam = 'HB-' + FONTS[fid].get('family_of', fid)
            if fid not in missing and f"'{fam}'" not in out: out.append(f"'{fam}'")
            for s in FONTS[fid]['sys']:
                if f'"{s}"' not in out: out.append(f'"{s}"')
        return ','.join(out + [generic])
    v = {'--f-title': stack(roles['title'], 'serif'), '--f-body': stack(roles['body'], 'sans-serif'),
         '--f-label': stack(roles['label'], 'sans-serif'), '--f-accent': stack(roles['accent'], 'serif'),
         '--display-w': css.get('display_w', css.get('title_w', 900)), '--title-w': css.get('title_w', 900), '--body-w': css.get('body_w', 400), '--accent-style': css.get('accent_style', 'italic'),
         '--accent-w': css.get('accent_w', 700), '--label-case': css.get('label_case', 'uppercase'),
         '--label-track': css.get('label_track', '.26em'), '--label-scale': css.get('label_scale', 1)}
    return ''.join(faces) + ':root{' + ';'.join(f'{k}:{x}' for k, x in v.items()) + '}', roles, missing


def _status(fid):
    p = path_of(fid)
    if p:
        if p.startswith(DEV_FONTS):
            return '已就绪（dev/fonts）'
        if any(p.startswith(sd) for sd in SYS_FONT_DIRS):
            return '已就绪（系统字体复用）'
        return '已缓存'
    if _is_fetching(fid):
        return '后台下载中…（当前由系统字体顶上）'
    return f'未下载（由系统字体顶上，后台可下约 {FONTS[fid].get("mb", "?")}MB）'


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'list':
        print(f'写入缓存目录：{CACHE}\n\n字体（全部开源免费、可商用、可嵌入 PDF；未缓存时先用系统衬线/无衬线字体顶上，同时后台静默下载）：')
        for k, f in FONTS.items(): print(f'  {k:20s} {f["name"]:28s} {f["zh"]:20s} {_status(k)}')
        print('\n字体方案（book.fonts）：')
        for k, p in PRESETS.items(): print(f'  {k:10s} {p["zh"]}\n             ' + ' | '.join(f'{r}: {"+".join(p[r])}' for r in ROLES))
    elif cmd == 'prefetch':
        started = prefetch_bg(sys.argv[2:] or list(PRESETS))
        if started:
            print(f'已在后台启动 {len(started)} 个推荐字体的静默下载（当前构建先用系统字体顶上，不阻塞流程）')
        else:
            print('推荐字体均已就绪或正在后台下载中')
    elif cmd == 'fetch':
        args = [x for x in sys.argv[2:] if x != '--quiet']
        quiet = '--quiet' in sys.argv[2:]
        want = args or list(PRESETS)
        ids = []
        for w in want:
            if w in PRESETS: ids += [x for r in ROLES for x in PRESETS[w][r]]
            elif w in FONTS: ids.append(w)
            else: sys.exit(f'未知方案/字体：{w}')
        ids = list(dict.fromkeys(
            i for x in ids for i in (
                [x]
                + ([FONTS[x]['pair']] if FONTS[x].get('pair') else [])
                + ([FONTS[x]['bold']] if FONTS[x].get('bold') else [])
            )
        ))
        bad = [i for i in ids if not fetch(i, quiet=quiet)]
        if not quiet:
            print('完成' if not bad else f'以下字体下载失败（将继续使用系统字体顶上）：{bad}')
        sys.exit(1 if bad else 0)
    else:
        sys.exit(__doc__)
