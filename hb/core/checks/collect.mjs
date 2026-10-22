// 在浏览器里对快照做只读测量（S3）。整个函数会被序列化后在页面中执行，不能引用外部变量。
// 只给元素临时加 data-hbm-i 编号（供 CDP 查字体），不改任何样式。
export function collectInPage(cfg) {
  const { geom, floors, tol } = cfg;
  const items = [];
  const textNodes = [];   // 给对比度、字体检查用
  const add = (o) => items.push(o);
  const r2 = (v) => Math.round(v * 100) / 100;
  const pxToMm = (v) => r2((v * 25.4) / 96);

  const roleOf = (el) => el.closest('[data-role]')?.getAttribute('data-role') || 'body';
  const cssPath = (el) => {
    const parts = [];
    for (let e = el; e && !e.classList?.contains('page'); e = e.parentElement) {
      let s = e.tagName.toLowerCase();
      if (e.classList.length) s += '.' + [...e.classList].slice(0, 2).join('.');
      const sib = e.parentElement ? [...e.parentElement.children].filter((c) => c.tagName === e.tagName) : [];
      if (sib.length > 1) s += `:nth-of-type(${sib.indexOf(e) + 1})`;
      parts.unshift(s);
      if (parts.length >= 3) break;
    }
    return parts.join(' > ');
  };
  const targetOf = (el) => el.closest('[data-source-id]')?.getAttribute('data-source-id')
    || el.closest('[data-edit-id]')?.getAttribute('data-edit-id') || cssPath(el);
  const allowOf = (el) => {
    const set = new Set();
    for (let e = el; e && !e.classList?.contains('page'); e = e.parentElement) {
      (e.getAttribute('data-overlap') || '').split(/\s+/).filter(Boolean).forEach((t) => set.add(t));
    }
    return set;
  };
  const effOpacity = (el) => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  const complexOf = (el) => {
    for (let e = el; e && !e.classList?.contains('page'); e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.transform && cs.transform !== 'none') {
        const m = new DOMMatrixReadOnly(cs.transform);
        if (Math.abs(m.b) > 1e-6 || Math.abs(m.c) > 1e-6) return '旋转/斜切变换';
      }
      if (cs.filter && cs.filter !== 'none') return 'filter';
      const mask = cs.maskImage || cs.webkitMaskImage;
      if (mask && mask !== 'none') return 'mask';
      if (cs.clipPath && cs.clipPath !== 'none') return 'clip-path';
    }
    return null;
  };
  const scaleOf = (el) => {
    const blk = el.closest('*');
    const h = blk.offsetHeight; const r = blk.getBoundingClientRect().height;
    return h > 0 && r > 0 ? r / h : 1;
  };
  const parseColor = (c) => {
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const v = m[1].split(/[ ,/]+/).filter(Boolean).map(Number);
    return { r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1 };
  };
  const inter = (a, b) => {
    const w = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
    const h = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
    return w > 0 && h > 0 ? { w, h, area: w * h } : null;
  };
  const SIDES = ['top', 'right', 'bottom', 'left'];
  const painted = (el, cs) => {
    const tag = el.tagName.toLowerCase();
    if (['img', 'svg', 'video', 'canvas', 'picture'].includes(tag)) return true;
    const bg = parseColor(cs.backgroundColor);
    return (bg && bg.a > 0) || (cs.backgroundImage && cs.backgroundImage !== 'none');
  };

  let nodeIndex = 0;
  const pages = [...document.querySelectorAll('.page')];
  const trim = { x: geom.bleed, y: geom.bleed, w: geom.mediaW - 2 * geom.bleed, h: geom.mediaH - 2 * geom.bleed };
  const safe = { x: geom.bleed + geom.safe.left, y: geom.bleed + geom.safe.top,
    w: geom.mediaW - 2 * geom.bleed - geom.safe.left - geom.safe.right, h: geom.mediaH - 2 * geom.bleed - geom.safe.top - geom.safe.bottom };
  const media = { x: 0, y: 0, w: geom.mediaW, h: geom.mediaH };

  pages.forEach((pg, pi) => {
    const P = pg.getBoundingClientRect();
    const pageId = pg.getAttribute('data-page-id');
    const rel = (r) => ({ x: r.left - P.left, y: r.top - P.top, w: r.width, h: r.height });
    const units = new Map();      // 文字单元：内容节点或直接含字的元素
    const contentVisible = new Map();

    // ---- 文字
    const walker = document.createTreeWalker(pg, NodeFilter.SHOW_TEXT);
    for (let t = walker.nextNode(); t; t = walker.nextNode()) {
      if (!t.textContent.trim()) continue;
      const el = t.parentElement;
      if (el.closest('svg')) continue;              // SVG 文字另行处理
      const content = el.closest('[data-source-id]');
      if (content && !contentVisible.has(content)) contentVisible.set(content, false);
      const role = roleOf(el);
      const cs = getComputedStyle(el);
      const range = document.createRange();
      range.selectNodeContents(t);
      const rects = [...range.getClientRects()].filter((r) => r.width > 0.1 && r.height > 0.1).map(rel);
      const color = parseColor(cs.color);
      const fill = parseColor(cs.webkitTextFillColor || cs.color);
      const opacity = effOpacity(el);
      const px = parseFloat(cs.fontSize) * scaleOf(el);
      const hidden = !rects.length || cs.visibility !== 'visible' || opacity < 0.02 || px < 1 ||
        ((fill ? fill.a : 1) === 0 && cs.backgroundClip !== 'text' && (cs.webkitBackgroundClip || '') !== 'text');
      if (hidden) continue;
      // 完全在页面外的文字也算没有展示
      const onPage = rects.some((r) => inter(r, media));
      if (content && onPage) contentVisible.set(content, true);
      const owner = content || el;
      if (!units.has(owner)) {
        units.set(owner, { el: owner, target: targetOf(owner), role: roleOf(owner), rects: [], allow: allowOf(owner),
          complex: complexOf(owner), minPx: Infinity, sample: '' });
      }
      const u = units.get(owner);
      u.rects.push(...rects);
      u.sample = (u.sample + t.textContent.trim()).slice(0, 40);
      const tag = el.tagName.toLowerCase();
      const floorRole = (tag === 'sup' || tag === 'sub' || el.closest('sup,sub')) ? 'aux' : (role === 'display' ? 'body' : role);
      if (role !== 'deco') {
        const minPx = floors[`${floorRole}_px`];
        if (px + 0.01 < minPx) u.small = { px: r2(px), min: minPx, role: floorRole };
        if (!el.hasAttribute('data-hbm-i')) el.setAttribute('data-hbm-i', String(nodeIndex++));
        textNodes.push({ page: pi, pageId, i: Number(el.getAttribute('data-hbm-i')), target: u.target, role,
          rects, color: fill && fill.a > 0 ? fill : color, opacity,
          gradientText: cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text',
          complex: u.complex, text: t.textContent });
      }
    }

    // ---- 伪元素文字（页码等）：只查字号
    for (const el of pg.querySelectorAll('*')) {
      for (const pseudo of ['::before', '::after']) {
        const pcs = getComputedStyle(el, pseudo);
        const c = pcs.content;
        if (!c || c === 'none' || c === 'normal' || c === '""' || c === "''") continue;
        if (!/counter|attr|[^\s"']/.test(c.replace(/^["']|["']$/g, ''))) continue;
        const role = roleOf(el);
        if (role === 'deco') continue;
        const px = parseFloat(pcs.fontSize) * scaleOf(el);
        const minPx = floors[`${role === 'display' ? 'body' : role}_px`];
        const target = cssPath(el) + pseudo;
        if (px + 0.01 < minPx) {
          add({ id: 'readability.size', status: 'fail', severity: 'hard', page: pageId, target,
            evidence: { font_px: r2(px), min_px: minPx, role }, message: `${pseudo} 生成的文字 ${r2(px)}px 低于 ${role} 下限 ${minPx}px` });
        }
        // 位置：伪元素没有可测矩形。非绝对定位时它排在宿主元素内，用宿主的盒子近似；绝对定位时交给目检。
        if (['absolute', 'fixed'].includes(pcs.position)) {
          add({ id: 'geometry.unverified', status: 'unverified', severity: 'hint', page: pageId, target,
            evidence: { reason: 'positioned pseudo-element' }, message: `${pseudo} 绝对定位的生成文字，位置无法自动核对，请目检` });
        } else {
          const R = rel(el.getBoundingClientRect());
          if (R.w > 0 && R.h > 0) {
            const over = Math.max(media.x - R.x, media.y - R.y, R.x + R.w - (media.x + media.w), R.y + R.h - (media.y + media.h));
            const d = { top: safe.y - R.y, left: safe.x - R.x, right: R.x + R.w - (safe.x + safe.w), bottom: R.y + R.h - (safe.y + safe.h) };
            const side = SIDES.reduce((m, k) => (d[k] > d[m] ? k : m), 'top');
            if (over > tol) {
              add({ id: 'overflow.page', status: 'fail', severity: 'hard', page: pageId, target,
                evidence: { overshoot_mm: pxToMm(over) }, message: `${pseudo} 生成的文字超出页面 ${pxToMm(over)}mm` });
            } else if (d[side] > tol) {
              add({ id: 'overflow.safe', status: 'fail', severity: 'hard', page: pageId, target,
                evidence: { overshoot_mm: pxToMm(d[side]), side }, message: `${pseudo} 生成的文字（如页码）越出印刷安全区（${side}）${pxToMm(d[side])}mm` });
            }
          }
        }
      }
    }

    // ---- 单元级检查
    const list = [...units.values()].filter((u) => u.role !== 'deco');
    for (const u of list) {
      if (u.small) {
        add({ id: 'readability.size', status: 'fail', severity: 'hard', page: pageId, target: u.target,
          evidence: { font_px: u.small.px, min_px: u.small.min, role: u.small.role, text: u.sample },
          message: `${u.small.role} 文字 ${u.small.px}px 低于下限 ${u.small.min}px：「${u.sample}」` });
      }
      if (u.complex) {
        add({ id: 'geometry.unverified', status: 'unverified', severity: 'hint', page: pageId, target: u.target,
          evidence: { reason: u.complex }, message: `${u.complex}：溢出、遮挡与裁切无法可靠自动判断，请在 PDF 上目检` });
        continue;
      }
      // 出页面
      let over = 0;
      for (const r of u.rects) over = Math.max(over, media.x - r.x, media.y - r.y, r.x + r.w - (media.x + media.w), r.y + r.h - (media.y + media.h));
      if (over > tol) {
        add({ id: 'overflow.page', status: 'fail', severity: 'hard', page: pageId, target: u.target,
          evidence: { overshoot_mm: pxToMm(over), text: u.sample }, message: `文字超出页面 ${pxToMm(over)}mm，被裁掉：「${u.sample}」` });
        continue;
      }
      // 出安全区
      let out = 0; let side = '';
      for (const r of u.rects) {
        const d = { top: safe.y - r.y, left: safe.x - r.x, right: r.x + r.w - (safe.x + safe.w), bottom: r.y + r.h - (safe.y + safe.h) };
        for (const s of SIDES) if (d[s] > out) { out = d[s]; side = s; }
      }
      if (out > tol) {
        add({ id: 'overflow.safe', status: 'fail', severity: 'hard', page: pageId, target: u.target,
          evidence: { overshoot_mm: pxToMm(out), side, text: u.sample },
          message: `文字越出印刷安全区（${side}）${pxToMm(out)}mm：「${u.sample}」` });
      }
      // 被祖先容器裁切
      let clipped = null;
      for (let a = u.el; a && a !== pg; a = a.parentElement) {   // 内容节点自身也可能 overflow:hidden
        const cs = getComputedStyle(a);
        const ox = cs.overflowX; const oy = cs.overflowY;
        if (ox === 'visible' && oy === 'visible') continue;
        const ar = rel(a.getBoundingClientRect());
        const box = { x: ar.x + a.clientLeft, y: ar.y + a.clientTop, w: a.clientWidth, h: a.clientHeight };
        for (const r of u.rects) {
          const d = Math.max(ox !== 'visible' ? box.x - r.x : 0, ox !== 'visible' ? r.x + r.w - (box.x + box.w) : 0,
            oy !== 'visible' ? box.y - r.y : 0, oy !== 'visible' ? r.y + r.h - (box.y + box.h) : 0);
          if (d > tol) { clipped = { d, by: cssPath(a) }; break; }
        }
        if (clipped) break;
      }
      if (clipped) {
        add({ id: 'clip.text', status: 'fail', severity: 'hard', page: pageId, target: u.target,
          evidence: { clipped_mm: pxToMm(clipped.d), container: clipped.by, text: u.sample },
          message: `文字被容器 ${clipped.by} 裁掉 ${pxToMm(clipped.d)}mm：「${u.sample}」` });
      }
    }
    // 文字互相遮挡
    for (let i = 0; i < list.length; i++) {
      for (let j = i + 1; j < list.length; j++) {
        const a = list[i]; const b = list[j];
        if (a.complex || b.complex || a.el.contains(b.el) || b.el.contains(a.el)) continue;
        if (a.allow.has(b.target) || b.allow.has(a.target)) continue;
        let hit = null;
        for (const ra of a.rects) { for (const rb of b.rects) { const x = inter(ra, rb); if (x && x.area > 2 && Math.min(x.w, x.h) > 1) { hit = x; break; } } if (hit) break; }
        if (hit) {
          add({ id: 'overlap.text', status: 'fail', severity: 'hard', page: pageId, target: a.target,
            evidence: { with: b.target, overlap_mm: [pxToMm(hit.w), pxToMm(hit.h)] },
            message: `文字「${a.sample}」与「${b.sample}」重叠（有意叠放请在其中一方写 data-overlap="${b.target}"）` });
        }
      }
    }

    // ---- 图片与色块：清晰度、出血、遮挡
    for (const el of pg.querySelectorAll('*')) {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility !== 'visible') continue;
      const R = rel(el.getBoundingClientRect());
      if (R.w <= 0 || R.h <= 0) continue;
      const deco = roleOf(el) === 'deco';
      const tag = el.tagName.toLowerCase();
      const target = targetOf(el);

      if (tag === 'img' && inter(R, media)) {
        const nw = el.naturalWidth; const nh = el.naturalHeight;
        const src = el.getAttribute('src') || '';
        if (nw && nh && !/\.svg(\?|#|$)/i.test(src)) {
          const fit = cs.objectFit;
          let dpi; let visible = 1;
          if (fit === 'cover') { const s = Math.max(R.w / nw, R.h / nh); dpi = 96 / s; visible = Math.min(1, (R.w / s) / nw) * Math.min(1, (R.h / s) / nh); }
          else if (fit === 'contain' || fit === 'scale-down') { const s = Math.min(R.w / nw, R.h / nh, fit === 'scale-down' ? 1 : Infinity); dpi = 96 / s; }
          else if (fit === 'none') { dpi = 96; }
          else { dpi = Math.min((96 * nw) / R.w, (96 * nh) / R.h); }
          const ev = { dpi: Math.round(dpi), natural_px: [nw, nh], display_mm: [pxToMm(R.w), pxToMm(R.h)], fit, visible_fraction: r2(visible), src };
          if (dpi < 150) {
            add({ id: 'image.dpi', status: 'fail', severity: deco ? 'hint' : 'hard', page: pageId, target, evidence: ev,
              message: `图片有效分辨率 ${Math.round(dpi)}dpi，低于 150dpi：${src}` });
          } else {
            add({ id: 'image.info', status: 'pass', severity: 'hint', page: pageId, target, evidence: ev, message: `图片 ${Math.round(dpi)}dpi` });
          }
        }
        // 文字压在非装饰图片上
        if (!deco) {
          for (const u of list) {
            if (u.complex || u.allow.has(target) || u.el.contains(el)) continue;
            const x = u.rects.map((r) => inter(r, R)).find((v) => v && v.area > 2);
            if (x) {
              add({ id: 'overlap.image', status: 'fail', severity: 'hard', page: pageId, target: u.target,
                evidence: { image: target }, message: `文字「${u.sample}」压在图片 ${target} 上（有意叠放请写 data-overlap="${target}"）` });
            }
          }
        }
      }
      if (!deco && cs.backgroundImage && /url\(/.test(cs.backgroundImage) && !/\.svg/i.test(cs.backgroundImage)) {
        add({ id: 'image.background', status: 'unverified', severity: 'hint', page: pageId, target,
          evidence: { background: cs.backgroundImage.slice(0, 120) }, message: 'CSS 背景图的分辨率未自动检查，请确认 ≥ 150dpi' });
      }

      // 出血：越过成品边的着色元素
      if (el === pg || !painted(el, cs)) continue;
      const cross = { top: trim.y - R.y, left: trim.x - R.x, right: R.x + R.w - (trim.x + trim.w), bottom: R.y + R.h - (trim.y + trim.h) };
      const reach = { top: media.y - R.y, left: media.x - R.x, right: R.x + R.w - (media.x + media.w), bottom: R.y + R.h - (media.y + media.h) };
      const declared = (el.getAttribute('data-bleed') || '').split(/\s+/);
      for (const s of SIDES) {
        if (cross[s] <= tol) continue;
        const ok = declared.includes('all') || declared.includes(s);
        if (ok && geom.bleed > 0 && reach[s] < -tol) {
          add({ id: 'image.bleed', status: 'fail', severity: 'hard', page: pageId, target,
            evidence: { side: s, short_mm: pxToMm(-reach[s]) }, message: `${target} 在 ${s} 侧出血不足，离媒体边还差 ${pxToMm(-reach[s])}mm，裁切后可能露白` });
        } else if (!ok) {
          add({ id: 'image.bleed', status: 'fail', severity: deco ? 'hint' : 'hard', page: pageId, target,
            evidence: { side: s, beyond_trim_mm: pxToMm(cross[s]) },
            message: `${target} 越过成品边（${s}）${pxToMm(cross[s])}mm 但没有声明 data-bleed` });
        }
      }
    }

    // ---- 内容节点没有展示出来
    for (const [el, vis] of contentVisible) {
      if (vis) continue;
      const repeat = el.hasAttribute('data-repeat');
      add({ id: 'content.hidden', status: 'fail', severity: repeat ? 'hint' : 'hard', page: pageId, target: el.getAttribute('data-source-id'),
        evidence: { repeat }, message: `内容 ${el.getAttribute('data-source-id')} 在页面上不可见（隐藏、透明、页外或字号过小）` });
    }
    // 没有任何文字的内容节点（display:none 时文本节点存在但无矩形，在上面已计入）
    for (const el of pg.querySelectorAll('[data-source-id]')) {
      if (!contentVisible.has(el) && el.textContent.trim()) {
        add({ id: 'content.hidden', status: 'fail', severity: el.hasAttribute('data-repeat') ? 'hint' : 'hard', page: pageId,
          target: el.getAttribute('data-source-id'), evidence: {}, message: `内容 ${el.getAttribute('data-source-id')} 在页面上不可见` });
      }
    }
    // SVG 内文字
    for (const t of pg.querySelectorAll('svg text')) {
      if (roleOf(t) === 'deco' || !t.textContent.trim()) continue;
      add({ id: 'readability.svg', status: 'unverified', severity: 'hint', page: pageId, target: targetOf(t),
        evidence: { text: t.textContent.trim().slice(0, 30) }, message: 'SVG 内文字的字号与位置未自动检查，请目检' });
    }
  });

  return { items, textNodes, pageIds: pages.map((p) => p.getAttribute('data-page-id')) };
}

// 对比度：给定每页“隐藏文字后”的截图，在文字矩形内采样背景，计算第 5 百分位对比度。
export async function contrastInPage({ shots, textNodes, floors }) {
  const lum = (r, g, b) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const out = [];
  const bitmaps = {};
  for (const [pi, b64] of Object.entries(shots)) {
    const blob = await (await fetch(`data:image/png;base64,${b64}`)).blob();
    const bmp = await createImageBitmap(blob);
    const cv = new OffscreenCanvas(bmp.width, bmp.height);
    const ctx = cv.getContext('2d');
    ctx.drawImage(bmp, 0, 0);
    bitmaps[pi] = { w: bmp.width, h: bmp.height, data: ctx.getImageData(0, 0, bmp.width, bmp.height).data };
  }
  for (const tn of textNodes) {
    const bm = bitmaps[tn.page];
    if (!bm) continue;
    if (tn.gradientText || tn.complex) { out.push({ tn, unverified: tn.gradientText ? '渐变/背景裁切文字' : tn.complex }); continue; }
    const fg = tn.color; const a = (fg?.a ?? 1) * tn.opacity;
    const ratios = [];
    for (const r of tn.rects) {
      const x0 = Math.max(0, Math.floor(r.x)); const y0 = Math.max(0, Math.floor(r.y));
      const x1 = Math.min(bm.w, Math.ceil(r.x + r.w)); const y1 = Math.min(bm.h, Math.ceil(r.y + r.h));
      const step = Math.max(1, Math.floor(Math.min(x1 - x0, y1 - y0) / 12));
      for (let y = y0; y < y1; y += step) {
        for (let x = x0; x < x1; x += step) {
          const k = (y * bm.w + x) * 4;
          const br = bm.data[k]; const bg = bm.data[k + 1]; const bb = bm.data[k + 2];
          const cr = a * fg.r + (1 - a) * br; const cg = a * fg.g + (1 - a) * bg; const cb = a * fg.b + (1 - a) * bb;
          const l1 = lum(cr, cg, cb); const l2 = lum(br, bg, bb);
          ratios.push((Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05));
        }
      }
    }
    if (!ratios.length) continue;
    ratios.sort((x, y) => x - y);
    const p05 = ratios[Math.floor(ratios.length * 0.05)];
    const role = tn.role === 'display' ? 'display' : tn.role;
    out.push({ tn, p05, min: ratios[0], median: ratios[Math.floor(ratios.length / 2)], floor: floors[`${role}_contrast`] });
  }
  return out.map((o) => ({ page: o.tn.pageId, target: o.tn.target, role: o.tn.role, text: o.tn.text.trim().slice(0, 30),
    unverified: o.unverified || null, p05: o.p05, min: o.min, median: o.median, floor: o.floor }));
}
