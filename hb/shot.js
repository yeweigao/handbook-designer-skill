// usage: node shot.js <projectDir> [bg]   -> writes <projectDir>/.qa/{b3.json,pgN.png,bgN.png}
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const dir=path.resolve(process.argv[2]||'.');const mode=process.argv[3]||'all';const Q=path.join(dir,'.qa');fs.mkdirSync(Q,{recursive:true});
// 先用 playwright 自带的 chromium；不行再找系统里的 chromium/chrome
const launch=async()=>{try{return await chromium.launch({args:['--no-sandbox']})}catch(e){const exe=require('child_process').execSync('which chromium || which chromium-browser || which google-chrome || true').toString().split('\n')[0].trim();if(!exe)throw e;return chromium.launch({executablePath:exe,args:['--no-sandbox']})}};
(async()=>{const b=await launch();
const p=await b.newPage({viewport:{width:794,height:1123},deviceScaleFactor:1});await p.goto('file://'+path.join(dir,'book.html'),{waitUntil:'networkidle'});
await p.waitForFunction(()=>document.body.dataset.ready==1,{timeout:30000});await p.waitForTimeout(300);
const info=await p.evaluate(()=>{const out=[],ov=[];const pages=[...document.querySelectorAll('.page')];
 // 文字自带底色（胶囊标签、卡片）时不需要给照片压暗/提亮
 const ownBg=e=>{for(let x=e.closest('.gt')?e.closest('.gt').parentElement:e;x&&!x.classList.contains('page');x=x.parentElement){const c=getComputedStyle(x);if(c.backgroundImage!='none'||(c.backgroundColor&&!/rgba\(.*,\s*0\)|transparent/.test(c.backgroundColor)))return 1}return 0};
 const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){const t=n.textContent.trim();if(!t)continue;const el=n.parentElement;if(el.tagName=='SCRIPT'||el.tagName=='STYLE')continue;const cs=getComputedStyle(el);
 const r=document.createRange();r.selectNodeContents(n);for(const rc of r.getClientRects()){const pg=pages.findIndex(x=>x.contains(el));if(pg<0)continue;const pr=pages[pg].getBoundingClientRect();
 if(rc.right>pr.right+1||rc.left<pr.left-1||rc.bottom>pr.bottom+1)ov.push([pg+1,'off-page',t.slice(0,15)]);
 out.push({pg,t:t.slice(0,24),x:rc.left-pr.left,y:rc.top-pr.top,w:rc.width,h:rc.height,color:cs.color,fs:parseFloat(cs.fontSize)||10,fw:parseInt(cs.fontWeight)||400,own:ownBg(el)});}}
 document.querySelectorAll('.flow').forEach(e=>{const pg=pages.findIndex(x=>x.contains(e));if(e.scrollHeight>e.clientHeight+2)ov.push([pg+1,'region',e.scrollHeight-e.clientHeight,e.innerText.slice(0,15)]);
  [...e.children].forEach(c=>{if(c.classList.contains('tk')&&c.scrollHeight>c.clientHeight+2)ov.push([pg+1,'step',c.scrollHeight-c.clientHeight,c.innerText.slice(0,15)])})});
 // 碰撞：同页两个绝对定位文字区（页眉/海报上下文字/纸面区/图注/页脚）的实际内容互相重叠
 pages.forEach((pgEl,pi)=>{const pr=pgEl.getBoundingClientRect();const regs=[];
  pgEl.querySelectorAll(':scope > div.a').forEach(el=>{let u=null;el.querySelectorAll('*').forEach(c=>{if(c.children.length)return;const r=c.getBoundingClientRect();if(!r.width||!r.height)return;
    u=u?{l:Math.min(u.l,r.left),t:Math.min(u.t,r.top),r:Math.max(u.r,r.right),b:Math.max(u.b,r.bottom)}:{l:r.left,t:r.top,r:r.right,b:r.bottom}});
   if(u&&el.innerText.trim())regs.push([u,el.innerText.trim().replace(/\s+/g,' ').slice(0,12)])});
  for(let i=0;i<regs.length;i++)for(let k=i+1;k<regs.length;k++){const A=regs[i][0],B=regs[k][0];const w=Math.min(A.r,B.r)-Math.max(A.l,B.l),h=Math.min(A.b,B.b)-Math.max(A.t,B.t);
   if(w>4&&h>4)ov.push([pi+1,'collide',Math.round(h),regs[i][1]+' ↔ '+regs[k][1]])}});
 return {out,ov}});
fs.writeFileSync(path.join(Q,'b3.json'),JSON.stringify(info.out));fs.writeFileSync(path.join(Q,'overflow.json'),JSON.stringify(info.ov));console.log('overflow',JSON.stringify(info.ov));
const pages=await p.$$('.page');
if(mode!='bg'){for(let i=0;i<pages.length;i++)fs.writeFileSync(path.join(Q,`pg${i}.png`),await pages[i].screenshot({type:'png'}));}
await p.evaluate(()=>{const st=document.createElement('style');st.textContent='*:not(#hb_a):not(#hb_b){color:transparent!important;-webkit-text-fill-color:transparent!important;-webkit-text-stroke-color:transparent!important;border-color:transparent!important;text-shadow:none!important}.gt,.cdn{background:none!important}';document.head.appendChild(st)});
for(let i=0;i<pages.length;i++)fs.writeFileSync(path.join(Q,`bg${i}.png`),await pages[i].screenshot({type:'png'}));
await b.close();process.exit(0)})().catch(e=>{console.error(e);process.exit(1)});
