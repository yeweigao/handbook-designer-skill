#!/usr/bin/env python3
"""Shared edge-to-edge photography, deliberate multi-image rhythm and real Thin fonts."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from test_editorial_layout import build

ROOT = Path(__file__).resolve().parents[2]
HB = ROOT / 'hb'


def main():
    with tempfile.TemporaryDirectory(prefix='hb-bleed-') as td:
        p = Path(td); (p / 'photos').mkdir()
        for name, color in [('red', '#D82424'), ('green', '#14B428'), ('blue', '#164BCB')]:
            Image.new('RGB', (1200, 900), color).save(p / 'photos' / (name + '.png'))
        items = [dict(img=name + '.png', caption='View %s' % (i + 1)) for i, name in enumerate(['red', 'green', 'blue'] * 2)]
        spec = dict(book=dict(lang='en', style='swiss', duotone='off'), pages=[
            dict(layout='PHOTO_OPEN', image='red.png', title='An image opens the story.', caption='A scene, then a reading field.'),
            dict(layout='MASONRY', title='Six observations', items=items),
            dict(layout='CONTACT', title='One scene, six views', image='red.png', items=items)])
        probe = p / 'probe.cjs'
        probe.write_text("""
const {chromium}=require(require.resolve('playwright',{paths:[process.argv[3]]}));const fs=require('fs');
(async()=>{let b;try{b=await chromium.launch({args:['--no-sandbox']})}catch(e){b=await chromium.launch({executablePath:process.env.HB_CHROME,args:['--no-sandbox']})}
const p=await b.newPage();await p.goto('file://'+process.argv[2]+'/book.html',{waitUntil:'networkidle'});await p.waitForFunction(()=>document.body.dataset.ready==1);
const r=await p.evaluate(()=>{
 const pages=[...document.querySelectorAll('.page')].map(pg=>{
  const P=pg.getBoundingClientRect();
  const images=[...pg.querySelectorAll('.cn-ed-figure img')].map(im=>{const q=im.getBoundingClientRect();return {x:q.left-P.left,y:q.top-P.top,w:q.width,h:q.height,fit:getComputedStyle(im).objectFit}});
  const captions=[...pg.querySelectorAll('figcaption')].map(c=>({text:c.innerText,after:c.getBoundingClientRect().top>=c.closest('figure').querySelector('img').getBoundingClientRect().bottom-.5}));
  const masonry=pg.querySelector('.cn-masonry');
  const grid=masonry&&masonry.querySelector('.cn-ed-grid');
  const title=pg.querySelector('.cn-disp');
  const links=[...pg.querySelectorAll('.cn-masonry-item')].map(e=>({id:e.getAttribute('aria-describedby'),caption:document.getElementById(e.getAttribute('aria-describedby'))?.innerText}));
  const cells=grid&&[...grid.children].map(e=>{const q=e.getBoundingClientRect();return {x:q.left-P.left,w:q.width}});
  return {w:P.width,h:P.height,images,captions,masonry:grid?{tracks:getComputedStyle(grid).gridTemplateColumns.split(' ').map(Number.parseFloat),gap:parseFloat(getComputedStyle(grid).columnGap),cells,links,titleY:title.getBoundingClientRect().top-P.top,overlays:[...masonry.querySelectorAll('.cn-masonry-item')].some(e=>e.innerText.trim())}:null};
 });
 return {qa:cnCheck(),pages,weights:[...document.querySelectorAll('.cn-disp')].map(e=>+getComputedStyle(e).fontWeight)};
});
await p.pdf({path:process.argv[2]+'/proof.pdf',preferCSSPageSize:true,printBackground:true});r.bad=await p.evaluate(()=>{const a=document.querySelector('.page img'),b=document.querySelector('[data-image-role="supporting"] img');if(a)a.style.height='80px';if(b)b.style.height='30px';return cnCheck()});fs.writeFileSync(process.argv[2]+'/probe.json',JSON.stringify(r));await b.close()})().catch(e=>{console.error(e);process.exit(1)});
""", encoding='utf-8')
        def measure():
            subprocess.run(['node', str(probe), str(p), str(HB)], check=True)
            return json.loads((p / 'probe.json').read_text(encoding='utf-8'))
        for style in ('photo', 'swiss', 'editorial', 'stijl', 'geo'):
            spec['book']['style'] = style
            build(p, spec); got = measure(); assert not got['qa'], (style, got['qa'])
            assert [len(pg['images']) for pg in got['pages']] == [1, 6, 7]
            assert sum(q[1]=='cn-imgarea' for q in got['bad']) >= 2, 'Primary/supporting image collapse escaped the gate'
            for i, pg in enumerate(got['pages']):
                assert min(im['x'] for im in pg['images']) == 0 and max(round(im['x'] + im['w'], 2) for im in pg['images']) == pg['w'], (style, i, pg)
                assert all(im['fit'] == 'cover' for im in pg['images'])
                assert all(c['after'] for c in pg['captions']), 'A caption detached from its photograph'
            opening = got['pages'][0]['images'][0];assert opening['y'] == 0 and opening['h'] > 400
            masonry = got['pages'][1]; photos=masonry['images']; grid=masonry['masonry']
            assert len(grid['tracks']) == 6 and max(grid['tracks'])-min(grid['tracks']) < .1
            for i, cell in enumerate(grid['cells']):
                assert abs(cell['w']-(sum(grid['tracks'][2*i:2*i+2])+grid['gap'])) < .1
                if i:
                    first, previous=photos[2*i], photos[2*(i-1)]
                    seam=first['x']-(previous['x']+previous['w'])
                    assert 0 < seam < masonry['w']/50, 'Masonry regained broad gutters'
                    axis=(cell['x']+grid['cells'][i-1]['x']+grid['cells'][i-1]['w'])/2
                    assert abs((first['x']+previous['x']+previous['w'])/2-axis) < .1, 'Photo seams left the six-track gutter axes'
                    vertical=photos[2*i+1]['y']-(first['y']+first['h'])
                    assert abs(vertical-seam) < .1, 'Horizontal and vertical photo seams differ'
            assert not grid['overlays'], 'A label or white-backed patch returned to a photograph'
            assert all(abs(photos[i]['y']) < .1 for i in (0,2,4)), 'Masonry no longer begins at the top trim'
            ends=[photos[i]['y']+photos[i]['h'] for i in (1,3,5)]
            assert max(ends)-min(ends) < .5, 'Bounded masonry lost its common lower edge'
            assert .60*masonry['h'] < ends[0] < .76*masonry['h'], 'Photo field lost its page-leading scale'
            assert grid['titleY'] >= max(ends), 'Title displaced or covered the photo field'
            starts=[photos[i]['y'] for i in (1,3,5)]
            assert len(set(round(v) for v in starts)) == 3, 'Independent columns collapsed into horizontal rows'
            assert len(grid['links']) == 6 and all(link['caption'] and link['id'] for link in grid['links']), 'Image lost its indexed caption'
            heights = [round(im['h']) for im in photos]
            assert len(set(heights)) >= 4, 'Masonry became a uniform tile grid'
        for canvas in ('a5','xhs'):
            small=copy.deepcopy(spec);small['book'].update(style='swiss',canvas=canvas)
            build(p,small);got=measure();assert not got['qa'],(canvas,got['qa'])
            assert [len(pg['images']) for pg in got['pages']] == [1,6,7]
        # Explicit inset is a structure choice, not a theme-specific override.
        inset = copy.deepcopy(spec);inset['pages'] = [inset['pages'][0]];inset['pages'][0]['bleed'] = 'inset'
        build(p, inset);got=measure();assert got['pages'][0]['images'][0]['x'] > 0 and got['pages'][0]['images'][0]['y'] > 0
        # 100 is opt-in, actually loaded, and shared with themes using a compatible title face.
        thin = dict(book=dict(lang='en',style='swiss',typography='light',display_weight=100),
                    pages=[dict(layout='PAPER',body=[dict(display='Observe.',size=96),dict(p='Keep ordinary reading text steady.')])])
        for style in ('swiss','editorial'):
            thin['book'].update(style=style, fonts='sans');build(p,thin);got=measure();assert not got['qa'] and got['weights']==[100],got
        outlines=[]
        for weight in (100,200):
            f=TTFont(next((p/'fonts').glob('hb-noto-sans-sc-%s-*'%weight)));assert 'fvar' not in f
            gs=f.getGlyphSet();pen=RecordingPen();gs[f.getBestCmap()[ord('A')]].draw(pen);outlines.append(repr(pen.value))
        assert outlines[0] != outlines[1], 'Thin was mapped to ExtraLight'
        bad=copy.deepcopy(thin);bad['book']['fonts']='serif';assert build(p,bad,expect=False).returncode != 0, 'Serif fabricated 100'
        bad=copy.deepcopy(thin);bad['book']['typography']='bold';assert build(p,bad,expect=False).returncode != 0
        for layout in ('MASONRY','CONTACT'):
            bad=copy.deepcopy(spec);bad['pages']=[dict(layout=layout,image='red.png',items=items[:5])]
            assert build(p,bad,expect=False).returncode != 0
            bad['pages'][0]['items']=copy.deepcopy(items);bad['pages'][0]['items'][0]['img']='art'
            assert build(p,bad,expect=False).returncode != 0
        # Printed edge pixels also expose theme ornament covering a geometrically correct image.
        for style in ('swiss','stijl','geo'):
            spec['book']['style']=style;build(p,spec);measure()
            subprocess.run(['pdftoppm','-f','1','-l','1','-scale-to','1123','-png',str(p/'proof.pdf'),str(p/'print')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            im=Image.open(p/'print-1.png').convert('RGB')
            for xy in [(2,2),(im.width-3,2),(2,200),(im.width-3,200)]:
                r,g,b=im.getpixel(xy);assert r>150 and g<80 and b<80,(style,'Photo covered by frame/ornament',xy,(r,g,b))
    print('BLEED: PASS — five themes, full trim, six-photo rhythm, captions, actual PDF, real 100 and unsupported-font rejection')


if __name__=='__main__':main()
