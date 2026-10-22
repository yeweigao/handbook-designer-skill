// S2 渲染运行时测试：node --test dev/tests/core/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { sanitizeInline } from '../../../hb/core/inject.mjs';

const REPO = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../..');
const CLI = path.join(REPO, 'hb/core/cli.mjs');
const FIX = path.join(REPO, 'dev/fixtures/contract');

function run(project, args = [], env = {}) {
  const r = spawnSync('node', [CLI, 'render', project, ...args], { encoding: 'utf8', env: { ...process.env, ...env } });
  const m = r.stdout.match(/构建 ([0-9a-f]{12}) → (.+)/);
  return { code: r.status, out: r.stdout + r.stderr, buildId: m?.[1], outDir: m ? path.resolve(m[2].trim()) : null };
}
const sh = (cmd, args) => spawnSync(cmd, args, { encoding: 'utf8' }).stdout;
const copyFixture = (name) => {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'hb-render-'));
  fs.cpSync(path.join(FIX, name), path.join(d, name), { recursive: true, filter: (s) => !s.includes('.build') });
  return path.join(d, name);
};
const manifest = (outDir, lang) => JSON.parse(fs.readFileSync(path.join(outDir, lang, 'manifest.json'), 'utf8'));

test('正例渲染：尺寸精确、页面框、无 Type 3', () => {
  const cases = [['minimal-zh', ['zh-CN'], '595.276 x 841.89', 2], ['bilingual', ['zh-CN', 'en'], '612.283 x 858.898', 4]];
  for (const [name, langs, size, pages] of cases) {
    const r = run(path.join(FIX, name));
    assert.equal(r.code, 0, r.out);
    for (const lang of langs) {
      const pdf = path.join(r.outDir, lang, 'book.pdf');
      const info = sh('pdfinfo', ['-box', '-f', '1', '-l', String(pages), pdf]);
      assert.match(info, new RegExp(`Pages:\\s+${pages}\\b`));
      const sizes = [...info.matchAll(/Page\s+\d+ size:\s+([\d.]+ x [\d.]+) pts/g)].map((m) => m[1]);
      assert.equal(sizes.length, pages);
      for (const s of sizes) assert.equal(s, size, `${name}/${lang}`);
      assert.doesNotMatch(sh('pdffonts', [pdf]), /Type 3/, `${name}/${lang} 出现 Type 3 字体`);
      const m = manifest(r.outDir, lang);
      assert.equal(m.status, 'pass');
      assert.equal(m.page_count, pages);
    }
  }
  const bi = run(path.join(FIX, 'bilingual'));
  const tb = sh('pdfinfo', ['-box', '-f', '1', '-l', '1', path.join(bi.outDir, 'en', 'book.pdf')]);
  const media = tb.match(/MediaBox:\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)/).slice(1).map(Number);
  const trim = tb.match(/TrimBox:\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)/).slice(1).map(Number);
  const bleed = (3 * 72) / 25.4;
  for (let i = 0; i < 4; i++) assert.ok(Math.abs(Math.abs(trim[i] - media[i]) - bleed) < 0.02, `TrimBox 应向内收 3mm：${trim} vs ${media}`);
});

test('多语言注入：英文快照含译文与 lang 属性', () => {
  const r = run(path.join(FIX, 'bilingual'), ['--lang', 'en']);
  assert.equal(r.code, 0, r.out);
  const snap = fs.readFileSync(path.join(r.outDir, 'en', 'snapshot.html'), 'utf8');
  assert.match(snap, /<html lang="en"/);
  assert.match(snap, /A Day Inside a Bilingual School/);
  assert.match(snap, /<em>not<\/em>/);
  assert.doesNotMatch(snap, /走进一所双语学校的一天/);
});

test('书签：显式层级优先，未标记时回退到每页首个标题', () => {
  const p = copyFixture('minimal-zh');
  const book = path.join(p, 'book.html');
  const source = fs.readFileSync(book, 'utf8');
  const marked = source
    .replace('<h1 data-role="display"', '<h1 data-outline="1" data-role="display"')
    .replace('<h2 data-role="display"', '<h2 data-outline="2" data-role="display"');
  fs.writeFileSync(book, marked);

  const explicit = run(p);
  assert.equal(explicit.code, 0, explicit.out);
  assert.deepEqual(manifest(explicit.outDir, 'zh-CN').outline, [
    { title: '让孩子在双语环境里自在成长', level: 1, page: 0 },
    { title: '开学第一个月', level: 2, page: 1 },
  ]);

  fs.writeFileSync(book, source);
  const fallback = run(p);
  assert.equal(fallback.code, 0, fallback.out);
  assert.deepEqual(manifest(fallback.outDir, 'zh-CN').outline, [
    { title: '让孩子在双语环境里自在成长', level: 1, page: 0 },
    { title: '开学第一个月', level: 1, page: 1 },
  ]);
});

test('行内标记白名单与转义', () => {
  assert.equal(sanitizeInline('a <em>b</em> c'), 'a <em>b</em> c');
  assert.equal(sanitizeInline('<script>x</script>'), '&lt;script&gt;x&lt;/script&gt;');
  assert.equal(sanitizeInline('<a href="javascript:alert(1)" onclick="x">y</a>'), '<a>y</a>');
  assert.equal(sanitizeInline('<span class="k" style="color:red">z</span>'), '<span class="k">z</span>');
  assert.equal(sanitizeInline('1 < 2 & 3'), '1 &lt; 2 &amp; 3');
});

test('确定性：两次独立进程渲染，指纹与逐页栅格一致', () => {
  const p = path.join(FIX, 'minimal-zh');
  const a = run(p, ['--out', '.build/det-a']);
  const b = run(p, ['--out', '.build/det-b']);
  assert.equal(a.code, 0, a.out);
  assert.equal(b.code, 0, b.out);
  assert.equal(a.buildId, b.buildId);
  const ma = manifest(a.outDir, 'zh-CN');
  const mb = manifest(b.outDir, 'zh-CN');
  assert.equal(ma.fingerprint, mb.fingerprint);
  assert.equal(ma.snapshot.sha256, mb.snapshot.sha256);
  for (const [o, d] of [[a.outDir, 'a'], [b.outDir, 'b']]) {
    spawnSync('pdftoppm', ['-r', '60', '-png', path.join(o, 'zh-CN', 'book.pdf'), path.join(o, 'ras')]);
  }
  const pages = fs.readdirSync(a.outDir).filter((f) => f.startsWith('ras')).sort();
  assert.equal(pages.length, 2);
  for (const f of pages) {
    assert.ok(fs.readFileSync(path.join(a.outDir, f)).equals(fs.readFileSync(path.join(b.outDir, f))), `${f} 栅格不一致`);
  }
  fs.rmSync(a.outDir, { recursive: true }); fs.rmSync(b.outDir, { recursive: true });
});

test('指纹覆盖 CSS、字体、图片、文案的改动', () => {
  const p = copyFixture('bilingual');
  const base = run(p).buildId;
  assert.ok(base);
  const changes = [
    () => fs.appendFileSync(path.join(p, 'book.css'), '\n.story h2 { letter-spacing: 0.01em; }\n'),
    () => fs.appendFileSync(path.join(p, 'assets/images/campus.jpg'), Buffer.from([0])),
    () => fs.appendFileSync(path.join(p, 'lang/en.css'), '\n/* x */\n'),
    () => { const f = path.join(p, 'copy/en.json'); const c = JSON.parse(fs.readFileSync(f)); c.strings['back-address'] += '.'; fs.writeFileSync(f, JSON.stringify(c)); },
  ];
  let prev = base;
  for (const change of changes) {
    change();
    const id = run(p).buildId;
    assert.ok(id && id !== prev, '改动后构建 ID 应变化');
    prev = id;
  }
});

test('字体文件损坏：渲染失败并指出字体', () => {
  const p = copyFixture('minimal-zh');
  fs.writeFileSync(path.join(p, 'assets/fonts/NotoSansSC-400.ttf'), 'not a font');
  const r = run(p);
  assert.notEqual(r.code, 0);
  assert.match(r.out, /resource\.font/);
});

test('字体文件缺失：契约校验拦下并给出文件名', () => {
  const p = copyFixture('minimal-zh');
  fs.rmSync(path.join(p, 'assets/fonts/NotoSansSC-700.ttf'));
  const r = run(p);
  assert.notEqual(r.code, 0);
  assert.match(r.out, /NotoSansSC-700\.ttf/);
});

test('外部请求在运行时被拦截（绕过静态校验时）', () => {
  const p = copyFixture('minimal-zh');
  const f = path.join(p, 'book.html');
  fs.writeFileSync(f, fs.readFileSync(f, 'utf8').replace('</footer>', '</footer><img src="https://example.com/a.png" alt="">'));
  const r = run(p, [], { HB_SKIP_VALIDATE: '1' });
  assert.notEqual(r.code, 0);
  assert.match(r.out, /network\.blocked/);
});

test('作者 CSS 改了页面宽度：报页面尺寸错误', () => {
  const p = copyFixture('minimal-zh');
  fs.appendFileSync(path.join(p, 'book.css'), '\n.page.month { width: 200mm; }\n');
  const r = run(p);
  assert.notEqual(r.code, 0);
  assert.match(r.out, /page\.size/);
});
