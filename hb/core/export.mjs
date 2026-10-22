// 导出与离线交付（S8）。
//   review <项目> --verdict deliverable|excellent|fail --by <审稿人> [--notes <文件>]
//       把视觉审稿结论绑定到当前构建（构建 ID 与各语言 PDF 哈希），写 .qa/<构建 ID>/visual-review.json。
//   export <项目> [--name <文件名>] [--draft]
//       正式导出：verify 有效 + 视觉审稿为可交付/优秀 → 在暂存目录生成全部交付物并逐项实测 → 全部通过才发布到 out/<文件名>/。
//       草稿（--draft）：不要求验收，只导出带「草稿 DRAFT」水印的 PDF。
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { loadProject, mmToPx } from './project.mjs';
import { verify } from './gate.mjs';
import { launch, waitResources } from './browser.mjs';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const sha256 = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const py = (script, args) => spawnSync('python3', [path.join(HERE, script), ...args], { encoding: 'utf8' });
const safeName = (s) => s.replace(/[\\/:*?"<>|\s]+/g, '-').replace(/^-+|-+$/g, '') || 'handbook';
const VERDICTS = { deliverable: '可交付', excellent: '优秀', fail: '不合格' };

export async function review(root, { verdict, by, notes }) {
  const { dir } = loadProject(root);
  if (!VERDICTS[verdict]) throw new Error(`--verdict 只能是 ${Object.keys(VERDICTS).join(' / ')}`);
  if (!by) throw new Error('需要 --by <审稿人>');
  const v = await verify(dir);
  if (!v.valid) throw new Error(`当前构建没有有效的技术验收，不能记录视觉审稿：${v.reasons.join('；')}`);
  const rec = { contract: 1, build_id: v.buildId, fingerprint: v.gate.fingerprint, verdict, by, date: new Date().toISOString(),
    pdf_sha256: Object.fromEntries(Object.entries(v.gate.languages).map(([l, g]) => [l, g.pdf_sha256])),
    notes: notes ? fs.readFileSync(notes, 'utf8') : '' };
  const file = path.join(dir, '.qa', v.buildId, 'visual-review.json');
  fs.writeFileSync(file, JSON.stringify(rec, null, 2) + '\n');
  return { ...rec, file: path.relative(dir, file) };
}

// 用浏览器打开离线 HTML：只允许 data: 与文件本身；字体与图片必须全部就绪；再导出 PDF 与正式版逐页比较。
async function checkOffline(browser, htmlFile, refPdf, geom, work) {
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 1600 }, deviceScaleFactor: 1, locale: 'zh-CN', timezoneId: 'UTC' });
  const external = [];
  await ctx.route('**/*', (r) => { const u = r.request().url(); if (u.startsWith('file:') || u.startsWith('data:')) return r.continue(); external.push(u); return r.abort(); });
  const page = await ctx.newPage();
  await page.emulateMedia({ media: 'print' });
  await page.goto('file://' + htmlFile, { waitUntil: 'load' });
  const res = await waitResources(page);
  const fileReqs = await page.evaluate(() => performance.getEntriesByType('resource').map((e) => e.name).filter((n) => !n.startsWith('data:')));
  const pdf = path.join(work, 'offline-check.pdf');
  await page.pdf({ path: pdf, width: `${geom.mediaW + 1}mm`, height: `${geom.mediaH + 1}mm`, printBackground: true });
  await ctx.close();
  py('pdfboxes.py', [pdf, String(geom.mediaW), String(geom.mediaH), String(geom.bleed)]);
  const cmp = py('compare_pdf.py', [refPdf, pdf, '50', '0.001']);
  const problems = [...external.map((u) => `外部请求 ${u}`), ...fileReqs.map((u) => `外部文件请求 ${u}`),
    ...res.fontFail.map((f) => `字体未加载 ${f}`), ...res.imgFail.map((i) => `图片未加载 ${i}`)];
  if (cmp.status !== 0) problems.push(`与正式 PDF 栅格不一致：${cmp.stdout.trim()}`);
  return { ok: problems.length === 0, problems, compare: JSON.parse(cmp.stdout || '{}') };
}

async function draftExport(ctx, name) {
  const { dir, p, geom } = ctx;
  const { render } = await import('./render.mjs');
  const r = await render(dir, {});
  const out = path.join(dir, 'out', `${name}-draft`);
  fs.rmSync(out, { recursive: true, force: true });
  fs.mkdirSync(out, { recursive: true });
  const { browser } = await launch();
  const wm = path.join(out, '.watermark.pdf');
  try {
    const page = await browser.newPage();
    const w = mmToPx(geom.mediaW); const h = mmToPx(geom.mediaH);
    await page.setContent(`<style>@page{margin:0}body{margin:0}</style><div style="width:${w}px;height:${h}px;display:flex;align-items:center;justify-content:center">
      <div style="transform:rotate(-32deg);font:800 96px/1 sans-serif;letter-spacing:.06em;color:rgba(230,30,40,.22);white-space:nowrap">草稿 DRAFT</div></div>`);
    await page.pdf({ path: wm, width: `${geom.mediaW + 1}mm`, height: `${geom.mediaH + 1}mm`, printBackground: true });
  } finally { await browser.close(); }
  py('pdfboxes.py', [wm, String(geom.mediaW), String(geom.mediaH), String(geom.bleed)]);
  const files = [];
  for (const l of r.results) {
    if (!l.pdf) continue;
    const dst = path.join(out, `${name}.${l.lang}.draft.pdf`);
    const s = spawnSync('python3', ['-c', `import pikepdf,sys
src,wm,dst=sys.argv[1:4]
with pikepdf.open(src) as pdf, pikepdf.open(wm) as w:
    for pg in pdf.pages: pg.add_overlay(w.pages[0])
    pdf.save(dst)`, path.join(dir, l.pdf.path), wm, dst], { encoding: 'utf8' });
    if (s.status !== 0) throw new Error(`草稿水印失败：${s.stderr}`);
    files.push(path.relative(dir, dst));
  }
  fs.rmSync(wm);
  fs.writeFileSync(path.join(out, 'delivery.json'), JSON.stringify({ contract: 1, status: 'draft', build_id: r.build_id, files }, null, 2) + '\n');
  return { status: 'draft', out: path.relative(dir, out), files, checks: [] };
}

export async function exportBook(root, opts = {}) {
  const ctx = loadProject(root);
  const { dir, p, geom } = ctx;
  const name = safeName(opts.name || p.title);
  if (opts.draft) return draftExport(ctx, name);

  const v = await verify(dir);
  if (!v.valid) return { status: 'refused', reasons: v.reasons };
  const buildId = v.buildId;
  const vrFile = path.join(dir, '.qa', buildId, 'visual-review.json');
  if (!fs.existsSync(vrFile)) return { status: 'refused', reasons: ['当前构建没有视觉审稿记录：审完最终 PDF 后运行 review 记录结论'] };
  const vr = JSON.parse(fs.readFileSync(vrFile, 'utf8'));
  if (vr.build_id !== buildId || Object.entries(v.gate.languages).some(([l, g]) => vr.pdf_sha256[l] !== g.pdf_sha256)) {
    return { status: 'refused', reasons: ['视觉审稿记录不是针对当前 PDF 的'] };
  }
  if (!['deliverable', 'excellent'].includes(vr.verdict)) return { status: 'refused', reasons: [`视觉审稿结论为「${VERDICTS[vr.verdict]}」`] };

  const staging = path.join(dir, 'out', `.staging-${buildId}`);
  fs.rmSync(staging, { recursive: true, force: true });
  fs.mkdirSync(staging, { recursive: true });
  const work = fs.mkdtempSync(path.join(os.tmpdir(), 'hb-export-'));
  const checks = [];
  const files = {};
  const add = (id, ok, message, evidence = {}) => checks.push({ id, status: ok ? 'pass' : 'fail', severity: 'hard', message, evidence });
  const { browser } = await launch();
  try {
    for (const lang of p.languages) {
      const g = v.gate.languages[lang];
      const src = path.join(dir, g.pdf);
      const pdf = path.join(staging, `${name}.${lang}.pdf`);
      fs.copyFileSync(src, pdf);
      add(`pdf.${lang}`, sha256(pdf) === g.pdf_sha256, '正式 PDF 与验收记录一致');
      // 可编辑 PDF
      const ed = path.join(staging, `${name}.${lang}.editable.pdf`);
      const e = py('editable_pdf.py', [dir, pdf, ed]);
      const edInfo = (() => { try { return JSON.parse(e.stdout.trim().split('\n').pop()); } catch { return {}; } })();
      const cmp = py('compare_pdf.py', [pdf, ed, '60', '0']);
      const fontsOut = spawnSync('pdffonts', [ed], { encoding: 'utf8' }).stdout || '';
      const subsetLeft = fontsOut.split('\n').slice(2).filter((l) => /^[A-Z]{6}\+/.test(l));
      add(`editable.${lang}`, e.status === 0 && cmp.status === 0 && !/Type 3/.test(fontsOut) && subsetLeft.length === 0,
        '可编辑 PDF：字体扩充嵌入（非子集）、无 Type 3、逐页栅格与正式版一致', { ...edInfo, compare: cmp.stdout.trim() });
      // 离线 HTML
      const html = path.join(staging, `${name}.${lang}.html`);
      const o = py('offline_html.py', [dir, path.join(dir, '.build', buildId, lang, 'snapshot.html'), html]);
      if (o.status !== 0) add(`offline.${lang}`, false, `离线 HTML 生成失败：${o.stderr.trim()}`);
      else {
        const oc = await checkOffline(browser, html, pdf, geom, work);
        add(`offline.${lang}`, oc.ok, oc.ok ? '离线 HTML：无外部请求、资源全部就绪、打印结果与正式 PDF 一致' : oc.problems.join('；'), oc.compare);
      }
      // 审稿拼图
      for (const k of ['sheet', 'spreads']) {
        const s = path.join(dir, '.qa', buildId, lang, 'raster', `${k}.png`);
        if (fs.existsSync(s)) fs.copyFileSync(s, path.join(staging, `${name}.${lang}.${k}.png`));
      }
    }
    // 源文件包 + 干净目录重建
    const zip = path.join(staging, `${name}.source.zip`);
    const pk = py('pack.py', [dir, buildId, zip]);
    if (pk.status !== 0) add('source.pack', false, `源文件包失败：${pk.stderr.trim()}`);
    else {
      const rb = path.join(work, 'rebuild');
      fs.mkdirSync(rb);
      spawnSync('python3', ['-c', 'import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])', zip, rb]);
      const c = spawnSync('node', [path.join(HERE, 'cli.mjs'), 'check', rb], { encoding: 'utf8' });
      const id = c.stdout.match(/验收 ([0-9a-f]{12})/)?.[1];
      const same = id === buildId && c.status === 0;
      let pixels = [];
      if (same) {
        for (const lang of p.languages) {
          const cmp = py('compare_pdf.py', [path.join(staging, `${name}.${lang}.pdf`), path.join(rb, '.build', id, lang, 'book.pdf'), '60', '0']);
          pixels.push(cmp.status === 0);
        }
      }
      add('source.rebuild', same && pixels.every(Boolean), same ? '源文件包在干净目录重建：构建 ID 相同、验收通过、逐页栅格一致'
        : `源文件包重建不一致：构建 ${id || '失败'}（期望 ${buildId}）\n${c.stdout.slice(-600)}`, { rebuilt_build: id });
    }
    // 来源与授权清单
    const assets = fs.existsSync(path.join(dir, 'sources/assets.json')) ? JSON.parse(fs.readFileSync(path.join(dir, 'sources/assets.json'), 'utf8')).assets : {};
    const credits = ['# 来源与授权', '', '## 图片与素材', '', '| 素材 | 文件 | 来源 | 授权 | 署名 |', '|---|---|---|---|---|',
      ...Object.entries(assets).map(([k, a]) => `| ${k} | ${a.file} | ${a.source || ''} | ${a.license || ''} | ${a.credit || ''} |`),
      '', '## 字体', '', ...p.fonts.map((f) => `- ${f.family} ${f.weight}：${f.file}（授权文本见源文件包中字体目录）`), ''];
    fs.writeFileSync(path.join(staging, 'credits.md'), credits.join('\n'));
  } finally {
    await browser.close();
    fs.rmSync(work, { recursive: true, force: true });
  }
  for (const f of fs.readdirSync(staging)) files[f] = sha256(path.join(staging, f));
  const ok = checks.every((c) => c.status === 'pass');
  const delivery = { contract: 1, status: ok ? 'delivered' : 'failed', name, build_id: buildId, fingerprint: v.gate.fingerprint,
    tools: v.gate.tools, visual_review: { verdict: vr.verdict, by: vr.by, date: vr.date }, checks, files };
  fs.writeFileSync(path.join(staging, 'delivery.json'), JSON.stringify(delivery, null, 2) + '\n');
  if (!ok) return { status: 'failed', staging: path.relative(dir, staging), checks };
  const out = path.join(dir, 'out', name);
  fs.rmSync(out, { recursive: true, force: true });
  fs.renameSync(staging, out);
  return { status: 'delivered', out: path.relative(dir, out), checks, files: Object.keys(files) };
}
