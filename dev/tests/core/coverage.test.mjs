// S5 原文提取与覆盖测试：node --test dev/tests/core/coverage.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const REPO = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../..');
const CLI = path.join(REPO, 'hb/core/cli.mjs');
const PY = (s) => path.join(REPO, 'hb/core', s);
const MIN = path.join(REPO, 'dev/fixtures/contract/minimal-zh');
const BI = path.join(REPO, 'dev/fixtures/contract/bilingual');
const QA = path.join(REPO, 'dev/fixtures/qa/base');
const json = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));

function copy(src) {
  const d = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'hb-cov-')), 'p');
  fs.cpSync(src, d, { recursive: true, filter: (s) => !/\.build|\.qa/.test(s) });
  return d;
}
function edit(d, file, a, b) {
  const f = path.join(d, file); const s = fs.readFileSync(f, 'utf8');
  assert.ok(s.includes(a), `${a} 不在 ${file}`); fs.writeFileSync(f, s.replace(a, b));
}
const append = (d, file, t) => fs.appendFileSync(path.join(d, file), '\n' + t + '\n');
const setProject = (d, fn) => { const f = path.join(d, 'project.json'); const p = json(f); fn(p); fs.writeFileSync(f, JSON.stringify(p, null, 2)); };
function check(d) {
  const r = spawnSync('node', [CLI, 'check', d], { encoding: 'utf8' });
  const id = r.stdout.match(/验收 ([0-9a-f]{12})/)?.[1];
  assert.ok(id, r.stdout + r.stderr);
  const cov = (lang = 'zh-CN') => json(path.join(d, '.qa', id, lang, 'coverage.json'));
  return { code: r.status, out: r.stdout, id, gate: json(path.join(d, '.qa', id, 'gate.json')), cov };
}
const has = (rep, id, sev, status = 'fail') => rep.items.some((i) => i.id === id && i.severity === sev && i.status === status);

test('提取：md / docx / pptx 得到稳定分段，统计数字不被当作页码', () => {
  const t = fs.mkdtempSync(path.join(os.tmpdir(), 'hb-ex-'));
  spawnSync('python3', [PY('extract.py'), path.join(REPO, 'dev/samples/product-brochure/doc.md'), path.join(t, 'md')]);
  const segs = json(path.join(t, 'md/sources/segments.json')).segments;
  assert.equal(segs.length, 160);
  assert.ok(segs.some((s) => s.text === '24' && s.kind === 'para'));
  spawnSync('python3', ['-c', `
import docx
from pptx import Presentation
d=docx.Document(); d.add_heading('开学指南',1); d.add_paragraph('第一个月的重点是熟悉校园。'); d.add_paragraph('报到当天带好水杯', style='List Bullet')
tb=d.add_table(rows=1, cols=2); tb.cell(0,0).text='日期'; tb.cell(0,1).text='9 月 1 日'; d.save(${JSON.stringify(path.join(t, 'a.docx'))})
p=Presentation(); s=p.slides.add_slide(p.slide_layouts[1]); s.shapes.title.text='校园开放日'; s.placeholders[1].text='上午九点开始'; p.save(${JSON.stringify(path.join(t, 'b.pptx'))})`]);
  for (const [f, kinds] of [['a.docx', ['heading', 'para', 'item', 'cell', 'cell']], ['b.pptx', ['heading', 'item']]]) {
    const r = spawnSync('python3', [PY('extract.py'), path.join(t, f), path.join(t, f + '.p')], { encoding: 'utf8' });
    assert.equal(r.status, 0, r.stderr);
    assert.deepEqual(json(path.join(t, f + '.p/sources/segments.json')).segments.map((s) => s.kind), kinds);
  }
  // 同一原稿重提取，ID 不变
  spawnSync('python3', [PY('extract.py'), path.join(REPO, 'dev/samples/product-brochure/doc.md'), path.join(t, 'md')]);
  assert.deepEqual(json(path.join(t, 'md/sources/segments.json')).segments.map((s) => s.id), segs.map((s) => s.id));
});

test('正例：三个样例全部可交付', () => {
  for (const fx of [MIN, BI, QA]) {
    const r = check(copy(fx));
    assert.equal(r.code, 0, r.out);
    assert.equal(r.gate.status, 'deliverable');
  }
});

const HIDE = [
  ['删掉段落', (d) => edit(d, 'book.html', /<p class="intro"[^]*?<\/p>\n/.exec(fs.readFileSync(path.join(d, 'book.html'), 'utf8'))[0], '')],
  ['透明副本', (d) => append(d, 'book.css', '.month .intro { opacity: 0; }')],
  ['移到页外', (d) => append(d, 'book.css', '.month .intro { position: absolute; left: -300mm; }')],
  ['透明文字色', (d) => append(d, 'book.css', '.month .intro { color: transparent; }')],
];
for (const [name, fn] of HIDE) {
  test(`原文缺失：${name} → coverage.missing`, () => {
    const d = copy(MIN); fn(d);
    const r = check(d);
    assert.notEqual(r.code, 0);
    assert.ok(has(r.cov(), 'coverage.missing', 'hard'), JSON.stringify(r.cov().items.filter((i) => i.status !== 'pass')));
  });
}

test('自创句：搬运模式判 EXTRA 硬项', () => {
  const d = copy(MIN);
  edit(d, 'book.html', '一起制定适应计划。', '一起制定适应计划。我们保证每个孩子都能考第一。');
  const r = check(d);
  assert.notEqual(r.code, 0);
  assert.ok(r.cov().items.some((i) => i.id === 'coverage.extra' && i.severity === 'hard' && /考第一/.test(i.message)));
});

test('冻结模式：设计添加的辅助文字与顺序调整都判硬项；搬运模式只提示顺序', () => {
  const swap = (d) => {
    const f = path.join(d, 'book.html'); let s = fs.readFileSync(f, 'utf8');
    const note = /  <p class="note"[^]*?<\/p>\n/.exec(s)[0]; const body = /  <p class="body"[^]*?<\/p>\n/.exec(s)[0];
    s = s.replace(note, '').replace(body, note + body); fs.writeFileSync(f, s);
  };
  const f1 = copy(MIN); setProject(f1, (p) => { p.content_mode = 'frozen'; }); swap(f1);
  const r1 = check(f1);
  assert.notEqual(r1.code, 0);
  assert.ok(has(r1.cov(), 'coverage.extra', 'hard'), '开学指南（aux）在冻结模式下应为 EXTRA');
  assert.ok(has(r1.cov(), 'coverage.order', 'hard'));
  const c1 = copy(MIN); swap(c1);
  const r2 = check(c1);
  assert.equal(r2.code, 0, r2.out);
  assert.ok(has(r2.cov(), 'coverage.order', 'hint'));
});

test('润色模式缺段只提示；adapt.json 声明省略后搬运模式通过；冻结模式拒绝 adapt.json', () => {
  const del = (d) => edit(d, 'book.html', /<p class="note"[^]*?<\/p>\n/.exec(fs.readFileSync(path.join(d, 'book.html'), 'utf8'))[0], '');
  const pol = copy(MIN); setProject(pol, (p) => { p.content_mode = 'polish'; }); del(pol);
  const r1 = check(pol);
  assert.equal(r1.code, 0, r1.out);
  assert.ok(has(r1.cov(), 'coverage.missing', 'hint'));
  const om = copy(MIN); del(om);
  const segs = json(path.join(om, 'sources/segments.json')).segments;
  const sid = segs.find((s) => s.text.startsWith('注：')).id;
  fs.writeFileSync(path.join(om, 'sources/adapt.json'), JSON.stringify({ omit: [{ segment: sid, reason: '印在背页通知里' }] }));
  assert.equal(check(om).code, 0);
  const fr = copy(MIN); setProject(fr, (p) => { p.content_mode = 'frozen'; });
  fs.writeFileSync(path.join(fr, 'sources/adapt.json'), '{"omit": []}');
  assert.ok(has(check(fr).cov(), 'coverage.adapt', 'hard'));
});

test('PDF 文字层缺失（默认语言与译文）都判硬项', () => {
  const d = copy(BI);
  const r = check(d);
  assert.equal(r.code, 0, r.out);
  for (const [lang, word] of [['zh-CN', '项目课'], ['en', 'project time']]) {
    const f = path.join(d, '.qa', r.id, lang, 'pdf-text.json');
    const t = json(f); t.pages = t.pages.map((p) => p.split(word).join('')); fs.writeFileSync(f, JSON.stringify(t));
    const c = spawnSync('python3', [PY('coverage.py'), d, r.id, lang], { encoding: 'utf8' });
    assert.equal(c.status, 1, c.stdout);
    assert.ok(has(r.cov(lang), 'coverage.pdf', 'hard'), lang);
  }
});

test('素材：授权未填与未登记都阻止交付', () => {
  const a = copy(BI);
  const f = path.join(a, 'sources/assets.json'); const j = json(f); j.assets.campus.license = ''; fs.writeFileSync(f, JSON.stringify(j));
  const r1 = check(a);
  assert.notEqual(r1.code, 0);
  assert.ok(has(r1.cov(), 'asset.license', 'hard', 'unverified'));
  const b = copy(QA);
  edit(b, 'book.html', ' data-asset="inline"', '');
  const r2 = check(b);
  assert.notEqual(r2.code, 0);
  assert.ok(has(r2.cov(), 'asset.unregistered', 'hard', 'unverified'));
});

test('无出处数字只作提示', () => {
  const d = copy(MIN);
  edit(d, 'book.html', '<span data-source-id="running-section">开学指南</span>', '<span data-source-id="running-section">开学指南 · 电话 4008 123 456</span>');
  const r = check(d);
  assert.equal(r.code, 0, r.out);
  assert.ok(has(r.cov(), 'facts.number', 'hint'));
});
