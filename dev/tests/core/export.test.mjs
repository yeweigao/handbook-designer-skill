// S8 导出与离线交付测试：node --test dev/tests/core/export.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';

const REPO = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../..');
const CLI = path.join(REPO, 'hb/core/cli.mjs');
const PY = (s) => path.join(REPO, 'hb/core', s);
const BI = path.join(REPO, 'dev/fixtures/contract/bilingual');
const MIN = path.join(REPO, 'dev/fixtures/contract/minimal-zh');
const cli = (...a) => spawnSync('node', [CLI, ...a], { encoding: 'utf8' });
const json = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));
const sha = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
function copy(src) {
  const d = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'hb-exp-')), 'p');
  fs.cpSync(src, d, { recursive: true, filter: (s) => !/\.build|\.qa|\/out/.test(s) });
  return d;
}

test('门槛：没有验收、没有审稿、审稿不合格、验收后被改动都拒绝正式导出', () => {
  const d = copy(MIN);
  let r = cli('export', d);
  assert.notEqual(r.status, 0); assert.match(r.stdout, /没有验收记录/);
  assert.notEqual(cli('review', d, '--verdict', 'deliverable', '--by', 'x').status, 0, '没有有效验收时不能记录审稿');
  assert.equal(cli('check', d).status, 0);
  r = cli('export', d);
  assert.notEqual(r.status, 0); assert.match(r.stdout, /没有视觉审稿记录/);
  assert.equal(cli('review', d, '--verdict', 'fail', '--by', 'x').status, 0);
  r = cli('export', d);
  assert.notEqual(r.status, 0); assert.match(r.stdout, /不合格/);
  assert.equal(cli('review', d, '--verdict', 'deliverable', '--by', 'x').status, 0);
  const id = fs.readdirSync(path.join(d, '.build')).find((x) => /^[0-9a-f]{12}$/.test(x));
  fs.appendFileSync(path.join(d, '.build', id, 'zh-CN', 'book.pdf'), '\n%x\n');
  r = cli('export', d);
  assert.notEqual(r.status, 0); assert.match(r.stdout, /PDF 在验收后被改动/);
  assert.ok(!fs.existsSync(path.join(d, 'out')) || fs.readdirSync(path.join(d, 'out')).every((x) => x.startsWith('.')));
});

test('正式导出：全部交付物生成并实测通过，交付记录哈希与文件一致', () => {
  const d = copy(BI);
  assert.equal(cli('check', d).status, 0);
  assert.equal(cli('review', d, '--verdict', 'excellent', '--by', '测试').status, 0);
  const r = cli('export', d, '--name', 'open-day');
  assert.equal(r.status, 0, r.stdout);
  const out = path.join(d, 'out', 'open-day');
  const del = json(path.join(out, 'delivery.json'));
  assert.equal(del.status, 'delivered');
  assert.deepEqual(del.checks.map((c) => c.id).sort(), ['editable.en', 'editable.zh-CN', 'offline.en', 'offline.zh-CN', 'pdf.en', 'pdf.zh-CN', 'source.rebuild']);
  assert.ok(del.checks.every((c) => c.status === 'pass'));
  for (const lang of ['zh-CN', 'en']) for (const k of ['pdf', 'editable.pdf', 'html', 'sheet.png', 'spreads.png']) assert.ok(fs.existsSync(path.join(out, `open-day.${lang}.${k}`)), `${lang}.${k}`);
  for (const [f, h] of Object.entries(del.files)) assert.equal(sha(path.join(out, f)), h, f);
  const fonts = spawnSync('pdffonts', [path.join(out, 'open-day.zh-CN.editable.pdf')], { encoding: 'utf8' }).stdout;
  assert.doesNotMatch(fonts, /^[A-Z]{6}\+/m);
  const zip = spawnSync('python3', ['-c', 'import zipfile,sys; print("\\n".join(zipfile.ZipFile(sys.argv[1]).namelist()))', path.join(out, 'open-day.source.zip')], { encoding: 'utf8' }).stdout;
  assert.match(zip, /^REBUILD\.md$/m); assert.match(zip, /^sources\/segments\.json$/m); assert.match(zip, /OFL\.txt$/m);
  assert.doesNotMatch(zip, /^(\.build|\.qa|out)\//m);
  assert.match(fs.readFileSync(path.join(out, 'credits.md'), 'utf8'), /campus/);
  assert.ok(!fs.readdirSync(path.join(d, 'out')).some((x) => x.startsWith('.staging')));
});

test('草稿导出：不需要验收，PDF 带水印', () => {
  const d = copy(MIN);
  const r = cli('export', d, '--draft', '--name', 'm');
  assert.equal(r.status, 0, r.stdout);
  const f = path.join(d, 'out', 'm-draft', 'm.zh-CN.draft.pdf');
  assert.match(spawnSync('pdftotext', ['-raw', f, '-'], { encoding: 'utf8' }).stdout, /草稿\s*DRAFT/);
  assert.equal(json(path.join(d, 'out', 'm-draft', 'delivery.json')).status, 'draft');
});

test('离线 HTML：外链、项目外文件、缺失文件都拒绝', () => {
  const d = copy(MIN);
  assert.equal(cli('render', d).status, 0);
  const id = fs.readdirSync(path.join(d, '.build')).find((x) => /^[0-9a-f]{12}$/.test(x));
  const snap = path.join(d, '.build', id, 'zh-CN', 'snapshot.html');
  const s = fs.readFileSync(snap, 'utf8');
  for (const [inject, msg] of [['<img src="https://example.com/a.png">', /网络/], ['<img src="../../x.png">', /项目目录以外|不存在/], ['<img src="assets/none.png">', /不存在/]]) {
    const bad = path.join(d, 'bad.html');
    fs.writeFileSync(bad, s.replace('</body>', inject + '</body>'));
    const r = spawnSync('python3', [PY('offline_html.py'), d, bad, path.join(d, 'o.html')], { encoding: 'utf8' });
    assert.equal(r.status, 1); assert.match(r.stderr, msg);
  }
});
