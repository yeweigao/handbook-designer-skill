/* Plain local showcase. Recipes are authored repository data, never remote HTML. */
(() => {
  const catalog = window.FOLIO_CATALOG;
  if (!catalog) { document.querySelector('#layout-count').textContent = '请运行 python3 dev/build-folio-css.py 生成展示数据。'; return; }
  const $ = (s) => document.querySelector(s);
  const labels = { reading: '阅读', information: '信息', photography: '摄影', itinerary: '行程', business: '经营', analysis: '分析', charts: '图表' };
  const dialog = $('#recipe-dialog');
  let activeRecipe;
  const mode = { type: 'bold', surface: 'paper' };
  const surfaceLabels = { paper: '白纸', dark: '黑底', accent: '强调色' };
  function applyMode(el) {
    el.classList.remove('fl-type-bold', 'fl-type-light', 'fl-surface-paper', 'fl-surface-dark', 'fl-surface-accent');
    el.classList.add(`fl-type-${mode.type}`, `fl-surface-${mode.surface}`);
  }
  function sourceFor(entry) {
    return `<section class="fl-scope fl-type-${mode.type} fl-surface-${mode.surface}">\n${entry.html}\n</section>`;
  }
  async function copySource(source, status, fallback) {
    try {
      if (!navigator.clipboard) throw Error('clipboard unavailable');
      await navigator.clipboard.writeText(source);
      status.textContent = '已复制';
    } catch {
      const field = document.createElement('textarea');
      field.value = source; field.setAttribute('aria-label', '待复制的 HTML');
      field.style.cssText = 'position:fixed;inset:0;opacity:0;pointer-events:none';
      (dialog.open ? dialog : document.body).append(field);
      const focus = document.activeElement; field.select();
      const copied = document.execCommand('copy'); field.remove(); focus?.focus();
      status.textContent = copied ? '已复制' : '复制不可用，请打开源码后手动复制';
      if (!copied && fallback) {
        const details = fallback.closest('details'); if (details) details.open = true;
        const selection = window.getSelection(); const range = document.createRange();
        range.selectNodeContents(fallback); selection.removeAllRanges(); selection.addRange(range);
        status.textContent = '源码已选中，请复制';
      }
    }
  }
  function pressed(group, selected) {
    group.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b === selected)));
  }
  function sheet(entry) {
    const el = document.createElement('div'); el.className = 'preview-sheet fl-scope'; applyMode(el);
    if (entry.data) el.style.width = `${entry.data.width + 60}px`;
    if (entry.id === 'panorama') el.style.width = '1180px';
    el.innerHTML = entry.html;
    // Card previews are aria-hidden; avoid duplicate SVG title IDs when the recipe opens.
    el.querySelectorAll('svg [id]').forEach(n => { const old = n.id; n.id = old + '-' + (++sheet.serial); el.querySelectorAll('[aria-labelledby]').forEach(a => { if(a.getAttribute('aria-labelledby') === old) a.setAttribute('aria-labelledby',n.id); }); });
    el.querySelectorAll('[class*="fl-l-"]').forEach(node => {
      const layout = Array.from(node.classList).find(c => c.startsWith('fl-l-'));
      if (layout) node.dataset.structure = layout.replace('fl-l-', '');
    });
    return el;
  }
  sheet.serial = 0;
  function fitSheet(viewport) {
    const el = viewport.querySelector('.preview-sheet'); if (!el || !viewport.clientWidth) return;
    el.style.transform = 'none';
    const natural = Math.max(el.scrollHeight, el.offsetHeight, 1);
    // Include authored overflow in the preview bounds; never shrink its font sizes.
    const width = Math.max(el.scrollWidth, el.offsetWidth);
    const modal = viewport.classList.contains('dialog-preview') || viewport.classList.contains('composition-preview');
    const scale = modal ? Math.min(1, viewport.clientWidth / width) : Math.min(viewport.clientWidth / width, viewport.clientHeight / natural);
    el.style.transform = `scale(${scale})`;
    el.style.left = `${(viewport.clientWidth - width * scale) / 2}px`;
    if (modal) { el.style.margin = '0'; el.style.transformOrigin = 'top left'; viewport.style.height = `${Math.ceil(natural * scale)}px`; }
  }
  function refit() { document.querySelectorAll('.preview-window, .dialog-preview, .composition-preview').forEach(fitSheet); }
  function openRecipe(entry) {
    activeRecipe = entry;
    $('#dialog-kicker').textContent = `${labels[entry.category] || '组合'} / ${entry.id}`;
    $('#dialog-title').textContent = entry.title;
    $('#dialog-description').textContent = entry.description;
    $('#dialog-grammar').textContent = `组合：${entry.grammar}`;
    $('#dialog-limits').textContent = `适用边界：${entry.limits}`;
    const specimen = $('#dialog-specimen'); specimen.replaceChildren();
    const specimenPage = typeof entry.specimenPage === 'string' ? { id: entry.specimenPage, label: entry.specimenPage } : entry.specimenPage;
    specimen.hidden = !specimenPage;
    if (specimenPage) {
      const link = document.createElement('a');
      link.href = `../samples/native/folio-swiss/preview.html#${encodeURIComponent(specimenPage.id)}`;
      link.textContent = `查看样刊对应页 · ${specimenPage.label || specimenPage.id} ↗`;
      specimen.append(link);
    }
    $('#dialog-code').textContent = sourceFor(entry);
    $('#dialog-classes').replaceChildren(...(entry.classes || []).map(name => { const code = document.createElement('code'); code.textContent = name; return code; }));
    $('#chart-data').hidden = !entry.data;
    $('#dialog-data').textContent = entry.data ? JSON.stringify(entry.data, null, 2) : '';
    // Every dialog has a single live chart, so its accessible title ID is unique.
    $('#copy-status').textContent = '';
    $('#dialog-preview').replaceChildren(sheet(entry));
    $('#dialog-preview').classList.toggle('structure', $('#structure-toggle').checked);
    dialog.showModal();
    dialog.scrollTop = 0;
    refit();
    $('#dialog-preview').querySelectorAll('img').forEach(img => img.addEventListener('load', refit, {once:true}));
  }
  function card(entry, index) {
    const article = document.createElement('article'); article.className = 'recipe-card'; article.dataset.category = entry.category; article.dataset.search = [entry.id,entry.title,entry.description,entry.grammar,...(entry.classes || [])].join(' ').toLowerCase();
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
  const sections = [
    { name: 'layout', entries: catalog.layouts || [], noun: '组布局', selected: 'all' },
    { name: 'component', entries: catalog.components || [], noun: '个组件', selected: 'all' },
    { name: 'atom', entries: catalog.atoms || [], noun: '组原子', selected: 'all' },
    { name: 'expression', entries: catalog.expressions || [], noun: '种表现', selected: 'all' }
  ];
  function filterSection(section) {
    const query = $(`#${section.name}-search`).value.trim().toLowerCase();
    let count = 0;
    $(`#${section.name}-gallery`).querySelectorAll('.recipe-card').forEach(card => {
      const show = (section.selected === 'all' || card.dataset.category === section.selected) && (!query || query.split(/\s+/).every(word => card.dataset.search.includes(word)));
      card.hidden = !show; if (show) count++;
    });
    $(`#${section.name}-count`).textContent = `${count} / ${section.entries.length} ${section.noun}`;
    $(`#${section.name}-empty`).hidden = count > 0;
    refit();
  }
  sections.forEach(section => {
    const gallery = $(`#${section.name}-gallery`);
    section.entries.forEach((entry, i) => gallery.append(card(entry, i)));
    $(`#${section.name}-search`).addEventListener('input', () => filterSection(section));
    const select = $(`#${section.name}-category`);
    if (select) {
      [...new Set(section.entries.map(entry => entry.category))].forEach(category => {
        const option = document.createElement('option'); option.value = category; option.textContent = labels[category] || category; select.append(option);
      });
      select.addEventListener('change', () => { section.selected = select.value; filterSection(section); });
    }
    filterSection(section);
  });
  $('#category-options').addEventListener('click', event => {
    const button = event.target.closest('button[data-category]'); if (!button) return;
    pressed($('#category-options'), button); sections[0].selected = button.dataset.category; filterSection(sections[0]);
  });
  $('#component-options').addEventListener('click', event => {
    const button = event.target.closest('button[data-component]'); if (!button) return;
    pressed($('#component-options'), button); sections[1].selected = button.dataset.component; filterSection(sections[1]);
  });
  $('#structure-toggle').addEventListener('change', event => {
    $('#layout-gallery').classList.toggle('structure',event.target.checked);
    $('#component-gallery').classList.toggle('structure',event.target.checked);
    $('#atom-gallery').classList.toggle('structure',event.target.checked);
    $('#expression-gallery').classList.toggle('structure',event.target.checked); refit();
  });
  $('#close-dialog').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if(event.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    if(event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
  });
  $('#copy-code').addEventListener('click', () => copySource(sourceFor(activeRecipe), $('#copy-status'), $('#dialog-code')));
  const composition = { html: $('#composition-template').innerHTML.trim() };
  const compositionSheet = sheet(composition);
  $('#composition-preview').append(compositionSheet);
  $('#composition-code').textContent = sourceFor(composition);
  $('#copy-composition').addEventListener('click', () => copySource(sourceFor(composition), $('#composition-copy-status'), $('#composition-code')));
  function updateMode() {
    document.querySelectorAll('.preview-sheet').forEach(applyMode);
    $('#composition-state').textContent = `${mode.type} · ${surfaceLabels[mode.surface]}`;
    $('#composition-copy-status').textContent = '';
    $('#composition-code').textContent = sourceFor(composition);
    if (activeRecipe) { $('#dialog-code').textContent = sourceFor(activeRecipe); $('#copy-status').textContent = ''; }
    refit();
  }
  $('#type-options').addEventListener('click', event => {
    const button = event.target.closest('button[data-type]'); if (!button) return;
    mode.type = button.dataset.type; pressed($('#type-options'), button); updateMode();
  });
  $('#surface-options').addEventListener('click', event => {
    const button = event.target.closest('button[data-surface]'); if (!button) return;
    mode.surface = button.dataset.surface; pressed($('#surface-options'), button); updateMode();
  });
  $('#composition-grid').addEventListener('change', event => {
    compositionSheet.firstElementChild.classList.toggle('fl-show-columns', event.target.checked);
    compositionSheet.firstElementChild.classList.toggle('fl-show-baseline', event.target.checked);
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
  [0,7,14,28,42,56,84,112,168].forEach((size,i) => {
    const row = document.createElement('div'); row.className='spacing-row';
    row.innerHTML=`<code>${i}</code><i style="width:${size}px" aria-hidden="true"></i><span>${size}px</span>`;
    $('#spacing-demo').append(row);
  });
  function updateImage(){ const value=`fl-frame fl-ratio-${$('#image-ratio').value} fl-focus-${$('#image-focus').value}`;$('#image-frame').className=value;$('#image-code').textContent=value; }
  $('#image-ratio').addEventListener('change',updateImage);$('#image-focus').addEventListener('change',updateImage);
  window.addEventListener('resize',refit);
  document.fonts.ready.then(refit);
  document.querySelectorAll('.preview-sheet img').forEach(img=>img.addEventListener('load',refit,{once:true}));
  refit();
})();
