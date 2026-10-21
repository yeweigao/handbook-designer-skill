<script>
// ================= 内容版式网格（canon.py）=================
// 顺序：大标题撑满栏宽 → 各块补齐到行距的整数倍 → 文字栈补齐 → 照片/色块按文字栈定位（data-y0 / data-y1）→ 按行平分 → 自检
const CN={T:88,L:24,B:1000,W:794,H:1123,C:84,G:28,N:38,I:50,O:100};(()=>{const g=(document.body&&document.body.dataset.grid||'').split(',').map(Number);if(g.length==10)[CN.T,CN.L,CN.B,CN.W,CN.H,CN.C,CN.G,CN.N,CN.I,CN.O]=g})();   // 网格：hb.py 按画布写在 body data-grid
function cnPg(e){return e.closest('.page')}
// 字重跟随实际字级，标题收缩、换小画布与在线改字均走同一条规则。
function cnTypeWeight(size){const base=parseFloat(getComputedStyle(document.body).getPropertyValue('--bs'))||16;
 const r=size/base,ov=window.__hbWeightMode;
 if(ov==='semi')return r>=2.4?700:r>=1.6?600:r>=1.15?500:r>=1?400:600;
 if(ov==='thin')return r>=2.4?100:r>=1.75?200:r>=1.2?300:r>=1?400:r>=.875?500:600;
 if(ov==='light'||document.body.dataset.typography==='light')return r>=2.4?(parseInt(getComputedStyle(document.body).getPropertyValue('--display-w'))||200):r>=1.75?250:r>=1.2?300:r>=1?400:r>=.875?500:600;
 return r>=2.4?900:r>=1.6?700:r>=1.15?600:r>=1?400:r>=.875?500:600}
function cnTypeText(pg){const found=new Set(),w=document.createTreeWalker(pg,NodeFilter.SHOW_TEXT);let t;
 while(t=w.nextNode()){const e=t.parentElement;if(t.textContent.trim()&&!e.closest('svg,script,style,.cn-brand-graphic')&&getComputedStyle(e).display!='none')found.add(e)}return [...found]}
function cnWeight(e){const base=cnTypeWeight(parseFloat(getComputedStyle(e).fontSize));e.style.fontWeight=document.body.dataset.typography==='bold'&&e.closest('b,strong')?Math.min(900,base+200):base}
function cnTypography(){document.querySelectorAll('.page').forEach(pg=>cnTypeText(pg).forEach(cnWeight))}
function cnTypeQA(){if(document.body.dataset.typography!=='light')return [];const out=[];
 document.querySelectorAll('.page').forEach((pg,i)=>{const groups=new Map();
  cnTypeText(pg).forEach(e=>{const cs=getComputedStyle(e),s=+parseFloat(cs.fontSize).toFixed(2),w=parseFloat(cs.fontWeight);if(!s||!w)return;
   const q=groups.get(s)||{min:1000,max:0,text:''};q.min=Math.min(q.min,w);q.max=Math.max(q.max,w);q.text=(e.textContent||'').trim().slice(0,18);groups.set(s,q)});
  let larger=0;[...groups].sort((a,b)=>b[0]-a[0]).forEach(([s,q])=>{
   if(q.min<larger||s<=20&&q.min<400)out.push([i+1,'cn-weight',0,`${s}px / ${q.min}：${q.text}`]);larger=Math.max(larger,q.max)})});return out}
function cnR(e){const P=cnPg(e).getBoundingClientRect(),r=e.getBoundingClientRect();return{top:r.top-P.top,bottom:r.bottom-P.top,left:r.left-P.left,right:r.right-P.left,height:r.height,width:r.width}}
function cnLines(e){   // 每一行的宽度（按竖直方向重叠归行：不同字体回退的字高度不同，不能按中线分组）
 const r=document.createRange();r.selectNodeContents(e);const L=[];
 [...r.getClientRects()].filter(q=>q.width>0).sort((a,b)=>a.top-b.top).forEach(q=>{const o=L.find(l=>Math.min(l.b,q.bottom)-Math.max(l.t,q.top)>.5*Math.min(l.b-l.t,q.height));
  if(o){o.l=Math.min(o.l,q.left);o.r=Math.max(o.r,q.right);o.t=Math.min(o.t,q.top);o.b=Math.max(o.b,q.bottom)}else L.push({l:q.left,r:q.right,t:q.top,b:q.bottom})});
 return L.map(o=>o.r-o.l)}
function cnFit(e){   // 大标题：量出最长一行，缩放到正好撑满栏宽（有上限）；在允许折行的地方（空格、·、，）折成 2–3 行能大很多时就折行；太长也折行
 const cs=getComputedStyle(e);const w=e.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
 const hasBr=!!e.querySelector('br');
 const brN=hasBr?(e.innerText||'').split('\n').length:0;   // 作者显式断了几行，就必须渲染成几行（不允许某一作者行再折）
 const mx=+e.dataset.fit,mn=+(e.dataset.min||Math.min(mx,44)),maxl=hasBr?brN:+(e.dataset.lines||3);   // 显式断行时行数固定为作者行数，字号缩到每行都放得下为止
 const set=s=>{e.style.fontSize=s+'px';cnWeight(e);const q=CN.L/2;e.style.lineHeight=(Math.ceil(s*1.04/q)*q)+'px'};const longest=()=>Math.max(0,...cnLines(e));
 e.classList.remove('cn-wrap','cn-any');set(100);let s=Math.floor(Math.min(mx,100*w/Math.max(1,longest())));
 if(s<mx){e.classList.add('cn-wrap');let best=0;
  for(let t=mx;t>=Math.max(mn,Math.ceil(s*1.3));t-=2){set(t);if(longest()<=w+.5&&cnLines(e).length<=maxl){best=t;break}}
  if(best){s=best}else if(s>=mn){e.classList.remove('cn-wrap')}
  else{let ok=false;for(let t=s<mn?mn:s;t>=mn;t-=2){set(t);if(longest()<=w+.5&&cnLines(e).length<=maxl){ok=true;s=t;break}}if(!ok){e.classList.add('cn-any');for(let t=mn+12;t>=mn;t-=2){set(t);if(longest()<=w+.5&&cnLines(e).length<=maxl){ok=true;s=t;break}}}if(!ok){s=mn;e.dataset.cnw='fit'}}}
 else if(s<mn){s=mn;e.dataset.cnw='fit'}
 set(s)}
function cnSnap(e,top){   // 高度补齐到行距的整数倍（重排时从原始内边距算起，不累加）
 if(e.dataset.p0==null){const cs=getComputedStyle(e);e.dataset.p0=parseFloat(cs.paddingTop)+','+parseFloat(cs.paddingBottom)}
 const [pt,pb]=e.dataset.p0.split(',').map(Number);e.style.paddingTop=pt+'px';e.style.paddingBottom=pb+'px';
 const h=e.getBoundingClientRect().height-pt-pb;const d=(CN.L-h%CN.L)%CN.L;if(d>.5){if(top)e.style.paddingTop=(pt+d)+'px';else e.style.paddingBottom=(pb+d)+'px'}}
function cnVal(v){if(String(v).includes('|')){const xs=String(v).split('|').map(cnVal).filter(x=>x!=null);return xs.length?Math.max(...xs):null}const m=String(v).match(/^([\w-]+)\.(top|bottom)([+-][\d.]+)?$/);if(!m)return CN.T+parseFloat(v)*CN.L;const t=document.getElementById(m[1]);if(!t)return null;return cnR(t)[m[2]]+(m[3]?parseFloat(m[3])*CN.L:0)}
function cnNeed(row){   // 一行至少要多高：文字的实际高度 + 图片的最小高度（图片吸收剩下的）
 let m=0;const cols=row.children.length==1&&!row.firstElementChild.classList.contains('cn-ibox')&&!row.firstElementChild.classList.contains('cn-cell')?[...row.firstElementChild.children]:[...row.children];
 cols.forEach(c=>{if(c.classList.contains('cn-ibox'))return;let need=0;
  if(c.querySelector(':scope>.cn-ibox')){[...c.children].forEach(k=>{need+=k.classList.contains('cn-ibox')?(+k.dataset.minh||72):k.getBoundingClientRect().height})}
  else{const cs=getComputedStyle(c);const inner=[...c.children].reduce((s,k)=>s+k.getBoundingClientRect().height,0);need=inner+parseFloat(cs.paddingTop)+parseFloat(cs.paddingBottom)}
  m=Math.max(m,need)});return Math.ceil(m/CN.L)*CN.L}
function cnRows(e){const rows=[...e.children].filter(c=>c.classList.contains('cn-row'));if(!rows.length)return;
 const g=String(e.dataset.gap||'0'),px=g.endsWith('px'),gp=px?parseFloat(g):parseFloat(g)*CN.L;const tot=e.clientHeight-gp*(rows.length-1);
 rows.forEach(r=>{r.style.height='auto'});const need=rows.map(cnNeed);const sum=need.reduce((a,b)=>a+b,0);
 let hs;if(sum<=tot){const extra=tot-sum;const each=Math.floor(extra/rows.length/CN.L)*CN.L;hs=need.map(n=>n+each);hs[hs.length-1]+=tot-hs.reduce((a,b)=>a+b,0)}
 else{const base=Math.floor(tot/rows.length/CN.L)*CN.L;hs=rows.map(()=>base);hs[hs.length-1]+=tot-base*rows.length}
 // 固定页内的行不能参与打印分页；普通流的第二行会被 Chromium 推到下一页，再被 page 的 overflow 裁掉。
 let top=0;rows.forEach((r,i)=>{const height=Math.max(0,hs[i]);r.style.position='absolute';r.style.left='0';r.style.width='100%';r.style.top=top+'px';r.style.height=height+'px';r.style.marginTop='0';top+=height+gp})}
function cnPlace(){const all=[...document.querySelectorAll('.page.cn [data-y0],.page.cn [data-y1],.page.cn [data-gold],.page.cn [data-rows]')];
 // 先排文字栈（它们只依赖别的文字栈），再排照片、色块和按行平分的区域（它们依赖文字栈的最终位置）
 [...all.filter(e=>e.classList.contains('cn-st')),...all.filter(e=>!e.classList.contains('cn-st'))].forEach(e=>{
 const st=e.classList.contains('cn-st');const y0=e.dataset.y0!=null?cnVal(e.dataset.y0):null,y1=e.dataset.y1!=null?cnVal(e.dataset.y1):null;
 if(st){const h=e.getBoundingClientRect().height;let top=y0!=null?y0:(y1!=null?Math.max(CN.T,y1-h):null);
  if(e.dataset.gold!=null){const lim=y1!=null?y1:CN.B;top=Math.min(CN.T+(+e.dataset.gold)*CN.L,lim-h)}
  if(top!=null){e.style.top=top+'px';e.style.bottom='auto'}
  if(e.classList.contains('cn-flow')&&y0!=null&&y1!=null)e.style.height=Math.max(CN.L,y1-y0)+'px'}
 else if(y0!=null||y1!=null){const R0=cnR(e);const t=y0!=null?y0:R0.top,b=y1!=null?y1:R0.bottom;e.style.top=t+'px';e.style.height=Math.max(0,b-t)+'px';e.style.bottom='auto'}
 if(e.dataset.rows!=null)cnRows(e)})}
function cnText(e){const a=[];const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let t;while(t=w.nextNode()){const el=t.parentElement;if(!t.textContent.trim()||el.closest('.deco'))continue;const fs=parseFloat(getComputedStyle(el).fontSize);const r=document.createRange();r.selectNodeContents(t);
 for(const q of r.getClientRects()){if(!q.width)continue;const m=(q.top+q.bottom)/2;a.push({l:q.left,r:q.right,t:m-.42*fs,b:m+.42*fs,el})}}return a}
function cnGlyph(e){// 装饰大字（章节号、条目数）真正有墨的范围：canvas 量字形，按行盒算基线
 const t=(e.innerText||'').trim();if(!t||t.includes('\n'))return null;const cs=getComputedStyle(e);const c=cnGlyph.c||(cnGlyph.c=document.createElement('canvas').getContext('2d'));
 c.font=`${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;const m=c.measureText(t);const R=e.getBoundingClientRect();const lh=parseFloat(cs.lineHeight)||R.height;
 const fa=m.fontBoundingBoxAscent,fd=m.fontBoundingBoxDescent;const base=R.top+(lh-(fa+fd))/2+fa;const x0=cs.textAlign=='right'?R.right-m.width:R.left;
 return {l:x0-m.actualBoundingBoxLeft,r:x0+m.actualBoundingBoxRight,t:base-m.actualBoundingBoxAscent,b:base+m.actualBoundingBoxDescent}}
function cnCheck(){const out=[];const pages=[...document.querySelectorAll('.page')];document.querySelectorAll('.cn-st[data-bad]').forEach(s=>delete s.dataset.bad);const pi=e=>pages.indexOf(cnPg(e))+1;const tx=e=>(e.innerText||'').trim().replace(/\s+/g,' ').slice(0,14);
 pages.forEach(pg=>{if(!pg.classList.contains('cn'))return;const P=pg.getBoundingClientRect();const sts=[...pg.querySelectorAll('.cn-st')].map(s=>[s,cnText(s)]);
  sts.forEach(([s,R])=>{if(!R.length)return;const top=Math.min(...R.map(q=>q.t))-P.top,bot=Math.max(...R.map(q=>q.b))-P.top;
   const d=s.dataset.free!=null?0:Math.max(CN.T-6-top,bot-CN.B-6);if(d>2){out.push([pi(s),'cn-over',Math.round(d),tx(s)]);s.dataset.bad=1}
   if(s.dataset.y1!=null&&!s.classList.contains('cn-flow')){const lim=cnVal(s.dataset.y1);if(lim!=null){const over=bot-lim-4;if(over>2){out.push([pi(s),'cn-over',Math.round(over),tx(s)]);s.dataset.bad=1}}}   // 文字栈的下沿越过了它该停的地方（y1：另一个栈的上沿 / 某一行）
   if(s.dataset.floor!=null){const f=CN.T+(+s.dataset.floor)*CN.L-(top);if(f>2){out.push([pi(s),'cn-over',Math.round(f),tx(s)]);s.dataset.bad=1}}
   if(s.dataset.in){const f=document.getElementById(s.dataset.in);if(f){const F=f.getBoundingClientRect();const dd=Math.max(F.top+12-(top+P.top),(bot+P.top)-(F.bottom-12));if(dd>2)out.push([pi(s),'cn-in',Math.round(dd),tx(s)])}}});
  for(let i=0;i<sts.length;i++)for(let j=i+1;j<sts.length;j++){let hit=0;for(const a of sts[i][1]){for(const b of sts[j][1]){const w=Math.min(a.r,b.r)-Math.max(a.l,b.l),hh=Math.min(a.b,b.b)-Math.max(a.t,b.t);if(w>1&&hh>1){hit=Math.max(hit,hh)}}}
   if(hit){out.push([pi(sts[i][0]),'cn-collide',Math.round(hit),tx(sts[i][0])+' ↔ '+tx(sts[j][0])]);sts[i][0].dataset.bad=1;sts[j][0].dataset.bad=1}}
  sts.forEach(([s])=>{if(s.dataset.bad==null)return;[s.dataset.y0,s.dataset.y1].filter(Boolean).forEach(v=>(String(v).match(/[\w-]+(?=\.(top|bottom))/g)||[]).forEach(id=>{const t=document.getElementById(id);if(t&&t.classList.contains('cn-st'))t.dataset.bad=1}))});
  pg.querySelectorAll('.cn-row').forEach(rw=>{const R=rw.getBoundingClientRect();let mb=-1e9;cnText(rw).forEach(q=>mb=Math.max(mb,q.b));if(mb>R.bottom+2)out.push([pi(rw),'cn-row',Math.round(mb-R.bottom),tx(rw)])});
  pg.querySelectorAll('[data-minh]').forEach(b=>{const h=b.getBoundingClientRect().height;if(h<+b.dataset.minh-1)out.push([pi(b),'cn-small',Math.round(h),'']) });
  pg.querySelectorAll('.cn-pic img').forEach(im=>{const r=im.getBoundingClientRect(),small=im.closest('[data-image-role="supporting"]'),min=small?Math.max(72,3*CN.L):150;if(r.height>0&&r.height<min)out.push([pi(im),'cn-imgarea',Math.round(r.height),(im.getAttribute('src')||'').split('/').pop()||'']) });   // 主图可见高度不足（F07/cn-imgarea：合照/主体被压成一条边）
  pg.querySelectorAll('[data-below]').forEach(f=>{const t=document.getElementById(f.dataset.below);if(!t)return;const R=cnText(t);if(!R.length)return;const d=Math.max(...R.map(q=>q.b))-(f.getBoundingClientRect().top-12);if(d>2)out.push([pi(f),'cn-band',Math.round(d),tx(t)])});   // 正文压进下方色带
  pg.querySelectorAll('[data-clear]').forEach(f=>{const t=document.getElementById(f.dataset.clear);if(!t)return;const d=f.getBoundingClientRect().bottom-(t.getBoundingClientRect().top-12);if(d>2)out.push([pi(f),'cn-in',Math.round(d),tx(t)])});
  if(!(pg.innerText||'').trim()&&!pg.querySelector('img'))out.push([pi(pg),'cn-over',0,'空白页（版面没排出来）']);
  pg.querySelectorAll('[data-cnw]').forEach(e=>out.push([pi(e),'cn-fit',0,tx(e)]));
  pg.querySelectorAll(':scope > .cn-num.deco, :scope > .cn-v > .cn-num.deco').forEach(d=>{const g=cnGlyph(d);if(!g)return;let hit=0,who='';   // 装饰大字压到文字
   sts.forEach(([s,R])=>R.forEach(q=>{const w=Math.min(q.r,g.r)-Math.max(q.l,g.l),hh=Math.min(q.b,g.b)-Math.max(q.t,g.t);if(w>4&&hh>4&&hh>hit){hit=hh;who=tx(s)}}));
   if(hit)out.push([pi(d),'cn-deco',Math.round(hit),(d.innerText||'').trim()+' ↔ '+who])})});
 return out.concat(cnTypeQA())}
function sjRail(pg,o){   // 节拍列：沿一条看不见的竖轴（ax）排小色块，色块从轴往页边长；o.dir=1 往右长、-1 往左长；o.t..o.b 是可用的高度
 const P=pg.getBoundingClientRect(),U=Math.round(CN.L/2),lk=o.lk,beat=lk==='beat',tone=lk==='tone',rnd=o.rnd,cs=o.cs;
 const sel=beat?'.cn-h,.cn-num,.cn-lab,.cn-disp,.cn-sub,.cn-tx p,.cn-li li,.cn-cap,.cn-qt':'.cn-h,.cn-num,.cn-disp';
 const ys=[...pg.querySelectorAll(sel)].filter(e=>!e.closest('.deco')&&!e.classList.contains('deco')&&e.getBoundingClientRect().height>0).map(e=>{const q=e.getBoundingClientRect(),st=getComputedStyle(e),fs=parseFloat(st.fontSize),lh=Math.min(q.height,parseFloat(st.lineHeight)||fs*1.4);return Math.round(q.top-P.top+Math.max(0,(lh-fs)/2))}).sort((a,b)=>a-b);
 const gap=beat?2*CN.L:3*CN.L,B=[];let last=o.t-gap;
 ys.forEach(y=>{if(y<o.t||y>o.b-U*2||y-last<gap)return;B.push(y);last=y});
 if(beat){const snap=y=>CN.T+Math.round((y-CN.T)/CN.L)*CN.L+Math.round((CN.L-CN.L*.6)/2),pts=[o.t-U,...B,o.b],add=[];   // 留白长的地方补拍，落在行线上
  for(let i=0;i<pts.length-1;i++){const g=pts[i+1]-pts[i];if(g>CN.L*5){const k=Math.round(g/(CN.L*3));for(let j=1;j<k;j++)add.push(snap(pts[i]+g*j/k))}}
  add.forEach(y=>{if(y>=o.t&&y<=o.b-U*2&&B.every(b=>Math.abs(b-y)>=CN.L*1.5))B.push(y)});B.sort((a,b)=>a-b)}
 else if(lk==='classic')for(let i=B.length-1;i>0;i--)if(rnd()<.3)B.splice(i,1);
 const greys=['#8F8A80','#B9B3A8','#6E6A63'],wt=beat?[1,3,5]:[1,1,1];let prev=-1,pb=null;   // 节奏：黄多、蓝次之、红最少
 const pick=()=>{if(tone){prev=(prev+1)%3;return greys[prev]}let tot=0;const w=wt.map((x,i)=>i===prev?0:x);w.forEach(x=>tot+=x);let r=rnd()*tot;for(let i=0;i<3;i++){if((r-=w[i])<0){prev=i;return cs[i]}}prev=2;return cs[2]};
 B.forEach((y,i)=>{const sp=(i+1<B.length?B[i+1]:o.b)-y,room=Math.min(sp-U,Math.max(U,sp*.6));if(room<U)return;const r=rnd();   // 色块最多占到下一拍的六成，拍与拍之间留白
  let hh=beat?(r<.18?U:r<.48?2*U:r<.7?3*U:r<.85?4*U:r<.95?6*U:8*U):(r<.45?U:r<.85?2*U:3*U);while(hh>room&&hh>U)hh-=U;
  const ws=hh===U?[4*U,3*U]:hh<=3*U?[hh,4*U,3*U,hh]:[4*U,3*U];let ww=Math.min(o.w,ws[Math.floor(rnd()*ws.length)]);if(!beat)ww=Math.min(ww,3*U);
  const x0=o.dir>0?o.ax:o.ax-ww;if(o.hit&&o.hit(x0,x0+ww,y,y+hh))return;
  if(beat&&pb&&y-pb>=U*1.5&&rnd()<.6){const ly=Math.round((pb+y)/2),a=o.dir>0?o.ax-10:o.edge,b=o.dir>0?o.edge:o.ax+10;if(!(o.hit&&o.hit(Math.min(a,b),Math.max(a,b),ly-2,ly+2)))o.el('sj-rail',`left:${Math.min(a,b)}px;top:${ly-.75}px;width:${Math.abs(b-a)}px;height:1.5px;background:${o.ink}`)}
  o.el('sj-rail',`left:${x0}px;top:${y}px;width:${ww}px;height:${hh}px;background:${pick()}`);pb=y+hh})}
function sjStructure(){document.querySelectorAll('.page.cn').forEach(pg=>{const m=pg.querySelector('.sj-meta');if(!m)return;   // 风格派：量出版面的结构，再画线、上色格、排节拍
 pg.querySelectorAll('.sj-line,.sj-blk,.sj-rail,.sj-tick,.sj-pn').forEach(e=>e.remove());pg.querySelectorAll('.cn-fo .cn-num').forEach(e=>e.style.visibility='');
 const P=pg.getBoundingClientRect(),W=P.width,H=P.height,cs=m.dataset.c.split(','),ink=m.dataset.ink,lk=m.dataset.look,full=m.dataset.full==='1',chap=m.dataset.chap==='1',beat=lk==='beat',tone=lk==='tone';
 let sd=(+pg.dataset.n||1)*7919;const rnd=()=>(sd=sd*16807%2147483647)/2147483647,U=Math.round(CN.L/2);
 const T=tone?1.5:beat?2.5:(full?10:6),lc=tone?'rgba(20,20,20,.42)':ink;
 const R=e=>{const q=e.getBoundingClientRect();return{l:q.left-P.left,r:q.right-P.left,t:q.top-P.top,b:q.bottom-P.top}};
 const el=(c,css)=>{const e=document.createElement('i');e.className=c+' deco';e.style.cssText=css;pg.appendChild(e);return e};
 const segs=[];const add=(o,p,a,b)=>{if(b-a>=8)segs.push({o,p,a,b})};
 // 1 版面里已有的分区（色块、图片、错位条目的格子）→ 主线。节奏画法：只要条目格之间的细线，图片不描边
 const parts=beat?[]:[...pg.querySelectorAll('.cn-field,.cn-pic')];pg.querySelectorAll('.cn-rows').forEach(rs=>{const g=String(rs.dataset.gap||'0');if(g==='0'||parseFloat(g)<=10&&g.endsWith('px'))rs.querySelectorAll(':scope>.cn-row>.cn-ibox,:scope>.cn-row>.cn-cell').forEach(e=>parts.push(e))});
 parts.forEach(e=>{if(e.closest('.deco'))return;const q=R(e);if(q.b-q.t<4||q.r-q.l<4)return;const l=Math.max(0,q.l),r=Math.min(W,q.r),t=Math.max(0,q.t),b=Math.min(H,q.b);
  if(t>2)add('h',t,l,r);if(b<H-2)add('h',b,l,r);if(l>2)add('v',l,t,b);if(r<W-2)add('v',r,t,b)});
 const merge=L=>{const out=[];['h','v'].forEach(o=>{const S=L.filter(s=>s.o===o).sort((x,y)=>x.p-y.p),used=S.map(()=>false);
  for(let i=0;i<S.length;i++){if(used[i])continue;const grp=[S[i]];used[i]=true;for(let j=i+1;j<S.length;j++)if(!used[j]&&Math.abs(S[j].p-S[i].p)<=10){grp.push(S[j]);used[j]=true}
   const p=grp.reduce((s,x)=>s+x.p,0)/grp.length,iv=grp.map(x=>[x.a,x.b]).sort((x,y)=>x[0]-y[0]);let cur=iv[0].slice();
   for(const [a,b] of iv.slice(1)){if(a<=cur[1]+12)cur[1]=Math.max(cur[1],b);else{out.push({o,p,a:cur[0],b:cur[1]});cur=[a,b]}}out.push({o,p,a:cur[0],b:cur[1]})}});return out};
 let lines=merge(segs);
 const pics=[...pg.querySelectorAll('.cn-pic,.cn-ibox')].map(R);const hit=(x0,x1,y0,y1)=>pics.some(q=>q.l<x1-1&&q.r>x0+1&&q.t<y1-1&&q.b>y0+1);
 const obst=[...pg.querySelectorAll('.cn-pic,.cn-ibox,.cn-field,.cn-st')].filter(e=>!e.closest('.deco')).map(R),busy=(x0,x1,y0,y1)=>obst.some(q=>q.l<x1-1&&q.r>x0+1&&q.t<y1-1&&q.b>y0+1);
 const rail=(ax,dir,t,b,edge,w)=>sjRail(pg,{ax,dir,t,b,edge,w:w||4*U,lk,cs,ink,rnd,el,hit:busy});
 if(!full){
  const odd=(+pg.dataset.n||1)%2===1,L0=odd?CN.I:CN.O,R0=L0+6*CN.C+5*CN.G,outerX=odd?R0+CN.G/2:L0-CN.G/2,innerX=odd?L0-CN.G/2:R0+CN.G/2;
  const sx0=odd?outerX:0,sx1=odd?W:outerX,ix0=odd?0:innerX,ix1=odd?innerX:W,ax=odd?R0+24:L0-24,edge=odd?W:0;
  // 2 标题区和正文之间：已有分区线就用它，没有就补一条主线；切口一侧标题区那一格上色（节奏画法：一根红条挂在节拍轴上）
  const hd=[...pg.querySelectorAll('.cn-st')].filter(s=>s.querySelector('.cn-disp')).map(s=>[s,R(s)]).sort((a,b)=>a[1].t-b[1].t)[0];
  let hy=null;
  if(hd&&hd[1].t<H*.45){const q=Object.assign({},hd[1]),ks=[...hd[0].children];let k=0,hb=null,nin=null;   // 页头 = 栈里开头的小标签、大标题、副题、导语；后面还有正文时，线画在页头下面
   for(;k<ks.length;k++){if(!ks[k].matches('.cn-lab,.cn-disp,.cn-sub,.cn-t20,.sj-ix'))break;const c=R(ks[k]);if(c.b>c.t)hb=c.b}
   if(hb!==null&&k<ks.length){q.b=hb;nin=R(ks[k]).t}
   const ex=lines.find(s=>s.o==='h'&&s.p>q.b-2&&s.p<q.b+3*CN.L&&(s.b-s.a)>W*.4);
   if(ex)hy=ex.p;else{const nx=[...pg.querySelectorAll('.cn-st,.cn-rows,.cn-pic')].filter(e=>e!==hd[0]).map(R).filter(x=>x.t>q.b+2).map(x=>x.t).concat(nin!==null?[nin]:[]);const nt=nx.length?Math.min(...nx):q.b+2*CN.L;
    if(nt-q.b>=24){hy=Math.min(q.b+CN.L,(q.b+nt)/2);lines.push(beat?{o:'h',p:hy,a:odd?innerX:0,b:odd?W:innerX}:{o:'h',p:hy,a:odd?0:outerX,b:odd?outerX:W})}}}
  let rt=hy||CN.T+2*CN.L;
  if(beat){const bh=Math.round(Math.min(hy?hy-U:CN.T+CN.L,CN.T+CN.L*1.5)),bx=odd?ax:ax-4*U;
   if(!hit(bx,bx+4*U,0,bh)){el('sj-blk',`left:${bx}px;top:0;width:${4*U}px;height:${bh}px;background:${cs[0]}`);if(chap)rt=bh+CN.L}}
  else if(hy&&!hit(sx0,sx1,0,hy)){el('sj-blk',`left:${sx0}px;top:0;width:${sx1-sx0}px;height:${hy}px;background:${cs[0]}`);lines.push({o:'v',p:outerX,a:0,b:hy})}
  // 3 页脚一行：经典 / 无线 = 订口一小格蓝、切口一小格黄；节奏 = 一根通栏细线，切口一侧一格黄（第 6 栏 + 页边），页码就在黄格里
  const fo=pg.querySelector('.cn-fo');let rb=CN.B;
  if(fo){const near=lines.filter(s=>s.o==='h'&&s.p<CN.B+CN.L/2+2&&s.p>CN.B-CN.L/2&&(s.b-s.a)>W*.4).sort((a,b)=>b.p-a.p)[0],yf=near?near.p:CN.B+CN.L/2;let rg=[[odd&&beat?innerX:0,odd||!beat?W:innerX]];pics.filter(q=>q.t<yf&&q.b>yf).forEach(q=>{rg=rg.flatMap(([a,b])=>q.r<=a||q.l>=b?[[a,b]]:[[a,q.l],[q.r,b]].filter(([x,y])=>y-x>8))});
   if(!near)rg.forEach(([a,b])=>lines.push({o:'h',p:yf,a,b}));else{near.a=Math.min(near.a,rg[0][0]);near.b=Math.max(near.b,rg[rg.length-1][1])}rb=yf-CN.L/2;
   const pn=(x0,x1,big)=>{const nb=fo.querySelector('.cn-num');if(!nb)return;const e=document.createElement('div');e.className='sj-pn'+(big?' sj-pnb':'');e.textContent=nb.textContent;e.style.cssText=`left:${x0}px;top:${yf}px;width:${x1-x0}px;height:${H-yf}px;color:${ink}`;pg.appendChild(e);nb.style.visibility='hidden'};
   if(beat){const cx=odd?L0+5*(CN.C+CN.G)-CN.G/2:L0+CN.C+CN.G/2,a=odd?cx:0,b=odd?W:cx;
    if(!hit(a,b,yf,H)){el('sj-blk',`left:${a}px;top:${yf}px;width:${b-a}px;height:${H-yf}px;background:${cs[2]}`);lines.push({o:'v',p:cx,a:yf,b:H});pn(a,b,true)}}
   else{if(!hit(sx0,sx1,yf,H)){el('sj-blk',`left:${sx0}px;top:${yf}px;width:${sx1-sx0}px;height:${H-yf}px;background:${cs[2]}`);lines.push({o:'v',p:outerX,a:yf,b:H});pn(sx0,sx1,false)}
    if(!hit(ix0,ix1,yf,H)){el('sj-blk',`left:${ix0}px;top:${yf}px;width:${ix1-ix0}px;height:${H-yf}px;background:${cs[1]}`);lines.push({o:'v',p:innerX,a:yf,b:H})}}}
  // 4 节拍：切口页边里一列小色块，跟着条目走（经典稀、节奏密、无线是灰）
  rail(ax,odd?1:-1,rt+(beat?U:CN.L),rb,edge,beat?4*U:3*U);
 }
 // 封面、封底（节奏画法）：Python 留好的节拍列
 pg.querySelectorAll('.sj-railbox').forEach(b=>{const q=R(b),d=+b.dataset.dir||1;rail(d>0?q.l:q.r,d,q.t,q.b,d>0?q.r:q.l,q.r-q.l)});
 // 5 画线（端头各伸出半个线宽，T 形交接对得上）
 merge(lines).forEach(s=>{const h=s.o==='h',a0=s.a>1?s.a-T/2:0,a1=s.b<(h?W:H)-1?s.b+T/2:(h?W:H);
  el('sj-line',h?`left:${a0}px;top:${s.p-T/2}px;width:${a1-a0}px;height:${T}px;background:${lc}`:`left:${s.p-T/2}px;top:${a0}px;width:${T}px;height:${a1-a0}px;background:${lc}`)})})}
function cnQA(){document.body.dataset.cnqa=JSON.stringify(cnCheck())}
function cnReading(){const en=!/^(zh|ja|ko)(-|$)/i.test(document.documentElement.lang||'zh');
 const wide=5*CN.C+4*CN.G;
 document.querySelectorAll('.page.cn .cn-tx:not(.cn-cols2)').forEach(e=>{
  if(e.dataset.reading==='keep')return;
  if(e.dataset.reading==='columns'){e.classList.add('cn-cols2');e.style.maxWidth='none';return}
  if(e.getBoundingClientRect().width<wide-1)return;
  const ps=[...e.querySelectorAll(':scope > p')];
  if(ps.length>1&&ps.every(p=>(p.textContent||'').replace(/\s/g,'').length<(en?120:100)))return;
  if((e.textContent||'').replace(/\s/g,'').length<(en?120:100))return;
  e.classList.add('cn-cols2');e.style.maxWidth='none'})}
function cnLayout(){cnTypography();document.querySelectorAll('.page.cn .cn-snap').forEach(e=>cnSnap(e,false));
 document.querySelectorAll('.page.cn .cn-st').forEach(e=>cnSnap(e,e.dataset.anchor=='bottom'));cnPlace()}
function canon(){document.querySelectorAll('.page.cn [data-fit]').forEach(e=>{e.dataset.fit0=e.dataset.fit;cnFit(e)});cnReading();cnLayout();
 // 放不下（出版心 / 出色块 / 互压 / 条目行放不下 / 图被挤小）→ 这一页的大标题先缩小一档再排，最多 6 轮；标题也是“吸收体”
 const pages=[...document.querySelectorAll('.page')];
 const bads=()=>new Set(cnCheck().filter(o=>o[1]!='cn-fit'&&o[1]!='cn-imgarea').map(o=>o[0]));   // cn-fit / cn-imgarea 是诊断项，不能靠缩字号修复，不参与收缩循环
 const shrink=()=>{for(let it=0;it<6;it++){const bad=bads();if(!bad.size)break;let changed=false;
  bad.forEach(pn=>{pages[pn-1].querySelectorAll('[data-fit]').forEach(e=>{const cur=parseFloat(e.style.fontSize)||+e.dataset.fit;const mn=+(e.dataset.min||44);
   if(cur>mn+1){e.dataset.fit=Math.max(mn,Math.floor(cur*.86));cnFit(e);changed=true}})});
  if(!changed)break;cnLayout()}};
 // 第一档：插图先让——出问题的文字栈里的图按整行缩矮（最少到 data-fmin），字号不动
 for(let it=0;it<24;it++){cnCheck();const fs=[...document.querySelectorAll('.cn-st[data-bad] .cn-figi[data-fh]')].filter(f=>parseFloat(f.style.height)-CN.L>=+f.dataset.fmin-.5);if(!fs.length)break;
  fs.forEach(f=>{f.style.height=(parseFloat(f.style.height)-CN.L)+'px'});cnLayout()}
 // 再让空白：块与块之间超过 1 行的间距逐行收到 1 行（space 块收到 0），仍在行线上
 for(let it=0;it<8;it++){cnCheck();const rg=[...document.querySelectorAll('.cn-st[data-bad] [data-rg]')];rg.forEach(g=>{g.style.rowGap='0px';delete g.dataset.rg});   // 卡片之间的行间距（卡片有顶线，收到 0 也分得开）
  const gs=[...document.querySelectorAll('.cn-st[data-bad] [data-g]')].filter(g=>+g.dataset.g>(g.dataset.gk?0:1));if(!gs.length&&!rg.length)break;if(rg.length&&!gs.length){cnLayout();continue}
  gs.forEach(g=>{g.dataset.g=+g.dataset.g-1;if(g.dataset.gk)g.style.height=(+g.dataset.g*CN.L)+'px';else g.style.marginTop=(+g.dataset.g*CN.L)+'px'});cnLayout()}
 // 最后让书写线：每组多行书写线逐行收（至少留 1 行），记在 body.dataset.cnlines，doctor 会列出来
 const lnp=new Set();
 for(let it=0;it<6;it++){cnCheck();const by=new Map();document.querySelectorAll('.cn-st[data-bad] .cn-ln[data-x]:not([style*="none"])').forEach(l=>by.set(l.parentElement,l));if(!by.size)break;
  by.forEach(l=>{l.style.display='none';lnp.add(pages.indexOf(l.closest('.page'))+1)});cnLayout()}
 if(lnp.size)document.body.dataset.cnlines=[...new Set([...(document.body.dataset.cnlines||'').split(',').filter(Boolean).map(Number),...lnp])].sort((a,b)=>a-b).join(',');
 shrink();
 // 第二档：标题缩到底还放不下 → 这一页的辅助字号（导语、小标题、标签、编号）回到行距 24 时的比例，正文字号不变（.cn-tight，doctor 会列出来）
 const still=[...bads()].filter(pn=>!pages[pn-1].classList.contains('cn-tight')&&getComputedStyle(pages[pn-1]).getPropertyValue('--s').trim()!='1');
 if(still.length){still.forEach(pn=>{const pg=pages[pn-1];pg.classList.add('cn-tight');pg.querySelectorAll('[data-fit]').forEach(e=>{e.dataset.fit=e.dataset.fit0||e.dataset.fit;cnFit(e)})});cnLayout();shrink()}
 document.body.dataset.cntight=pages.map((p,i)=>p.classList.contains('cn-tight')?i+1:0).filter(Boolean).join(',');
 cnQA()}
function grow(){document.querySelectorAll('.cn-flow').forEach(f=>{const bx=[...f.querySelectorAll('.cn-bx')];if(!bx.length||f.querySelector('.cn-fill'))return;const last=f.lastElementChild;const free=f.getBoundingClientRect().bottom-last.getBoundingClientRect().bottom;   // 书写页没有自动铺线时：方框按整行长高，吃掉剩下的空白
 const rows=[...new Set(bx.map(b=>Math.round(b.getBoundingClientRect().top)))];const add=Math.min(Math.floor(free/rows.length/CN.L),4)*CN.L;if(add>0)bx.forEach(b=>{b.style.height=(b.offsetHeight+add)+'px'})})}
// 内容（文字和图片）实际落到哪里：装饰（.deco 几何覆盖、出血图）可以压出边界，不算溢出
function cbottom(e){let mb=-1e9;const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let t;
 while(t=w.nextNode()){if(!t.textContent.trim())continue;const el=t.parentElement;if(el.closest('.deco')||getComputedStyle(el).display=='none'||el.closest('[style*="display: none"]'))continue;const r=document.createRange();r.selectNodeContents(t);for(const q of r.getClientRects())mb=Math.max(mb,q.bottom)}
 return mb}
function overBy(e){const b=cbottom(e);return b>-1e8?b-e.getBoundingClientRect().bottom:0}
function fit(){document.querySelectorAll('.rcp').forEach(r=>{const base=parseFloat(getComputedStyle(r).fontSize);let fs=base;
 const over=()=>[...r.querySelectorAll('.rcell')].some(c=>overBy(c)>1)||overBy(r)>1;
 while(over()&&fs>base*0.84){fs-=0.25;r.style.fontSize=fs+'px'}
 r.querySelectorAll('.rband.auto').forEach(b=>{if(b.getBoundingClientRect().height<130)b.style.display='none'});
 // 没有补位图带的页：字号整体放大（最多 +15%），把版面撑满
 if(r.classList.contains('grow')&&!over()){while(!over()&&fs<base*1.15){fs+=0.25;r.style.fontSize=fs+'px'}if(over()){fs-=0.25;r.style.fontSize=fs+'px'}}
 r.dataset.fit=(fs/base).toFixed(2);
 // 留白检查：内容（文字和可见图片）只占到版面多高
 const R0=r.getBoundingClientRect();let mb=Math.max(R0.top,cbottom(r));r.querySelectorAll('img').forEach(e=>{if(e.closest('.deco'))return;const b=e.getBoundingClientRect();if(b.height&&b.width&&e.offsetParent)mb=Math.max(mb,Math.min(b.bottom,R0.bottom))});
 const ratio=(mb-R0.top)/R0.height;if(ratio<0.62&&!r.classList.contains('r-one'))r.dataset.sparse=ratio.toFixed(2)})}
// 上半色块：高度停在第一排卡片的中间，卡片跨过色块边界
function split(){document.querySelectorAll('.sblock').forEach(b=>{const pg=b.closest('.page');const c=pg.querySelector('.rcards .cd');if(!c)return;const r=c.getBoundingClientRect(),P=pg.getBoundingClientRect();b.style.height=Math.round(r.top-P.top+r.height*.45)+'px'})}
// 自动补位的几何（.fz-auto）：只要压到任何正文就隐藏
function fz(){document.querySelectorAll('.fz-auto').forEach(z=>{const pg=z.closest('.page');const Z=z.getBoundingClientRect();const w=document.createTreeWalker(pg,NodeFilter.SHOW_TEXT);let t;
 while(t=w.nextNode()){if(!t.textContent.trim()||t.parentElement.closest('.deco'))continue;const r=document.createRange();r.selectNodeContents(t);for(const q of r.getClientRects()){if(q.right>Z.left&&q.left<Z.right&&q.bottom>Z.top&&q.top<Z.bottom){z.style.display='none';return}}}})}
// 黄金分割：带 data-golden 的标题组往下挪，让标题的视觉中心落在页高 0.382（或 0.618）；下面的内容挡着就只挪到能挪的位置
function golden(){document.querySelectorAll('[data-golden]').forEach(g=>{
 const pg=g.closest('.page'),P=pg.getBoundingClientRect();
 const t=[...g.querySelectorAll('.disp,.hd0 .sf')].filter(e=>!e.hasAttribute('aria-label'))[0];if(!t)return;
 const r=t.getBoundingClientRect();const d=P.top+P.height*(+g.dataset.golden)-(r.top+r.height/2);if(d<=0)return;
 if(g.classList.contains('a')){const gb=cbottom(g);let lim=P.bottom-60;
  pg.querySelectorAll(':scope>div.a').forEach(o=>{if(o===g||o.classList.contains('deco')||!o.innerText.trim())return;const R=o.getBoundingClientRect();if(R.top>gb-1)lim=Math.min(lim,R.top)});
  g.style.top=(parseFloat(g.style.top)+Math.max(0,Math.min(d,lim-32-gb)))+'px'}
 else{const c=g.closest('.rcp');const room=c.getBoundingClientRect().bottom-cbottom(c)-8;g.style.paddingTop=(parseFloat(getComputedStyle(g).paddingTop)+Math.max(0,Math.min(d,room)))+'px'}})}
function cnLinks(){// 网址、邮箱自动变成可点链接（HTML 和 PDF 里都能点）
 const re=/(https?:\/\/[^\s，。、；）)<>"']+|www\.[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+(?:\/[^\s，。、；）)<>"']*)?|[\w.+-]+@[\w-]+(?:\.[\w-]+)+)/g;
 document.querySelectorAll('.page').forEach(pg=>{const w=document.createTreeWalker(pg,NodeFilter.SHOW_TEXT);const ns=[];let t;while(t=w.nextNode()){if(t.parentElement.closest('a,script,style,svg'))continue;re.lastIndex=0;if(re.test(t.textContent))ns.push(t)}
  ns.forEach(t=>{const f=document.createDocumentFragment();let last=0;const s=t.textContent;s.replace(re,(m,_,i)=>{f.append(s.slice(last,i));const a=document.createElement('a');a.className='hb-link';
   a.href=m.includes('@')&&!m.startsWith('http')?'mailto:'+m:(m.startsWith('http')?m:'https://'+m.replace(/[.,]$/,''));a.textContent=m;f.append(a);last=i+m.length;return m});f.append(s.slice(last));t.replaceWith(f)})})}
// Brand artwork is decorative and never changes layout. Protect final visible photo/QR/logo rectangles.
function cnBrandGraphics(){document.querySelectorAll('.cn-brand-graphic').forEach(svg=>{
 const pg=svg.closest('.page'),P=pg.getBoundingClientRect(),mask=svg.querySelector('mask');mask.querySelectorAll('[data-cut]').forEach(e=>e.remove());
 if(svg.dataset.overImage==='1')return;
 const zones=[...pg.querySelectorAll('.cn-zone')];
 const sources=[...zones,...pg.querySelectorAll('img')].filter(e=>!zones.length||e.tagName!=='IMG'||e.closest('.cn-st'));
 sources.forEach(e=>{let R=e.getBoundingClientRect(),a=e.parentElement;
  let l=Math.max(R.left,P.left),t=Math.max(R.top,P.top),r=Math.min(R.right,P.right),b=Math.min(R.bottom,P.bottom);
  while(a&&a!==pg){const s=getComputedStyle(a),q=a.getBoundingClientRect();if(s.overflowX!=='visible'){l=Math.max(l,q.left);r=Math.min(r,q.right)}if(s.overflowY!=='visible'){t=Math.max(t,q.top);b=Math.min(b,q.bottom)}a=a.parentElement}
  if(r<=l||b<=t)return;const rect=document.createElementNS('http://www.w3.org/2000/svg','rect');
  for(const [k,v] of Object.entries({x:l-P.left-1,y:t-P.top-1,width:r-l+2,height:b-t+2,fill:'black','data-cut':'1'}))rect.setAttribute(k,v);mask.appendChild(rect)})})}
// 主题装饰留在阅读纸面，不能把已经到裁切边的摄影重新盖成带边框的图片。
function cnPhotoDecor(){document.querySelectorAll('.page.cn').forEach(pg=>{
 const P=pg.getBoundingClientRect(),photos=[...pg.querySelectorAll('.cn-pic,.cn-figi,.cn-ibox')].filter(e=>!e.closest('.deco')).map(e=>e.getBoundingClientRect());
 pg.querySelectorAll('.sj-line,.sj-blk,.sj-rail,.sj-tick').forEach(e=>{
  const D=e.getBoundingClientRect(),cuts=[];let path=`M0 0H${D.width}V${D.height}H0Z`;
  photos.forEach(R=>{const l=Math.max(D.left,R.left,P.left)-D.left,t=Math.max(D.top,R.top,P.top)-D.top,r=Math.min(D.right,R.right,P.right)-D.left,b=Math.min(D.bottom,R.bottom,P.bottom)-D.top;
   if(r>l&&b>t)cuts.push({l,t,r,b})});
  // 先求矩形并集：嵌套或相交的图位不能在evenodd中相互抵消。
  const xs=[...new Set(cuts.flatMap(c=>[c.l,c.r]))].sort((a,b)=>a-b);
  for(let i=0;i<xs.length-1;i++){const l=xs[i],r=xs[i+1],ys=cuts.filter(c=>c.l<r&&c.r>l).map(c=>[c.t,c.b]).sort((a,b)=>a[0]-b[0]),merged=[];
   ys.forEach(q=>{const last=merged[merged.length-1];if(last&&q[0]<=last[1])last[1]=Math.max(last[1],q[1]);else merged.push(q.slice())});
   merged.forEach(([t,b])=>path+=`M${l} ${t}H${r}V${b}H${l}Z`)}
  e.style.clipPath=cuts.length?`path(evenodd, "${path}")`:'';
 })})}

function cnFitNums(){
 document.querySelectorAll('.page.cn .cn-stats .cn-num').forEach(e=>{
  const cell=e.parentElement;if(!cell)return;
  if(!e.dataset.origFs)e.dataset.origFs=parseFloat(e.style.fontSize)||38;
  const maxW=Math.max(48,cell.clientWidth-8);
  let s=parseFloat(e.dataset.origFs);e.style.fontSize=s+'px';e.style.lineHeight=(s+6)+'px';
  while(e.scrollWidth>maxW&&s>16){s-=2;e.style.fontSize=s+'px';e.style.lineHeight=(s+6)+'px'}
 });
}
function fill(){cnLinks();canon();cnFitNums();sjStructure();fit();split();golden();fz();grow();document.querySelectorAll('.fill').forEach(e=>{e.innerHTML='';const n=Math.max(0,Math.floor(e.clientHeight/CN.L));e.innerHTML='<div class="cn-ln"></div>'.repeat(n)});cnTypography();cnBrandGraphics();cnPhotoDecor();cnQA();document.body.dataset.ready=1;hbNotifyParent()}
// 网格透视：book.html#grid 打开时，内容版式页叠上 6 栏网格（红色栏、蓝色行线、版心框）
function cnGrid(){if(location.hash!='#grid')return;document.querySelectorAll('.page').forEach((pg,i)=>{if(!pg.classList.contains('cn'))return;const r=(i+1)%2==1,L=r?CN.I:CN.O;let h='';const tw=6*CN.C+5*CN.G;
 for(let c=0;c<6;c++)h+=`<div style="position:absolute;left:${L+c*(CN.C+CN.G)}px;top:0;width:${CN.C}px;height:${CN.H}px;background:rgba(226,60,90,.10)"></div>`;
 for(let l=0;l<=CN.N+1;l++)h+=`<div style="position:absolute;left:0;top:${CN.T+l*CN.L}px;width:${CN.W}px;border-top:.5px solid rgba(40,150,220,.4)"></div>`;
 h+=`<div style="position:absolute;left:${L}px;top:${CN.T}px;width:${tw}px;height:${CN.B-CN.T}px;outline:1.2px solid rgba(226,60,90,.9)"></div>`;
 const g=document.createElement('div');g.className='deco';g.style.cssText='position:absolute;inset:0;pointer-events:none;z-index:99';g.innerHTML=h;pg.appendChild(g)})}

// ================= Live Studio Engine (支持 file:// 跨源 postMessage 实时切换字体、字重、字号、配色、缩放与双页跨页视图) =================
const HB_STUDIO_FONTS={
 natgeo:{title:"'HB-playfair','Playfair Display','HB-noto-serif-sc','Noto Serif CJK SC','Source Han Serif SC','Songti SC',serif",body:"'HB-noto-sans-sc','PingFang SC','Hiragino Sans GB',-apple-system,sans-serif",label:"'HB-oswald','Oswald','DIN Condensed','Avenir Next Condensed','PingFang SC',sans-serif",accent:"'HB-playfair-italic','Playfair Display','HB-noto-serif-sc','Songti SC',serif",track:"0.24em"},
 editorial:{title:"'Source Serif 4','Baskerville','HB-noto-serif-sc','Noto Serif CJK SC','Source Han Serif SC','Songti SC',serif",body:"'Source Serif 4','Georgia','HB-noto-serif-sc','Songti SC',serif",label:"'Inter',-apple-system,'SF Pro Text','PingFang SC',sans-serif",accent:"'Source Serif 4','Baskerville','HB-noto-serif-sc','Songti SC',serif",track:"0.14em"},
 swiss:{title:"'Inter',-apple-system,'SF Pro Display','Helvetica Neue','HB-noto-sans-sc','PingFang SC',sans-serif",body:"'Inter',-apple-system,'SF Pro Text','Helvetica Neue','HB-noto-sans-sc','PingFang SC',sans-serif",label:"'Inter','Helvetica Neue','PingFang SC',sans-serif",accent:"'Inter','Helvetica Neue','PingFang SC',sans-serif",track:"0.12em"},
 wenkai:{title:"'HB-playfair','Playfair Display','LXGW WenKai GB','Kaiti SC','STKaiti',serif",body:"'LXGW WenKai GB','Kaiti SC','STKaiti',serif",label:"'HB-oswald','Oswald','PingFang SC',sans-serif",accent:"'Playfair Display','Kaiti SC','STKaiti',serif",track:"0.16em"},
 poster:{title:"'HB-oswald','Oswald','Smiley Sans','Avenir Next Condensed','PingFang SC',sans-serif",body:"'HB-noto-sans-sc','PingFang SC',-apple-system,sans-serif",label:"'HB-oswald','Oswald','DIN Condensed','PingFang SC',sans-serif",accent:"'HB-oswald','Oswald','PingFang SC',sans-serif",track:"0.22em"}
};
const HB_STUDIO_PALETTES={
 natgeo:{paper:'#F4F1EA',ink:'#151B2E',hd:'#22306E',acc:'#3F7062',num:'#22306E',lab:'#22306E',mut:'#5A6275',rule:'#151B2E',line:'rgba(21,27,46,0.22)',gold:'#F2C14E',portal:true},
 nature:{paper:'#FAF8F1',ink:'#18251F',hd:'#24523E',acc:'#685022',num:'#24523E',lab:'#24523E',mut:'#4A574F',rule:'#18251F',line:'rgba(24,37,31,0.22)',gold:'#E4B93D',portal:true},
 campus:{paper:'#FBFAF7',ink:'#202B32',hd:'#1F3A5F',acc:'#665644',num:'#1F3A5F',lab:'#1F3A5F',mut:'#4B575E',rule:'#202B32',line:'rgba(32,43,50,0.22)',gold:'#C89B3C',portal:false},
 ink:{paper:'#FDFCF3',ink:'#292720',hd:'#292720',acc:'#625B4D',num:'#292720',lab:'#292720',mut:'#514E46',rule:'#292720',line:'rgba(41,39,32,0.22)',gold:'#D8D0BA',portal:false},
 swiss:{paper:'#FAFAF8',ink:'#151515',hd:'#151515',acc:'#A32F25',num:'#A32F25',lab:'#A32F25',mut:'#50504D',rule:'#151515',line:'rgba(21,21,21,0.22)',gold:'#A32F25',portal:false}
};
let HB_STUDIO_STATE={font:'default',weight:null,scale:1,palette:null,gridXRay:false,spreadView:false,zoom:'100'};
function hbNotifyParent(){
 if(window.parent===window)return;
 const pages=[...document.querySelectorAll('.page')];
 const pills=pages.map((pg,i)=>{
  const k=pg.querySelector('.cn-lab')?.textContent?.trim()?.split('·')[0]?.trim()||'';
  return {n:i+1,label:`P${String(i+1).padStart(2,'0')}${k?' · '+k.slice(0,14):''}`};
 });
 const qa=(typeof cnCheck==='function'?cnCheck():[]).filter(q=>q[1]==='cn-over'||q[1]==='cn-collide');
 window.parent.postMessage({type:'hb-studio-status',pageCount:pages.length,overCount:qa.length,pills},'*');
}
function hbApplyStudioState(st){
 HB_STUDIO_STATE=Object.assign(HB_STUDIO_STATE,st||{});
 let el=document.getElementById('hb-live-studio-css');
 if(!el){el=document.createElement('style');el.id='hb-live-studio-css';document.head.appendChild(el)}
 const S=HB_STUDIO_STATE;
 const vw=window.innerWidth||1200;
 let z=1;
 if(S.zoom==='fit'){
  const targetW=S.spreadView?(CN.W*2+80):(CN.W+80);
  z=Math.min(1.08,Math.max(0.45,(vw-48)/targetW));
 }else{
  z=(parseFloat(S.zoom)||100)/100;
 }
 let css=`
  html { background: #141821 !important; }
  body {
   background: #141821 !important;
   margin: 0 auto !important;
   padding: 28px 24px 64px !important;
   zoom: ${z.toFixed(3)};
   display: ${S.spreadView?'grid':'flex'} !important;
   ${S.spreadView
     ? `grid-template-columns: ${CN.W}px ${CN.W}px; justify-content: center; column-gap: 0px; row-gap: 36px;`
     : `flex-direction: column; align-items: center; gap: 28px;`}
  }
  .page {
   margin: 0 !important;
   flex-shrink: 0;
   box-shadow: 0 18px 46px rgba(0,0,0,0.46) !important;
   transition: box-shadow 0.2s ease;
  }
 `;
 if(S.spreadView){
  // 封面（第1页）与封底（偶数末页）单独成行居中显示，内页成对跨页并带书脊中缝阴影
  css+=`
   .page:first-of-type {
    grid-column: 1 / -1 !important;
    justify-self: center !important;
    box-shadow: 0 22px 54px rgba(0,0,0,0.55) !important;
   }
   .page:last-of-type:nth-of-type(even) {
    grid-column: 1 / -1 !important;
    justify-self: center !important;
    box-shadow: 0 22px 54px rgba(0,0,0,0.55) !important;
   }
   .page:nth-of-type(even):not(:last-of-type) {
    justify-self: end !important;
    box-shadow: -14px 18px 42px rgba(0,0,0,0.45), inset -16px 0 24px -14px rgba(0,0,0,0.32) !important;
    border-right: 1px solid rgba(0,0,0,0.18);
   }
   .page:nth-of-type(odd):not(:first-of-type) {
    justify-self: start !important;
    box-shadow: 14px 18px 42px rgba(0,0,0,0.45), inset 16px 0 24px -14px rgba(0,0,0,0.32) !important;
   }
  `;
 }
 if(S.font&&S.font!=='default'&&HB_STUDIO_FONTS[S.font]){
  const f=HB_STUDIO_FONTS[S.font];
  document.documentElement.style.setProperty('--f-title',f.title);
  document.documentElement.style.setProperty('--f-body',f.body);
  document.documentElement.style.setProperty('--f-label',f.label);
  document.documentElement.style.setProperty('--f-accent',f.accent);
  document.documentElement.style.setProperty('--label-track',f.track);
  css+=`
   :root, body, .page, .cn-st {
    --f-title: ${f.title} !important;
    --f-body: ${f.body} !important;
    --f-label: ${f.label} !important;
    --f-accent: ${f.accent} !important;
    --label-track: ${f.track} !important;
   }
   .page .cn-disp, .page .cn-h, .page .cn-num { font-family: ${f.title} !important; }
   .page .cn-tx, .page .cn-tx p, .page .cn-li li { font-family: ${f.body} !important; }
   .page .cn-lab, .page .cn-cap, .page .cn-fo, .page .cn-th { font-family: ${f.label} !important; }
   .page .cn-sub, .page .cn-qt { font-family: ${f.accent} !important; }
  `;
 }else if(S.font==='default'){
  ['--f-title','--f-body','--f-label','--f-accent','--label-track'].forEach(k=>document.documentElement.style.removeProperty(k));
 }
 const wMap={
  bold:{disp:900,h:700,sub:600,body:400,lab:600,mode:'bold'},
  semi:{disp:700,h:600,sub:500,body:400,lab:600,mode:'bold'},
  light:{disp:200,h:250,sub:300,body:400,lab:500,mode:'light'},
  thin:{disp:100,h:200,sub:300,body:400,lab:500,mode:'light'}
 }[S.weight];
 window.__hbWeightMode=S.weight||null;
 if(wMap){
  document.body.dataset.typography=wMap.mode;
  document.body.style.setProperty('--display-w',String(wMap.disp));
  document.body.style.setProperty('--title-w',String(wMap.disp));
  // 当处于 Light/Thin 阶梯且未选择特定字体时，中文标题自动纳入 PingFang SC 以呈现真实的 100/200/300 极细与轻盈字重梯度
  if((S.weight==='light'||S.weight==='thin')&&(!S.font||S.font==='default')){
   css+=`:root, body, .page, .cn-st { --f-title: 'HB-playfair','Playfair Display','HB-noto-serif-sc','PingFang SC','Heiti SC',sans-serif !important; }`;
  }
 }
 if(S.palette&&HB_STUDIO_PALETTES[S.palette]){
  const p=HB_STUDIO_PALETTES[S.palette];
  document.querySelectorAll('.page.paper, .page.sf-paper').forEach(pg=>{
   pg.style.background=p.paper;
   pg.querySelectorAll('.cn-st, .cn-v').forEach(stEl=>{
    stEl.style.setProperty('--fg',p.ink);
    stEl.style.setProperty('--hd',p.hd);
    stEl.style.setProperty('--acc',p.acc);
    stEl.style.setProperty('--num',p.num);
    stEl.style.setProperty('--lab',p.lab);
    stEl.style.setProperty('--mut',p.mut);
    stEl.style.setProperty('--rule',p.rule);
    stEl.style.setProperty('--line',p.line);
   });
   pg.querySelectorAll('.cn-wash-down, .cn-wash-side').forEach(wEl=>{
    wEl.style.setProperty('--page-bg',p.paper);
   });
  });
  css+=`
   .page.paper .cn-lab::before, .page.sf-paper .cn-lab::before {
    ${p.portal?`content:"";display:inline-block;width:9px;height:14px;border:2.5px solid ${p.gold};margin-right:6px;`:`display:none !important;`}
   }
  `;
 }
 if(S.gridXRay){
  css+=`
   .page::before {
    content: "" !important;
    position: absolute !important;
    inset: 0 !important;
    z-index: 999 !important;
    pointer-events: none !important;
    background-image:
     repeating-linear-gradient(180deg, rgba(242,193,78,0.22) 0 1px, transparent 1px 28px),
     linear-gradient(90deg,
      transparent 0 50px,
      rgba(56,189,248,0.14) 50px 130px, transparent 130px 162px,
      rgba(56,189,248,0.14) 162px 242px, transparent 242px 274px,
      rgba(56,189,248,0.14) 274px 354px, transparent 354px 386px,
      rgba(56,189,248,0.14) 386px 466px, transparent 466px 498px,
      rgba(56,189,248,0.14) 498px 578px, transparent 578px 610px,
      rgba(56,189,248,0.14) 610px 690px, transparent 690px 100%) !important;
    background-position: 0 88px, 0 0 !important;
   }
  `;
 }
 el.textContent=css;
 // 重新拟合并测量标题与大数字
 document.querySelectorAll('.page.cn [data-fit]').forEach(e=>{
  const baseFit=+(e.dataset.fit0||e.dataset.fit||44);
  e.dataset.fit=Math.round(baseFit*(parseFloat(S.scale)||1));
  cnFit(e);
 });
 // 让 cnTypography() 按每个元素的实际像素字号（fontSize）动态赋予阶梯字重：大字>=38px、中字26-37px、导语18-25px、正文16px、眉标<=14px 各司其职
 cnTypography();
 cnFitNums();
 cnLayout();
 cnQA();
 hbNotifyParent();
}
window.addEventListener('message',e=>{
 const d=e.data;if(!d||typeof d!=='object')return;
 if(d.type==='hb-studio')hbApplyStudioState(d.state);
 else if(d.type==='hb-scroll-page'){
  const pg=document.querySelectorAll('.page')[d.index||0];
  if(pg)pg.scrollIntoView({behavior:'smooth',block:'start'});
 }
});
window.addEventListener('resize',()=>{if(HB_STUDIO_STATE.zoom==='fit')hbApplyStudioState({})});
// 排印会在测量时切换字重，先载入本书注册的真实静态字重，避免回退字体测量后再跳字。
document.fonts.ready.then(()=>Promise.all([...document.fonts].map(face=>face.load()))).then(()=>setTimeout(()=>{fill();cnGrid();if(window.parent!==window)hbApplyStudioState({})},50))</script>
window.addEventListener("message", (e) => {
  const d = e && e.data;
  if (!d || typeof d !== "object") return;
  if (d.type === "hb-glass") {
    document.querySelectorAll(".page.cn").forEach(p => {
      if (!d.glass || d.glass === "liquid") p.removeAttribute("data-glass");
      else p.setAttribute("data-glass", d.glass);
    });
  }
});
if (window.self !== window.top) {
  document.documentElement.classList.add("in-iframe");
  if (document.body) document.body.classList.add("in-iframe");
  window.addEventListener("DOMContentLoaded", () => {
    if (document.body) document.body.classList.add("in-iframe");
    const b = document.getElementById("bar");
    if (b) b.style.display = "none";
  });
}
