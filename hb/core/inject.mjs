// 多语言文案注入（契约 §4）：白名单行内标记保留，其余一律按文本转义。
// 这里只生成安全的 HTML 片段；在浏览器里按 data-source-id 替换由 render.mjs 完成。
import fs from 'node:fs';
import path from 'node:path';

const TAG = /<(\/?)(em|strong|a|br|sup|sub|span)\b([^<>]*?)(\/?)>/gi;
const ATTR = /([a-zA-Z-]+)\s*=\s*("([^"]*)"|'([^']*)')/g;
const ALLOWED_ATTR = { a: ['href'], span: ['class', 'lang'] };

export const escapeText = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const escapeAttr = (s) => escapeText(s).replace(/"/g, '&quot;');

function cleanTag(close, name, attrs) {
  name = name.toLowerCase();
  if (close) return name === 'br' ? '' : `</${name}>`;
  const keep = [];
  for (const m of attrs.matchAll(ATTR)) {
    const k = m[1].toLowerCase();
    const v = m[3] ?? m[4] ?? '';
    if (!(ALLOWED_ATTR[name] || []).includes(k)) continue;
    if (k === 'href' && /^\s*(javascript|data|vbscript):/i.test(v)) continue;
    keep.push(` ${k}="${escapeAttr(v)}"`);
  }
  return `<${name}${keep.join('')}>`;
}

export function sanitizeInline(str) {
  let out = '';
  let last = 0;
  for (const m of str.matchAll(TAG)) {
    out += escapeText(str.slice(last, m.index));
    out += cleanTag(m[1] === '/', m[2], m[3] || '');
    last = m.index + m[0].length;
  }
  return out + escapeText(str.slice(last));
}

export function loadCopy(dir, lang) {
  const file = path.join(dir, 'copy', `${lang}.json`);
  const c = JSON.parse(fs.readFileSync(file, 'utf8'));
  const out = {};
  for (const [k, v] of Object.entries(c.strings)) out[k] = sanitizeInline(v);
  return out;
}
