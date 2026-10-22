// 由 project.json 生成唯一的打印 CSS 与字体 CSS（契约 §2）。作者 CSS 不得再声明 @page / @font-face。
const n = (v) => Number(v.toFixed(4)).toString();

export function printCss({ geom }) {
  const { trimW, trimH, bleed, mediaW, mediaH, safe } = geom;
  const inset = (s) => n(bleed + s);
  return `/* 由 hb/core/print-css.mjs 生成，勿手改 */
@page { size: ${n(mediaW)}mm ${n(mediaH)}mm; margin: 0; }
:root {
  --trim-w: ${n(trimW)}mm; --trim-h: ${n(trimH)}mm; --bleed: ${n(bleed)}mm;
  --media-w: ${n(mediaW)}mm; --media-h: ${n(mediaH)}mm;
  --safe-top: ${n(safe.top)}mm; --safe-right: ${n(safe.right)}mm; --safe-bottom: ${n(safe.bottom)}mm; --safe-left: ${n(safe.left)}mm;
  --inset-top: ${inset(safe.top)}mm; --inset-right: ${inset(safe.right)}mm; --inset-bottom: ${inset(safe.bottom)}mm; --inset-left: ${inset(safe.left)}mm;
}
html, body { margin: 0; padding: 0; }
body { counter-reset: page-n; }
.page { position: relative; box-sizing: border-box; width: var(--media-w); height: var(--media-h); overflow: hidden;
        break-after: page; break-inside: avoid; counter-increment: page-n; }
.page:last-child { break-after: auto; }
@media screen {
  body { display: flex; flex-direction: column; align-items: center; gap: 24px; padding: 24px 0; }
}
`;
}

const FORMAT = { '.ttf': 'truetype', '.otf': 'opentype', '.woff': 'woff', '.woff2': 'woff2' };

export function fontCss({ p }) {
  return p.fonts.map((f) => {
    const ext = f.file.slice(f.file.lastIndexOf('.')).toLowerCase();
    return `@font-face { font-family: ${JSON.stringify(f.family)}; src: url(${JSON.stringify(f.file)}) format("${FORMAT[ext]}"); ` +
      `font-weight: ${f.weight || '400'}; font-style: ${f.style || 'normal'}; font-display: block; }`;
  }).join('\n') + '\n';
}
