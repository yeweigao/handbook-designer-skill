#!/usr/bin/env python3
"""可编辑 PDF：字体完整嵌入“常用字库”，拿到 PDF 的人能直接在 PDF 编辑器里改字、加字。
  python3 hb/editable_pdf.py <project_dir> <输出.pdf> [普通版.pdf]      （export.sh 会自动调用）

为什么需要它：浏览器导出的 PDF 只嵌入“书里用到的字”（子集），别人在 Acrobat 里改字时，
书里没出现过的字就没有字形，只能换成别的字体。这里把每个字体扩充到
GB2312 全部 6763 个常用汉字 + 常用符号 + 西文，重新渲染，再把 PDF 里的子集字体换成这份完整字库，
并去掉“子集”标记（字体名前缀 ABCDEF+），编辑器就会把它当作完整嵌入的字体使用。
代价：PDF 变大（每个中文字体字重约 2–5MB）。版式与普通 PDF 完全一致。
"""
import os, sys, io, re, json, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import yaml, fonts as F
from styles import STYLES

def common_charset():
    cs = set(chr(c) for c in range(0x20, 0x7F)) | set(chr(c) for c in range(0xA0, 0x180))
    for hi in range(0xA1, 0xF8):            # GB2312：符号区 + 6763 个汉字
        for lo in range(0xA1, 0xFF):
            try: cs.add(bytes([hi, lo]).decode('gb2312'))
            except UnicodeDecodeError: pass
    cs |= set('　、。·ˉˇ¨〃々—～‖…‘’“”〔〕〈〉《》「」『』〖〗【】±×÷∶∧∨∑∏∪∩∈∷√⊥∥∠⌒⊙∫∮≡≌≈∽∝≠≮≯≤≥∞∵∴♂♀°′″℃＄¤￠￡‰§№☆★○●◎◇◆□■△▲※→←↑↓〓！＂＃￥％＆＇（）＊＋，－．／０１２３４５６７８９：；＜＝＞？＠［＼］＾＿｀｛｜｝￣')
    return ''.join(sorted(cs))

def main(P, out, ref=None):
    P = os.path.abspath(P); E = os.path.join(P, '.editable')
    spec = yaml.safe_load(open(os.path.join(P, 'book.yaml'), encoding='utf-8')); BK = spec.get('book', {})
    style = STYLES[str(BK.get('style', 'photo'))]; lang = str(BK.get('lang', 'zh')); cjk = lang.split('-')[0].lower() in ('zh', 'ja', 'ko')
    html = open(os.path.join(P, 'book.html'), encoding='utf-8').read()
    used = re.sub(r'<[^>]+>', '', html)
    print('扩充字库（GB2312 常用字 6763 个 + 本书用字），较大的中文字体需要几十秒……', flush=True)
    os.makedirs(E, exist_ok=True)
    only = None
    if ref and os.path.exists(ref):      # 只扩充普通版 PDF 里真正用到的字重
        import pikepdf
        only = {}
        for o in pikepdf.open(ref).objects:
            if isinstance(o, pikepdf.Dictionary) and o.get('/Subtype') == '/Type0':
                mm = re.match(r'HBSubset(.+?)(\d{3})$', str(o.BaseFont).split('+', 1)[-1].lstrip('/'))
                if mm and mm.group(2): only.setdefault(mm.group(1), set()).add(int(mm.group(2)))
    if not only: only = None
    css, roles, miss = F.build_css(BK.get('fonts', style['fonts']), used + common_charset(), E, cjk, fmt='ttf', only=only)
    m = re.search(r'<style>(.*?):root\{[^}]*\}', html, re.S)          # 替换开头的 @font-face + :root 变量
    html = html[:m.start(1)] + css + html[m.end():]
    open(os.path.join(E, 'book.html'), 'w', encoding='utf-8').write(html)
    if not os.path.exists(os.path.join(E, 'img')): os.symlink(os.path.join(P, 'img'), os.path.join(E, 'img'))
    tmp = os.path.join(E, 'render.pdf')
    subprocess.run(['node', os.path.join(HERE, 'pdf.js'), E, tmp], check=True)
    # 子集 → 完整字库
    import pikepdf
    from fontTools.ttLib import TTFont
    byname = {}
    for fn in os.listdir(os.path.join(E, 'fonts')):
        if not fn.startswith('hb-'): continue
        t = TTFont(os.path.join(E, 'fonts', fn)); byname[t['name'].getDebugName(6)] = t
    pdf = pikepdf.open(tmp); streams = {}; done = set(); n = 0
    for obj in pdf.objects:
        if not isinstance(obj, pikepdf.Dictionary) or obj.get('/Subtype') != '/Type0': continue
        base = str(obj.BaseFont); clean = base.split('+', 1)[-1]; t = byname.get(clean)
        if t is None: continue
        d = obj.DescendantFonts[0]; fd = d.FontDescriptor
        if clean not in streams:
            b = io.BytesIO(); t.flavor = None; t.save(b)
            streams[clean] = pdf.make_stream(b.getvalue())
            upm = t['head'].unitsPerEm; go = t.getGlyphOrder(); hm = t['hmtx'].metrics
            streams[clean + '/W'] = pikepdf.Array([0, pikepdf.Array([round(hm[g][0] * 1000 / upm) for g in go])])
        fd.FontFile2 = streams[clean]
        d.W = streams[clean + '/W']
        for k in ('/CIDSet',):
            if k in fd: del fd[k]
        obj.BaseFont = pikepdf.Name('/' + clean); d.BaseFont = pikepdf.Name('/' + clean); fd.FontName = pikepdf.Name('/' + clean)
        n += 1
    pdf.save(out, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    if ref and os.path.exists(ref):      # 自检：可编辑版用到的字体/字重必须和普通版一致（否则版式可能不同）
        names = lambda p: {str(o.BaseFont).split('+', 1)[-1].lstrip('/') for o in pikepdf.open(p).objects if isinstance(o, pikepdf.Dictionary) and o.get('/Subtype') == '/Type0'}
        a_, b_ = names(ref), names(out)
        if a_ != b_: print(f'警告：可编辑版与普通版的字体不一致（普通版独有 {sorted(a_ - b_)}；可编辑版独有 {sorted(b_ - a_)}），请以普通版为准并检查。')
        else: print('自检：与普通版使用完全相同的字体和字重 ✓')
    t3 = sum(1 for o in pdf.objects if isinstance(o, pikepdf.Dictionary) and o.get('/Subtype') == '/Type3')
    print(f'可编辑 PDF → {out}（{os.path.getsize(out) // 1048576 + 1}MB；{len([k for k in streams if not k.endswith("/W")])} 个字体完整嵌入常用字库，替换 {n} 处；Type 3：{t3}）')
    if miss: print('注意：这些字体没下载，仍是系统字体回退，可能不可编辑：' + '、'.join(miss))

if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
