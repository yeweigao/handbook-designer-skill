// 每页导出成图片（小红书 3:4 画布：1080×1440）：node pngs.js <project> <out_dir> [宽度px]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const dir=path.resolve(process.argv[2]);const out=path.resolve(process.argv[3]);const want=+(process.argv[4]||1080);fs.mkdirSync(out,{recursive:true});
const launch=async()=>{try{return await chromium.launch({args:['--no-sandbox']})}catch(e){const exe=process.env.HB_CHROME||require('child_process').execSync('which chromium || which chromium-browser || which google-chrome || true').toString().split('\n')[0].trim();if(!exe)throw e;return chromium.launch({executablePath:exe,args:['--no-sandbox']})}};
const friendly=e=>{const m=String(e&&e.message||e);if(/ERR_FILE_NOT_FOUND|ENOENT/.test(m))return '找不到 book.html：先运行 bash hb/run.sh <项目>';if(/Executable doesn.t exist|browserType\.launch|Failed to launch/i.test(m))return '浏览器启动失败：cd hb && npm install && npx playwright install chromium（或安装系统 Chrome/Edge）';return null};
(async()=>{const b=await launch();const html='file://'+path.join(dir,'book.html');
let p=await b.newPage({viewport:{width:900,height:1200}});await p.goto(html);const W=await p.evaluate(()=>document.querySelector('.page').getBoundingClientRect().width);await p.close();
p=await b.newPage({viewport:{width:900,height:1200},deviceScaleFactor:want/W});await p.goto(html,{waitUntil:'networkidle'});
await p.waitForFunction(()=>document.body.dataset.ready==1,{timeout:30000});await p.waitForTimeout(400);
const pages=await p.$$('.page');for(let i=0;i<pages.length;i++)fs.writeFileSync(path.join(out,`${String(i+1).padStart(2,'0')}.png`),await pages[i].screenshot({type:'png'}));
console.log(`图片 ${pages.length} 张 → ${out}（宽 ${want}px）`);await b.close();process.exit(0)})().catch(e=>{const f=friendly(e);if(f)console.error(f);else console.error(e);process.exit(1)});
