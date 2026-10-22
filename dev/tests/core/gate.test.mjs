// S4 最终 PDF 检查与验收绑定测试：node --test dev/tests/core/gate.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const REPO = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../..');
const CLI = path.join(REPO, 'hb/core/cli.mjs');
const PY = (s) => path.join(REPO, 'hb/core', s);
const FIX = path.join(REPO, 'dev/fixtures/contract');
const cli = (...a) => spawnSync('node', [CLI, ...a], { encoding: 'utf8' });
const env = (e) => ({ ...process.env, ...e });
const copy = (name) => {
  const d = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'hb-gate-')), name);
  fs.cpSync(path.join(FIX, name), d, { recursive: true, filter: (s) => !/\.build|\.qa/.test(s) });
  return d;
};
const buildOf = (out) => out.match(/(?:构建|验收) ([0-9a-f]{12})/)[1];
const json = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));

test('check：全部检查通过，可交付', () => {
  const d = copy('bilingual');
  const r = cli('check', d);
  assert.equal(r.status, 0, r.stdout);
  const g = json(path.join(d, '.qa', buildOf(r.stdout), 'gate.json'));
  assert.equal(g.status, 'deliverable');
  const v = cli('verify', d);
  assert.equal(v.status, 0, v.stdout);
  for (const lang of ['zh-CN', 'en']) {
    const c = g.languages[lang].checks;
    assert.deepEqual([c.render, c.measure, c.postflight, c.raster, c.coverage], ['pass', 'pass', 'pass', 'pass', 'pass']);
    assert.match(g.languages[lang].pdf_sha256, /^[0-9a-f]{64}$/);
  }
  assert.equal(g.blocking.length, 0);
  const raster = path.join(d, '.qa', g.build_id, 'en', 'raster');
  for (const f of ['page-001.png', 'page-004.png', 'sheet.png', 'spreads.png']) assert.ok(fs.existsSync(path.join(raster, f)), f);
});

test('verify：源改动或 PDF 被改动后旧验收失效', () => {
  const d = copy('minimal-zh');
  const r = cli('check', d);
  const id = buildOf(r.stdout);
  // PDF 被改动
  fs.appendFileSync(path.join(d, '.build', id, 'zh-CN', 'book.pdf'), '\n%tampered\n');
  let v = cli('verify', d);
  assert.notEqual(v.status, 0);
  assert.match(v.stdout, /PDF 在验收后被改动/);
  // 源改动：指纹变化，找不到对应验收记录
  fs.appendFileSync(path.join(d, 'book.css'), '\n.month h2 { letter-spacing: 0.02em; }\n');
  v = cli('verify', d);
  assert.notEqual(v.status, 0);
  assert.match(v.stdout, /没有验收记录/);
});

test('postflight：缺 pikepdf 时为 unverified 并阻止', () => {
  const d = copy('minimal-zh');
  const id = buildOf(cli('render', d).stdout);
  const r = spawnSync('python3', [PY('postflight.py'), d, id, 'zh-CN'], { encoding: 'utf8', env: env({ HB_POSTFLIGHT_NO_PIKEPDF: '1' }) });
  assert.equal(r.status, 1);
  const rep = json(path.join(d, '.qa', id, 'zh-CN', 'postflight.json'));
  assert.ok(rep.items.filter((i) => i.status === 'unverified').length >= 4);
  assert.equal(rep.status, 'fail');
});

test('postflight：页面尺寸被改坏、PDF 哈希不符都判失败', () => {
  const d = copy('minimal-zh');
  const id = buildOf(cli('render', d).stdout);
  const pdf = path.join(d, '.build', id, 'zh-CN', 'book.pdf');
  spawnSync('python3', ['-c', `import pikepdf\nwith pikepdf.open(${JSON.stringify(pdf)}, allow_overwriting_input=True) as p:\n  pg=p.pages[0]; b=[float(x) for x in pg.MediaBox]; pg.MediaBox=pikepdf.Array([b[0],b[1],b[0]+500,b[3]]); p.save(${JSON.stringify(pdf)})`]);
  const r = spawnSync('python3', [PY('postflight.py'), d, id, 'zh-CN'], { encoding: 'utf8' });
  assert.equal(r.status, 1);
  const ids = json(path.join(d, '.qa', id, 'zh-CN', 'postflight.json')).items.filter((i) => i.status === 'fail').map((i) => i.id);
  assert.ok(ids.includes('pdf.boxes') && ids.includes('pdf.hash'), ids.join(','));
});

test('postflight：骑马钉页数不是 4 的倍数判失败', () => {
  const d = copy('bilingual');
  const f = path.join(d, 'book.html');
  fs.writeFileSync(f, fs.readFileSync(f, 'utf8').replace(/<section class="page" data-page-id="p-back">[\s\S]*?<\/section>\n/, ''));
  const cf = path.join(d, 'copy/en.json');
  const c = json(cf); delete c.strings['back-address']; fs.writeFileSync(cf, JSON.stringify(c));
  const id = buildOf(cli('render', d).stdout);
  const r = spawnSync('python3', [PY('postflight.py'), d, id, 'en'], { encoding: 'utf8' });
  assert.equal(r.status, 1);
  assert.ok(json(path.join(d, '.qa', id, 'en', 'postflight.json')).items.some((i) => i.id === 'pdf.binding' && i.status === 'fail'));
});

test('postflight：可变字体导致的 Type 3 被查出', () => {
  const d = copy('minimal-zh');
  fs.copyFileSync(path.join(REPO, 'dev/fonts/Inter-VF.ttf'), path.join(d, 'assets/fonts/Inter-VF.ttf'));
  const pj = path.join(d, 'project.json'); const p = json(pj);
  p.fonts.push({ family: 'Inter VF', file: 'assets/fonts/Inter-VF.ttf', weight: '400', style: 'normal' });
  fs.writeFileSync(pj, JSON.stringify(p, null, 2));
  fs.appendFileSync(path.join(d, 'design.css'), '\n.page { font-family: "Inter VF", var(--font-body); }\n');
  const id = buildOf(spawnSync('node', [CLI, 'render', d], { encoding: 'utf8', env: env({ HB_SKIP_VALIDATE: '1' }) }).stdout);
  const r = spawnSync('python3', [PY('postflight.py'), d, id, 'zh-CN'], { encoding: 'utf8' });
  assert.equal(r.status, 1);
  const f = json(path.join(d, '.qa', id, 'zh-CN', 'postflight.json')).items.find((i) => i.id === 'pdf.fonts' && i.status === 'fail');
  assert.ok(f && f.evidence.type3?.length, '应报告 Type 3');
});
