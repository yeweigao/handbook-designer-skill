#!/usr/bin/env python3
"""Verify paragraph-note association, theme-independent geometry, and printed multi-image survival."""
import copy
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile
import re

import numpy as np
from PIL import Image
import yaml

HB = Path(__file__).resolve().parents[2] / 'hb'


def build(project, spec, expect=True):
    (project / 'book.yaml').write_text(yaml.safe_dump(spec, allow_unicode=True), encoding='utf-8')
    got = subprocess.run(['python3', str(HB / 'hb.py'), str(project)],
                         capture_output=True, text=True)
    if expect:
        assert got.returncode == 0, got.stdout + got.stderr
    return got


def main():
    with tempfile.TemporaryDirectory(prefix='hb-editorial-') as td:
        project = Path(td)
        (project / 'photos').mkdir()
        for name, color in [('red', '#D82424'), ('green', '#14B428'), ('blue', '#164BCB')]:
            Image.new('RGB', (1200, 900), color).save(project / 'photos' / (name + '.png'))
        spec = dict(book=dict(lang='en', style='editorial', color_mode='accent',
                              duotone='off', typography='bold', fonts=dict(preset='sans', title=['playfair']),
                              colors=dict(A='#244C3C', B='#B54932', PAPER='#F7F4EB')),
                    pages=[
                        dict(layout='MARGINALIA', title='Observe, then ask.', sections=[
                            dict(t='First passage', x='A short observation stays with its long note.',
                                 note_title='Keep this beside it',
                                 note='Look closely before interpreting what you see. ' * 8),
                            dict(t='Second passage', x='This passage follows the complete first pair.',
                                 note='A second note belongs only to this passage.')]),
                        dict(layout='SEQUENCE', title='A visual sequence', items=[
                            dict(img='red.png', t='First scene', x='The principal scene.'),
                            dict(img='green.png', t='Second scene', x='A supporting view.'),
                            dict(img='blue.png', t='Third scene', x='A final view.')]),
                        dict(layout='RHYTHM', title='Pause and read.', intro='A side voice.',
                             text=['A primary paragraph.', 'A complete second paragraph.',
                                   'A complete third paragraph.'], quote='A moment to reflect.'),
                    ])
        probe = project / 'probe.cjs'
        probe.write_text("""
const {chromium}=require(require.resolve('playwright',{paths:[process.argv[3]]}));
const fs=require('fs');
(async()=>{
let b;try{b=await chromium.launch({args:['--no-sandbox']})}
catch(e){if(!process.env.HB_CHROME)throw e;b=await chromium.launch({executablePath:process.env.HB_CHROME,args:['--no-sandbox']})}
const p=await b.newPage();
await p.goto('file://'+process.argv[2]+'/'+(process.argv[4]||'book.html'),{waitUntil:'networkidle'});
await p.waitForFunction(()=>document.body.dataset.ready==1);
const got=await p.evaluate(()=>{
const pg=document.querySelector('.page'),pairs=[...pg.querySelectorAll('.cn-ed-grid')];
const rows=pairs.map(e=>{const r=e.getBoundingClientRect();return [r.top,r.bottom]});
const all=[...document.querySelectorAll('.cn-ed-grid,.cn-ed-cell')].map(e=>{
const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height].map(x=>Math.round(x*100)/100)});
return {rows,all,qa:JSON.parse(document.body.dataset.cnqa||'[]'),
bodySize:getComputedStyle(pg.querySelector('.cn-tx')).fontSize,
loaded:[...document.images].every(i=>i.complete&&i.naturalWidth>0),
imageBoxes:[...document.querySelectorAll('#p2 img')].map(e=>{const r=e.getBoundingClientRect();return [r.width,r.height]}),
images:[...document.querySelectorAll('#p2 img')].length};
});
fs.writeFileSync(process.argv[2]+'/probe.json',JSON.stringify(got));
await p.pdf({path:process.argv[2]+'/proof.pdf',preferCSSPageSize:true,printBackground:true});
await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
""", encoding='utf-8')
        previous = None
        for style in ('photo', 'swiss', 'editorial'):
            spec['book']['style'] = style
            spec['book']['color_mode'] = 'mono' if style == 'swiss' else 'accent'
            build(project, spec)
            subprocess.run(['node', str(probe), str(project), str(HB)], check=True)
            got = json.loads((project / 'probe.json').read_text(encoding='utf-8'))
            assert not got['qa'], got['qa']
            assert got['rows'][1][0] >= got['rows'][0][1], 'Long note detached from its paragraph'
            assert got['bodySize'] == '16px', 'Body text shrank'
            assert got['loaded'] and got['images'] == 3, 'Multi-image sequence lost an image'
            subprocess.run(['python3', str(HB / 'images.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            inventory = yaml.safe_load((project / 'images.yaml').read_text(encoding='utf-8'))['images']
            for name, (width, height) in zip(('red', 'green', 'blue'), got['imageBoxes']):
                expected = round(96 / max(width / 1200, height / 900))
                assert inventory[name + '.png']['dpi'] == expected, 'Image inventory used the full page width instead of its grid span'
            if previous is not None:
                assert [(r[0], r[2]) for r in got['all']] == previous, 'Theme changed grid columns or width'
            previous = [(r[0], r[2]) for r in got['all']]
        subprocess.run(['pdftoppm', '-f', '2', '-l', '2', '-scale-to', '1123', '-png',
                        str(project / 'proof.pdf'), str(project / 'print')], check=True)
        pixels = np.asarray(Image.open(project / 'print-2.png').convert('RGB'))
        for c in range(3):
            others = [i for i in range(3) if i != c]
            area = ((pixels[:, :, c] > 130) & (pixels[:, :, others[0]] < 100)
                    & (pixels[:, :, others[1]] < 130)).sum()
            assert area > 10000, 'An image disappeared in printed PDF'
        bad = copy.deepcopy(spec)
        bad['pages'] = [dict(layout='PLATE', title='No invented illustration')]
        got = build(project, bad, expect=False)
        assert got.returncode != 0 and '实际' in got.stdout + got.stderr, 'Missing PLATE image was silently filled'
        for source in (False, '', 'art', 'placeholder'):
            bad['pages'][0]['image'] = source
            assert build(project, bad, expect=False).returncode != 0, 'Empty artwork became decorative filler'
        for count in (2, 4):
            bad['pages'] = [dict(layout='SEQUENCE', items=[dict(img='red.png')] * count)]
            assert build(project, bad, expect=False).returncode != 0, 'Invalid image count accepted'
        bad['pages'] = [dict(layout='SEQUENCE', items=[dict(img='red.png'), dict(img='green.png'), {}])]
        assert build(project, bad, expect=False).returncode != 0, 'Missing sequence image accepted'
        # Functional raster artwork keeps its colors even in a monochrome book.
        plate = copy.deepcopy(spec)
        plate['book']['duotone'] = 'all'
        plate['pages'][0] = dict(layout='PLATE', title='An observed object', image='red.png', text='Read the diagram with its original colors.')
        build(project, plate)
        usage = json.loads((project / 'map.json').read_text(encoding='utf-8'))['use']
        assert not usage[0].get('duo'), 'PLATE changed functional image colors'
        plate['pages'][0]['image'] = dict(src='red.png', duo=True)
        build(project, plate)
        usage = json.loads((project / 'map.json').read_text(encoding='utf-8'))['use']
        assert usage[0].get('duo'), 'Explicit image treatment was ignored'
        plate['pages'][0]['image'] = 'ai:leaf'
        assert build(project, plate, expect=False).returncode != 0, 'Missing AI artwork accepted'
        (project / 'photos/ai_leaf.png').write_bytes((project / 'photos/red.png').read_bytes())
        build(project, plate)
        # SVG survives the normal standalone path as vector bytes, and loads offline.
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="#D82424"/></svg>'
        (project / 'photos/diagram.svg').write_bytes(svg)
        plate['pages'][0]['image'] = 'diagram.svg'
        build(project, plate)
        subprocess.run(['python3', str(HB / 'standalone.py'), str(project / 'book.html'),
                        str(project / 'standalone.html')], check=True, stdout=subprocess.DEVNULL)
        html = (project / 'standalone.html').read_text(encoding='utf-8')
        embedded = re.search(r'data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)', html)
        assert embedded and base64.b64decode(embedded.group(1)) == svg, 'SVG changed during standalone export'
        assert not re.search(r'src="(?!data:)[^"]+"', html), 'Standalone retained an external image'
        subprocess.run(['node', str(probe), str(project), str(HB), 'standalone.html'], check=True)
        got = json.loads((project / 'probe.json').read_text(encoding='utf-8'))
        assert got['loaded'] and not got['qa'], 'Offline SVG did not load or overflowed'
        # Small formats must retain their ordinary body size and report oversized prose.
        for canvas in ('a5', 'xhs'):
            small = copy.deepcopy(spec)
            small['book']['canvas'] = canvas
            small['pages'] = [dict(layout='RHYTHM', title='Keep reading.', intro='A short lead.',
                                  text=['A complete short paragraph.', 'Another paragraph.'])]
            build(project, small)
            subprocess.run(['node', str(HB / 'shot.js'), str(project)], check=True, stdout=subprocess.DEVNULL)
            qa = json.loads((project / '.qa/overflow.json').read_text(encoding='utf-8'))
            assert not qa, (canvas, qa)
        too_long = copy.deepcopy(spec)
        too_long['pages'] = [dict(layout='RHYTHM', title='Long text', text=['Visible words. ' * 2000])]
        build(project, too_long)
        subprocess.run(['node', str(HB / 'shot.js'), str(project)], check=True, stdout=subprocess.DEVNULL)
        qa = json.loads((project / '.qa/overflow.json').read_text(encoding='utf-8'))
        assert any(q[1] == 'cn-over' for q in qa), 'Long prose was clipped without a QA failure'
    print('EDITORIAL: PASS — note pairing, three themes, printed images, SVG export, color fidelity, material validation, small canvases, overflow')


if __name__ == '__main__':
    main()
