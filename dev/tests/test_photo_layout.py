#!/usr/bin/env python3
"""固定页图片回归：真实渲染 PDF，防止第二张图在打印分页时消失。

测试图为程序生成的纯色控制图，无第三方素材；不代替真实照片的主体裁切审稿。
"""
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image
import numpy as np
import yaml

HB_DIR = Path(__file__).resolve().parents[2] / 'hb'
sys.path.insert(0, str(HB_DIR))
import wash


def main():
    hb = HB_DIR
    if not shutil.which('pdftoppm'):
        raise SystemExit('照片 PDF 回归需要 pdftoppm（Poppler）；未执行，不能视为通过')
    with tempfile.TemporaryDirectory(prefix='hb-photo-') as td:
        project = Path(td)
        (project / 'photos').mkdir()
        for name, color in [('red', '#D82424'), ('blue', '#164BCB')]:
            Image.new('RGB', (1600, 800), color).save(project / 'photos' / (name + '.jpg'))
        control = np.zeros((1000, 1600, 3), dtype=np.uint8)
        control[:333] = (216, 36, 36); control[333:667] = (20, 180, 40); control[667:] = (22, 75, 203)
        Image.fromarray(control).save(project / 'frame.jpg')
        wash.bake2(str(project / 'frame.jpg'), str(project / 'frame-out.jpg'), 794, 1123,
                   (.5, .5), (397, 1123 * .2), 1, lambda x, y: 0 * x, (0, 0, 1, .4))
        a = np.asarray(Image.open(project / 'frame-out.jpg').convert('RGB'))[:round(1123 * .4 * wash.S)]
        assert ((a[..., 2] > 140) & (a[..., 0] < 90) & (a[..., 1] < 130)).mean() > .15, '半页图框仍按整页裁图'
        pages = [dict(layout='FULL', index=str(i), title='Chapter ' + str(i)) for i in range(1, 8)]
        pages += [
            dict(layout='MIX', title='Two photographs', images=['red.jpg', 'blue.jpg'],
                 sections=[dict(t='First', x='The upper image is red.'), dict(t='Second', x='The lower image is blue.')]),
            dict(layout='PAPER', body=[dict(title='Primary image'), dict(figure='red.jpg', role='primary')]),
            dict(layout='ONE', title='Balanced reading', image='blue.jpg',
                 text=['A complete paragraph keeps the reading width comfortable. ' * 7] * 2),
            dict(layout='PAPER', body=[dict(figure='blue.jpg', bleed='page')], folio=False),
            dict(layout='PAPER', body=[dict(title='Reading columns'),
                 dict(p='A complete paragraph keeps the reading width comfortable. ' * 12)]),
            dict(layout='ONE', title='A complete introduction',
                 intro='This introduction stays in one reading block, with its full meaning intact. ' * 3),
            dict(layout='PAPER', body=[dict(p='A complete paragraph keeps the reading width comfortable. ' * 6, flow='keep')]),
            dict(layout='PAPER', body=[dict(p='Two explicitly selected reading columns keep the intended reading direction.', flow='columns')]),
            dict(layout='PAPER', body=[dict(kv=[['Schools:', '5'], ['Delegates:', '42']]),
                 dict(p='This introduction stays in one reading block, with its full meaning intact. ' * 3, size=18)]),
            dict(layout='PAPER', body=[dict(title='Five days'), dict(timeline=[['D1', 'Fri · Arrival', 'Evening\nArrival and check-in.'],
                 ['D2', 'Sat · Session', 'Morning / Afternoon / Evening\nConference sessions.'],
                 ['D3', 'Sun · Session', 'Debate and closing.']], style='axis', next='D4–D5 →')]),
            dict(layout='PAPER', body=[dict(title='Five days'), dict(timeline=[['D4', 'Mon · Field Study', 'Observation and research.'],
                 ['D5', 'Tue · Explore', 'Old-city visit and return.']], style='axis')]),
            dict(layout='FULL', index='19', title='Chapter 19'),
            dict(layout='SPREAD_H', image='blue.jpg', image_position='bottom', split=564,
                 left=dict(body=[dict(title='Left reading area')]), right=dict(body=[dict(title='Right reading area')])),
            dict(layout='FULL', index='22', title='Chapter 22'),
            dict(layout='FULL', index='23', title='Chapter 23'),
            dict(layout='FULL', index='24', title='Chapter 24'),
        ]
        titles = {f'{i:02d}': 'Experience ' + str(i) for i in range(1, 6)}
        pages += [dict(layout='PAPER', body=[dict(series_header=dict(series='experiences', item=i)),
                  dict(p='Read the full experience.', flow='keep')]) for i in titles]
        pages += [dict(layout='PAPER', body=[dict(series_header=dict(series='experiences', item='03',
                  continuation=True, title='Fieldwork output')), dict(timeline=[dict(k='D1', t='Arrival',
                  period='Evening', events=['Check-in', 'Meal stop'])], style='axis'),
                  dict(items=['Meals', 'Insurance'], style='bullet'),
                  dict(cards=[dict(t='Field visit', meta=['Old city', 'Morning'], x=['Observation notes', 'Draft clauses'])], cols=1)])]
        pages += [dict(layout='PAPER', surface=sf, body=[dict(title='Paper surface ' + sf),
                  dict(items=['Meals', 'Insurance'], style='plain')]) for sf in ('A', 'B', 'dark', 'paper')]
        pages += [dict(layout='GRID', title='Navigation', toc=[['01', 'Workshop', 'Read the guide', '1']], notes=['Navigation note'])]
        spec = dict(book=dict(title='Photo layout regression', lang='en', style='swiss', duotone='off', image_bleed='both',
                    colors=dict(A='#002BA5', B='#F0F2F5', INK='#111111', PAPER='#FFFFFF', TINT='#F2F2F2'),
                    typesetting='editorial', typography='bold', fonts=dict(preset='sans', title=['playfair'], css=dict(title_w=500)),
                    series=dict(experiences=dict(label='EXPERIENCE', items=titles))), pages=pages)
        (project / 'book.yaml').write_text(yaml.safe_dump(spec), encoding='utf-8')
        subprocess.run(['python3', str(hb / 'hb.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
        probe = project / 'probe.cjs'
        probe.write_text('''const {chromium}=require(require.resolve('playwright',{paths:[process.argv[3]]}));
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});const p=await b.newPage();
await p.goto('file://'+process.argv[2]+'/book.html',{waitUntil:'networkidle'});
await p.waitForFunction(()=>document.body.dataset.ready==1);
const got=await p.evaluate(()=>{const pages=[...document.querySelectorAll('.page')];
const f=pages[8].querySelector('.cn-figi img'),r=f.getBoundingClientRect();
const P=pages[8].getBoundingClientRect(),b=pages[10].querySelector('.cn-figi img').getBoundingClientRect(),B=pages[10].getBoundingClientRect();
const intro=pages[12].querySelector('.cn-tx'),kept=pages[13].querySelector('.cn-tx'),forced=pages[14].querySelector('.cn-tx'),big=pages[15].querySelector('.cn-tx');
const axes=[pages[16],pages[17]].map(pg=>{const a=pg.querySelector('.cn-timeaxis'),row=a.querySelector('.cn-axisrow'),date=row.querySelector('.cn-axisdate');return {width:a.clientWidth,columns:getComputedStyle(row).gridTemplateColumns,dateFont:parseFloat(getComputedStyle(date).fontSize),bodyFont:parseFloat(getComputedStyle(row.querySelector('.cn-tx')).fontSize),days:[...a.querySelectorAll('.cn-axisdate')].map(e=>e.textContent),rail:getComputedStyle(a,'::before').width}});
const spread=[pages[19],pages[20]].map(pg=>{const z=pg.querySelector('.cn-zone').getBoundingClientRect(),a=pg.getBoundingClientRect();return {top:z.top-a.top,height:z.height,source:pg.querySelector('img').getAttribute('src')}});
const series=pages.slice(24,29).map(pg=>{const h=pg.querySelector('.cn-series-header'),num=h.querySelector('.cn-series-index'),title=h.querySelector('.cn-ttl');return {item:h.dataset.item,numberFamily:getComputedStyle(num).fontFamily,titleFamily:getComputedStyle(title).fontFamily,size:getComputedStyle(title).fontSize,weight:getComputedStyle(title).fontWeight}});
const surfaces=pages.slice(30,34).map(pg=>({bg:getComputedStyle(pg).backgroundColor,fg:getComputedStyle(pg.querySelector('.cn-st')).color,footer:getComputedStyle(pg.querySelector('.cn-fo')).color,marker:getComputedStyle(pg.querySelector('ul li'),'::before').content,padding:getComputedStyle(pg.querySelector('ul li')).paddingLeft,text:pg.querySelector('ul').textContent}));
const note=pages[34].querySelector('.cn-notes li'),notes={text:note.textContent,marker:getComputedStyle(note,'::before').content,padding:getComputedStyle(note).paddingLeft};
return {notes,surfaces,series,cardMeta:[...pages[29].querySelectorAll('.cn-cardmeta span')].map(e=>e.textContent),cardBody:pages[29].querySelector('.cn-card .cn-tx').textContent,cardMarkers:[...pages[29].querySelectorAll('.cn-card ul li')].map(e=>({marker:getComputedStyle(e,'::before').content,padding:getComputedStyle(e).paddingLeft})),bulletMarker:getComputedStyle(pages[29].querySelector('.cn-list-bullet li'),'::before').content,bullet:pages[29].querySelector('ul.cn-li')?.textContent,continuation:pages[29].querySelector('.cn-series-cont').textContent,events:[...pages[29].querySelectorAll('.cn-axis-events li')].map(e=>e.textContent),period:pages[29].querySelector('.cn-axisperiod').textContent,bodyLeading:getComputedStyle(kept).lineHeight,leadSize:getComputedStyle(big).fontSize,figure:[r.width,r.height],bleed:[r.left-P.left,r.right-P.left],fullpage:[b.left-B.left,b.top-B.top,b.width,b.height],reading:!!pages[11].querySelector('.cn-tx.cn-cols2'),columns:!!pages[9].querySelector('.cn-cols2'),body:parseFloat(getComputedStyle(pages[9].querySelector('.cn-tx')).fontSize),introColumns:getComputedStyle(intro).columnCount,bigColumns:getComputedStyle(big).columnCount,keptColumns:getComputedStyle(kept).columnCount,forcedColumns:getComputedStyle(forced).columnCount,wrap:getComputedStyle(kept.querySelector('p')).textWrapStyle,axes,spread}});
require('fs').writeFileSync(process.argv[2]+'/probe.json',JSON.stringify(got));await b.close()})().catch(e=>{console.error(e);process.exit(1)});
''', encoding='utf-8')
        subprocess.run(['node', str(probe), str(project), str(hb)], check=True)
        got = json.loads((project / 'probe.json').read_text())
        assert got['figure'][0] == 794 and got['figure'][1] >= 300, got
        assert got['bleed'] == [0, 794] and got['fullpage'] == [0, 0, 794, 1123], got
        assert got['reading'] and got['columns'] and got['body'] == 16, got
        assert got['introColumns'] == got['keptColumns'] == got['bigColumns'] == 'auto' and got['forcedColumns'] == '2', got
        assert got['wrap'] == 'pretty', got
        assert got['bodyLeading'] == '24px' and got['leadSize'] == '20px', got
        assert [s['item'] for s in got['series']] == ['01', '02', '03', '04', '05'], got
        assert len({(s['size'], s['weight'], s['titleFamily'], s['numberFamily']) for s in got['series']}) == 1, got
        assert 'HB-playfair' in got['series'][0]['titleFamily'] and 'HB-noto-sans-sc' in got['series'][0]['numberFamily'], got
        assert '03' in got['continuation'] and 'Fieldwork output' in got['continuation'], got
        assert got['events'] == ['Check-in', 'Meal stop'] and got['period'] == 'Evening', got
        assert got['bullet'] == 'MealsInsurance', got
        assert [got['surfaces'][i]['bg'] for i in (0, 2, 3)] == ['rgb(0, 43, 165)', 'rgb(17, 17, 17)', 'rgb(255, 255, 255)'], got['surfaces']
        gray = [int(v) for v in got['surfaces'][1]['bg'][4:-1].split(',')]
        assert len(set(gray)) == 1 and 230 <= gray[0] < 255, got['surfaces']
        assert [s['fg'] for s in got['surfaces']] == ['rgb(255, 255, 255)', 'rgb(17, 17, 17)', 'rgb(255, 255, 255)', 'rgb(17, 17, 17)'], got['surfaces']
        assert all(s['marker'] == 'none' and s['padding'] == '0px' and s['text'] == 'MealsInsurance' for s in got['surfaces']), got['surfaces']
        assert got['notes'] == dict(text='Navigation note', marker='none', padding='0px'), got['notes']
        assert got['surfaces'][0]['footer'] == got['surfaces'][2]['footer'] == 'rgba(255, 255, 255, 0.84)', got['surfaces']
        assert got['cardMeta'] == ['Old city', 'Morning'] and got['cardBody'] == 'Observation notesDraft clauses', got
        assert len(got['cardMarkers']) == 2 and all(x['marker'] == 'none' and x['padding'] == '0px' for x in got['cardMarkers']), got
        assert got['bulletMarker'] == '"•"', got
        ax, bx = got['axes']
        assert ax['width'] == bx['width'] and ax['columns'] == bx['columns'], got
        assert ax['dateFont'] == bx['dateFont'] > ax['bodyFont'] == bx['bodyFont'] == 16, got
        assert ax['rail'] == bx['rail'] == '2px' and ax['days'] + bx['days'] == ['D1', 'D2', 'D3', 'D4', 'D5'], got
        assert got['spread'][0] == got['spread'][1] and got['spread'][0]['top'] == 564, got
        subprocess.run(['node', str(hb / 'pdf.js'), str(project), str(project / 'test.pdf')], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['pdftoppm', '-f', '8', '-l', '8', '-singlefile', '-scale-to', '842', '-png',
                        str(project / 'test.pdf'), str(project / 'page8')], check=True, stdout=subprocess.DEVNULL)
        a = np.asarray(Image.open(project / 'page8.png').convert('RGB')).astype(float)
        red = ((a[..., 0] > 150) & (a[..., 1] < 90) & (a[..., 2] < 90)).mean()
        blue = ((a[..., 2] > 140) & (a[..., 0] < 90) & (a[..., 1] < 130)).mean()
        assert red > .12 and blue > .12, dict(red=float(red), blue=float(blue))
        subprocess.run(['pdftoppm', '-f', '11', '-l', '11', '-singlefile', '-scale-to', '842', '-png',
                        str(project / 'test.pdf'), str(project / 'page11')], check=True, stdout=subprocess.DEVNULL)
        a = np.asarray(Image.open(project / 'page11.png').convert('RGB')).astype(float)
        assert ((a[..., 2] > 140) & (a[..., 0] < 90) & (a[..., 1] < 130)).mean() > .98
        for n, color in ((31, (0, 43, 165)), (33, (17, 17, 17))):
            subprocess.run(['pdftoppm', '-f', str(n), '-l', str(n), '-singlefile', '-scale-to', '842', '-png',
                            str(project / 'test.pdf'), str(project / ('surface' + str(n)))], check=True, stdout=subprocess.DEVNULL)
            a = np.asarray(Image.open(project / ('surface' + str(n) + '.png')).convert('RGB')).astype(float)
            assert (np.max(np.abs(a - color), axis=2) < 10).mean() > .9, '实际PDF纸面未保留选定实色'
        for n in (20, 21):
            subprocess.run(['pdftoppm', '-f', str(n), '-l', str(n), '-singlefile', '-scale-to', '842', '-png',
                            str(project / 'test.pdf'), str(project / ('spread' + str(n)))], check=True, stdout=subprocess.DEVNULL)
            a = np.asarray(Image.open(project / ('spread' + str(n) + '.png')).convert('RGB')).astype(float)
            blue = (a[..., 2] > 140) & (a[..., 0] < 90) & (a[..., 1] < 130)
            assert blue[:int(len(a) * .45)].mean() < .01 and blue[int(len(a) * .6):].mean() > .98
        spec['pages'] = [dict(layout='PAPER', body=[dict(series_header=dict(series='experiences', item='06'))])]
        (project / 'book.yaml').write_text(yaml.safe_dump(spec), encoding='utf-8')
        bad = subprocess.run(['python3', str(hb / 'hb.py'), str(project)], capture_output=True, text=True)
        assert bad.returncode != 0 and 'series_header' in bad.stdout + bad.stderr, '不存在的系列项未被拒绝'
        from pypdf import PdfReader
        chapters = {'01': 'Chapter one', '02': 'Chapter two', '03': 'Chapter three', '04': 'Chapter four'}
        spec['book']['series']['chapters'] = dict(label='CHAPTER', items=chapters)
        spec['book']['binding'] = 'saddle'
        spec['pages'] = [dict(layout='FULL', title='Cover')]
        for ch, title in chapters.items():
            spec['pages'].append(dict(layout='PAPER', chapter=ch, body=[dict(series_header=dict(series='chapters', item=ch))]) if ch == '03' else dict(layout='FULL', index=ch, title=title))
        spec['pages'] += [dict(layout='PAPER', body=[dict(title=t)]) for t in ('Information', 'Invitation', 'Register')]
        (project / 'book.yaml').write_text(yaml.safe_dump(spec), encoding='utf-8')
        subprocess.run(['bash', str(hb / 'run.sh'), str(project)], check=True, stdout=subprocess.DEVNULL)
        html = (project / 'book.html').read_text(encoding='utf-8')
        assert re.findall(r'data-chapter="([^"]+)"', html) == list(chapters), '合并章节缺少语义章标'
        subprocess.run(['bash', str(hb / 'export.sh'), str(project), 'chapters'], check=True,
                       stdout=subprocess.DEVNULL, env=dict(os.environ, HB_NO_EDITABLE=''))
        for filename in ('chapters.pdf', 'chapters_可编辑.pdf'):
            pdf = PdfReader(project / 'out' / filename)
            got_chapters = [(x.title, pdf.get_destination_page_number(x) + 1) for x in pdf.outline if not isinstance(x, list) and re.match(r'^0[1-4] · ', x.title)]
            assert got_chapters == [(k + ' · ' + v, i + 2) for i, (k, v) in enumerate(chapters.items())], (filename, got_chapters)
        spec['pages'].pop()
        (project / 'book.yaml').write_text(yaml.safe_dump(spec), encoding='utf-8')
        bad = subprocess.run(['python3', str(hb / 'hb.py'), str(project)], capture_output=True, text=True)
        assert bad.returncode != 0 and '骑马钉总页数' in bad.stdout + bad.stderr, '不合装订的页数未被拦截'
        spec['pages'].append(dict(layout='PAPER', body=[dict(title='Register')]))
        spec['pages'][3]['chapter'] = '02'
        (project / 'book.yaml').write_text(yaml.safe_dump(spec), encoding='utf-8')
        bad = subprocess.run(['python3', str(hb / 'hb.py'), str(project)], capture_output=True, text=True)
        assert bad.returncode != 0 and '章节顺序不完整' in bad.stdout + bad.stderr, '章号丢失/重复未被拦截'
        print('PHOTO REGRESSION: PASS（照片/排印/系列/清单、章节合页书签、骑马钉页数与章序门禁）')


if __name__ == '__main__':
    main()
