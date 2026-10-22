// 验收汇总与绑定（S4）：check = 渲染 → 测量 → 最终 PDF 检查 → 栅格 → （原文覆盖）→ gate.json；
// verify = 重新计算当前源的指纹与 PDF 哈希，与 gate.json 比对。任何输入或产物变化都让旧验收失效。
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { loadProject } from './project.mjs';
import { render } from './render.mjs';
import { measure } from './measure.mjs';
import { launch } from './browser.mjs';
import { fingerprint, makeTools } from './fingerprint.mjs';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const sha256 = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const readJson = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));

async function coverageFor(dir, buildId, lang) {
  // 原文覆盖由 S5 的 coverage.mjs 提供；尚未实现或未运行时是硬项 unverified，阻止交付。
  let mod = null;
  try { mod = await import('./coverage.mjs'); } catch { /* 尚未实现 */ }
  if (!mod?.coverage) {
    return { status: 'fail', items: [{ id: 'coverage.missing', status: 'unverified', severity: 'hard', page: null, target: null, evidence: {},
      message: '原文覆盖检查尚未实现（S5），内容完整性未验证' }] };
  }
  return mod.coverage(dir, buildId, lang);
}

function runPy(script, args) {
  const r = spawnSync('python3', [path.join(HERE, script), ...args], { encoding: 'utf8' });
  return { code: r.status, out: (r.stdout || '') + (r.stderr || '') };
}

export async function check(root, opts = {}) {
  const { dir, p } = loadProject(root);
  const langs = opts.langs?.length ? opts.langs : p.languages;
  const r = await render(dir, { langs });
  const buildId = r.build_id;
  const qaRoot = path.join(dir, '.qa', buildId);
  fs.mkdirSync(qaRoot, { recursive: true });
  const m = await measure(dir, { langs, build: buildId });
  const languages = {};
  const blocking = [];
  for (const lang of langs) {
    const rl = r.results.find((x) => x.lang === lang);
    const ml = m.results.find((x) => x.lang === lang);
    const checks = {};
    checks.render = rl.status;
    for (const e of rl.errors) blocking.push({ lang, id: `render.${e.code}`, status: 'fail', message: e.message });
    checks.measure = ml.status;
    for (const i of ml.items) if (i.severity === 'hard' && i.status !== 'pass') blocking.push({ lang, ...i });
    if (rl.pdf) {
      const pf = runPy('postflight.py', [dir, buildId, lang]);
      const pr = readJson(path.join(qaRoot, lang, 'postflight.json'));
      checks.postflight = pr.status;
      for (const i of pr.items) if (i.severity === 'hard' && i.status !== 'pass') blocking.push({ lang, ...i });
      const rs = runPy('rasterize.py', [dir, buildId, lang]);
      checks.raster = rs.code === 0 ? 'pass' : 'fail';
      if (rs.code !== 0) blocking.push({ lang, id: 'raster', status: 'unverified', severity: 'hard', message: `最终 PDF 栅格化失败，无法视觉审稿：${rs.out.trim()}` });
      void pf;
    } else {
      checks.postflight = 'fail';
      checks.raster = 'fail';
      blocking.push({ lang, id: 'pdf.exists', status: 'fail', severity: 'hard', message: '渲染没有产出 PDF' });
    }
    const cov = await coverageFor(dir, buildId, lang);
    checks.coverage = cov.status;
    for (const i of cov.items) if (i.severity === 'hard' && i.status !== 'pass') blocking.push({ lang, ...i });
    const pdf = path.join(dir, '.build', buildId, lang, 'book.pdf');
    languages[lang] = { checks, pdf: fs.existsSync(pdf) ? path.relative(dir, pdf) : null,
      pdf_sha256: fs.existsSync(pdf) ? sha256(pdf) : null, pages: rl.page_count };
  }
  const gate = { contract: 1, build_id: buildId, fingerprint: r.fingerprint, tools: r.tools, languages,
    status: blocking.length ? 'blocked' : 'deliverable', blocking,
    visual_review: 'not-recorded' };
  fs.writeFileSync(path.join(qaRoot, 'gate.json'), JSON.stringify(gate, null, 2) + '\n');
  const md = [`# 验收 · ${buildId}`, '', `技术状态：**${gate.status === 'deliverable' ? '可交付' : '不可交付'}**（视觉审稿另行记录）`, '',
    '| 语言 | 渲染 | 测量 | PDF 检查 | 栅格 | 原文覆盖 | 页数 |', '|---|---|---|---|---|---|---|',
    ...Object.entries(languages).map(([l, v]) => `| ${l} | ${v.checks.render} | ${v.checks.measure} | ${v.checks.postflight} | ${v.checks.raster} | ${v.checks.coverage} | ${v.pages} |`)];
  if (blocking.length) md.push('', '## 阻止交付的项', '', ...blocking.map((b) => `- [${b.lang}] ${b.status} ${b.id}${b.page ? ` · ${b.page}` : ''}${b.target ? ` · ${b.target}` : ''}：${b.message}`));
  fs.writeFileSync(path.join(qaRoot, 'gate.md'), md.join('\n') + '\n');
  return { ...gate, file: path.relative(dir, path.join(qaRoot, 'gate.json')) };
}

export async function verify(root) {
  const { dir, p } = loadProject(root);
  const { browser, info } = await launch();
  let fp;
  try { fp = fingerprint(dir, p, makeTools(info)); } finally { await browser.close(); }
  const gatePath = path.join(dir, '.qa', fp.buildId, 'gate.json');
  if (!fs.existsSync(gatePath)) {
    return { valid: false, buildId: fp.buildId, reasons: ['当前源没有验收记录：源文件、工具或环境在上次检查后变化过，或从未检查。请运行 check'] };
  }
  const gate = readJson(gatePath);
  const reasons = [];
  if (gate.fingerprint !== fp.fingerprint) reasons.push('验收记录的指纹与当前源不一致');
  for (const lang of p.languages) {
    const g = gate.languages[lang];
    if (!g) { reasons.push(`验收记录里没有 ${lang}`); continue; }
    const pdf = path.join(dir, '.build', fp.buildId, lang, 'book.pdf');
    if (!fs.existsSync(pdf)) reasons.push(`${lang} 的 PDF 不存在`);
    else if (sha256(pdf) !== g.pdf_sha256) reasons.push(`${lang} 的 PDF 在验收后被改动`);
  }
  if (gate.status !== 'deliverable') reasons.push(`验收状态为 ${gate.status}（${gate.blocking.length} 个阻止项）`);
  return { valid: reasons.length === 0, buildId: fp.buildId, reasons, gate };
}
