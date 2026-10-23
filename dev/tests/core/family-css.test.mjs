import test, {before,after} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {launch} from '../../../hb/core/browser.mjs';
const css = await fs.readFile(new URL('../../../families/folio/design.css',import.meta.url),'utf8');
let browser;
before(async()=>{({browser}=await launch());});
after(async()=>{await browser?.close();});
async function fixture(html,run){const page=await browser.newPage();try{await page.setContent(html);await page.addStyleTag({content:css});return await run(page);}finally{await page.close();}}
const near=(a,b,t=.08)=>assert.ok(Math.abs(a-b)<t,`${a} ≠ ${b}`);
const pxmm=96/25.4;

test('surface roles remain readable in both nesting directions, including headings and leads',async()=>{
 const styles=await fixture(`<div class="fl-scope"><div class="fl-surface-dark" id="dark"><h3 class="fl-h3">Heading</h3><p class="fl-lead">Lead</p><p class="fl-key fl-text-muted">Muted</p><p class="fl-key fl-text-accent">Accent</p><div id="paper" class="fl-surface-paper"><h3 class="fl-h3">Paper</h3><p class="fl-text-muted">Muted</p><p class="fl-text-accent">Accent</p><div id="accent" class="fl-surface-accent"><p class="fl-text-muted">Nested accent</p></div></div></div></div>`,page=>page.evaluate(()=>['dark','paper','accent'].flatMap(id=>{const parent=document.getElementById(id);return [...parent.children].filter(el=>el.tagName!=='DIV').map(el=>({bg:getComputedStyle(parent).backgroundColor,color:getComputedStyle(el).color}));})));
 const lum=color=>{const v=color.match(/[\d.]+/g).slice(0,3).map(Number).map(n=>{n/=255;return n<=.04045?n/12.92:((n+.055)/1.055)**2.4;});return v[0]*.2126+v[1]*.7152+v[2]*.0722;};
 for(const {bg,color} of styles){const a=lum(bg),b=lum(color);assert.ok((Math.max(a,b)+.05)/(Math.min(a,b)+.05)>=4.5,`${color} on ${bg}`);}
 assert.notEqual(styles[0].color,styles[4].color);
});

test('safe areas mirror normally and explicit sides/safety overrides take precedence',async()=>{
 const rects=await fixture(`<style>.page{position:relative;width:216mm;height:303mm;--bleed:3mm;--safe-left:8mm;--safe-right:8mm}</style><section class="page"><div class="fl-area"></div></section><section class="page"><div class="fl-area"></div></section><section class="page" data-side="left" style="--safe-left:26mm"><div class="fl-area"></div></section>`,page=>page.evaluate(()=>[...document.querySelectorAll('.page')].map(p=>{const a=p.firstElementChild.getBoundingClientRect(),r=p.getBoundingClientRect();return [a.left-r.left,r.right-a.right];})));
 near(rects[0][0],22*pxmm);near(rects[0][1],18*pxmm);near(rects[1][0],18*pxmm);near(rects[1][1],22*pxmm);near(rects[2][0],29*pxmm);near(rects[2][1],22*pxmm);
});

test('layout slots align to six tracks and ordinary atoms override layout defaults',async()=>{
 const result=await fixture(`<div class="fl-scope" style="width:720px;--fl-gutter:24px"><div class="fl-grid fl-cols-6"><div id="span4" class="fl-span-4">four</div><div>rest</div><div id="offset" class="fl-start-2 fl-span-3">three</div></div><div class="fl-l-sidebar"><div id="main" class="fl-l-main">main</div><aside id="aside" class="fl-l-aside">aside</aside></div><div class="fl-l-sidebar"><div id="override" class="fl-l-main fl-start-2 fl-span-3">override</div></div><div id="stack" class="fl-l-stack fl-gap-1"></div></div>`,page=>page.evaluate(()=>{const rect=id=>{const e=document.getElementById(id),r=e.getBoundingClientRect(),p=e.parentElement.getBoundingClientRect();return [r.x-p.x,r.width];};return {span4:rect('span4'),offset:rect('offset'),main:rect('main'),aside:rect('aside'),override:rect('override'),gap:getComputedStyle(document.getElementById('stack')).gap};}));
 assert.deepEqual(result.main,result.span4);near(result.aside[0],496);near(result.offset[0],124);near(result.offset[1],348);assert.deepEqual(result.override,result.offset);assert.equal(result.gap,'7px');
});

test('font and weight atoms request declared role weights without synthetic alternatives',async()=>{
 const weights=await fixture(`<div class="fl-scope"><p class="fl-font-body fl-weight-strong">Body<strong>x</strong></p><p class="fl-font-label fl-weight-strong">Label<strong>x</strong></p><p class="fl-font-display fl-weight-regular">Display<strong>x</strong></p><p class="fl-font-number fl-weight-strong">123<strong>x</strong></p></div>`,page=>page.evaluate(()=>[...document.querySelectorAll('p')].map(el=>[getComputedStyle(el).fontWeight,getComputedStyle(el.firstChild.nextSibling).fontWeight,getComputedStyle(el).fontSynthesis])));
 assert.deepEqual(weights,[['600','600','none'],['600','600','none'],['900','900','none'],['600','600','none']]);
});

test('bold and light restore the size ladder, heading families and number family',async()=>{
 const rows=await fixture(`<div class="fl-scope fl-type-bold"><span id="b-display" class="fl-display">Display</span><span id="b-h1" class="fl-h1">H1</span><span id="b-h2" class="fl-h2">H2</span><span id="b-h3" class="fl-h3">H3</span><span id="b-lead" class="fl-lead">Lead</span><span id="b-body" class="fl-body">Body<strong> emphasized</strong></span><span id="b-small" class="fl-body fl-size-small">Small</span><span id="b-key" class="fl-key">Key</span><span id="b-aux" class="fl-aux">Aux</span><span id="b-number" class="fl-number">2026</span></div><div class="fl-scope fl-type-light"><span id="l-display" class="fl-display">Display</span><span id="l-h1" class="fl-h1">H1</span><span id="l-h2" class="fl-h2">H2</span><span id="l-h3" class="fl-h3">H3</span><span id="l-lead" class="fl-lead">Lead</span><span id="l-body" class="fl-body">Body<strong> emphasized</strong></span><span id="l-small" class="fl-body fl-size-small">Small</span><span id="l-key" class="fl-key">Key</span><span id="l-aux" class="fl-aux">Aux</span><span id="l-number" class="fl-number">2026</span></div>`,page=>page.evaluate(()=>['display','h1','h2','h3','lead','body','small','key','aux','number'].flatMap(role=>['b','l'].map(mode=>{const el=document.getElementById(`${mode}-${role}`),style=getComputedStyle(el);return {id:el.id,weight:style.fontWeight,family:style.fontFamily,strong:el.querySelector('strong')&&getComputedStyle(el.querySelector('strong')).fontWeight};}))));
 assert.deepEqual(rows.map(x=>x.weight),['900','200','700','250','700','300','600','400','600','400','400','400','500','500','600','600','600','600','900','200']);
 for(const row of rows.filter(x=>['display','h1','h2','h3'].some(role=>x.id.endsWith(role))))
  assert.match(row.family,row.id.startsWith('b-')?/Noto Serif SC/:/Noto Sans SC/);
 assert.match(rows.find(x=>x.id==='b-number').family,/Inter/);assert.match(rows.find(x=>x.id==='l-number').family,/Inter/);
 assert.equal(rows.find(x=>x.id==='b-body').strong,'600');assert.equal(rows.find(x=>x.id==='l-body').strong,'400');
});

test('image ratios, fit and focus compose; bounded masonry keeps every crop within its column',async()=>{
 const img='<img src="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%271200%27 height=%27800%27/%3E" alt="">';
 const result=await fixture(`<div class="fl-scope"><figure id="frame" class="fl-frame fl-ratio-portrait fl-focus-left" style="width:240px">${img}</figure><figure class="fl-frame fl-focus-top" style="width:200px"><img id="fit" class="fl-fit-contain fl-focus-right" alt=""></figure><div class="fl-l-masonry" style="width:600px;--fl-masonry-height:300px"><div class="fl-l-column" style="--fl-masonry-rows:1fr 2fr"><figure class="fl-frame">${img}</figure><figure class="fl-frame">${img}</figure></div><div class="fl-l-column" style="--fl-masonry-rows:2fr 1fr"><figure class="fl-frame">${img}</figure><figure class="fl-frame">${img}</figure></div></div></div>`,page=>page.evaluate(()=>{const frame=document.getElementById('frame'),f=frame.getBoundingClientRect(),im=frame.querySelector('img'),fit=getComputedStyle(document.getElementById('fit'));return {size:[f.width,f.height],imageHeight:im.getBoundingClientRect().height,focus:getComputedStyle(im).objectPosition,fit:[fit.objectFit,fit.objectPosition],overflow:[...document.querySelectorAll('.fl-l-column')].some(c=>[...c.children].some(f=>f.getBoundingClientRect().right>c.getBoundingClientRect().right+.1||f.getBoundingClientRect().bottom>c.getBoundingClientRect().bottom+.1))};}));
 near(result.size[0],240);near(result.size[1],320);near(result.imageHeight,320);assert.equal(result.focus,'0% 50%');assert.deepEqual(result.fit,['contain','100% 50%']);assert.equal(result.overflow,false);
});

test('panorama uses trim-width shift with nonzero bleed and explicit figure side overrides page side',async()=>{
 const result=await fixture(`<style>.page{position:relative;width:216mm;height:303mm;--trim-w:210mm;--bleed:3mm;--media-w:216mm;--media-h:303mm}</style><section class="page" data-side="left"><figure class="fl-l-panorama"><img class="fl-l-panorama-image" alt=""></figure></section><section class="page" data-side="right"><figure class="fl-l-panorama"><img class="fl-l-panorama-image" alt=""></figure></section><section class="page" data-side="right"><figure class="fl-l-panorama" data-side="left"><img class="fl-l-panorama-image" alt=""></figure></section>`,page=>page.evaluate(()=>[...document.querySelectorAll('.fl-l-panorama-image')].map(el=>{const s=getComputedStyle(el);return {left:parseFloat(s.left),width:el.getBoundingClientRect().width,focus:s.objectPosition};})));
 near(result[0].width,426*pxmm);near(result[1].width,result[0].width);near(result[1].left,-210*pxmm);near(result[2].left,0);assert.equal(result[0].focus,result[1].focus);
 // Trimmed left edge at bleed+trim equals right page's bleed after its scene shift.
 near(213*pxmm,3*pxmm-result[1].left);
});

test('local showcase filters recipes, opens source, preserves layout in structure mode, and fits mobile',async()=>{
 const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
 try{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(new URL('../../folio-css/index.html',import.meta.url).href);await page.evaluate(()=>document.fonts.ready);
  assert.deepEqual(await page.evaluate(()=>[document.fonts.check("900 24px 'Noto Serif SC'"),document.fonts.check("250 24px 'Noto Sans SC'"),document.fonts.check('900 14px Inter')]),[true,true,true]);
  assert.equal(await page.locator('.recipe-card').count(),await page.evaluate(()=>['atoms','layouts','components','expressions'].reduce((n,k)=>n+FOLIO_CATALOG[k].length,0)));
  await page.locator('button[data-category=photography]').click();assert.equal(await page.locator('#layout-gallery .recipe-card:visible').count(),await page.evaluate(()=>FOLIO_CATALOG.layouts.filter(e=>e.category==='photography').length));
  const geometry=()=>page.locator('#layout-gallery .recipe-card:visible .preview-sheet').first().evaluate(e=>[e.scrollWidth,e.scrollHeight]);
  const before=await geometry();await page.locator('#structure-toggle').check();assert.deepEqual(await geometry(),before);
  await page.locator('#layout-gallery .recipe-card:visible button').first().click();assert.equal(await page.locator('dialog').evaluate(e=>e.open),true);assert.match(await page.locator('#dialog-code').innerText(),/fl-l-photo-pair/);
  await page.keyboard.press('Escape');assert.equal(await page.locator('dialog').evaluate(e=>e.open),false);
  await page.locator('button[data-grid="4,2"]').click();assert.equal(await page.locator('#grid-content .fl-span-4').count(),1);
  await page.locator('#image-ratio').selectOption('square');await page.locator('#image-focus').selectOption('right');assert.match(await page.locator('#image-code').innerText(),/fl-ratio-square fl-focus-right/);
  await page.locator('button[data-component=charts]').click();assert.equal(await page.locator('#component-gallery .recipe-card:visible').count(),4);
  await page.locator('#component-gallery .recipe-card:visible button').first().click();assert.equal(await page.locator('#chart-data').isVisible(),true);assert.match(await page.locator('#dialog-data').textContent(),/values/);await page.keyboard.press('Escape');
  await page.setViewportSize({width:390,height:844});const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);assert.equal(overflow,0);
  assert.deepEqual(errors,[]);
 }finally{await page.close();}
});

test('every showcase entry links to a real specimen page, including the two-page panorama',async()=>{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 try{
  await page.goto(new URL('../../folio-css/index.html',import.meta.url).href);
  const entries=await page.evaluate(()=>['atoms','layouts','components','expressions'].flatMap(k=>FOLIO_CATALOG[k]).map(e=>({id:e.id,location:window.FOLIO_SPECIMEN?.[e.id]})));
  const preview=await fs.readFile(new URL('../../samples/native/folio-swiss/preview.html',import.meta.url),'utf8');
  const anchors=new Set([...preview.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]));
  for(const entry of entries){assert.ok(entry.location?.page,`${entry.id}: missing page number`);assert.ok(anchors.has(entry.location.id),`${entry.id}: missing anchor ${entry.location.id}`);}
  await page.locator('#layout-search').fill('panorama');
  await page.locator('#layout-gallery .recipe-card:visible button').click();
  const expected=entries.find(e=>e.id==='panorama').location;
  assert.match(await page.locator('#dialog-specimen').innerText(),new RegExp(`第 ${expected.page} 页`));
  assert.ok((await page.locator('#dialog-specimen a').getAttribute('href')).endsWith('#panorama-1'));
  await page.keyboard.press('Escape');
  await page.locator('#expression-search').fill('x-edge');
  await page.locator('#expression-gallery .recipe-card:visible button').click();
  assert.match(await page.locator('#dialog-specimen').innerText(),/第 100 页/);
 }finally{await page.close();}
});
