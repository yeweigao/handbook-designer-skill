// Folio 编辑包（S9）：node hb/core/cli.mjs folio-pack <项目> [--lang <语言>] [--name <文件名>]
// 用当前源对应的构建（没有就先渲染）生成离线单文件 HTML，加上构建标记（hb-build / hb-lang / hb-title），
// 写到 out/folio/<名>.<语言>.folio.html；同时把同一份文件存为 .build/<构建 ID>/<语言>/folio-base.html，供写回时三方比对。
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { loadProject } from './project.mjs';
import { launch } from './browser.mjs';
import { fingerprint, makeTools } from './fingerprint.mjs';
import { render } from './render.mjs';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');

export async function folioPack(root, opts = {}) {
  const { dir, p } = loadProject(root);
  const { browser, info } = await launch();
  let buildId;
  try { buildId = fingerprint(dir, p, makeTools(info)).buildId; } finally { await browser.close(); }
  const langs = opts.langs?.length ? opts.langs : p.languages;
  if (langs.some((l) => !fs.existsSync(path.join(dir, '.build', buildId, l, 'snapshot.html')))) {
    const r = await render(dir, { langs });
    if (r.status !== 'pass') throw new Error('当前源渲染失败，不能导出编辑包：先修复后运行 check');
    buildId = r.build_id;
  }
  const name = (opts.name || p.title).replace(/[\\/:*?"<>|\s]+/g, '-');
  const outDir = path.join(dir, 'out', 'folio');
  fs.mkdirSync(outDir, { recursive: true });
  const files = [];
  for (const lang of langs) {
    const base = path.join(dir, '.build', buildId, lang, 'folio-base.html');
    const r = spawnSync('python3', [path.join(HERE, 'offline_html.py'), dir, path.join(dir, '.build', buildId, lang, 'snapshot.html'), base], { encoding: 'utf8' });
    if (r.status !== 0) throw new Error(r.stderr.trim());
    const meta = `<meta name="hb-contract" content="1"><meta name="hb-build" content="${buildId}"><meta name="hb-lang" content="${esc(lang)}"><meta name="hb-title" content="${esc(p.title)}">`;
    const html = fs.readFileSync(base, 'utf8').replace(/<head\b[^>]*>/i, (m) => m + meta);
    fs.writeFileSync(base, html);
    const out = path.join(outDir, `${name}.${lang}.folio.html`);
    fs.copyFileSync(base, out);
    files.push(path.relative(dir, out));
  }
  return { buildId, files };
}
