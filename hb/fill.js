<script>
function grow(){document.querySelectorAll('.flow').forEach(f=>{const bx=[...f.querySelectorAll('.bx')];if(!bx.length)return;f.style.justifyContent='flex-start';const last=f.lastElementChild;const free=f.getBoundingClientRect().bottom-last.getBoundingClientRect().bottom-4;
 if(free>12){const rows=[...new Set(bx.map(b=>Math.round(b.getBoundingClientRect().top)))];const add=Math.min(free/rows.length,120);bx.forEach(b=>{b.style.height=(b.offsetHeight+add)+'px'})}f.style.justifyContent=''})}
function fill(){grow();document.querySelectorAll('.fill').forEach(e=>{e.innerHTML='';const n=Math.max(0,Math.floor(e.clientHeight/32));e.innerHTML='<div class="ln"></div>'.repeat(n)});document.body.dataset.ready=1}
document.fonts.ready.then(()=>setTimeout(fill,50))</script>
