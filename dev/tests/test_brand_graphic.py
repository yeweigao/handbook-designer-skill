"""Brand backgrounds: no reflow, protected images, and real PDF visibility. Synthetic assets only."""
from pathlib import Path
import copy
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image
import yaml

HB_DIR = Path(__file__).resolve().parents[2] / 'hb'
sys.path.insert(0, str(HB_DIR))
import brand_graphic


def main():
    hb = HB_DIR
    with tempfile.TemporaryDirectory(prefix='hb-brand-') as td:
        p = Path(td)
        (p / 'photos').mkdir()
        (p / 'photos/symbol.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="12"><path d="M0 0L100 100M0 50L50 100M50 0L100 50"/></svg>', encoding='utf-8')
        Image.new('RGB', (1400, 700), '#DC2020').save(p / 'photos/red.jpg')
        spec = dict(book=dict(title='Brand artwork control', lang='en', style='swiss', duotone='off',
                             colors=dict(A='#002BA5', B='#FFFFFF', PAPER='#FFFFFF', TINT='#FFFFFF', INK='#111111'),
                             brand_graphic=dict(file='photos/symbol.svg', opacity=.05, variants=dict(whole={}))),
                    pages=[dict(layout='PAPER', brand_graphic='whole', body=[dict(title='Read the guide'),
                               dict(p='The graphic must not change the reading geometry.'), dict(figure='red.jpg', h=224)]),
                           dict(layout='SPREAD_H', image='red.jpg', image_position='bottom', split=564,
                                left=dict(brand_graphic=dict(variant='whole', spread='left', frame=[.15, -.25, .7, 1.7], angle=90), body=[dict(title='Left page')]),
                                right=dict(brand_graphic=dict(variant='whole', spread='right', frame=[.15, -.25, .7, 1.7], angle=90), body=[dict(title='Right page')])),
                           dict(layout='PAPER', surface='A', brand_graphic='whole', body=[dict(title='Blue paper')])])
        (p / 'book.yaml').write_text(yaml.safe_dump(spec), encoding='utf-8')
        subprocess.run(['bash', str(hb / 'run.sh'), str(p)], check=True, stdout=subprocess.DEVNULL)
        probe = p / 'probe.cjs'
        probe.write_text('''const {chromium}=require('playwright'),fs=require('fs');
(async()=>{const b=await chromium.launch(),p=await b.newPage({viewport:{width:794,height:1123}});await p.goto('file://'+process.argv[2]+'/book.html');await p.waitForFunction(()=>document.body.dataset.ready==1);
const geometry=()=>p.evaluate(()=>[...document.querySelectorAll('.cn-st')].map(e=>{const r=e.getBoundingClientRect(),P=e.closest('.page').getBoundingClientRect();return [r.x-P.x,r.y-P.y,r.width,r.height,e.textContent]}));
const shared=await p.evaluate(()=>[2,3].map(n=>{const e=document.querySelector('#p'+n+' .cn-brand-ink');const m=e.transform.baseVal.consolidate().matrix;return [m.a,m.b,m.c,m.d,m.e,m.f]}));if(shared[0].slice(0,4).some((x,i)=>x!==shared[1][i])||Math.abs(shared[0][4]-shared[1][4]-794)>.001||shared[0][5]!==shared[1][5]||await p.locator('.cn-brand-graphic svg').count())throw Error('Source cropped or spread transforms discontinuous');
const before=await geometry();const photo=await p.locator('#p1 .cn-figi').screenshot();const spreadPhotos=[];for(const id of ['#p2 .cn-zone','#p3 .cn-zone'])spreadPhotos.push(await p.locator(id).screenshot());
const cuts=await p.evaluate(()=>[...document.querySelectorAll('.cn-brand-graphic')].map(e=>({color:getComputedStyle(e).color,opacity:e.querySelector('.cn-brand-ink').getAttribute('opacity'),cuts:e.querySelectorAll('[data-cut]').length})));
await p.evaluate(()=>{document.querySelectorAll('.cn-brand-graphic').forEach(e=>e.style.display='none');document.querySelectorAll('.page').forEach(e=>e.scrollTop=0)});const after=await geometry();const photoAfter=await p.locator('#p1 .cn-figi').screenshot();for(let i=0;i<2;i++)if(!spreadPhotos[i].equals(await p.locator('#p'+(i+2)+' .cn-zone').screenshot()))throw Error('Spread photograph changed by the graphic');
if(JSON.stringify(before)!==JSON.stringify(after)||!photo.equals(photoAfter)||cuts.length!==4||cuts[0].color!=='rgb(0, 43, 165)'||cuts[3].color!=='rgb(255, 255, 255)'||cuts.some(e=>e.opacity!=='0.05')||cuts.slice(0,3).some(e=>!e.cuts))throw Error(JSON.stringify({before,after,cuts}));
fs.writeFileSync(process.argv[2]+'/probe.json',JSON.stringify({textGeometryUnchanged:true,photoPixelsIdentical:true,cuts}));await b.close()})().catch(e=>{console.error(e);process.exit(1)});
''', encoding='utf-8')
        subprocess.run(['node', str(probe), str(p)], check=True)
        subprocess.run(['node', str(hb / 'pdf.js'), str(p), str(p / 'control.pdf')], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['pdftoppm', '-f', '4', '-l', '4', '-scale-to', '1123', '-png', str(p / 'control.pdf'), str(p / 'page')], check=True)
        pixels = np.array(Image.open(p / 'page-4.png').convert('RGB'))
        # White 5% geometry on the blue paper, excluding solid white text.
        faint = (pixels[:, :, 0] >= 8) & (pixels[:, :, 0] <= 20) & (pixels[:, :, 1] >= 48) & (pixels[:, :, 1] <= 64) & (pixels[:, :, 2] >= 165) & (pixels[:, :, 2] <= 180)
        assert faint.sum() > 10000, 'Brand geometry disappeared from the actual PDF'
        if os.environ.get('HB_BRAND_GALLERY'):
            from PIL import ImageDraw
            out = Image.new('RGB', (4 * 260, 394), '#E5E5E5')
            draw = ImageDraw.Draw(out)
            for i in range(4):
                im = Image.open(p / '.qa' / ('pg' + str(i) + '.png')).convert('RGB')
                im.thumbnail((250, 354))
                out.paste(im, (i * 260 + 5, 30))
                draw.text((i * 260 + 5, 9), ['WHITE / PHOTO', 'SPREAD LEFT', 'SPREAD RIGHT', 'BLUE / REVERSE'][i], fill='#111111')
            out.save(os.environ['HB_BRAND_GALLERY'], quality=92)
        assert brand_graphic.render(1, {}, spec['book'], str(p), 794, 1123, '#002BA5') == ''
        # Exercise the public builder: a declared spread is a pair, not two independent pictures.
        for label, change in [('missing-right', None), ('angle', 0), ('opacity', .08), ('frame', [0, 0, 1, 1])]:
            invalid = copy.deepcopy(spec)
            right = invalid['pages'][1]['right']
            if change is None:
                right.pop('brand_graphic')
            else:
                right['brand_graphic'][label] = change
            (p / 'book.yaml').write_text(yaml.safe_dump(invalid), encoding='utf-8')
            result = subprocess.run([sys.executable, str(hb / 'hb.py'), str(p)], capture_output=True, text=True)
            assert result.returncode != 0 and 'brand_graphic' in result.stdout and '共享' in result.stdout, (label, result.stdout, result.stderr)
        invalid = copy.deepcopy(spec)
        invalid['pages'][1]['left'].pop('brand_graphic')
        (p / 'book.yaml').write_text(yaml.safe_dump(invalid), encoding='utf-8')
        result = subprocess.run([sys.executable, str(hb / 'hb.py'), str(p)], capture_output=True, text=True)
        assert result.returncode != 0 and '共享跨页缺少' in result.stdout, (result.stdout, result.stderr)
        proof_spec = copy.deepcopy(spec)
        proof_spec['book']['binding'] = 'saddle'
        proof_spec['book']['series'] = {'chapters': {'label': 'CHAPTER', 'items': {'01': 'First', '02': 'Second'}}}
        proof_spec['pages'][0]['chapter'] = '01'
        proof_spec['pages'] += [dict(layout='PAPER', body=[dict(title='Information page')]) for _ in range(4)]
        proof_spec['pages'][-1]['chapter'] = '02'
        (p / 'book.yaml').write_text(yaml.safe_dump(proof_spec), encoding='utf-8')
        subprocess.run(['bash', str(hb / 'run.sh'), str(p), '--proof'], check=True, stdout=subprocess.DEVNULL)
        assert (p / '.proof/photos').is_symlink(), 'Proof no longer exercises shared photos'
        gate = json.loads((p / '.proof/.qa/gate.json').read_text(encoding='utf-8'))
        assert gate['result'] == 'PASS' and gate['scope'] == 'proof', gate
        result = subprocess.run([sys.executable, str(hb / 'gate.py'), 'check', str(p / '.proof')], capture_output=True, text=True)
        assert result.returncode != 0 and '试排/方向样张' in result.stdout, result.stdout
        # The same partial book remains invalid outside the proof entry point.
        result = subprocess.run([sys.executable, str(hb / 'hb.py'), str(p / '.proof')], capture_output=True, text=True)
        assert result.returncode != 0 and '骑马钉总页数' in result.stdout and '章节顺序不完整' in result.stdout, result.stdout
        for file in ('../symbol.svg', '/tmp/symbol.svg'):
            unsafe = copy.deepcopy(spec['book'])
            unsafe['brand_graphic']['file'] = file
            try:
                brand_graphic.render(1, {'brand_graphic': 'whole'}, unsafe, str(p), 794, 1123, '#002BA5')
            except ValueError:
                pass
            else:
                raise AssertionError('Non-project SVG accepted: ' + file)
        with tempfile.TemporaryDirectory(prefix='hb-outside-') as outside:
            external = Path(outside) / 'symbol.svg'
            external.write_text((p / 'photos/symbol.svg').read_text(encoding='utf-8'), encoding='utf-8')
            (p / 'photos/escape.svg').symlink_to(external)
            unsafe = copy.deepcopy(spec['book'])
            unsafe['brand_graphic']['file'] = 'photos/escape.svg'
            try:
                brand_graphic.render(1, {'brand_graphic': 'whole'}, unsafe, str(p), 794, 1123, '#002BA5')
            except ValueError:
                pass
            else:
                raise AssertionError('Unrelated external SVG symlink accepted')
        for bad in ({'variant': 'missing'}, {'variant': 'whole', 'opacity': 2}, {'variant': 'whole', 'spread': 'left'}):
            try:
                brand_graphic.render(1, {'brand_graphic': bad}, spec['book'], str(p), 794, 1123, '#002BA5')
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid brand graphic accepted: ' + json.dumps(bad))
        (p / 'photos/symbol.svg').write_text('<svg viewBox="0 0 1 1"><script/></svg>', encoding='utf-8')
        try:
            brand_graphic.render(1, {'brand_graphic': 'whole'}, spec['book'], str(p), 794, 1123, '#002BA5')
        except ValueError:
            pass
        else:
            raise AssertionError('Active SVG accepted')
    print('BRAND GRAPHIC: PASS（无重排、照片/跨页保护、白蓝纸取色、PDF可见、完整母形/共享矩阵、试排/共享素材/正式导出隔离、缺配对/参数不一致/非法资源拒绝）')


if __name__ == '__main__':
    main()
