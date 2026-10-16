#!/usr/bin/env python3
"""字体系统：开源字体登记表 + 按需下载 + 按书裁切（subset）嵌入。

  python3 hb/fonts.py list                    # 列出所有字体、字体方案与本机状态
  python3 hb/fonts.py fetch [方案或字体id …]   # 下载中文字体到缓存（默认下载全部方案用到的字体）
  python3 hb/fonts.py fetch hand              # 只下载“手写”方案需要的字体

所有字体都是开源、可免费商用、可嵌入文档的（SIL OFL 1.1；霞鹜新晰黑/新致宋为 IPA Font License 1.0，PDF 与印刷嵌入明确允许）。西文字体随 skill 附带；
中文字体体积大（每个 5–25MB），首次使用时下载到缓存目录 $HB_FONT_CACHE（默认 ~/.cache/handbook-designer/fonts），
也可以手动把文件放进该目录。构建时只截取本书用到的字，嵌进 HTML/PDF，并改掉内部字体名（OFL 对修改版的要求）。
下载不到时自动回退到系统字体（如本机的 Noto CJK / 苹方 / 宋体），并给出提示，不会中断构建。
"""
import os, sys, io, re, json, hashlib, zipfile, shutil, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLED = os.path.join(HERE, 'fonts')
CACHE = os.environ.get('HB_FONT_CACHE') or os.path.join(os.path.expanduser('~'), '.cache', 'handbook-designer', 'fonts')
GF = 'https://raw.githubusercontent.com/google/fonts/main/ofl/'
GFJ = 'https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/'          # 同一仓库的 jsDelivr 镜像（国内通常可访问）
WK = 'https://github.com/lxgw/LxgwWenkaiGB/releases/latest/download/'   # 文楷 GB：大陆规范字形（教材、学校用更合适）

# id: 名称、文件、来源、权重范围、斜体、系统回退名
FONTS = {
  # ---- 西文（随 skill 附带）
  'playfair':        dict(name='Playfair Display', zh='高对比衬线标题', file='PlayfairDisplay-VF.ttf', bundled=True, w=(400, 900), sys=['Playfair Display', 'Georgia']),
  'playfair-italic': dict(name='Playfair Display Italic', zh='衬线斜体', file='PlayfairDisplay-Italic-VF.ttf', bundled=True, w=(400, 900), italic=True, sys=['Playfair Display', 'Georgia']),
  'eb-garamond':     dict(name='EB Garamond', zh='经典 Garamond 正文衬线', file='EBGaramond-VF.ttf', bundled=True, w=(400, 800), sys=['EB Garamond', 'Garamond', 'Georgia']),
  'eb-garamond-italic': dict(name='EB Garamond Italic', zh='Garamond 斜体', file='EBGaramond-Italic-VF.ttf', bundled=True, w=(400, 800), italic=True, sys=['EB Garamond', 'Garamond', 'Georgia']),
  'inter':           dict(name='Inter', zh='现代无衬线（界面与正文）', file='Inter-VF.ttf', bundled=True, w=(100, 900), sys=['Inter', 'Helvetica Neue', 'Arial']),
  'geist':           dict(name='Geist', zh='当代几何无衬线（Vercel 出品，弥散/科技感标题与正文）', file='Geist-VF.ttf', bundled=True, w=(100, 900), sys=['Geist', 'Inter', 'Helvetica Neue', 'Arial']),
  'comfortaa':       dict(name='Comfortaa', zh='圆润几何无衬线（亲和、科技感）', file='Comfortaa-VF.ttf', bundled=True, w=(300, 700), sys=['Comfortaa', 'Nunito', 'Arial Rounded MT Bold']),
  'oswald':          dict(name='Oswald', zh='窄体无衬线（小标签）', file='Oswald-VF.ttf', bundled=True, w=(200, 700), sys=['Oswald', 'Arial Narrow']),
  'source-serif-4':  dict(name='Source Serif 4', zh='Adobe 印刷级正文衬线（光学尺寸）', file='SourceSerif4-VF.ttf', bundled=True, w=(200, 900), sys=['Source Serif 4', 'Source Serif Pro', 'Georgia']),
  'source-serif-4-italic': dict(name='Source Serif 4 Italic', zh='Source Serif 斜体', file='SourceSerif4-Italic-VF.ttf', bundled=True, w=(200, 900), italic=True, sys=['Source Serif 4', 'Georgia']),
  'libre-baskerville': dict(name='Libre Baskerville', zh='Baskerville 复刻，小字号清晰', file='LibreBaskerville-VF.ttf', w=(400, 700), mb=1,
                          urls=[GF + 'librebaskerville/LibreBaskerville%5Bwght%5D.ttf', GFJ + 'librebaskerville/LibreBaskerville%5Bwght%5D.ttf'], sys=['Libre Baskerville', 'Baskerville', 'Georgia']),
  'ibm-plex-sans':   dict(name='IBM Plex Sans', zh='IBM 无衬线，理性有个性', file='IBMPlexSans-VF.ttf', w=(100, 700), mb=1,
                          urls=[GF + 'ibmplexsans/IBMPlexSans%5Bwdth,wght%5D.ttf', GFJ + 'ibmplexsans/IBMPlexSans%5Bwdth,wght%5D.ttf'], sys=['IBM Plex Sans', 'Helvetica Neue', 'Arial']),
  'caveat':          dict(name='Caveat', zh='自然手写体', file='Caveat-VF.ttf', bundled=True, w=(400, 700), sys=['Caveat']),
  # ---- 中文（按需下载）
  'noto-serif-sc':   dict(name='思源宋体 Noto Serif SC', zh='中文衬线（宋体）', file='NotoSerifSC-VF.ttf', w=(200, 900), mb=24,
                          urls=[GF + 'notoserifsc/NotoSerifSC%5Bwght%5D.ttf', GFJ + 'notoserifsc/NotoSerifSC%5Bwght%5D.ttf'],
                          sys=['Noto Serif CJK SC', 'Source Han Serif SC', 'Noto Serif SC', 'Songti SC', 'STSong', 'SimSun']),
  'noto-sans-sc':    dict(name='思源黑体 Noto Sans SC', zh='中文无衬线（黑体）', file='NotoSansSC-VF.ttf', w=(100, 900), mb=17,
                          urls=[GF + 'notosanssc/NotoSansSC%5Bwght%5D.ttf', GFJ + 'notosanssc/NotoSansSC%5Bwght%5D.ttf'],
                          sys=['Noto Sans CJK SC', 'Source Han Sans SC', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei']),
  # 霞鹜新晰黑 / 新致宋：IPA 字体衍生，许可为 IPA Font License 1.0（可商用，PDF/印刷嵌入明确允许）。只有常规体，粗体自动借用思源
  'lxgw-neo-xihei':  dict(name='霞鹜新晰黑 LXGW Neo XiHei', zh='中文黑体，比思源更有书卷味（只有常规体）', file='LXGWNeoXiHei.ttf', w=(1, 599), mb=8, license='IPA',
                          urls=['https://github.com/lxgw/LxgwNeoXiHei/releases/latest/download/LXGWNeoXiHei.ttf'],
                          sys=['LXGW Neo XiHei', '霞鹜新晰黑'], bold='noto-sans-sc'),
  'lxgw-neo-zhisong': dict(name='霞鹜新致宋 LXGW Neo ZhiSong', zh='中文宋体，端正雅致（只有常规体）', file='LXGWNeoZhiSong.ttf', w=(1, 599), mb=11, license='IPA',
                          urls=['https://github.com/lxgw/LxgwNeoZhiSong/releases/latest/download/LXGWNeoZhiSong.ttf'],
                          sys=['LXGW Neo ZhiSong', '霞鹜新致宋'], bold='noto-serif-sc'),
  'lxgw-wenkai':     dict(name='霞鹜文楷 GB LXGW WenKai GB', zh='中文手写楷体，大陆规范字形（正文可用）', file='LXGWWenKaiGB-Regular.ttf', w=(1, 499), mb=26,
                          urls=[WK + 'LXGWWenKaiGB-Regular.ttf'], sys=['LXGW WenKai GB', 'LXGW WenKai', '霞鹜文楷', 'Kaiti SC', 'STKaiti', 'KaiTi'],
                          pair='lxgw-wenkai-medium'),
  'lxgw-wenkai-medium': dict(name='霞鹜文楷 GB Medium', zh='文楷粗体（标题）', file='LXGWWenKaiGB-Medium.ttf', w=(500, 1000), mb=26,
                          urls=[WK + 'LXGWWenKaiGB-Medium.ttf'], sys=['LXGW WenKai GB Medium', 'LXGW WenKai GB', 'Kaiti SC', 'KaiTi'], family_of='lxgw-wenkai'),
  'lxgw-marker-gothic': dict(name='霞鹜漫黑 LXGW Marker Gothic', zh='中文马克笔圆头黑体（亲和标题）', file='LXGWMarkerGothic-Regular.ttf', w=(1, 1000), mb=3,
                          urls=[GF + 'lxgwmarkergothic/LXGWMarkerGothic-Regular.ttf', GFJ + 'lxgwmarkergothic/LXGWMarkerGothic-Regular.ttf'], sys=['LXGW Marker Gothic', '霞鹜漫黑']),
  'smiley-sans':     dict(name='得意黑 Smiley Sans', zh='中文海报标题（斜体窄黑）', file='SmileySans-Oblique.ttf', w=(1, 1000), mb=6,
                          urls=['https://github.com/atelier-anchor/smiley-sans/releases/download/v2.0.1/smiley-sans-v2.0.1.zip'],
                          sys=['Smiley Sans', '得意黑']),
  'zcool-kuaile':    dict(name='站酷快乐体 ZCOOL KuaiLe', zh='中文童趣标题（低幼）', file='ZCOOLKuaiLe-Regular.ttf', w=(1, 1000), mb=2,
                          urls=[GF + 'zcoolkuaile/ZCOOLKuaiLe-Regular.ttf', GFJ + 'zcoolkuaile/ZCOOLKuaiLe-Regular.ttf'], sys=['ZCOOL KuaiLe']),
  'ma-shan-zheng':   dict(name='马善政楷书 Ma Shan Zheng', zh='中文毛笔楷书标题', file='MaShanZheng-Regular.ttf', w=(1, 1000), mb=6,
                          urls=[GF + 'mashanzheng/MaShanZheng-Regular.ttf', GFJ + 'mashanzheng/MaShanZheng-Regular.ttf'], sys=['Ma Shan Zheng']),
}

# 字体方案：四个角色 title（标题/大字）· body（正文）· label（小标签/页眉/表头）· accent（编号/英文副题/任务字母）
# 每个角色是一串字体：西文字体在前（只含拉丁字），中文字体在后（补中文）。
PRESETS = {
  'magazine': dict(zh='杂志混排（默认）：思源宋体粗标题 + 霞鹜新晰黑正文 + 窄体小标签', title=['playfair', 'noto-serif-sc'],
                   body=['lxgw-neo-xihei', 'noto-sans-sc'], label=['oswald', 'lxgw-neo-xihei', 'noto-sans-sc'], accent=['playfair-italic', 'noto-serif-sc'],
                   css=dict(title_w=900, accent_style='italic', label_case='uppercase', label_track='.26em', label_scale=1)),
  'serif':    dict(zh='经典衬线：霞鹜新致宋 + Source Serif 4，书卷气、适合长文', title=['playfair', 'lxgw-neo-zhisong', 'noto-serif-sc'],
                   body=['source-serif-4', 'lxgw-neo-zhisong', 'noto-serif-sc'], label=['source-serif-4', 'lxgw-neo-zhisong'],
                   accent=['source-serif-4-italic', 'lxgw-neo-zhisong'],
                   css=dict(title_w=500, accent_style='italic', label_case='uppercase', label_track='.22em', label_scale=1.1, body_w=400)),
  'sans':     dict(zh='现代无衬线：思源黑体粗标题 + 霞鹜新晰黑正文 + Inter，干净理性', title=['inter', 'noto-sans-sc'],
                   body=['inter', 'lxgw-neo-xihei', 'noto-sans-sc'], label=['inter', 'lxgw-neo-xihei', 'noto-sans-sc'], accent=['inter', 'noto-sans-sc'],
                   css=dict(title_w=900, accent_style='normal', label_case='uppercase', label_track='.2em', label_scale=1, accent_w=800)),
  'hand':     dict(zh='手写亲和：霞鹜文楷 + Caveat，温暖、适合学生和亲子', title=['caveat', 'lxgw-wenkai'], body=['lxgw-wenkai'],
                   label=['caveat', 'lxgw-wenkai'], accent=['caveat', 'lxgw-wenkai'],
                   css=dict(title_w=700, accent_style='normal', label_case='none', label_track='.06em', label_scale=1.35, accent_w=700)),
}
ROLES = ('title', 'body', 'label', 'accent')

def path_of(fid):
    f = FONTS[fid]
    if f.get('bundled'): return os.path.join(BUNDLED, f['file'])
    for d in (CACHE, BUNDLED):
        p = os.path.join(d, f['file'])
        if os.path.exists(p) and os.path.getsize(p) > 10000: return p
    return None

def fetch(fid, quiet=False, timeout=180):
    f = FONTS[fid]
    if path_of(fid): return path_of(fid)
    os.makedirs(CACHE, exist_ok=True); dst = os.path.join(CACHE, f['file'])
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

def resolve(spec, cjk=True):
    """spec: 方案名或 {preset: hand, title: [...], ...}。返回 {role: [font ids]} 与 css 参数。"""
    spec = spec or 'magazine'
    if isinstance(spec, str): spec = {'preset': spec}
    pre = PRESETS.get(spec.get('preset', 'magazine'))
    if pre is None: raise SystemExit(f"ERROR: 未知字体方案 {spec.get('preset')}，可选 {list(PRESETS)}")
    roles = {r: list(pre[r]) for r in ROLES}
    if not cjk and roles['body'][0] in ('lxgw-neo-xihei', 'noto-sans-sc'): roles['body'] = ['inter'] + roles['body']   # 西文书：正文用 Inter
    for r in ROLES:
        if r in spec:
            v = spec[r]; v = [v] if isinstance(v, str) else list(v)
            bad = [x for x in v if x not in FONTS]
            if bad: raise SystemExit(f'ERROR: 未知字体 {bad}，可选 {list(FONTS)}')
            roles[r] = v
    for r, ids in roles.items():   # 文楷：自动带上 Medium 作为粗体
        for x in list(ids):
            if FONTS[x].get('pair') and FONTS[x]['pair'] not in ids: ids.insert(ids.index(x) + 1, FONTS[x]['pair'])
    return roles, dict(pre['css'], **spec.get('css', {}))

WEIGHTS = (400, 500, 600, 700, 800, 900)

def _subset(src, outs, text, fid, flavor=None):
    """裁切到本书用字；可变字体再按字重实例化成静态字体（Chromium 把可变字体写进 PDF 时会变成 Type 3，印刷厂不友好）。
    outs: {字重或 None: 输出路径}"""
    from fontTools import subset
    from fontTools.ttLib import TTFont
    opt = subset.Options(); opt.name_IDs = ['*']; opt.notdef_outline = True   # 版面特性用 fontTools 默认集（'*' 会把竖排、异体等几万个字形全拉进来）
    opt.layout_features += ['palt', 'halt', 'pwid']
    opt.drop_tables += ['DSIG']
    f = TTFont(src, lazy=False)
    s = subset.Subsetter(opt); s.populate(text=text); s.subset(f)
    nm = 'HB Subset ' + fid   # OFL：修改版（子集）不得沿用保留字体名，改内部名称；版权与许可信息保留
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
    """fmt: 'ttf' 输出未压缩字体（可编辑 PDF 用，快）；only: {'noto-serif-sc': {600, 900}, …} 只生成这些字重"""
    """为一本书生成 @font-face + 角色变量；子集文件写到 <proj>/fonts/。返回 CSS 字符串。"""
    roles, css = resolve(spec, cjk)
    od = os.path.join(proj, 'fonts'); os.makedirs(od, exist_ok=True)
    text = ''.join(sorted(set(text + ''.join(chr(c) for c in range(32, 127)) + '·—–“”‘’…、，。：；！？（）《》「」『』【】0123456789')))
    key = hashlib.md5((text + 'v2').encode()).hexdigest()[:10]
    faces = []; files = {}; missing = []
    want = list(dict.fromkeys(f for ids in roles.values() for f in ids))
    want += [FONTS[f]['bold'] for f in want if FONTS[f].get('bold') and FONTS[f]['bold'] not in want]   # 只有常规体的字体：粗体借用搭档
    try: import brotli; ext = 'woff2'  # noqa
    except ImportError: ext = 'woff'
    if fmt == 'ttf': ext = 'ttf'
    for fid in want:
        src = path_of(fid)
        if not src and not os.environ.get('HB_NO_FETCH'):   # 首次使用自动下载（下载不到就用系统字体，不中断）
            src = fetch(fid, quiet=False, timeout=60)
        if not src: missing.append(fid); continue
        lo, hi = FONTS[fid]['w']
        from fontTools.ttLib import TTFont
        var = 'fvar' in TTFont(src, lazy=True)   # 可变字体 → 按字重实例化
        ws = [w for w in WEIGHTS if lo <= w <= hi] if var else [None]
        if var and not ws: ws = [lo]
        if var and only is not None: ws = [w for w in ws if w in only.get(fid, set())] or ws[:1]
        outs = {w: os.path.join(od, f'hb-{fid}-{w or "x"}-{key}.{ext}') for w in ws}
        if not all(os.path.exists(o) for o in outs.values()):
            for old in os.listdir(od):
                if old.startswith(f'hb-{fid}-'): os.remove(os.path.join(od, old))
            _subset(src, outs, text, fid, 'ttf' if fmt == 'ttf' else None)
        files[fid] = {w: os.path.basename(o) for w, o in outs.items()}
    def face(fam, fn, lo, hi, italic=False):
        return (f"@font-face{{font-family:'{fam}';src:url(fonts/{fn}) format('{'truetype' if ext == 'ttf' else ext}');"
                f"font-weight:{lo}{'' if hi is None else ' ' + str(hi)};font-style:{'italic' if italic else 'normal'};font-display:block}}")
    for fid, fw in files.items():
        f = FONTS[fid]; lo, hi = f['w']; fam = 'HB-' + f.get('family_of', fid)
        for w, fn in fw.items():
            faces.append(face(fam, fn, lo, hi, f.get('italic')) if w is None else face(fam, fn, w, None, f.get('italic')))
        if f.get('bold') and f['bold'] in files:          # 粗体借用搭档：600 以上的字重
            for w, fn in files[f['bold']].items():
                if w is None: faces.append(face('HB-' + fid, fn, 600, 1000))
                elif w >= 600: faces.append(face('HB-' + fid, fn, w, None))
    # 许可清单：随项目字体目录分发
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
        log('提示：以下字体本机还没有，暂用系统字体代替（排版可能略有差异）：' + '、'.join(FONTS[m]['name'] for m in missing)
            + f'\n      下载：python3 {os.path.join(HERE, "fonts.py")} fetch ' + ' '.join(sorted(set(FONTS[m].get('family_of', m) for m in missing))))
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
         '--title-w': css.get('title_w', 900), '--body-w': css.get('body_w', 400), '--accent-style': css.get('accent_style', 'italic'),
         '--accent-w': css.get('accent_w', 700), '--label-case': css.get('label_case', 'uppercase'),
         '--label-track': css.get('label_track', '.26em'), '--label-scale': css.get('label_scale', 1)}
    return ''.join(faces) + ':root{' + ';'.join(f'{k}:{x}' for k, x in v.items()) + '}', roles, missing

def _status(fid):
    return '随附' if FONTS[fid].get('bundled') else ('已下载' if path_of(fid) else f'未下载（约 {FONTS[fid].get("mb", "?")}MB）')

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'list':
        print(f'缓存目录：{CACHE}\n\n字体（全部开源免费、可商用、可嵌入 PDF；许可 OFL 1.1，霞鹜新晰黑/新致宋为 IPA Font License 1.0）：')
        for k, f in FONTS.items(): print(f'  {k:20s} {f["name"]:28s} {f["zh"]:20s} {_status(k)}')
        print('\n字体方案（book.fonts）：')
        for k, p in PRESETS.items(): print(f'  {k:10s} {p["zh"]}\n             ' + ' | '.join(f'{r}: {"+".join(p[r])}' for r in ROLES))
    elif cmd == 'fetch':
        want = sys.argv[2:] or list(PRESETS)
        ids = []
        for w in want:
            if w in PRESETS: ids += [x for r in ROLES for x in PRESETS[w][r]]
            elif w in FONTS: ids.append(w)
            else: sys.exit(f'未知方案/字体：{w}')
        ids = list(dict.fromkeys(i for x in ids for i in ([x] + ([FONTS[x]['pair']] if FONTS[x].get('pair') else []))))
        bad = [i for i in ids if not FONTS[i].get('bundled') and not fetch(i)]
        print('完成' if not bad else f'以下字体下载失败：{bad}。可手动下载后放到 {CACHE}/（文件名见 fonts.py 里的 file 字段）')
        sys.exit(1 if bad else 0)
    else:
        sys.exit(__doc__)
