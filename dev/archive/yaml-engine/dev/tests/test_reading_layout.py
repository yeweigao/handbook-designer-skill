#!/usr/bin/env python3
"""Exercise image-first entries and complete bilingual passages across explicit continuations."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile

import yaml
from make_test_photos import ensure
from test_editorial_layout import build

ROOT = Path(__file__).resolve().parents[2]
HB = ROOT / 'hb'


def main():
    with tempfile.TemporaryDirectory(prefix='hb-reading-') as td:
        project = Path(td)
        source = ROOT / 'templates/book.reading.yaml'
        (project / 'book.yaml').write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
        ensure(str(project), str(source))
        subprocess.run(['python3', str(HB / 'i18n.py'), 'split', str(project / 'book.yaml')], check=True)
        probe = project / 'probe.cjs'
        probe.write_text("""
const {chromium}=require(require.resolve('playwright',{paths:[process.argv[3]]}));
const fs=require('fs');
(async()=>{
let b;try{b=await chromium.launch({args:['--no-sandbox']})}
catch(e){if(!process.env.HB_CHROME)throw e;b=await chromium.launch({executablePath:process.env.HB_CHROME,args:['--no-sandbox']})}
const p=await b.newPage();
await p.goto('file://'+process.argv[2]+'/'+(process.argv[4]?'out/edit_en.html':'book.html'),{waitUntil:'networkidle'});
await p.waitForFunction(()=>document.body.dataset.ready==1);
if(process.argv[4]){
 await p.waitForFunction(()=>document.querySelectorAll('[data-src="book.series.essays.items.01"]').length===2);
 await p.locator('button[data-m="edit"]').click();
 await p.locator('[data-src="book.series.essays.items.01"]').first().fill('Describe one detail');
 await p.locator('button[data-m="view"]').click();
 await p.waitForFunction(()=>[...document.querySelectorAll('[data-src="book.series.essays.items.01"]')].every(e=>e.textContent==='Describe one detail'));
 await p.locator('button[data-m="edit"]').click();
 await p.locator('[data-src="book.series.essays.items.01"]').last().fill('Write what you see');
 await p.locator('button[data-m="view"]').click();
 await p.waitForFunction(()=>[...document.querySelectorAll('[data-src="book.series.essays.items.01"]')].every(e=>e.textContent==='Write what you see'&&!e.classList.contains('hb-changed')));
 await b.close();return;
}
const got=await p.evaluate(()=>{
const rect=e=>e.getBoundingClientRect();
return {qa:JSON.parse(document.body.dataset.cnqa||'[]'),loaded:[...document.images].every(i=>i.complete&&i.naturalWidth>0),
readings:[...document.querySelectorAll('.cn-reading')].map(el=>{
 const [side,main]=el.querySelectorAll('.cn-ed-cell'),h=side.querySelector('.cn-series-header');
 return {before:rect(main).top<rect(h||side.firstElementChild).top,title:side.querySelector('.cn-ttl').textContent,
 label:h?.querySelector('.cn-lab').textContent,item:h?.dataset.item,series:h?.dataset.series,
 paragraphs:[...main.querySelectorAll('.cn-tx:not(.cn-t20) p')].map(e=>e.textContent),
 sizes:[...main.querySelectorAll('.cn-tx:not(.cn-t20)')].map(e=>getComputedStyle(e).fontSize)};
}),openings:[...document.querySelectorAll('.page')].filter(pg=>pg.querySelector('.cn-ed-figure')&&!pg.querySelector('.cn-ed-rule')).map(pg=>({
before:rect(pg.querySelector('.cn-ed-figure')).bottom<=rect(pg.querySelector('.cn-disp')).top,
imageHeight:rect(pg.querySelector('img')).height}))};
});
fs.writeFileSync(process.argv[2]+'/probe.json',JSON.stringify(got));await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
""", encoding='utf-8')

        def measure(folder):
            subprocess.run(['node', str(probe), str(folder), str(HB)], check=True)
            return json.loads((folder / 'probe.json').read_text(encoding='utf-8'))

        for lang in ('zh', 'en'):
            folder = project / lang
            spec = yaml.safe_load((folder / 'book.yaml').read_text(encoding='utf-8'))
            build(folder, spec)
            got = measure(folder)
            assert not got['qa'], got['qa']
            assert got['loaded'] and len(got['openings']) == 2
            assert all(o['before'] and o['imageHeight'] > 300 for o in got['openings'])
            expected = [page for page in spec['pages'] if page['layout'] == 'READING']
            assert len(got['readings']) == len(expected) == 4
            for result, page in zip(got['readings'], expected):
                assert result['before'], 'Body no longer begins above the sidebar title'
                assert result['paragraphs'] == page['text'], 'A paragraph changed, split or reordered'
                assert result['sizes'] == ['16px'], 'Body font shrank to fit'
                q = page['series_header']
                assert result['series'] == q['series'] and result['item'] == q['item']
                assert result['title'] == spec['book']['series'][q['series']]['items'][q['item']]
                if q.get('continuation'):
                    assert ('续读' if lang == 'zh' else 'CONTINUED') in result['label']

        subprocess.run(['python3', str(HB / 'edit_page.py'), str(project / 'en')], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['node', str(probe), str(project / 'en'), str(HB), 'editor'], check=True)
        base = copy.deepcopy(spec)
        for change, message in [('empty', '需要 text'), ('orphan', '续页前缺'), ('image', '需要实际')]:
            bad = copy.deepcopy(base)
            if change == 'empty': bad['pages'][1]['text'] = []
            elif change == 'orphan': bad['pages'] = [bad['pages'][2]]
            else: bad['pages'][0]['image'] = 'art'
            result = build(project / 'en', bad, expect=False)
            assert result.returncode != 0 and message in result.stderr + result.stdout

        # Over-capacity copy remains intact and is reported; this is not automatic pagination.
        crowded = copy.deepcopy(base)
        crowded['pages'] = [crowded['pages'][1]]
        crowded['pages'][0]['text'] *= 5
        build(project / 'en', crowded)
        got = measure(project / 'en')
        assert got['qa'], 'Over-capacity reading page was silently accepted'
        assert got['readings'][0]['sizes'] == ['16px']
        assert got['readings'][0]['paragraphs'] == crowded['pages'][0]['text']

        # The two new arrangements still use the canonical dimensions on small canvases.
        for canvas in ('a5', 'xhs'):
            small = copy.deepcopy(base)
            small['book']['canvas'] = canvas
            small['pages'] = [dict(layout='PHOTO_OPEN', image='forest-wide.jpg', title='Look closely.'),
                              dict(layout='READING', title='Keep a record', text=['A short, complete observation.'])]
            build(project / 'en', small)
            got = measure(project / 'en')
            assert not got['qa'] and got['openings'][0]['before'] and got['readings'][0]['sizes'] == ['14px'], got

        # Legacy images.py regression: only the grid property value is a list of tracks.
        folder = project / 'en'
        image = next((folder / 'img').glob('*.jpg'))
        (folder / 'map.json').write_text(json.dumps({'use': [dict(file='forest-wide.jpg', img=image.name, page=1)]}), encoding='utf-8')
        (folder / 'book.html').write_text('<section class="page" data-n="1"><div style="width:640px">'
            '<div style="display:grid;grid-template-columns:424px 184px;column-gap:32px">'
            '<div style="height:200px"><img src="img/' + image.name + '"></div></div></div></section>', encoding='utf-8')
        subprocess.run(['python3', str(HB / 'images.py'), str(folder)], check=True, stdout=subprocess.DEVNULL)
        assert yaml.safe_load((folder / 'images.yaml').read_text(encoding='utf-8'))['images']['forest-wide.jpg']['dpi'] > 0
    print('READING: PASS — bilingual paragraphs, continuation identity, unchanged body size, image-first order, over-capacity rejection, small canvases, grid image inventory')


if __name__ == '__main__':
    main()
