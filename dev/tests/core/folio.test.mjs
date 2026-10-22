// S9 Folio 联动测试：node --test dev/tests/core/folio.test.mjs
// 1) 写回逻辑：用编辑包基准模拟 Folio 的改动（改字、换图、样式、批量规则、无 ID 改动、冲突、其他语言）。
// 2) 真实往返：若 FOLIO_DIR（默认 ../folio-html-studio）已安装依赖，启动 Folio 开发服务器，在真实界面里改字、拖动、换图，
//    下载后写回、确认图片授权，再完整验收。没有 Folio 时该项跳过并说明。
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import zlib from 'node:zlib';
import { spawn, spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';

const REPO = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../..');
const CLI = path.join(REPO, 'hb/core/cli.mjs');
const BI = path.join(REPO, 'dev/fixtures/contract/bilingual');
const FOLIO = process.env.FOLIO_DIR || path.resolve(REPO, '../folio-html-studio');
const cli = (...a) => spawnSync('node', [CLI, ...a], { encoding: 'utf8' });
const json = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));
function copy() {
  const d = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'hb-folio-')), 'p');
  fs.cpSync(BI, d, { recursive: true, filter: (s) => !/\.build|\.qa|\/out/.test(s) });
  return d;
}
function pack(d, lang) {
  const r = cli('folio-pack', d, '--lang', lang, '--name', 'pkg');
  assert.equal(r.status, 0, r.stdout + r.stderr);
  return path.join(d, 'out/folio', `pkg.${lang}.folio.html`);
}
// 生成纯色 PNG（足够分辨率，用于换图）
function png(w, h, [r, g, b]) {
  const crc = (buf) => { let c, n = -1; for (const x of buf) { c = (n ^ x) & 0xff; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; n = (n >>> 8) ^ c; } return (n ^ -1) >>> 0; };
  const chunk = (t, d) => { const l = Buffer.alloc(4); l.writeUInt32BE(d.length); const td = Buffer.concat([Buffer.from(t), d]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([l, td, c]); };
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 2;
  const row = Buffer.alloc(1 + w * 3); for (let i = 0; i < w; i++) { row[1 + i * 3] = r; row[2 + i * 3] = g; row[3 + i * 3] = b; }
  const raw = Buffer.concat(Array.from({ length: h }, () => row));
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}
const sync = (d, file, ...extra) => spawnSync('node', [CLI, 'folio-sync', d, file, ...extra], { encoding: 'utf8' });

test('写回：改字、换图、局部样式、批量规则；无 ID 改动列出；冲突不覆盖', () => {
  const d = copy();
  const base = pack(d, 'zh-CN');
  let h = fs.readFileSync(base, 'utf8');
  h = h.replace('从早读到社团活动，用一个上午看懂孩子在这里怎样学习。', '从早读到社团活动，<b>看懂</b>孩子怎样学习。<div>一个上午</div>');
  h = h.replace(/<img[^>]*data-edit-id="img-day-left"[^>]*>/, (tag) => tag.replace(/src="[^"]*"/, `src="data:image/png;base64,${png(40, 30, [200, 30, 30]).toString('base64')}"`));
  h = h.replace(/(<h1[^>]*data-source-id="cover-title")/, `$1 data-folio-id="f1" data-folio-overrides="{&quot;styles&quot;:{&quot;font-size&quot;:&quot;60px&quot;},&quot;dx&quot;:12,&quot;dy&quot;:-8}"`);
  h = h.replace(/(<div class="cover-band")/, `$1 data-folio-overrides="{&quot;styles&quot;:{&quot;height&quot;:&quot;50mm&quot;}}"`);
  h = h.replace(/(<p[^>]*data-source-id="day-p1")/, '$1 data-folio-style="s1"').replace(/(<p[^>]*data-source-id="day-p2")/, '$1 data-folio-style="s1"');
  h = h.replace('</head>', '<style id="folio-shared-styles" data-rules="[{&quot;selector&quot;:&quot;[data-folio-style=\\&quot;s1\\&quot;]&quot;,&quot;styles&quot;:{&quot;line-height&quot;:&quot;30px&quot;}}]"></style></head>');
  h = h.replace('杭州市示例路 1 号</p>', '杭州市示例路 1 号</p><p>无 ID 的新段落</p>');
  const edited = path.join(d, 'edited.html');
  fs.writeFileSync(edited, h);
  const r = sync(d, edited);
  assert.equal(r.status, 1, r.stdout);          // 有未写回项
  const rep = json(path.join(d, '.qa/folio-sync', fs.readdirSync(path.join(d, '.qa/folio-sync')).find((f) => f.endsWith('.json'))));
  const book = fs.readFileSync(path.join(d, 'book.html'), 'utf8');
  assert.match(book, /从早读到社团活动，<strong>看懂<\/strong>孩子怎样学习。<br>一个上午/);
  assert.match(book, /<img[^>]*src="assets\/images\/folio-img-day-left-[0-9a-f]{10}\.png"[^>]*>/);
  assert.match(book, /data-asset="folio-img-day-left-[0-9a-f]{10}"/);
  const css = fs.readFileSync(path.join(d, 'edits.css'), 'utf8');
  assert.match(css, /\[data-source-id="cover-title"\] \{ font-size: 60px !important; transform: translate\(12px, -8px\)/);
  assert.match(css, /\[data-source-id="day-p1"\], \[data-source-id="day-p2"\] \{ line-height: 30px !important; \}/);
  assert.ok(rep.unmapped.some((u) => u.kind === 'style'), '无 ID 的色块样式应列为未写回');
  assert.ok(rep.unmapped.some((u) => u.kind === 'text'), '无 ID 的新段落应列为未写回');
  const assets = json(path.join(d, 'sources/assets.json')).assets;
  const added = Object.entries(assets).find(([k]) => k.startsWith('folio-img-day-left'));
  assert.ok(added && added[1].license === '', '新图片登记但授权留空');
  // 同一份修改再写回一次：作者源已变，全部按冲突处理，不重复写
  const again = sync(d, edited);
  assert.equal(again.status, 1);
  assert.equal(fs.readFileSync(path.join(d, 'book.html'), 'utf8'), book);
  assert.match(again.stdout, /冲突/);
});

test('写回：其他语言的改字进入 copy/<语言>.json；源已被改动时报冲突', () => {
  const d = copy();
  const base = pack(d, 'en');
  const h = fs.readFileSync(base, 'utf8').replace('Break time is split between the playground and the library.', 'Break time is shared between the playground and the library.');
  const edited = path.join(d, 'edited-en.html');
  fs.writeFileSync(edited, h);
  const cf = path.join(d, 'copy/en.json');
  const before = json(cf);
  const r = sync(d, edited, '--dry-run');
  assert.equal(r.status, 0, r.stdout);
  assert.deepEqual(json(cf), before, 'dry-run 不写文件');
  assert.equal(sync(d, edited).status, 0);
  assert.match(json(cf).strings['day-p3'], /^Break time is shared/);
  // 冲突：导出编辑包后有人改了同一条译文
  const d2 = copy();
  const b2 = pack(d2, 'en');
  const c2 = json(path.join(d2, 'copy/en.json')); c2.strings['day-p3'] = 'Someone else changed this.'; fs.writeFileSync(path.join(d2, 'copy/en.json'), JSON.stringify(c2));
  const e2 = path.join(d2, 'e.html'); fs.writeFileSync(e2, fs.readFileSync(b2, 'utf8').replace('Break time is split', 'Break time is now split'));
  const r2 = sync(d2, e2);
  assert.equal(r2.status, 1);
  assert.equal(json(path.join(d2, 'copy/en.json')).strings['day-p3'], 'Someone else changed this.');
});

const haveFolio = fs.existsSync(path.join(FOLIO, 'node_modules/vite')) && fs.existsSync(path.join(FOLIO, 'src/bridge.js'));
test('真实往返：Folio 界面改字、拖动、换图 → 下载 → 写回 → 验收可交付', { skip: !haveFolio && `没有找到已安装依赖的 Folio（${FOLIO}）` , timeout: 300000 }, async () => {
  const require = createRequire(path.join(FOLIO, 'package.json'));
  const { chromium } = require('playwright');
  const d = copy();
  const pkg = pack(d, 'zh-CN');
  const build = fs.readFileSync(pkg, 'utf8').match(/name="hb-build" content="([0-9a-f]{12})"/)[1];
  const port = 4300 + Math.floor(Math.random() * 500);
  const server = spawn('npm', ['run', 'dev', '--', '--port', String(port), '--strictPort'], { cwd: FOLIO, stdio: 'pipe', detached: true });
  let browser;
  try {
    for (let i = 0; i < 150; i++) { try { if ((await fetch(`http://127.0.0.1:${port}`)).ok) break; } catch { /* 等待 */ } await new Promise((r) => setTimeout(r, 100)); }
    const libRoot = path.join(os.homedir(), '.local/hb-libs/root/usr/lib');
    const libs = fs.existsSync(libRoot) ? fs.readdirSync(libRoot).map((x) => path.join(libRoot, x)) : [];
    browser = await chromium.launch({ executablePath: process.env.HB_CHROMIUM || undefined, env: libs.length ? { ...process.env, LD_LIBRARY_PATH: libs.join(':') } : undefined });
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1100 }, acceptDownloads: true });
    const page = await ctx.newPage();
    await page.goto(`http://127.0.0.1:${port}`);
    await page.locator('.paper-wrap[aria-busy="false"]').waitFor({ timeout: 20000 });
    await page.getByLabel('选择 HTML 或 ZIP', { exact: true }).setInputFiles(pkg);
    await page.waitForFunction(() => document.querySelector('.page-total')?.textContent.replace(/\s/g, '') === '/4', null, { timeout: 20000 });
    const frame = page.frames().find((f) => f.parentFrame());
    assert.match(await page.locator('.hb-source').innerText(), new RegExp(build));
    // 无 ID 的色块：选中后出现提示
    await frame.locator('.cover-band').click({ position: { x: 300, y: 6 } });
    await page.locator('.hb-untraceable').waitFor({ timeout: 5000 });
    // 有内容 ID 的导语：没有提示；改字
    await frame.locator('[data-source-id="cover-lead"]').click();
    await page.locator('.selected-summary p', { hasText: '从早读到社团活动' }).first().waitFor();
    assert.equal(await page.locator('.hb-untraceable').count(), 0);
    await page.getByRole('button', { name: '编辑文字', exact: true }).click();
    await frame.locator('[data-source-id="cover-lead"][contenteditable="true"]').waitFor();
    await frame.locator('[data-source-id="cover-lead"]').fill('从早读到社团活动，看懂孩子怎样学习。');
    await page.getByRole('heading', { name: '编辑属性' }).click();
    // 悬浮文字工具条可能覆盖标题中部，从标题上沿发起单次拖动。
    await frame.locator('[data-source-id="cover-title"]').hover({ position: { x: 30, y: 10 } });
    const t = await frame.locator('[data-source-id="cover-title"]').boundingBox();
    await page.mouse.move(t.x + 30, t.y + 10); await page.mouse.down(); await page.mouse.move(t.x + 50, t.y + 25, { steps: 6 }); await page.mouse.up();
    await page.waitForTimeout(300);
    // 第 2 页换图
    await page.getByRole('button', { name: '下一页' }).click();
    // 跨页图比页面宽，locator.click 会先把它滚到中央；改为在可见位置直接用鼠标点击
    const img = await frame.locator('[data-edit-id="img-day-left"]').boundingBox();
    await page.mouse.click(img.x + 120, img.y + 80);
    await page.locator('.hb-untraceable').count();
    await page.getByLabel('选择替换图片', { exact: true }).setInputFiles({ name: 'new.png', mimeType: 'image/png', buffer: png(2600, 1850, [30, 120, 80]) });
    await frame.waitForFunction(() => document.querySelector('[data-edit-id="img-day-left"]').naturalWidth === 2600);
    const dl = page.waitForEvent('download');
    await page.getByRole('button', { name: '下载 HTML', exact: true }).click();
    const edited = path.join(d, 'folio-edited.html');
    await (await dl).saveAs(edited);
    const r = sync(d, edited);
    assert.equal(r.status, 0, r.stdout);
    const book = fs.readFileSync(path.join(d, 'book.html'), 'utf8');
    assert.match(book, /从早读到社团活动，看懂孩子怎样学习。/);
    assert.match(book, /folio-img-day-left-[0-9a-f]{10}\.png/);
    assert.match(fs.readFileSync(path.join(d, 'edits.css'), 'utf8'), /\[data-source-id="cover-title"\] \{ transform: translate\(/);
    // 未确认授权时不能交付；确认后完整验收可交付
    assert.notEqual(cli('check', d).status, 0);
    const af = path.join(d, 'sources/assets.json'); const a = json(af);
    for (const [k, v] of Object.entries(a.assets)) if (k.startsWith('folio-')) v.license = '用户自有（测试）';
    fs.writeFileSync(af, JSON.stringify(a, null, 2));
    const c = cli('check', d);
    assert.equal(c.status, 0, c.stdout);
  } finally {
    if (browser) await browser.close();
    try { process.kill(-server.pid); } catch { /* 已退出 */ }
  }
});
