import test, {before, after} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {launch} from '../../../hb/core/browser.mjs';

const css = await fs.readFile(new URL('../../../families/folio/folio.css', import.meta.url), 'utf8');
let browser;
before(async () => { ({browser} = await launch()); });
after(async () => { await browser?.close(); });

async function fixture(html, read) {
  const page = await browser.newPage();
  try {
    await page.setContent(html);
    await page.addStyleTag({content: css});
    return await read(page);
  } finally {
    await page.close();
  }
}
const near = (actual, expected, label = '') => assert.ok(Math.abs(actual - expected) < .1, `${label}: ${actual} ≠ ${expected}`);
const pxmm = 96 / 25.4;
function contrast(a, b) {
  const luminance = color => {
    const rgb = color.match(/[\d.]+/g).slice(0, 3).map(Number).map(value => {
      const s = value / 255;
      return s <= .04045 ? s / 12.92 : ((s + .055) / 1.055) ** 2.4;
    });
    return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
  };
  const x = luminance(a), y = luminance(b);
  return (Math.max(x, y) + .05) / (Math.min(x, y) + .05);
}

test('every nested paper, soft, dark and accent surface resets readable text roles', async () => {
  const surfaces = ['paper', 'soft', 'dark', 'accent'];
  const html = surfaces.flatMap(outer => surfaces.flatMap(middle => surfaces.map(inner =>
    `<div class="fl-scope fl-surface-${outer}"><div class="fl-surface-${middle}"><section data-case="${outer}/${middle}/${inner}" class="fl-surface-${inner}"><p class="fl-text-main">正文</p><p class="fl-text-muted">来源说明</p><p class="fl-text-accent">重点</p></section></div></div>`
  ))).join('');
  const rows = await fixture(html, page => page.evaluate(() => [...document.querySelectorAll('[data-case]')].map(el => ({
    name: el.dataset.case,
    bg: getComputedStyle(el).backgroundColor,
    colors: [...el.children].map(child => getComputedStyle(child).color),
  }))));
  assert.equal(rows.length, 64);
  for (const row of rows) {
    for (const color of row.colors) assert.ok(contrast(color, row.bg) >= 4.5, `${row.name}: ${color} on ${row.bg}`);
    const reference = rows.find(other => other.name === `paper/paper/${row.name.split('/').at(-1)}`);
    assert.deepEqual([row.bg, ...row.colors], [reference.bg, ...reference.colors], `${row.name} leaked ancestor roles`);
  }
});

test('size atoms select actual ladder weights with or without a role, while numbers keep the numeric family', async () => {
  const sizes = [
    ['aux', 11, 600, 600], ['key', 13, 600, 600], ['small', 14, 500, 500],
    ['body', 16, 400, 400], ['lead', 20, 600, 400], ['h3', 24, 600, 400],
    ['h2', 32, 700, 300], ['h1', 46, 700, 250], ['display', 64, 900, 200],
    ['hero', 112, 900, 200], ['giant', 196, 900, 200], ['colossal', 280, 900, 200],
  ];
  const html = ['bold', 'light'].map(mode => `<section class="fl-scope fl-type-${mode}">${sizes.map(([name]) =>
    ['', 'fl-number', 'fl-font-number'].map(role => `<p data-mode="${mode}" data-size="${name}" data-role="${role}" class="${role} fl-size-${name}">2026<strong>28</strong></p>`).join('')
  ).join('')}</section>`).join('');
  const rows = await fixture(html, page => page.evaluate(() => [...document.querySelectorAll('p')].map(el => {
    const s = getComputedStyle(el);
    return {...el.dataset, px: parseFloat(s.fontSize), weight: +s.fontWeight, family: s.fontFamily,
      strong: +getComputedStyle(el.querySelector('strong')).fontWeight, synthesis: s.fontSynthesis};
  })));
  assert.equal(rows.length, 72);
  for (const row of rows) {
    const [, px, bold, light] = sizes.find(([name]) => name === row.size);
    const numeric = row.role !== '';
    const weight = row.mode === 'bold' ? bold : light;
    assert.equal(row.px, px, `${row.mode}/${row.role}/${row.size} size`);
    assert.equal(row.weight, weight, `${row.mode}/${row.role}/${row.size} weight`);
    assert.equal(row.strong, row.mode === 'light' ? weight : Math.min(weight + 200, 900), `${row.mode}/${row.role}/${row.size} strong`);
    assert.equal(row.synthesis, 'none');
    if (numeric) assert.match(row.family, /^Inter(?:,|$)/);
  }
});

test('legend and metadata child defaults yield to span, start, alignment and font atoms', async () => {
  const rows = await fixture(`<div class="fl-scope" style="--fl-gutter:24px;width:720px">
    <div class="fl-legend"><span id="number" class="fl-start-2 fl-span-2 fl-text-center fl-weight-regular">01</span><span id="caption" class="fl-start-4 fl-span-2">A caption</span><span id="credit" class="fl-start-1 fl-span-2 fl-row-start-2 fl-text-start fl-text-accent">Credit</span></div>
    <div class="fl-meta"><span>Series</span><span id="meta-end" class="fl-start-3 fl-span-2 fl-text-start fl-font-number fl-size-key">12</span></div>
  </div>`, page => page.evaluate(() => ['number', 'caption', 'credit', 'meta-end'].map(id => {
    const el = document.getElementById(id), s = getComputedStyle(el), r = el.getBoundingClientRect(), p = el.parentElement.getBoundingClientRect();
    return {id, x: r.left - p.left, width: r.width, align: s.textAlign, weight: s.fontWeight, family: s.fontFamily, color: s.color};
  })));
  for (const row of rows) near(row.width, 224, `${row.id} span`);
  near(rows[0].x, 124, 'legend number start');
  near(rows[1].x, 372, 'legend caption start');
  near(rows[2].x, 0, 'legend credit start');
  near(rows[3].x, 248, 'metadata last item start');
  assert.equal(rows[0].align, 'center');
  assert.equal(rows[0].weight, '600');
  assert.equal(rows[2].align, 'start');
  assert.equal(rows[3].align, 'start');
  assert.match(rows[3].family, /^Inter(?:,|$)/);
  assert.equal(rows[3].weight, '600');
  assert.equal(rows[2].color, 'rgb(200, 48, 36)');
});

test('three, four and five-event timelines keep explicit tracks and full-width rows', async () => {
  const rows = await fixture(`<div class="fl-scope">${[3, 4, 5].map(count => `<div data-count="${count}" class="fl-l-timeline fl-axis fl-surface-accent" style="width:720px;--fl-gutter:24px;--fl-timeline-count:${count}"><h2 class="fl-l-full">行程</h2>${Array.from({length: count}, (_, i) => `<article class="fl-l-item ${i === 1 ? 'fl-axis-now' : ''}"><p>第 ${i + 1} 站</p><p>活动内容</p></article>`).join('')}<p class="fl-l-full">说明与来源</p></div>`).join('')}</div>`, page => page.evaluate(() => [...document.querySelectorAll('[data-count]')].map(el => {
    const r = el.getBoundingClientRect(), now = el.querySelector('.fl-axis-now');
    const rect = child => { const box = child.getBoundingClientRect(); return {x: box.left - r.left, y: box.top - r.top, width: box.width}; };
    return {count: +el.dataset.count, tracks: getComputedStyle(el).gridTemplateColumns.split(' ').length,
      items: [...el.querySelectorAll('.fl-l-item')].map(rect), full: [...el.querySelectorAll('.fl-l-full')].map(rect),
      fullTicks: [...el.querySelectorAll('.fl-l-full')].map(child => getComputedStyle(child, '::before').content),
      marker: getComputedStyle(now, '::before').backgroundColor, markerWidth: parseFloat(getComputedStyle(now, '::before').width),
      tickWidth: parseFloat(getComputedStyle(el.querySelector('.fl-l-item'), '::before').width), bg: getComputedStyle(el).backgroundColor};
  })));
  for (const row of rows) {
    assert.equal(row.tracks, row.count, `timeline ${row.count} created an implicit track`);
    const width = (720 - (row.count - 1) * 24) / row.count;
    row.items.forEach((item, i) => { near(item.width, width); near(item.x, i * (width + 24)); near(item.y, row.items[0].y); });
    for (const full of row.full) { near(full.x, 0); near(full.width, 720); }
    assert.ok(row.full[0].y < row.items[0].y && row.full[1].y > row.items[0].y);
    assert.deepEqual(row.fullTicks, ['none', 'none']);
    assert.ok(contrast(row.marker, row.bg) >= 4.5, `current marker disappears on accent surface: ${row.marker}`);
    assert.ok(row.markerWidth > row.tickWidth, 'current event also needs a non-colour distinction');
  }
});

const image = '<img src="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%271200%27 height=%27800%27/%3E" alt="">';
test('top and full bleed compose with frames and preserve mirrored text safety', async () => {
  const rows = await fixture(`<style>.page{position:relative;width:216mm;height:303mm;--bleed:3mm;--safe-top:8mm;--safe-bottom:8mm;--safe-left:8mm;--safe-right:8mm}</style>${['top', 'full'].flatMap(kind => ['left', 'right'].map(side => `<section class="page" data-side="${side}" data-kind="${kind}"><div class="fl-l-bleed-${kind}"><figure class="fl-l-photo fl-frame">${image}</figure><div class="fl-area fl-l-copy">Copy</div>${kind === 'full' ? '<div class="fl-l-caption">Caption</div>' : ''}</div></section>`)).join('')}`, page => page.evaluate(() => [...document.querySelectorAll('.page')].map(el => {
    const r = el.getBoundingClientRect();
    const rect = selector => { const x = el.querySelector(selector).getBoundingClientRect(); return {left: x.left - r.left, top: x.top - r.top, right: r.right - x.right, bottom: r.bottom - x.bottom, width: x.width, height: x.height}; };
    const caption = el.querySelector('.fl-l-caption'), cs = caption && getComputedStyle(caption);
    return {kind: el.dataset.kind, side: el.dataset.side, width: r.width, height: r.height, photo: rect('figure'), image: rect('img'), copy: rect('.fl-l-copy'), caption: cs && {left: parseFloat(cs.paddingLeft), right: parseFloat(cs.paddingRight), bottom: parseFloat(cs.paddingBottom)}};
  })));
  for (const row of rows) {
    near(row.photo.left, 0); near(row.photo.top, 0); near(row.photo.width, row.width);
    near(row.photo.height, row.height * (row.kind === 'top' ? .58 : 1));
    near(row.image.width, row.photo.width); near(row.image.height, row.photo.height);
    near(row.copy.left, (row.side === 'left' ? 18 : 22) * pxmm);
    near(row.copy.right, (row.side === 'left' ? 22 : 18) * pxmm);
    near(row.copy.bottom, 24 * pxmm);
    near(row.copy.top, row.kind === 'top' ? row.photo.height + 28 : 21 * pxmm);
    if (row.caption) {
      near(row.caption.left, row.copy.left); near(row.caption.right, row.copy.right);
      assert.ok(row.caption.bottom >= 11 * pxmm - .1);
    }
  }
});

test('short top-bleed images cannot pull copy inside explicit safe bounds', async () => {
  const row = await fixture(`<style>.page{position:relative;width:216mm;height:303mm;--bleed:3mm;--safe-top:30mm;--safe-bottom:25mm;--safe-left:26mm;--safe-right:27mm;--fl-image-height:40px}</style><section class="page" data-side="left"><div class="fl-l-bleed-top"><figure class="fl-l-photo fl-frame">${image}</figure><div class="fl-area fl-l-copy">Readable copy</div></div></section>`, page => page.evaluate(() => {
    const page = document.querySelector('.page').getBoundingClientRect(), copy = document.querySelector('.fl-l-copy').getBoundingClientRect(), photo = document.querySelector('figure').getBoundingClientRect();
    return {top: copy.top - page.top, bottom: page.bottom - copy.bottom, left: copy.left - page.left, right: page.right - copy.right, gap: copy.top - photo.bottom};
  }));
  assert.ok(row.top >= 33 * pxmm - .1, `top-bleed copy enters safe area: ${row.top}px < ${33 * pxmm}px`);
  assert.ok(row.gap >= 28 - .1);
  near(row.bottom, 28 * pxmm); near(row.left, 29 * pxmm); near(row.right, 30 * pxmm);
});

test('column and baseline overlays combine and reset only their own nested diagnostic layers', async () => {
  const rows = await fixture(`<div class="fl-scope"><div id="both" class="fl-show-columns fl-show-baseline" style="width:720px;padding:28px"><div id="base" class="fl-show-baseline"><div id="columns12" class="fl-show-columns-12"><div id="plain">No overlay</div></div></div><div id="columns" class="fl-show-columns"><div id="both12" class="fl-show-columns-12 fl-show-baseline">Combined twelve</div></div></div></div>`, page => page.evaluate(() => ['both', 'base', 'columns12', 'plain', 'columns', 'both12'].map(id => {
    const el = document.getElementById(id), s = getComputedStyle(el);
    return {id, image: s.backgroundImage, origin: s.backgroundOrigin, clip: s.backgroundClip};
  })));
  const byId = Object.fromEntries(rows.map(row => [row.id, row]));
  for (const id of ['both', 'both12']) assert.equal((byId[id].image.match(/repeating-linear-gradient/g) || []).length, 2, `${id} loses a diagnostic layer`);
  for (const id of ['base', 'columns12', 'columns']) assert.equal((byId[id].image.match(/repeating-linear-gradient/g) || []).length, 1, `${id} inherited another overlay`);
  assert.doesNotMatch(byId.base.image, /to right/);
  assert.match(byId.columns.image, /to right/);
  assert.notEqual(byId.columns.image, byId.columns12.image);
  assert.equal(byId.plain.image, 'none');
  for (const row of rows.filter(row => row.id !== 'plain')) {
    assert.ok(row.origin.split(',').every(value => value.trim() === 'content-box'));
    assert.ok(row.clip.split(',').every(value => value.trim() === 'content-box'));
  }
});
