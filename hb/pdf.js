// usage: node pdf.js <projectDir> <out.pdf>
const {chromium}=require('playwright');const path=require('path');
const dir=path.resolve(process.argv[2]||'.');const out=path.resolve(process.argv[3]||path.join(dir,'handbook.pdf'));
// 先用 playwright 自带的 chromium；不行再找系统里的 chromium/chrome
const launch=async()=>{try{return await chromium.launch({args:['--no-sandbox']})}catch(e){const exe=require('child_process').execSync('which chromium || which chromium-browser || which google-chrome || true').toString().split('\n')[0].trim();if(!exe)throw e;return chromium.launch({executablePath:exe,args:['--no-sandbox']})}};
(async()=>{const b=await launch();
const p=await b.newPage();await p.goto('file://'+path.join(dir,'book.html'),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
await p.waitForFunction(()=>document.body.dataset.ready==1);await p.waitForTimeout(600);
if(process.env.HB_DRAFT)await p.evaluate(()=>document.querySelectorAll('.page').forEach(pg=>{const d=document.createElement('div');d.setAttribute('data-deco','1');   // 草稿水印
 d.style.cssText='position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:9999';
 d.innerHTML='<div style="transform:rotate(-32deg);font:800 104px/1 Inter,sans-serif;letter-spacing:.06em;color:rgba(230,30,40,.22);white-space:nowrap">草稿 DRAFT</div>';pg.appendChild(d)}));
await p.pdf({path:out,preferCSSPageSize:true,printBackground:true,tagged:true,outline:true});/* tagged/outline：较新的 playwright 支持，旧版会忽略 */await b.close();console.log('PDF',out);process.exit(0)})().catch(e=>{console.error(e);process.exit(1)});
