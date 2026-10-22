// 渲染运行时（S2）：项目 → 文案注入 → 打印/字体 CSS → 资源就绪 → 每种语言的快照与 PDF → 输入指纹。
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { loadProject, mmToPx } from './project.mjs';
import { printCss, fontCss } from './print-css.mjs';
import { loadCopy } from './inject.mjs';
import { serve } from './server.mjs';
import { launch, openPage, waitResources } from './browser.mjs';
import { fingerprint, makeTools, fileSha256 } from './fingerprint.mjs';
import { flowInPage } from './checks/flow.mjs';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const TIMEOUT = 30000;

export class RenderError extends Error {
  constructor(code, message, extra = {}) { super(message); this.code = code; Object.assign(this, extra); }
}

export function runValidate(dir) {
  const r = spawnSync('python3', [path.join(HERE, 'validate.py'), dir, '--json'], { encoding: 'utf8' });
  if (r.error) throw new RenderError('validate.run', `无法运行契约校验：${r.error.message}`);
  let rep;
  try { rep = JSON.parse(r.stdout); } catch { throw new RenderError('validate.run', `契约校验输出无法解析：${r.stderr || r.stdout}`); }
  const errors = rep.items.filter((i) => i.level === 'error');
  if (errors.length) {
    throw new RenderError('validate.failed', '契约校验不通过：\n' +
      errors.map((e) => `  ${e.code} ${e.where}: ${e.message}`).join('\n'), { items: errors });
  }
  return rep.items;
}

export function assemble({ dir, p, geom }, lang, langDir) {
  let html = fs.readFileSync(path.join(dir, p.entry), 'utf8');
  const base = path.relative(langDir, dir).split(path.sep).join('/') + '/';
  const links = [...p.styles];
  if (fs.existsSync(path.join(dir, 'lang', `${lang}.css`))) links.push(`lang/${lang}.css`);
  if (fs.existsSync(path.join(dir, 'edits.css'))) links.push('edits.css');
  const head = `<meta charset="utf-8"><base href="${base}" data-hb="base">` +
    `<style data-hb="print">\n${printCss({ geom })}</style>` +
    `<style data-hb="fonts">\n${fontCss({ p })}</style>` +
    links.map((l) => `<link rel="stylesheet" href="${l}" data-hb="style">`).join('');
  if (!/<head\b[^>]*>/i.test(html)) throw new RenderError('html.head', `${p.entry} 缺少 <head>`);
  html = html.replace(/<head\b[^>]*>/i, (m) => m + head);
  html = /<html\b[^>]*\blang\s*=/i.test(html)
    ? html.replace(/(<html\b[^>]*\blang\s*=\s*)(["'])[^"']*\2/i, `$1"${lang}"`)
    : html.replace(/<html\b/i, `<html lang="${lang}"`);
  return html;
}

async function renderLang(ctx, browser, server, lang, langDir, fp, tools) {
  const { dir, p, geom } = ctx;
  const errors = [];
  const blocked = [];
  const relOf = (abs) => path.relative(dir, abs).split(path.sep).join('/');
  fs.mkdirSync(langDir, { recursive: true });

  // 1. 组装并注入文案，序列化为快照
  const assembledPath = path.join(langDir, '.assembled.html');
  fs.writeFileSync(assembledPath, assemble(ctx, lang, langDir));
  const a = await openPage(browser, server.origin, blocked);
  await a.page.emulateMedia({ media: 'print' });
  await a.page.goto(`${server.origin}/${relOf(assembledPath)}`, { waitUntil: 'load', timeout: TIMEOUT });
  let flows = null;
  if (lang !== p.default_language) {
    // 其他语言：先把续页片段合并回整段，注入译文，再按同一续排算法重新分页（默认语言的分页已由 paginate 写回作者源）
    await a.page.evaluate(flowInPage, { mergeOnly: true });
    const copy = loadCopy(dir, lang);
    const r = await a.page.evaluate((copy) => {
      const missing = []; const seen = new Set();
      for (const el of document.querySelectorAll('[data-source-id]')) {
        const id = el.dataset.sourceId;
        if (!(id in copy)) { missing.push(id); continue; }
        el.innerHTML = copy[id]; seen.add(id);
      }
      return { missing, extra: Object.keys(copy).filter((k) => !seen.has(k)) };
    }, copy);
    for (const id of r.missing) errors.push({ code: 'inject.untranslated', message: `缺译：${id}` });
    for (const id of r.extra) errors.push({ code: 'inject.extra', message: `多余译文：${id}` });
    const pre = await waitResources(a.page, TIMEOUT);
    for (const f of pre.fontFail) errors.push({ code: 'resource.font', message: `字体加载失败：${f}（检查 project.json 的 fonts 与字体文件是否完整）` });
    if (await a.page.evaluate(() => !!document.querySelector('[data-flow]'))) {
      flows = await a.page.evaluate(flowInPage, { firstPage: p.first_page });
      for (const e of flows.errors) errors.push({ code: e.code, page: e.page, message: `[续排 ${e.flow || ''}] ${e.message}` });
    }
  }
  const snapshot = '<!DOCTYPE html>\n' + await a.page.evaluate(() => document.documentElement.outerHTML) + '\n';
  await a.context.close();
  fs.rmSync(assembledPath);
  const snapshotPath = path.join(langDir, 'snapshot.html');
  fs.writeFileSync(snapshotPath, snapshot);

  // 2. 从快照渲染：等待资源，核对页面尺寸，导出 PDF
  const s = await openPage(browser, server.origin, blocked);
  await s.page.emulateMedia({ media: 'print' });
  await s.page.goto(`${server.origin}/${relOf(snapshotPath)}`, { waitUntil: 'networkidle', timeout: TIMEOUT });
  const res = await waitResources(s.page, TIMEOUT);
  for (const f of res.fontFail) errors.push({ code: 'resource.font', message: `字体加载失败：${f}（检查 project.json 的 fonts 与字体文件是否完整）` });
  for (const i of res.imgFail) errors.push({ code: 'resource.image', message: `图片加载或解码失败：${i}` });

  const expected = { width_mm: geom.mediaW, height_mm: geom.mediaH, width_px: mmToPx(geom.mediaW), height_px: mmToPx(geom.mediaH) };
  const pages = await s.page.evaluate(() => [...document.querySelectorAll('.page')].map((el) => {
    const r = el.getBoundingClientRect();
    return { id: el.dataset.pageId, width_px: Number(r.width.toFixed(3)), height_px: Number(r.height.toFixed(3)) };
  }));
  if (!pages.length) errors.push({ code: 'page.none', message: '没有任何 .page' });
  for (const pg of pages) {
    if (Math.abs(pg.width_px - expected.width_px) > 0.5 || Math.abs(pg.height_px - expected.height_px) > 0.5) {
      errors.push({ code: 'page.size', page: pg.id,
        message: `页面 ${pg.id} 实际 ${pg.width_px}×${pg.height_px}px，应为 ${expected.width_px.toFixed(2)}×${expected.height_px.toFixed(2)}px（不要在作者 CSS 里改 .page 宽高）` });
    }
  }

  // PDF 书签：有 [data-outline]（值为层级 1/2/3）时只用它们；否则每页第一个 h1/h2 作为一级书签。
  const outline = await s.page.evaluate(() => {
    const pagesEl = [...document.querySelectorAll('.page')];
    const pageOf = (el) => pagesEl.indexOf(el.closest('.page'));
    const text = (el) => (el.innerText || '').replace(/\s+/g, ' ').trim();
    const marked = [...document.querySelectorAll('.page [data-outline]')];
    if (marked.length) return marked.map((el) => ({ title: text(el), level: Number(el.dataset.outline) || 1, page: pageOf(el) }));
    return pagesEl.map((pg, i) => { const h = pg.querySelector('h1, h2'); return h ? { title: text(h), level: 1, page: i } : null; }).filter(Boolean);
  });
  const outlinePath = path.join(langDir, 'outline.json');
  fs.writeFileSync(outlinePath, JSON.stringify(outline, null, 1) + '\n');

  const pdfPath = path.join(langDir, 'book.pdf');
  const fatal = errors.some((e) => e.code.startsWith('resource.') || e.code.startsWith('inject.'));
  if (!fatal) {
    // Chrome 的纸张尺寸按 1/75 英寸取整：先按每边大 1mm 输出，再由 pdfboxes.py 精确裁切并写入页面框。
    await s.page.pdf({ path: pdfPath, width: `${geom.mediaW + 1}mm`, height: `${geom.mediaH + 1}mm`, printBackground: true });
    const r = spawnSync('python3', [path.join(HERE, 'pdfboxes.py'), pdfPath, String(geom.mediaW), String(geom.mediaH), String(geom.bleed), outlinePath], { encoding: 'utf8' });
    if (r.status !== 0) errors.push({ code: 'pdf.boxes', message: `PDF 页面框处理失败：${(r.stderr || r.error?.message || '').trim()}（需要 pikepdf）` });
  }
  await s.context.close();

  // 3. 请求核对：被拒绝的外部请求、缺失文件、指纹未覆盖的依赖
  for (const url of [...new Set(blocked)]) errors.push({ code: 'network.blocked', message: `拦截了外部请求：${url}` });
  const outRel = relOf(langDir).split('/').slice(0, -1).join('/') + '/';
  const requested = [...new Set(server.log.filter((l) => l.status === 200).map((l) => l.path))]
    .filter((x) => !x.startsWith(outRel)).sort();
  for (const l of server.log) {
    if (l.status !== 200) errors.push({ code: 'resource.missing', message: `请求的文件${l.status === 403 ? '在项目目录以外' : '不存在'}：${l.path}` });
  }
  const known = new Set(fp.inputs.map((i) => i.path));
  for (const r of requested) {
    if (!known.has(r)) errors.push({ code: 'fingerprint.gap', message: `渲染用到了指纹没有覆盖的文件：${r}（指纹扫描规则有遗漏）` });
  }
  server.log.length = 0;

  const manifest = {
    contract: 1, build_id: fp.buildId, fingerprint: fp.fingerprint, lang, tools, expected, pages,
    page_count: pages.length, inputs: fp.inputs, requested, flows, outline,
    snapshot: { path: relOf(snapshotPath), sha256: fileSha256(snapshotPath) },
    pdf: fs.existsSync(pdfPath) && !fatal && !errors.some((e) => e.code === 'pdf.boxes') ? { path: relOf(pdfPath), sha256: fileSha256(pdfPath), bytes: fs.statSync(pdfPath).size } : null,
    status: errors.length ? 'fail' : 'pass', errors,
  };
  fs.writeFileSync(path.join(langDir, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  return manifest;
}

export async function render(root, opts = {}) {
  const ctx = loadProject(root);
  const { dir, p } = ctx;
  let warnings = [];
  if (process.env.HB_SKIP_VALIDATE === '1') warnings.push({ code: 'validate.skipped', message: '已跳过契约校验（仅供测试）' });
  else warnings = runValidate(dir).filter((i) => i.level === 'warning');

  const langs = opts.langs?.length ? opts.langs : p.languages;
  for (const l of langs) if (!p.languages.includes(l)) throw new RenderError('lang.unknown', `项目没有语言 ${l}`);

  const { browser, info } = await launch();
  const server = await serve(dir);
  try {
    const tools = makeTools(info);
    const fp = fingerprint(dir, p, tools);
    const outDir = opts.out ? path.resolve(dir, opts.out) : path.join(dir, '.build', fp.buildId);
    const rel = path.relative(dir, outDir);
    if (!rel || rel.startsWith('..') || path.isAbsolute(rel)) throw new RenderError('out.outside', '输出目录必须在项目目录内');
    fs.mkdirSync(outDir, { recursive: true });
    const results = [];
    for (const lang of langs) results.push(await renderLang(ctx, browser, server, lang, path.join(outDir, lang), fp, tools));
    const build = { contract: 1, build_id: fp.buildId, fingerprint: fp.fingerprint, tools, warnings,
      languages: results.map((r) => ({ lang: r.lang, status: r.status, pages: r.page_count, pdf: r.pdf?.path || null })),
      status: results.every((r) => r.status === 'pass') ? 'pass' : 'fail' };
    fs.writeFileSync(path.join(outDir, 'build.json'), JSON.stringify(build, null, 2) + '\n');
    return { ...build, outDir, results };
  } finally {
    await server.close();
    await browser.close();
  }
}
