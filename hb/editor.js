/* 在线编辑页（edit_page.py 把它嵌进单文件 HTML，作为网页发布）。
   改字：点「改字」后直接在页面上改，离开输入框就保存到共享数据库（db：edits），页面当场重排并跑版面检查（溢出、重叠标红）。
   换图：点「换图」再点一张照片，选新图上传（assets），记到 db：images。
   批注：点「批注」再点任意位置，写评论（comments）。
   Claude 收到“同步修改”后读 db → sync_edits.py 写回 book.yaml（只改这一种语言）→ 重建、检查、重新发布。
   没有共享数据库时（本地打开）：修改留在本页，点「导出修改」下载 edits.json 交给 Claude。 */
(function () {
  const E = window.HB_EDIT; if (!E) return;
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const norm = s => String(s || '').replace(/<[^>]+>/g, '').replace(/[\u200b\s]+/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').toLowerCase();
  const TA = document.createElement('textarea');
  const txt = el => { TA.innerHTML = el.innerHTML.replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, ''); return TA.value.replace(/\u200b/g, ''); };   // 不受 CSS 大写影响；<br> → 换行
  const sid = s => s.replace(/[^A-Za-z0-9]+/g, '_').slice(0, 180);
  let db = null, assets = null, comments = null, user = null, me = '', mode = 'view';
  const local = { edits: {}, images: {} };   // 没有 db 时的本地记录
  // ---------------------------------------------------------------- 工具条
  const css = document.createElement('style');
  css.textContent = `
  #hbx{position:fixed;top:0;left:0;right:0;z-index:99999;display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:8px 16px;
    background:rgba(20,20,24,.94);color:#fff;font:13px/1.4 -apple-system,"PingFang SC","Noto Sans SC",sans-serif;box-shadow:0 2px 12px rgba(0,0,0,.3)}
  #hbx b{font-weight:600;margin-right:6px}#hbx button{font:inherit;color:#fff;background:#3a3a44;border:1px solid #555;border-radius:6px;padding:5px 12px;cursor:pointer}
  #hbx button.on{background:#fff;color:#111;border-color:#fff}#hbx .st{margin-left:auto;opacity:.85}#hbx .bad{color:#ff8a8a}
  body{padding-top:56px!important}
  body.m-edit [data-src]{outline:1px dashed rgba(0,140,255,.55);outline-offset:2px;cursor:text}
  body.m-edit [data-src]:focus{outline:2px solid #08f;background:rgba(0,140,255,.06)}
  body.m-img img[data-file]{outline:3px dashed #f90;outline-offset:-3px;cursor:pointer}
  body.m-note .page *{cursor:crosshair}
  [data-src].hb-changed{box-shadow:inset 0 -2px 0 rgba(255,170,0,.9)}
  .hb-badge{position:absolute;right:8px;top:8px;z-index:9998;background:#e5243b;color:#fff;font:12px/1.4 sans-serif;padding:4px 8px;border-radius:4px;max-width:60%}
  .page.hb-bad{outline:4px solid #e5243b}
  @media print{#hbx,.hb-badge{display:none!important}body{padding-top:0!important}.page.hb-bad{outline:none}[data-src]{outline:none!important;box-shadow:none!important}}`;
  document.head.appendChild(css);
  const bar = document.createElement('div'); bar.id = 'hbx';
  bar.innerHTML = `<b>${E.title} · ${E.lang}</b><button data-m="view">浏览</button><button data-m="edit">改字</button><button data-m="img">换图</button><button data-m="note">批注</button><button id="hbx-dl">导出修改</button><span class="st" id="hbx-st">载入中…</span>`;
  document.body.prepend(bar);
  const st = (t, bad) => { const e = $('#hbx-st'); e.textContent = t; e.className = 'st' + (bad ? ' bad' : ''); };
  function setMode(m) {
    mode = m; document.body.classList.toggle('m-edit', m === 'edit'); document.body.classList.toggle('m-img', m === 'img'); document.body.classList.toggle('m-note', m === 'note');
    $$('#hbx button[data-m]').forEach(b => b.classList.toggle('on', b.dataset.m === m));
    $$('[data-src]').forEach(e => e.contentEditable = m === 'edit' ? 'plaintext-only' : 'false');
  }
  $$('#hbx button[data-m]').forEach(b => b.onclick = () => setMode(b.dataset.m));
  // ---------------------------------------------------------------- 文字 ↔ yaml 字段
  function mapLeaves() {
    const pages = {}; $$('.page').forEach(p => pages[p.dataset.n] = p);
    let hit = 0;
    E.leaves.forEach(L => {
      const cands = [];
      L.pages.forEach(n => { const pg = pages[n]; if (pg) cands.push(...$$('*', pg).filter(e => !e.closest('svg,script,style,.hb-badge') && !e.dataset.src)); });
      const ln = L.norm.toLowerCase(); let best = null, bd = 1e9;
      cands.forEach(e => { if (norm(txt(e)) !== ln) return; const d = e.getElementsByTagName('*').length; if (d < bd) { bd = d; best = e; } });
      if (!best) cands.forEach(e => {   // 引擎加了前缀 / 后缀的（“— 署名”、编号）：只认没有子元素、多出不超过 4 个字的
        if (e.children.length) return; const t = norm(txt(e)); if (t.length > ln.length + 4 || !t.includes(ln)) return; if (!best || t.length < norm(txt(best)).length) best = e; });
      if (best) { best.dataset.src = L.path; best.dataset.old = txt(best); best.dataset.orig = L.text; best.dataset.pre = txt(best).indexOf(L.text) > 0 ? txt(best).slice(0, txt(best).indexOf(L.text)) : ''; hit++; }
    });
    $$('img').forEach(im => { const f = E.imgs[(im.getAttribute('data-name') || '')]; if (f) im.dataset.file = f; });
    return hit;
  }
  function pageOf(e) { const p = e.closest('.page'); return p ? +p.dataset.n : 0; }
  // ---------------------------------------------------------------- 重排 + 检查
  function relayout() {
    $$('[data-fit0]').forEach(e => { e.dataset.fit = e.dataset.fit0; e.removeAttribute('data-cnw'); e.style.fontSize = ''; });
    try { if (typeof canon === 'function') canon(); if (typeof cnQA === 'function') cnQA(); } catch (err) { console.log('[hb] relayout', err); }
    $$('.hb-badge').forEach(b => b.remove()); $$('.page.hb-bad').forEach(p => p.classList.remove('hb-bad'));
    let qa = []; try { qa = JSON.parse(document.body.dataset.cnqa || '[]'); } catch (e) { }
    const KIND = { 'cn-over': '文字超出版心', 'cn-in': '标题超出色块', 'cn-collide': '文字互相压住', 'cn-row': '条目放不下', 'cn-small': '图片被挤太小', 'cn-fit': '标题太长', 'cn-deco': '大字压到文字' };
    const pagesEl = $$('.page'); const byPg = {};
    qa.forEach(([pg, k, px, t]) => (byPg[pg] = byPg[pg] || []).push(`${KIND[k] || k}${px ? ' ' + px + 'px' : ''}`));
    Object.entries(byPg).forEach(([pg, xs]) => { const p = pagesEl[pg - 1]; if (!p) return; p.classList.add('hb-bad'); const b = document.createElement('div'); b.className = 'hb-badge'; b.textContent = `第${p.dataset.n}页：${xs.join('；')} → 缩短文字`; p.appendChild(b); });
    return Object.keys(byPg).length;
  }
  // ---------------------------------------------------------------- 保存
  async function saveEdit(el) {
    let now = txt(el).trim(); const old = (el.dataset.old || '').trim();
    if (el.dataset.pre && now.startsWith(el.dataset.pre)) now = now.slice(el.dataset.pre.length);   // 去掉引擎加的前缀
    if (now === old && !el.classList.contains('hb-changed')) return;
    const row = { path: el.dataset.src, lang: E.lang, page: pageOf(el), old: el.dataset.orig, new: now, by: me, at: Date.now(), status: 'pending' };
    el.classList.toggle('hb-changed', norm(now) !== norm(el.dataset.orig)); el.dataset.old = now;
    const id = sid(E.lang + '__' + row.path);
    if (db) { try { await db.collection('edits').doc(id).set(row); } catch (e) { st('保存失败：' + (e.code || e.message), true); return; } }
    else local.edits[id] = row;
    const bad = relayout(); report(bad);
  }
  function report(bad) {
    const n = $$('.hb-changed').length;
    st(`${n} 处修改${db ? '已保存（所有人可见）' : '（本地，点“导出修改”交给 Claude）'}` + (bad ? ` · ${bad} 页放不下，标红了` : ' · 版面检查通过'), bad);
  }
  document.addEventListener('focusout', e => { const el = e.target.closest && e.target.closest('[data-src]'); if (el && mode === 'edit') saveEdit(el); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && document.activeElement && document.activeElement.dataset && document.activeElement.dataset.src) document.activeElement.blur(); });
  // ---------------------------------------------------------------- 换图、批注
  document.addEventListener('click', async e => {
    if (e.target.closest('#hbx')) return;
    if (mode === 'img') {
      const im = e.target.closest('img[data-file]'); if (!im) { st('点一张照片（橙色虚线框）'); return; }
      if (!assets) { st('这个页面没有上传权限：把新照片直接发给 Claude，说明换第几页哪张', true); return; }
      const inp = document.createElement('input'); inp.type = 'file'; inp.accept = 'image/jpeg,image/png,image/webp';
      inp.onchange = async () => {
        const f = inp.files[0]; if (!f) return; st('上传中…');
        try {
          const r = await assets.upload(f); im.src = r.url; im.style.objectFit = 'cover';
          const row = { page: pageOf(im), file: im.dataset.file, asset: r.id, name: f.name, lang: E.lang, by: me, at: Date.now(), status: 'pending' };
          const id = sid(E.lang + '__' + row.page + '__' + row.file);
          if (db) await db.collection('images').doc(id).set(row); else local.images[id] = row;
          st(`第${row.page}页的照片已换成 ${f.name}（同步时写回）`);
        } catch (err) { st('上传失败：' + (err.code || err.message), true); }
      };
      inp.click(); e.preventDefault(); return;
    }
    if (mode === 'note') {
      const el = e.target.closest('[data-src], img, .page'); if (!el) return;
      if (!comments) { st('这个页面不能批注：直接在聊天里说“第 N 页……”', true); return; }
      try { await comments.openComposer({ element: el }); } catch (err) { st('批注打不开：' + (err.code || err.message), true); }
      e.preventDefault();
    }
  }, true);
  // ---------------------------------------------------------------- 导出 edits.json（离线兜底）
  $('#hbx-dl').onclick = async () => {
    let rows = Object.values(local.edits), imgs = Object.values(local.images);
    if (db) { try { rows = (await db.collection('edits').get()).docs.map(d => d.data()); imgs = (await db.collection('images').get()).docs.map(d => d.data()); } catch (e) { } }
    const data = JSON.stringify({ lang: E.lang, edits: rows.filter(r => r.status !== 'synced'), images: imgs.filter(r => r.status !== 'synced') }, null, 1);
    const dl = window.claude && await window.claude.use('downloads').catch(() => null);
    if (dl) { try { await dl.save({ filename: `edits_${E.lang}.json`, data }); return; } catch (e) { } }
    const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([data], { type: 'application/json' })); a.download = `edits_${E.lang}.json`; a.click();
  };
  // ---------------------------------------------------------------- 启动
  function applyRow(r) {
    if (r.lang !== E.lang || r.status === 'synced') return false;
    const el = $(`[data-src="${CSS.escape(r.path)}"]`); if (!el || el === document.activeElement) return false;
    if (norm(txt(el)) === norm((el.dataset.pre || '') + r.new)) { el.classList.add('hb-changed'); return false; }
    el.innerText = (el.dataset.pre || '') + r.new; el.dataset.old = txt(el); el.classList.add('hb-changed'); return true;
  }
  function applyImg(r) {
    if (r.lang !== E.lang || r.status === 'synced') return;
    const pg = $(`.page[data-n="${r.page}"]`); const im = pg && $(`img[data-file="${CSS.escape(r.file)}"]`, pg);
    if (im) { im.src = '/_blob/' + r.asset; im.style.objectFit = 'cover'; }
  }
  async function start() {
    for (let i = 0; i < 200 && document.body.dataset.ready != 1; i++) await new Promise(r => setTimeout(r, 50));
    const hit = mapLeaves(); setMode('view');
    st(`可改 ${hit} 处文字` + (E.leaves.length > hit ? `（${E.leaves.length - hit} 处没对上，在聊天里说）` : ''));
    if (!window.claude) { report(0); return; }
    [db, assets, comments, user] = await Promise.all(['db', 'assets', 'comments', 'user'].map(n => window.claude.use(n).catch(() => null)));
    if (user) { try { me = await user.id(); } catch (e) { } }
    if (!assets) $('#hbx button[data-m="img"]').title = '只有能编辑这个页面的人可以换图';
    if (db) {
      db.collection('edits').onSnapshot(s => { let ch = 0; s.docs.forEach(d => { ch += applyRow(d.data()) ? 1 : 0; }); report(ch ? relayout() : 0); }, e => st('读取修改失败：' + e.code, true));
      db.collection('images').onSnapshot(s => s.docs.forEach(d => applyImg(d.data())));
    } else report(0);
  }
  start();
})();
