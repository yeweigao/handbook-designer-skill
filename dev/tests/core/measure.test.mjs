// S3 版面测量测试：node --test dev/tests/core/measure.test.mjs
// 正例（合法的海报叠放、满版出血、旋转装饰字、页边页码）必须零硬项；每个反例只引入一处问题，必须被对应检查判为硬项失败。
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const REPO = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../..');
const CLI = path.join(REPO, 'hb/core/cli.mjs');
const BASE = path.join(REPO, 'dev/fixtures/qa/base');

function renderMeasure(project) {
  const r = spawnSync('node', [CLI, 'render', project], { encoding: 'utf8' });
  const id = r.stdout.match(/构建 ([0-9a-f]{12})/)?.[1];
  assert.ok(id, r.stdout + r.stderr);
  const m = spawnSync('node', [CLI, 'measure', project], { encoding: 'utf8' });
  const rep = JSON.parse(fs.readFileSync(path.join(project, '.qa', id, 'zh-CN', 'measure.json'), 'utf8'));
  return { code: m.status, out: m.stdout + m.stderr, rep };
}
function mutated(changes) {
  const d = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'hb-measure-')), 'p');
  fs.cpSync(BASE, d, { recursive: true, filter: (s) => !/\.build|\.qa/.test(s) });
  for (const [file, a, b] of changes) {
    const f = path.join(d, file);
    const s = fs.readFileSync(f, 'utf8');
    if (a === null) fs.writeFileSync(f, s + '\n' + b + '\n');
    else { assert.ok(s.includes(a), `${a} 不在 ${file}`); fs.writeFileSync(f, s.replace(a, b)); }
  }
  return d;
}
const css = (rule) => ['book.css', null, rule];
const html = (a, b) => ['book.html', a, b];
const hard = (rep, id) => rep.items.filter((i) => i.id === id && i.severity === 'hard' && i.status === 'fail');

test('正例：合法复杂版式零硬项', () => {
  const { code, rep, out } = renderMeasure(BASE);
  assert.equal(code, 0, out);
  assert.equal(rep.status, 'pass');
  assert.equal(rep.summary.blocking, 0);
  const dpi = rep.items.filter((i) => i.id === 'image.info').map((i) => i.evidence.dpi).sort((a, b) => a - b);
  assert.deepEqual(dpi, [180, 300]);
});

const NEGATIVE = [
  ['文字超出页面', [css('.poster-lead { top: calc(var(--bleed) + 296mm); }')], 'overflow.page'],
  ['页码出安全区', [css('.text .folio { bottom: calc(var(--bleed) + 3mm); }')], 'overflow.safe'],
  ['文字被容器裁掉', [html('孩子觉得被听见，才会愿意多说一句。', '孩子觉得被听见，才会愿意多说一句。'.repeat(20))], 'clip.text'],
  ['文字重叠未声明', [html('data-overlap="poster-title img-poster"', 'data-overlap="img-poster"')], 'overlap.text'],
  ['文字压图未声明', [html('data-source-id="poster-lead" data-overlap="img-poster"', 'data-source-id="poster-lead"')], 'overlap.image'],
  ['正文字号过小', [css('.text .cols { font-size: 12px; line-height: 20px; }')], 'readability.size'],
  ['页码伪元素过小', [css('.folio { font-size: 8px; }')], 'readability.size'],
  ['正文对比度不足', [css('.text .cols { color: #c4c4c4; }')], 'readability.contrast'],
  ['压图文字对比度不足', [css('.poster-lead { color: #2a3f5a; }')], 'readability.contrast'],
  ['缺字回退', [html('改到室内体育馆。', '改到室内体育馆龘。')], 'font.fallback'],
  ['字体栈不含声明字体', [css('.text .intro { font-family: "Nonexistent Face", sans-serif; }')], 'font.fallback'],
  ['低分辨率图片', [html('<div class="band"', '<img src="assets/images/small.png" alt="" data-edit-id="img-small" style="position:absolute;left:30mm;top:60mm;width:120mm;height:80mm"><div class="band"')], 'image.dpi'],
  ['出血不足', [css('.band { bottom: 1mm; }')], 'image.bleed'],
  ['越过成品边未声明出血', [html(' data-asset="poster" data-bleed="all"', ' data-asset="poster"')], 'image.bleed'],
  ['内容透明', [css('.text .intro { opacity: 0; }')], 'content.hidden'],
  ['内容 display:none', [css('[data-source-id="text-p2"] { display: none; }')], 'content.hidden'],
  ['内容字号小于 1px', [css('.text .intro { font-size: 0.5px; }')], 'content.hidden'],
  ['内容文字透明色', [css('.text .intro { color: transparent; }')], 'content.hidden'],
];

for (const [name, changes, id] of NEGATIVE) {
  test(`反例：${name} → ${id}`, () => {
    const { code, rep, out } = renderMeasure(mutated(changes));
    assert.notEqual(code, 0, `应以非 0 退出\n${out}`);
    assert.ok(hard(rep, id).length > 0, `期望 ${id} 硬项失败，实际：\n${rep.items.filter((i) => i.status !== 'pass').map((i) => `${i.id} ${i.message}`).join('\n')}`);
    if (name === '缺字回退') assert.match(hard(rep, id)[0].message, /龘/);
    if (name === '页码伪元素过小') assert.match(hard(rep, id)[0].target, /::after/);
  });
}

test('旋转的内容文字：只给待目检提示，不阻断', () => {
  const { code, rep } = renderMeasure(mutated([css('.text h2 { transform: rotate(-3deg); }')]));
  assert.equal(code, 0);
  assert.ok(rep.items.some((i) => i.id === 'geometry.unverified' && i.severity === 'hint'));
});

test('授权放宽下限：按放宽值检查并留下提示', () => {
  const d = mutated([css('[data-role="aux"], .folio { font-size: 9.5px; }')]);
  assert.notEqual(renderMeasure(d).code, 0, '未授权时应失败');
  const pj = path.join(d, 'project.json');
  const p = JSON.parse(fs.readFileSync(pj, 'utf8'));
  p.readability_waiver = { reason: '测试', approved_by: '测试', date: '2026-10-22', values: { aux_px: 9 } };
  fs.writeFileSync(pj, JSON.stringify(p, null, 2));
  const { code, rep } = renderMeasure(d);
  assert.equal(code, 0);
  assert.ok(rep.items.some((i) => i.id === 'readability.waiver'));
});
