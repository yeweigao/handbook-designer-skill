#!/usr/bin/env python3
"""Actual weight instances, post-fit hierarchy, body floor, rejected skins and clash."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile

from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

from test_editorial_layout import build

ROOT = Path(__file__).resolve().parents[2]
HB = ROOT / 'hb'


def main():
    with tempfile.TemporaryDirectory(prefix='hb-swiss-') as td:
        p = Path(td)
        cases = [(72, '瑞士风 Large statement', 200), (44, '1,240', 250),
                 (40, 'Single accent.', 300), (18, 'Keep a clear reading line.', 400),
                 (15, 'FIELD NOTES / 2026', 500), (13, 'OBSERVE / RETURN', 600)]
        html = ''.join('<div data-case="%s" style="font-family:var(--f-title);font-size:%spx;line-height:%spx">%s</div>'
                       % (i, size, max(28, size + 12), text) for i, (size, text, _) in enumerate(cases))
        spec = dict(book=dict(lang='zh', style='swiss'), pages=[
            dict(layout='PAPER', body=[dict(html=html)]),
            dict(layout='FULL', image=False, title='把必要的\n留下来', intro='清楚的文字，是阅读的起点。', folio=False),
            dict(layout='READING', title='留意差异', text=['位置、形状与关系，让记录可以被再次阅读。'])])
        build(p, spec)
        probe = p / 'probe.cjs'
        probe.write_text("""
const {chromium}=require(require.resolve('playwright',{paths:[process.argv[3]]}));const fs=require('fs');
(async()=>{let b;try{b=await chromium.launch({args:['--no-sandbox']})}catch(e){if(!process.env.HB_CHROME)throw e;b=await chromium.launch({executablePath:process.env.HB_CHROME,args:['--no-sandbox']})}
const p=await b.newPage();await p.goto('file://'+process.argv[2]+'/book.html',{waitUntil:'networkidle'});await p.waitForFunction(()=>document.body.dataset.ready==1);
const got=await p.evaluate(()=>({qa:JSON.parse(document.body.dataset.cnqa||'[]'),cases:[...document.querySelectorAll('[data-case]')].map(e=>+getComputedStyle(e).fontWeight),
loaded:[...document.fonts].every(f=>f.status==='loaded'),liveqa:cnCheck(),mode:document.body.className,heading:[...document.querySelectorAll('[data-fit]')].map(e=>({size:parseFloat(getComputedStyle(e).fontSize),weight:+getComputedStyle(e).fontWeight,expected:cnTypeWeight(parseFloat(getComputedStyle(e).fontSize))})),
body:[...document.querySelectorAll('.cn-tx p')].map(e=>({size:getComputedStyle(e).fontSize,weight:+getComputedStyle(e).fontWeight})),
circles:document.querySelectorAll('.page > .cn-v > .deco[style*="border-radius:50%"],.page > .deco[style*="border-radius:50%"] ').length}));
await p.pdf({path:process.argv[2]+'/type.pdf',preferCSSPageSize:true,printBackground:true});
const bad=await p.evaluate(()=>{document.querySelector('[data-case="3"]').style.fontWeight='300';cnQA();return JSON.parse(document.body.dataset.cnqa)});
const fixed=await p.evaluate(()=>{canon();return JSON.parse(document.body.dataset.cnqa)});
fs.writeFileSync(process.argv[2]+'/probe.json',JSON.stringify({got,bad,fixed}));await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
""", encoding='utf-8')
        subprocess.run(['node', str(probe), str(p), str(HB)], check=True)
        result = json.loads((p / 'probe.json').read_text(encoding='utf-8'))
        got = result['got']
        assert not got['qa'] and not got['circles'] and got['loaded'] and got['liveqa'] == got['qa'], got
        assert 'm-mono' in got['mode'] and got['cases'] == [c[2] for c in cases]
        assert all(h['weight'] == h['expected'] for h in got['heading'])
        assert got['body'] and all(t['weight'] >= 400 for t in got['body'])
        assert any(q[1] == 'cn-weight' for q in result['bad']), 'A thin small-text mutation escaped the gate'
        assert not result['fixed'], 'Reflow did not restore the weight policy'
        assert b'/Subtype /Type3' not in (p / 'type.pdf').read_bytes()

        # Verify the embedded files have real, distinct low-weight outlines, not only CSS labels.
        outlines = []
        for weight in (200, 250, 300, 400):
            path = next((p / 'fonts').glob('hb-noto-sans-sc-%s-*' % weight))
            font = TTFont(path)
            assert 'fvar' not in font, 'PDF font remained variable'
            glyphs = font.getGlyphSet(); pen = RecordingPen()
            glyphs[font.getBestCmap()[ord('A')]].draw(pen)
            outlines.append(repr(pen.value))
        assert len(set(outlines)) == 4, 'Low weights were mapped to one regular outline'
        # Theme and type scale are independent: every maintained theme accepts both profiles.
        for style in ('photo', 'swiss', 'editorial', 'stijl'):
            for mode in ('bold', 'light'):
                variant = copy.deepcopy(spec); variant['book'].update(style=style, typography=mode)
                build(p, variant)
                subprocess.run(['node', str(probe), str(p), str(HB)], check=True)
                current = json.loads((p / 'probe.json').read_text(encoding='utf-8'))['got']
                assert not current['qa'] and current['liveqa'] == current['qa'] and current['loaded'], (style, mode, current['qa'], current['liveqa'])
                assert current['cases'] == ([900, 700, 700, 400, 500, 600] if mode == 'bold' else [c[2] for c in cases])
                assert all(any(f.name.startswith('hb-'+fid+'-') for fid in ('noto-sans-sc','noto-serif-sc')) for f in (p / 'fonts').glob('hb-*')), 'Optional Inter loaded in the default font setup'
        for style in ('geo', 'notebook', 'inkwash', 'papercut', 'riso', 'aurora', 'nebula'):
            bad = copy.deepcopy(spec); bad['book']['style'] = style
            assert build(p, bad, expect=False).returncode != 0, 'Retired style remained selectable'
        for setting in (dict(color_mode='clash'), dict(color_mode='accent'), dict(gradient='brand')):
            bad = copy.deepcopy(spec); bad['book'].update(setting)
            assert build(p, bad, expect=False).returncode != 0, 'Swiss accepted multiple-color or gradient mode'
    print('SHARED TYPE: PASS — four themes × two profiles, Source Han defaults, real low-weight outlines, fit-aware hierarchy, readable body, negative gate, retired themes rejected')


if __name__ == '__main__':
    main()
