import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {launch} from '../../../hb/core/browser.mjs';
const css=await fs.readFile(new URL('../../../families/folio/folio.css',import.meta.url),'utf8');
let browser;before(async()=>{({browser}=await launch());});after(async()=>browser?.close());
async function run(html,cb){const p=await browser.newPage();try{await p.setContent(html);await p.addStyleTag({content:css});return await cb(p);}finally{await p.close();}}
test('two dimensional tracks span with bounded image fill, preserving intrinsic source',async()=>{
 const d=await run('<div class="fl-scope"><div class="fl-grid fl-cols-3 fl-rows-3 fl-gap-2" style="width:600px;height:600px"><figure id="photo" class="fl-frame fl-frame-fill fl-span-2 fl-row-span-2"><img src="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%271200%27 height=%27800%27/%3E"></figure><p id="other" class="fl-start-3 fl-row-start-3">caption</p></div></div>',p=>p.evaluate(()=>{const e=document.querySelector('#photo'),i=e.firstChild;return {fh:e.offsetHeight,ih:i.offsetHeight,fw:e.offsetWidth,iw:i.offsetWidth,fit:getComputedStyle(i).objectFit,other:getComputedStyle(document.querySelector('#other')).gridRowStart};}));
 assert.equal(d.fh,d.ih);assert.equal(d.fw,d.iw);assert.equal(d.fit,'cover');assert.equal(d.other,'3');assert.ok(d.fh>390&&d.fh<400);
});
test('outer bleed mirrors by explicit page side and keeps body away from photo',async()=>{
 const r=await run('<style>.page{position:relative;width:800px;height:1100px;--bleed:0px}</style>'+['left','right'].map(s=>`<section class="page" data-side="${s}"><div class="fl-l-bleed-outer"><figure class="fl-l-photo fl-frame"></figure><div class="fl-area fl-l-copy">Text</div></div></section>`).join(''),p=>p.evaluate(()=>[...document.querySelectorAll('.page')].map(el=>{const b=el.getBoundingClientRect(),f=el.querySelector('figure').getBoundingClientRect(),c=el.querySelector('.fl-l-copy').getBoundingClientRect();return{l:f.left-b.left,r:f.right-b.left,cl:c.left-b.left,cr:c.right-b.left};})));
 assert.equal(r[0].l,0);assert.ok(r[0].cl>r[0].r,JSON.stringify(r));assert.equal(r[1].r,800);assert.ok(r[1].cr<r[1].l);
});
test('reading face uses real regular weight and inverse tone leaves background transparent',async()=>{
 const r=await run('<div class="fl-scope"><p id="r" class="fl-font-reading fl-leading-reading">Reading</p><div id="tone" class="fl-tone-inverse"><p class="fl-h3">Inverse</p><div class="fl-surface-paper"><p>Paper</p></div></div></div>',p=>p.evaluate(()=>{const r=getComputedStyle(document.querySelector('#r')),t=getComputedStyle(document.querySelector('#tone'));return{weight:r.fontWeight,leading:r.lineHeight,bg:t.backgroundColor,color:t.color,nested:getComputedStyle(document.querySelector('.fl-surface-paper')).color};}));
 assert.equal(r.weight,'400');assert.equal(r.leading,'24px');assert.equal(r.bg,'rgba(0, 0, 0, 0)');assert.notEqual(r.color,r.nested);
});

test('bottom bleed remains absolutely placed when composed with a frame',async()=>{
 const r=await run('<style>.page{position:relative;width:800px;height:1100px;--bleed:0px}</style><section class="page"><div class="fl-l-bleed-bottom"><figure class="fl-l-photo fl-frame"></figure><div class="fl-area fl-l-copy">Text</div></div></section>',p=>p.evaluate(()=>{const a=document.querySelector('.page').getBoundingClientRect(),b=document.querySelector('figure').getBoundingClientRect(),c=document.querySelector('.fl-l-copy').getBoundingClientRect();return {bottom:b.bottom-a.bottom,height:b.height,gap:b.top-c.bottom};}));
 assert.equal(r.bottom,0);assert.equal(r.height,462);assert.ok(r.gap>=27);
});
