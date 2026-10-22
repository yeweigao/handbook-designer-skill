// S6 长文续页测试：node --test dev/tests/core/paginate.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const REPO = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../..');
const CLI = path.join(REPO, 'hb/core/cli.mjs');
const FLOW = path.join(REPO, 'dev/fixtures/flow/long-bilingual');
const json = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));
const cli = (...a) => spawnSync('node', [CLI, ...a], { encoding: 'utf8' });
function copy() {
  const d = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'hb-flow-')), 'p');
  fs.cpSync(FLOW, d, { recursive: true, filter: (s) => !/\.build|\.qa/.test(s) });
  return d;
}

let paged;   // 续排后的项目，供后续用例复用
test('续排：写回作者源，24 页以上，规则成立', () => {
  paged = copy();
  const before = fs.readFileSync(path.join(paged, 'book.html'), 'utf8');
  const r = cli('paginate', paged);
  assert.equal(r.status, 0, r.stdout + r.stderr);
  const rep = json(path.join(paged, '.qa/paginate/report.json'));
  assert.equal(rep.errors.length, 0);
  assert.ok(rep.pages >= 24, `只有 ${rep.pages} 页`);
  const f = rep.flows[0];
  assert.ok(f.added_pages.length >= 20);
  // 标题不落框底；每个片段至少两行
  assert.ok(!f.frame_tails.some((t) => /^h[1-6]$/.test(t)), f.frame_tails.join(','));
  for (const [id, ls] of Object.entries(f.fragments)) for (const l of ls) assert.ok(l >= 2, `${id} 片段只有 ${l} 行`);
  assert.equal(f.forced.length, 0);
  // 写回：作者源变化、差异文件存在、契约校验通过、内容 ID 片段编号连续
  const after = fs.readFileSync(path.join(paged, 'book.html'), 'utf8');
  assert.notEqual(after, before);
  assert.match(fs.readFileSync(path.join(paged, '.qa/paginate/book.html.diff'), 'utf8'), /^\+.*data-flow-generated="story"/m);
  assert.equal(spawnSync('python3', [path.join(REPO, 'hb/core/validate.py'), paged]).status, 0);
  // 只移动内容：所有原文字符一个不少
  const text = (h) => h.replace(/<[^>]+>/g, '').replace(/\s+/g, '');
  const body = (h) => text(h.slice(h.indexOf('data-flow="story"')));
  assert.equal(body(after).replace(/续排测试用长篇手册/g, '').length, body(before).replace(/续排测试用长篇手册/g, '').length);
});

test('续排幂等：再运行一次不改动作者源', () => {
  const before = fs.readFileSync(path.join(paged, 'book.html'), 'utf8');
  const r = cli('paginate', paged);
  assert.equal(r.status, 0, r.stdout);
  assert.match(r.stdout, /无需改动/);
  assert.equal(fs.readFileSync(path.join(paged, 'book.html'), 'utf8'), before);
});

test('续排后中英两版完整验收可交付，英文在渲染时续排出更多页', () => {
  const r = cli('check', paged);
  assert.equal(r.status, 0, r.stdout);
  const g = json(path.join(paged, '.qa', r.stdout.match(/验收 ([0-9a-f]{12})/)[1], 'gate.json'));
  assert.equal(g.status, 'deliverable');
  assert.ok(g.languages.en.pages > g.languages['zh-CN'].pages);
  const m = json(path.join(paged, '.build', g.build_id, 'en', 'manifest.json'));
  assert.ok(m.flows.flows[0].added_pages.length > 0);
});

test('英文渲染时续排是确定的', () => {
  const a = cli('render', paged, '--lang', 'en', '--out', '.build/det-a');
  const b = cli('render', paged, '--lang', 'en', '--out', '.build/det-b');
  assert.equal(a.status, 0); assert.equal(b.status, 0);
  const sa = json(path.join(paged, '.build/det-a/en/manifest.json')).snapshot.sha256;
  const sb = json(path.join(paged, '.build/det-b/en/manifest.json')).snapshot.sha256;
  assert.equal(sa, sb);
});

test('文字框没有固定高度：报错且不改作者源', () => {
  const d = copy();
  fs.appendFileSync(path.join(d, 'book.css'), '\n.frame { position: static; height: auto; }\n');
  const before = fs.readFileSync(path.join(d, 'book.html'), 'utf8');
  const r = cli('paginate', d);
  assert.notEqual(r.status, 0);
  assert.match(r.stdout, /flow\.unbounded/);
  assert.equal(fs.readFileSync(path.join(d, 'book.html'), 'utf8'), before);
});

test('比整个文字框还高的图：报 flow.too-large', () => {
  const d = copy();
  fs.appendFileSync(path.join(d, 'book.css'), '\n.fig img { height: 260mm; }\n');
  const r = cli('paginate', d);
  assert.notEqual(r.status, 0);
  assert.match(r.stdout, /flow\.too-large/);
});
