/* Plain local showcase. Recipes are authored repository data, never remote HTML. */
(() => {
  const catalog = window.FOLIO_CATALOG;
  if (!catalog) { document.querySelector('#layout-count').textContent = '请运行 python3 dev/build-folio-css.py 生成展示数据。'; return; }
  const $ = (s) => document.querySelector(s);
  const labels = { reading: '阅读', information: '信息', photography: '摄影' };
  const dialog = $('#recipe-dialog');
  let activeRecipe;
  function pressed(group, selected) {
    group.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b === selected)));
  }
  function sheet(entry) {
    const el = document.createElement('div'); el.className = 'preview-sheet fl-scope';
    if (entry.id === 'panorama') el.style.width = '1180px';
    el.innerHTML = entry.html;
    el.querySelectorAll('[class*="fl-l-"]').forEach(node => {
      const layout = Array.from(node.classList).find(c => c.startsWith('fl-l-'));
      if (layout) node.dataset.structure = layout.replace('fl-l-', '');
    });
    return el;
  }
  function fitSheet(viewport) {
    const el = viewport.querySelector('.preview-sheet'); if (!el || !viewport.clientWidth) return;
    el.style.transform = 'none';
    const natural = Math.max(el.scrollHeight, el.offsetHeight, 1);
    const width = el.offsetWidth;
    const modal = viewport.classList.contains('dialog-preview');
    const scale = modal ? Math.min(1, viewport.clientWidth / width) : Math.min(viewport.clientWidth / width, viewport.clientHeight / natural);
    el.style.transform = `scale(${scale})`;
    el.style.left = `${(viewport.clientWidth - width * scale) / 2}px`;
    if (modal) { el.style.margin = '0'; el.style.transformOrigin = 'top left'; viewport.style.height = `${Math.ceil(natural * scale)}px`; }
  }
  function refit() { document.querySelectorAll('.preview-window, .dialog-preview').forEach(fitSheet); }
  function openRecipe(entry) {
    activeRecipe = entry;
    $('#dialog-kicker').textContent = `${labels[entry.category] || '组合'} / ${entry.id}`;
    $('#dialog-title').textContent = entry.title;
    $('#dialog-description').textContent = entry.description;
    $('#dialog-grammar').textContent = `组合：${entry.grammar}`;
    $('#dialog-limits').textContent = `适用边界：${entry.limits}`;
    $('#dialog-code').textContent = entry.html;
    $('#copy-status').textContent = '';
    $('#dialog-preview').replaceChildren(sheet(entry));
    $('#dialog-preview').classList.toggle('structure', $('#structure-toggle').checked);
    dialog.showModal();
    dialog.scrollTop = 0;
    refit();
    $('#dialog-preview').querySelectorAll('img').forEach(img => img.addEventListener('load', refit, {once:true}));
  }
  function card(entry, index) {
    const article = document.createElement('article'); article.className = 'recipe-card'; article.dataset.category = entry.category;
    const button = document.createElement('button'); button.type = 'button'; button.setAttribute('aria-label', `查看${entry.title}与源码`);
    const preview = document.createElement('div'); preview.className = 'preview-window'; preview.setAttribute('aria-hidden', 'true'); preview.append(sheet(entry));
    const title = document.createElement('div'); title.className = 'recipe-title';
    const n = document.createElement('span'); n.textContent = String(index + 1).padStart(2, '0');
    const name = document.createElement('b'); name.textContent = entry.title;
    const arrow = document.createElement('i'); arrow.textContent = '↗';
    title.append(n, name, arrow);
    const description = document.createElement('p'); description.className = 'recipe-description'; description.textContent = entry.description;
    button.append(preview, title, description); button.addEventListener('click', () => openRecipe(entry)); article.append(button);
    return article;
  }
  catalog.layouts.forEach((entry,i) => $('#layout-gallery').append(card(entry,i)));
  catalog.components.forEach((entry,i) => $('#component-gallery').append(card(entry,i)));
  $('#layout-count').textContent = `${catalog.layouts.length} 组布局`;
  $('#category-options').addEventListener('click', event => {
    const button = event.target.closest('button[data-category]'); if (!button) return;
    pressed($('#category-options'),button); let count = 0;
    $('#layout-gallery').querySelectorAll('.recipe-card').forEach(card => {
      const show = button.dataset.category === 'all' || card.dataset.category === button.dataset.category;
      card.hidden = !show; if(show) count++;
    });
    $('#layout-count').textContent = `${count} 组布局`; refit();
  });
  $('#structure-toggle').addEventListener('change', event => {
    $('#layout-gallery').classList.toggle('structure',event.target.checked);
    $('#component-gallery').classList.toggle('structure',event.target.checked); refit();
  });
  $('#close-dialog').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if(event.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    if(event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
  });
  $('#copy-code').addEventListener('click', async () => {
    try {
      if (!navigator.clipboard) throw Error('clipboard unavailable');
      await navigator.clipboard.writeText(activeRecipe.html);
      $('#copy-status').textContent = '已复制';
    } catch {
      const selection = window.getSelection(); const range = document.createRange(); range.selectNodeContents($('#dialog-code')); selection.removeAllRanges(); selection.addRange(range);
      $('#copy-status').textContent = document.execCommand('copy') ? '已复制' : '源码已选中，请复制';
    }
  });
  const gridCopy = [
    ['先看整体','一页内容可以有共同的对齐轴线，同时容纳不同的阅读速度。'],
    ['再看关系','正文、旁注和照片各有分量。列宽与留白帮助读者理解它们的关系。'],
    ['留下一点空白','留白用于分组，也为翻页提供停顿。']
  ];
  function updateGrid(spans) {
    $('#grid-content').replaceChildren(...spans.map((span,i) => {
      const item = document.createElement('article'); item.className = `fl-span-${span}`;
      const heading = document.createElement('h4'); heading.className = 'fl-h3'; heading.textContent = gridCopy[i][0];
      const paragraph = document.createElement('p'); paragraph.className = 'fl-key'; paragraph.textContent = gridCopy[i][1]; item.append(heading,paragraph); return item;
    }));
    $('#grid-code').textContent = `fl-grid fl-cols-6 → ${spans.map(n=>`fl-span-${n}`).join(' + ')}`;
  }
  $('#grid-options').addEventListener('click', event => { const b = event.target.closest('button[data-grid]'); if(b){ pressed($('#grid-options'),b);updateGrid(b.dataset.grid.split(',')); } });
  updateGrid([3,3]);
  [0,7,14,28,42,56,84].forEach((size,i) => {
    const row = document.createElement('div'); row.className='spacing-row';
    row.innerHTML=`<code>${i}</code><i style="width:${size*2}px" aria-hidden="true"></i><span>${size}px</span>`;
    $('#spacing-demo').append(row);
  });
  function updateImage(){ const value=`fl-frame fl-ratio-${$('#image-ratio').value} fl-focus-${$('#image-focus').value}`;$('#image-frame').className=value;$('#image-code').textContent=value; }
  $('#image-ratio').addEventListener('change',updateImage);$('#image-focus').addEventListener('change',updateImage);
  window.addEventListener('resize',refit);
  document.fonts.ready.then(refit);
  document.querySelectorAll('.preview-sheet img').forEach(img=>img.addEventListener('load',refit,{once:true}));
  refit();
})();
