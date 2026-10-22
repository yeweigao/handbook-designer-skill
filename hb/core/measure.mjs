// 版面测量（S3）：在渲染快照上以打印媒体只读测量，输出 pass / fail / unverified 报告。不修改任何样式与文件。
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { loadProject, mmToPx } from './project.mjs';
import { serve } from './server.mjs';
import { launch, openPage, waitResources } from './browser.mjs';
import { fingerprint, makeTools } from './fingerprint.mjs';
import { collectInPage, contrastInPage } from './checks/collect.mjs';

const HERE = path.dirname(new URL(import.meta.url).pathname);
export const DEFAULT_FLOORS = { body_px: 14, key_px: 12, aux_px: 10, body_contrast: 4.5, key_contrast: 4.5, aux_contrast: 3, display_contrast: 3 };
export const CHECKS = ['overflow.page', 'overflow.safe', 'clip.text', 'overlap.text', 'overlap.image', 'readability.size',
  'readability.contrast', 'font.fallback', 'image.dpi', 'image.bleed', 'content.hidden'];
const HIDE_TEXT = `*, *::before, *::after, *::marker { color: transparent !important; -webkit-text-fill-color: transparent !important;
  text-shadow: none !important; -webkit-text-stroke-color: transparent !important; text-decoration-color: transparent !important; }
  svg text, svg tspan { fill: transparent !important; stroke: transparent !important; }`;

export function floorsFor(p) {
  const floors = { ...DEFAULT_FLOORS };
  const notes = [];
  if (p.readability_waiver?.values) {
    Object.assign(floors, p.readability_waiver.values);
    notes.push({ id: 'readability.waiver', status: 'pass', severity: 'hint', page: null, target: null,
      evidence: p.readability_waiver, message: `已授权放宽可读性下限：${JSON.stringify(p.readability_waiver.values)}（${p.readability_waiver.reason}）` });
  }
  for (const [k, v] of Object.entries(p.readability || {})) floors[k] = Math.max(floors[k], v);
  return { floors, notes };
}

async function fontFallback(page, collected, p, dir) {
  const items = [];
  const client = await page.context().newCDPSession(page);
  await client.send('DOM.enable');
  await client.send('CSS.enable');
  const doc = await client.send('DOM.getDocument', { depth: -1 });
  const { nodeIds } = await client.send('DOM.querySelectorAll', { nodeId: doc.root.nodeId, selector: '[data-hbm-i]' });
  const byIndex = new Map();
  for (const tn of collected.textNodes) {
    if (!byIndex.has(tn.i)) byIndex.set(tn.i, []);
    byIndex.get(tn.i).push(tn);
  }
  const fallbacks = [];
  for (const nodeId of nodeIds) {
    const { attributes } = await client.send('DOM.getAttributes', { nodeId });
    const idx = Number(attributes[attributes.indexOf('data-hbm-i') + 1]);
    const { fonts } = await client.send('CSS.getPlatformFontsForNode', { nodeId });
    const sys = fonts.filter((f) => !f.isCustomFont && f.glyphCount > 0);
    if (sys.length) fallbacks.push({ idx, fonts: sys.map((f) => `${f.familyName}${f.postScriptName ? ` (${f.postScriptName})` : ''}`), nodes: byIndex.get(idx) || [] });
  }
  await client.detach();
  if (!fallbacks.length) return items;
  const req = { fonts: p.fonts.map((f) => path.join(dir, f.file)), texts: Object.fromEntries(fallbacks.map((f) => [String(f.idx), f.nodes.map((n) => n.text).join('')])) };
  const r = spawnSync('python3', [path.join(HERE, 'fontcover.py')], { input: JSON.stringify(req), encoding: 'utf8' });
  const miss = r.status === 0 ? JSON.parse(r.stdout) : {};
  for (const f of fallbacks) {
    const n = f.nodes[0] || {};
    const chars = miss[String(f.idx)] || '';
    items.push({ id: 'font.fallback', status: 'fail', severity: 'hard', page: n.pageId, target: n.target,
      evidence: { system_fonts: f.fonts, uncovered_chars: chars },
      message: chars
        ? `字符「${chars}」不在任何声明字体里，回退到系统字体 ${f.fonts.join('、')}`
        : `回退到系统字体 ${f.fonts.join('、')}：所需字形在已声明字体中存在，但该元素的 font-family 没有包含它` });
  }
  return items;
}

async function measureLang(ctx, browser, server, buildId, lang, floors) {
  const { dir, p, geom } = ctx;
  const snapshot = path.join(dir, '.build', buildId, lang, 'snapshot.html');
  if (!fs.existsSync(snapshot)) {
    return [{ id: 'measure.build', status: 'unverified', severity: 'hard', page: null, target: null, evidence: { build: buildId },
      message: `没有构建 ${buildId} 的 ${lang} 快照：先运行 node hb/core/cli.mjs render` }];
  }
  const blocked = [];
  const { context, page } = await openPage(browser, server.origin, blocked);
  try {
    await page.emulateMedia({ media: 'print' });
    await page.goto(`${server.origin}/${path.relative(dir, snapshot).split(path.sep).join('/')}`, { waitUntil: 'networkidle' });
    const res = await waitResources(page);
    const items = [];
    for (const f of res.fontFail) items.push({ id: 'measure.resource', status: 'unverified', severity: 'hard', page: null, target: null, evidence: { font: f }, message: `字体未加载，测量不可信：${f}` });
    const px = { mediaW: mmToPx(geom.mediaW), mediaH: mmToPx(geom.mediaH), bleed: mmToPx(geom.bleed),
      safe: Object.fromEntries(Object.entries(geom.safe).map(([k, v]) => [k, mmToPx(v)])) };
    const collected = await page.evaluate(collectInPage, { geom: px, floors, tol: 0.5 });
    items.push(...collected.items);

    // 对比度：隐藏全部文字后截取每页，作为文字背后的真实背景
    const style = await page.addStyleTag({ content: HIDE_TEXT });
    const shots = {};
    const pagesLoc = page.locator('.page');
    const n = await pagesLoc.count();
    const need = new Set(collected.textNodes.map((t) => t.page));
    for (let i = 0; i < n; i++) if (need.has(i)) shots[i] = (await pagesLoc.nth(i).screenshot({ animations: 'disabled' })).toString('base64');
    await style.evaluate((e) => e.remove());
    const contrast = await page.evaluate(contrastInPage, { shots, textNodes: collected.textNodes, floors });
    const worst = new Map();
    for (const c of contrast) {
      const key = `${c.page}|${c.target}`;
      if (c.unverified) {
        items.push({ id: 'readability.contrast', status: 'unverified', severity: 'hint', page: c.page, target: c.target,
          evidence: { reason: c.unverified }, message: `${c.unverified}：对比度无法自动测量，请目检` });
        continue;
      }
      if (c.p05 < c.floor && (!worst.has(key) || worst.get(key).p05 > c.p05)) worst.set(key, c);
    }
    for (const c of worst.values()) {
      const r = (v) => Math.round(v * 100) / 100;
      items.push({ id: 'readability.contrast', status: 'fail', severity: 'hard', page: c.page, target: c.target,
        evidence: { contrast_p05: r(c.p05), contrast_min: r(c.min), contrast_median: r(c.median), min: c.floor, role: c.role, text: c.text },
        message: `${c.role} 文字对比度 ${r(c.p05)}:1（按背景最差 5% 计）低于 ${c.floor}:1：「${c.text}」` });
    }

    // 字体回退（CDP 报告的实际渲染字体）
    try { items.push(...await fontFallback(page, collected, p, dir)); }
    catch (e) {
      items.push({ id: 'font.fallback', status: 'unverified', severity: 'hard', page: null, target: null, evidence: { error: String(e.message || e) }, message: '无法读取实际使用的字体（CDP 失败）' });
    }
    for (const url of blocked) items.push({ id: 'measure.resource', status: 'unverified', severity: 'hard', page: null, target: null, evidence: { url }, message: `快照请求了外部资源：${url}` });
    return items;
  } finally {
    await context.close();
  }
}

function summarize(items) {
  const out = [...items];
  for (const id of CHECKS) {
    if (!items.some((i) => i.id === id && i.status !== 'pass')) {
      out.push({ id, status: 'pass', severity: 'hard', page: null, target: null, evidence: {}, message: '全部通过' });
    }
  }
  const count = (s, sev) => out.filter((i) => i.status === s && (!sev || i.severity === sev)).length;
  const blocking = out.filter((i) => i.severity === 'hard' && i.status !== 'pass').length;
  return { items: out, summary: { fail: count('fail', 'hard'), unverified: count('unverified', 'hard'), hints: out.filter((i) => i.severity === 'hint' && i.status !== 'pass').length, blocking } };
}

function writeReport(dir, buildId, lang, floors, rep) {
  const qa = path.join(dir, '.qa', buildId, lang);
  fs.mkdirSync(qa, { recursive: true });
  const status = rep.summary.blocking ? 'fail' : 'pass';
  const json = { contract: 1, check: 'measure', build_id: buildId, lang, floors, status, summary: rep.summary, items: rep.items };
  fs.writeFileSync(path.join(qa, 'measure.json'), JSON.stringify(json, null, 2) + '\n');
  const lines = [`# 版面测量 · ${buildId} · ${lang}`, '', `状态：**${status === 'pass' ? '通过' : '不通过'}**　硬项失败 ${rep.summary.fail}　硬项未验证 ${rep.summary.unverified}　提示 ${rep.summary.hints}`, '',
    '| 检查 | 结果 |', '|---|---|'];
  for (const id of CHECKS) {
    const bad = rep.items.filter((i) => i.id === id && i.status !== 'pass');
    lines.push(`| ${id} | ${bad.length ? `${bad.filter((i) => i.severity === 'hard').length} 硬项 / ${bad.filter((i) => i.severity === 'hint').length} 提示` : '通过'} |`);
  }
  const bad = rep.items.filter((i) => i.status !== 'pass');
  if (bad.length) {
    lines.push('', '## 明细', '', '| 级别 | 状态 | 检查 | 页面 | 对象 | 说明 |', '|---|---|---|---|---|---|');
    for (const i of bad) lines.push(`| ${i.severity} | ${i.status} | ${i.id} | ${i.page || ''} | ${i.target || ''} | ${String(i.message).replace(/\|/g, '\\|')} |`);
  }
  fs.writeFileSync(path.join(qa, 'measure.md'), lines.join('\n') + '\n');
  return { status, file: path.relative(dir, path.join(qa, 'measure.json')) };
}

export async function measure(root, opts = {}) {
  const ctx = loadProject(root);
  const { dir, p } = ctx;
  const { floors, notes } = floorsFor(p);
  const langs = opts.langs?.length ? opts.langs : p.languages;
  const { browser, info } = await launch();
  const server = await serve(dir);
  try {
    const buildId = opts.build || fingerprint(dir, p, makeTools(info)).buildId;
    const results = [];
    for (const lang of langs) {
      const items = [...notes, ...await measureLang(ctx, browser, server, buildId, lang, floors)];
      const rep = summarize(items);
      const w = writeReport(dir, buildId, lang, floors, rep);
      results.push({ lang, ...w, summary: rep.summary, items: rep.items });
    }
    return { buildId, results, status: results.every((r) => r.status === 'pass') ? 'pass' : 'fail' };
  } finally {
    await server.close();
    await browser.close();
  }
}
