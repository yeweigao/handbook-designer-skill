// 续排（S6）：在浏览器里把 data-flow 内容流按实际排版分配到各个文字框。整个函数被序列化后在页面中执行。
// 只移动内容（整块移动或在句子边界拆分），不改字号、行距、间距，不删内容。
// 默认语言由 paginate 写回作者源；其他语言在渲染时对注入译文后的 DOM 运行。
export function flowInPage(opts) {
  const report = { flows: [], errors: [], hints: [] };
  const KEEP_NEXT = (el) => /^H[1-6]$/.test(el.tagName) || el.getAttribute('data-flow-keep') === 'next';
  const SPLITTABLE = (el) => el.hasAttribute('data-source-id') && !el.querySelector('img,svg,table,figure,ul,ol') &&
    ['P', 'DIV', 'BLOCKQUOTE', 'LI', 'DD'].includes(el.tagName);
  const lineHeight = (el) => { const cs = getComputedStyle(el); const lh = parseFloat(cs.lineHeight); return Number.isFinite(lh) ? lh : parseFloat(cs.fontSize) * 1.2; };
  const lines = (el) => Math.round(el.getBoundingClientRect().height / lineHeight(el));
  const fits = (frame) => frame.scrollHeight <= frame.clientHeight + 0.5 && frame.scrollWidth <= frame.clientWidth + 0.5;
  const pageOf = (el) => el.closest('.page');

  // 先把同一内容节点的连续片段合并回整段
  function mergeFragments(root) {
    const els = [...root.querySelectorAll('[data-fragment]')];
    const groups = new Map();
    for (const el of els) {
      const id = el.getAttribute('data-source-id');
      if (!groups.has(id)) groups.set(id, []);
      groups.get(id).push(el);
    }
    for (const list of groups.values()) {
      list.sort((a, b) => Number(a.getAttribute('data-fragment')) - Number(b.getAttribute('data-fragment')));
      const [first, ...rest] = list;
      for (const r of rest) { first.innerHTML += r.innerHTML; r.remove(); }
      first.removeAttribute('data-fragment');
    }
  }
  if (opts.mergeOnly) { mergeFragments(document.body); return report; }

  // 拆分候选（按纯文字偏移计算，行内标记由 Range 保留）：
  //   sentence：句末；line：可断行处（中日韩字之间、空格后），遵守避头尾。
  const CJK = /[　-鿿豈-﫿＀-￯]/;
  const NO_START = /[，。、；：！？）」』”’》〉…·%,.;:!?)\]}]/;
  const NO_END = /[（「『“‘《〈([{]/;
  function boundaries(el, mode) {
    const text = el.textContent;
    const out = [];
    if (mode === 'sentence') {
      const re = /[。！？；!?;](?=[^”’」』）)]|$)|[。！？!?][”’」』）)]|[.!?][”’)]?\s+/g;
      for (const m of text.matchAll(re)) { const end = m.index + m[0].length; if (end > 0 && end < text.length) out.push(end); }
      return out;
    }
    for (let i = 1; i < text.length; i++) {
      const a = text[i - 1]; const b = text[i];
      const breakable = /\s/.test(a) || (CJK.test(a) && CJK.test(b)) || (CJK.test(a) && /\S/.test(b) && !/[A-Za-z0-9]/.test(b)) || (CJK.test(b) && !/[A-Za-z0-9]/.test(a));
      if (breakable && !NO_START.test(b) && !NO_END.test(a)) out.push(i);
    }
    return out;
  }
  function rangeAt(el, offset) {
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let acc = 0;
    for (let t = w.nextNode(); t; t = w.nextNode()) {
      if (acc + t.data.length >= offset) return { node: t, off: offset - acc };
      acc += t.data.length;
    }
    return null;
  }
  function splitAt(el, offset) {
    const pos = rangeAt(el, offset);
    const r1 = document.createRange(); r1.setStart(el, 0); r1.setEnd(pos.node, pos.off);
    const r2 = document.createRange(); r2.setStart(pos.node, pos.off); r2.setEnd(el, el.childNodes.length);
    const head = el.cloneNode(false); head.appendChild(r1.cloneContents());
    const tail = el.cloneNode(false); tail.appendChild(r2.cloneContents());
    const first = tail.firstChild;
    if (first && first.nodeType === 3) first.data = first.data.replace(/^\s+/, '');
    return [head, tail];
  }
  // 在候选中二分找“放进框后仍不溢出、且至少 minHead 行”的最长头部，返回候选下标或 null
  function search(el, frame, cands, minHead) {
    let best = null; let lo = 0; let hi = cands.length - 1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      const [head] = splitAt(el, cands[mid]);
      frame.appendChild(head);
      const ok = fits(frame) && lines(head) >= minHead;
      frame.removeChild(head);
      if (ok) { best = mid; lo = mid + 1; } else hi = mid - 1;
    }
    return best;
  }
  const tailLines = (el, frame, off) => { const [, tail] = splitAt(el, off); frame.appendChild(tail); const l = lines(tail); frame.removeChild(tail); return l; };
  const leftover = (el, frame, off) => {
    const [head] = splitAt(el, off); frame.appendChild(head);
    const left = frame.getBoundingClientRect().bottom - head.getBoundingClientRect().bottom;
    frame.removeChild(head); return left;
  };
  // 返回 { parts: [head, tail], mode } 或 null。优先句末；句末拆完框底仍空出一行以上时改在行尾拆。
  function trySplit(el, frame, force, total) {
    if (force) {
      const cands = boundaries(el, 'line');
      const idx = search(el, frame, cands.length ? cands : [...el.textContent].map((_, i) => i).slice(1), 1);
      return idx === null ? null : { parts: splitAt(el, (cands.length ? cands : [...el.textContent].map((_, i) => i).slice(1))[idx]), mode: 'forced' };
    }
    if (total < 4) return null;   // 首尾各至少两行
    let sentence = null;
    for (const mode of ['sentence', 'line']) {
      const cands = boundaries(el, mode);
      let idx = search(el, frame, cands, 2);
      while (idx !== null && idx >= 0 && tailLines(el, frame, cands[idx]) < 2) idx--;
      if (idx === null || idx < 0) continue;
      if (mode === 'sentence') {
        if (leftover(el, frame, cands[idx]) <= lineHeight(el) + 0.5) return { parts: splitAt(el, cands[idx]), mode };
        sentence = cands[idx];
        continue;
      }
      const off = Math.max(cands[idx], sentence ?? 0);
      return { parts: splitAt(el, off), mode: off === sentence ? 'sentence' : 'line' };
    }
    return sentence === null ? null : { parts: splitAt(el, sentence), mode: 'sentence' };
  }

  const names = [];
  for (const f of document.querySelectorAll('[data-flow]')) {
    const n = f.getAttribute('data-flow');
    if (!names.includes(n) && (!opts.flow || opts.flow === n)) names.push(n);
  }
  for (const name of names) {
    const info = { flow: name, frames: 0, added_pages: [], removed_pages: [], fragments: {}, forced: [], splits: { sentence: 0, line: 0 } };
    const allFrames = () => [...document.querySelectorAll(`[data-flow="${CSS.escape(name)}"]`)];
    // 收集内容块，去掉之前生成的续页
    const blocks = [];
    for (const f of allFrames()) for (const c of [...f.children]) { blocks.push(c); c.remove(); }
    for (const pg of [...document.querySelectorAll(`.page[data-flow-generated="${CSS.escape(name)}"]`)]) {
      info.removed_pages.push(pg.getAttribute('data-page-id'));
      pg.remove();
    }
    const holder = document.createElement('div');
    blocks.forEach((b) => holder.appendChild(b));
    mergeFragments(holder);
    const queue = [...holder.children];
    const frames = allFrames();
    if (!frames.length) continue;
    const template = pageOf(frames[frames.length - 1]);
    let lastPage = template;
    let counter = 2;
    const makeContinuation = () => {
      const clone = template.cloneNode(true);
      while (document.querySelector(`.page[data-page-id="${template.getAttribute('data-page-id')}-c${counter}"]`)) counter++;
      const id = `${template.getAttribute('data-page-id')}-c${counter++}`;
      clone.setAttribute('data-page-id', id);
      clone.setAttribute('data-flow-generated', name);
      clone.removeAttribute('data-spread');
      clone.querySelectorAll('[data-flow]').forEach((f) => { if (f.getAttribute('data-flow') !== name) f.remove(); });
      clone.querySelectorAll('[data-source-id]:not([data-repeat]), [data-edit-id]').forEach((e) => e.remove());
      const fr = [...clone.querySelectorAll(`[data-flow="${CSS.escape(name)}"]`)];
      fr.forEach((f) => { f.innerHTML = ''; });
      lastPage.after(clone);
      lastPage = clone;
      info.added_pages.push(id);
      return fr;
    };
    let fi = 0;
    const H0 = new Map();
    while (queue.length) {
      if (fi >= frames.length) {
        if (info.added_pages.length > (opts.maxPages || 200)) { report.errors.push({ code: 'flow.runaway', flow: name, message: `续页超过 ${opts.maxPages || 200} 页，停止` }); break; }
        frames.push(...makeContinuation());
      }
      const frame = frames[fi];
      if (!H0.has(frame)) H0.set(frame, frame.clientHeight);
      let placed = 0;
      while (queue.length) {
        const b = queue[0];
        frame.appendChild(b);
        if (frame.clientHeight > H0.get(frame) + 0.5) {
          report.errors.push({ code: 'flow.unbounded', flow: name, page: pageOf(frame).getAttribute('data-page-id'),
            message: '续排文字框没有固定高度（随内容长高），无法分页：给框设定 height 或 top/bottom' });
          queue.length = 0; break;
        }
        if (fits(frame)) { queue.shift(); placed++; continue; }
        const total = lines(b);   // 必须在移出框之前测量：脱离文档的元素量不到高度
        frame.removeChild(b);
        const sp = SPLITTABLE(b) ? trySplit(b, frame, false, total) : null;
        if (sp) { frame.appendChild(sp.parts[0]); queue[0] = sp.parts[1]; info.splits[sp.mode]++; placed++; }
        else if (placed === 0) {
          // 空框也放不下：可拆的强制按字拆，否则报错并整块放入
          const fsp = SPLITTABLE(b) ? trySplit(b, frame, true, total) : null;
          if (fsp) { frame.appendChild(fsp.parts[0]); queue[0] = fsp.parts[1]; info.forced.push(b.getAttribute('data-source-id')); placed++; }
          else {
            frame.appendChild(b); queue.shift();
            report.errors.push({ code: 'flow.too-large', flow: name, page: pageOf(frame).getAttribute('data-page-id'),
              target: b.getAttribute('data-source-id') || b.getAttribute('data-edit-id') || b.tagName.toLowerCase(),
              message: '内容块比整个文字框还高，无法续排：缩小图片/表格或加大文字框' });
          }
        }
        break;
      }
      // 标题等“随下文”的块不能落在框底
      while (frame.children.length > 1 && KEEP_NEXT(frame.lastElementChild) && queue.length) queue.unshift(frame.lastElementChild), frame.lastElementChild.remove();
      fi++;
    }
    // 没用到的作者文字框：留空提示；没用到的生成页已在开头删除
    for (let k = fi; k < frames.length; k++) {
      if (!frames[k].children.length) report.hints.push({ code: 'flow.empty-frame', flow: name, page: pageOf(frames[k]).getAttribute('data-page-id'), message: '续排文字框为空' });
    }
    info.frames = Math.max(fi, 1);
    // 片段编号
    const seen = new Map();
    for (const f of allFrames()) for (const c of f.children) {
      const id = c.getAttribute('data-source-id');
      if (!id) continue;
      if (!seen.has(id)) seen.set(id, []);
      seen.get(id).push(c);
    }
    for (const [id, list] of seen) {
      if (list.length > 1) {
        list.forEach((c, i) => c.setAttribute('data-fragment', String(i + 1)));
        info.fragments[id] = list.map((c) => lines(c));   // 每个片段的行数（供检查孤行）
      } else list[0].removeAttribute('data-fragment');
    }
    info.frame_tails = [];
    for (const f of allFrames()) if (f.lastElementChild) info.frame_tails.push(f.lastElementChild.tagName.toLowerCase());
    report.flows.push(info);
  }
  // 跨页左右位置是否被插入的续页打乱
  const pages = [...document.querySelectorAll('.page')];
  const firstRight = opts.firstPage !== 'left';
  const groups = new Map();
  pages.forEach((p, i) => { const s = p.getAttribute('data-spread'); if (s) { if (!groups.has(s)) groups.set(s, []); groups.get(s).push(i + 1); } });
  for (const [s, ns] of groups) {
    const leftFirst = firstRight ? ns[0] % 2 === 0 : ns[0] % 2 === 1;
    if (ns.length !== 2 || ns[1] !== ns[0] + 1 || !leftFirst) report.errors.push({ code: 'flow.spread-shift', message: `续页插入后跨页 ${s} 的左右位置错了（第 ${ns.join('、')} 页）：调整续排框或增减页面` });
  }
  report.pages = pages.length;
  return report;
}
