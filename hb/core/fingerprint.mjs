// 输入指纹（契约 §6）：项目内所有被引用文件的内容哈希 + 工具版本。构建 ID = 指纹前 12 位。
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const sha256 = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
const SKIP = /^(#|data:|https?:|\/\/|mailto:|tel:|javascript:)/i;
const HTML_REF = /\s(?:src|href|poster|xlink:href)\s*=\s*(?:"([^"]*)"|'([^']*)')/gi;
const SRCSET = /\ssrcset\s*=\s*(?:"([^"]*)"|'([^']*)')/gi;
const CSS_URL = /url\(\s*(['"]?)(.*?)\1\s*\)/gi;
const CSS_IMPORT = /@import\s+(?:url\(\s*)?(['"])(.*?)\1/gi;

export function collectInputs(dir, p) {
  const files = new Set();
  const rel = (abs) => path.relative(dir, abs).split(path.sep).join('/');
  const add = (abs) => {
    if (!fs.existsSync(abs) || !fs.statSync(abs).isFile()) return false;
    const r = rel(abs);
    if (r.startsWith('..')) return false;
    if (files.has(r)) return false;
    files.add(r);
    return true;
  };
  const resolveRef = (baseDir, ref) => {
    ref = (ref || '').trim();
    if (!ref || SKIP.test(ref)) return null;
    return path.resolve(baseDir, ref.split('#')[0].split('?')[0]);
  };
  const scanCss = (abs) => {
    if (!add(abs)) return;
    const css = fs.readFileSync(abs, 'utf8').replace(/\/\*[\s\S]*?\*\//g, '');
    const base = path.dirname(abs);
    for (const m of css.matchAll(CSS_IMPORT)) { const f = resolveRef(base, m[2]); if (f) scanCss(f); }
    for (const m of css.matchAll(CSS_URL)) { const f = resolveRef(base, m[2]); if (f) add(f); }
  };
  const scanHtml = (abs) => {
    if (!add(abs)) return;
    const html = fs.readFileSync(abs, 'utf8');
    const base = path.dirname(abs);
    for (const m of html.matchAll(HTML_REF)) { const f = resolveRef(base, m[1] ?? m[2]); if (f) add(f); }
    for (const m of html.matchAll(SRCSET)) {
      for (const part of (m[1] ?? m[2]).split(',')) { const f = resolveRef(base, part.trim().split(/\s+/)[0]); if (f) add(f); }
    }
    for (const m of html.matchAll(CSS_URL)) { const f = resolveRef(base, m[2]); if (f) add(f); }
  };

  add(path.join(dir, 'project.json'));
  scanHtml(path.join(dir, p.entry));
  for (const s of p.styles) scanCss(path.join(dir, s));
  for (const f of p.fonts) add(path.join(dir, f.file));
  for (const lang of p.languages) {
    if (lang !== p.default_language) add(path.join(dir, 'copy', `${lang}.json`));
    scanCss(path.join(dir, 'lang', `${lang}.css`));
  }
  scanCss(path.join(dir, 'edits.css'));
  return [...files].sort().map((r) => ({ path: r, sha256: sha256(fs.readFileSync(path.join(dir, r))) }));
}

export function toolHash() {
  const names = fs.readdirSync(HERE).filter((f) => /\.(mjs|py)$/.test(f)).sort();
  const h = crypto.createHash('sha256');
  for (const f of names) h.update(f).update('\0').update(fs.readFileSync(path.join(HERE, f))).update('\0');
  return h.digest('hex');
}

export function fingerprint(dir, p, tools) {
  const inputs = collectInputs(dir, p);
  const canonical = JSON.stringify({ contract: 1, inputs: inputs.map((i) => [i.path, i.sha256]), tools });
  const fp = sha256(canonical);
  return { fingerprint: fp, buildId: fp.slice(0, 12), inputs };
}

export const fileSha256 = (file) => sha256(fs.readFileSync(file));
