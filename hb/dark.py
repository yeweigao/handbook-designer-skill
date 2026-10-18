# 文字下的整宽渐进“衬底”：浅色字 → 压暗（像 ND 渐变镜）；深色字 → 提亮（像一层薄纸）。不做逐段光晕。
# 只改动 map.json 里登记的照片/底图；按文字行带生成、横向贯穿，迭代到对比度达标（WCAG AA ×1.03）。
import json,re,numpy as np
from PIL import Image
def gaussian_filter1d(p,sig,mode=None):
    r=int(3*sig); k=np.exp(-.5*(np.arange(-r,r+1)/sig)**2); k/=k.sum()
    return np.convolve(np.pad(p,r,mode='edge'),k,'valid')
M=json.load(open('map.json')); W,H=M.get('W',794),M.get('H',1123); B=json.load(open('.qa/b3.json'))
def lum(c):
    c=c/255.0; c=np.where(c<=.03928,c/12.92,((c+.055)/1.055)**2.4); return .2126*c[...,0]+.7152*c[...,1]+.0722*c[...,2]
def hx(c): c=c.lstrip('#'); return np.array([int(c[i:i+2],16) for i in (0,2,4)],np.float32)
LOCAL=set(M.get('local',[])); CLIP=M.get('clip',{}); FLAT=set(M.get('flat',[]))   # 平面风格的底图不加衬底（纯色上的渐变衬底会显脏），靠构图避开文字、QA 把关
COL=np.array([6,12,10],np.float32); PAPERC=hx(M.get('paper','#FBFAF7')); SIG=70
groups={}
for b in B:
    m=M['map'].get(str(b['pg']))
    if not m or b.get('own'): continue   # 自带底色的文字（胶囊标签等）不改照片
    c=b['color']
    rgb=np.array([float(v) for v in re.findall(r'[\d.]+',c)[:3]]) if 'rgb' in c else np.array([int(c[i:i+2],16) for i in (1,3,5)]) if c.startswith('#') and len(c)==7 else np.array([255.,255,255])
    ox=(W if m['side']=='R' else 0); Lt=lum(rgb)
    need=3 if (b['fs']>=24 or (b['fs']>=18.66 and b.get('fw',400)>=700)) else 4.5   # WCAG AA：大字=24px，或 18.66px 粗体
    if Lt>=.4: tg=(Lt+.05)/(need*1.03)-.05; mode='d'        # 浅色字：背景亮度上限
    else: tg=need*1.03*(Lt+.05)-.05; mode='l'               # 深色字：背景亮度下限
    groups.setdefault(m['img'],[]).append((b['x']+ox,b['y'],b['w'],b['h'],tg,mode))
for name,kind in M['imgs'].items():
    base=np.asarray(Image.open('img/'+name.replace('.jpg','_base.jpg')).convert('RGB')).astype(np.float32)
    ih,iw=base.shape[:2]; PW=(2*W if kind!='single' else W)+4; PH=H+2
    sx,sy=iw/PW,ih/PH
    rects=[]
    for (x,y,w,h,tg,mode) in ([] if name in FLAT else groups.get(name,[])):
        x0,y0=max(0,int((x+2)*sx)),max(0,int((y+1)*sy)); x1,y1=min(iw,int((x+w+2)*sx)+1),min(ih,int((y+h+1)*sy)+1)
        if x1>x0 and y1>y0 and 0<=tg<=1: rects.append((x0,y0,x1,y1,tg,mode))
    q=4; sh,sw=ih//q+1,iw//q+1
    def band(n,lo,hi,sig):
        p=np.zeros(n,np.float32); p[max(0,lo):max(0,min(n,hi))]=1
        g=gaussian_filter1d(p,sig); return g/max(g.max(),1e-3)
    gys=[band(sh,(y0-int(20*sy))//q,(y1+int(20*sy))//q,SIG*sy/q) for (x0,y0,x1,y1,_,_) in rects]
    gxs=[]
    for (x0,y0,x1,y1,_,mode) in rects:
        cx=(x0+x1)/2/sx; side_lo,side_hi=(0,W+2) if cx<W+2 else (W+2,2*W+4)
        local=name in LOCAL and y0/sy>H-60
        if mode=='l': lo=side_lo*sx; hi=side_hi*sx; sg=40     # 提亮只在文字所在的那一页内（不跨到对页的白字下面）
        elif local: lo=max(side_lo*sx,x0-140*sx); hi=min(side_hi*sx,x1+140*sx); sg=90
        elif name in CLIP and cx<W+2: lo=(CLIP[name][0]+2)*sx; hi=(CLIP[name][1]+2)*sx; sg=60
        else: lo=-200*sx; hi=(2*W+204)*sx; sg=50
        gxs.append(np.maximum(band(sw,int(lo)//q,int(hi)//q,sg*sx/q),0))
    def build(req,mode):
        m=np.zeros((sh,sw),np.float32)
        for gy,gx,a,r in zip(gys,gxs,req,rects):
            if a>0 and r[5]==mode: m=np.maximum(m,a*np.outer(gy,gx))
        m=np.clip(m,0,.9)
        return np.asarray(Image.fromarray((m*255).astype(np.uint8)).resize((iw,ih),Image.BILINEAR),np.float32)/255
    req=np.zeros(len(rects)); out=base; md=ml=np.zeros((ih,iw),np.float32)
    for it in range(12):
        if not rects: break
        md=build(req,'d'); ml=build(req,'l')
        out=base*(1-md[...,None])+COL*md[...,None]; out=out*(1-ml[...,None])+PAPERC*ml[...,None]; Lo=lum(out); more=False
        for i,(x0,y0,x1,y1,TG,mode) in enumerate(rects):
            if req[i]>=1.2: continue
            if mode=='d':
                l=np.percentile(Lo[y0:y1,x0:x1],95)
                if l>TG: req[i]+=max(.06,1-(TG/l)**(1/2.2)); more=True
            else:
                l=np.percentile(Lo[y0:y1,x0:x1],5)
                if l<TG: req[i]+=max(.06,1-(max(l,1e-3)/TG)**(1/2.2)); more=True
        if not more: break
    Image.fromarray(out.clip(0,255).astype(np.uint8)).save('img/'+name,quality=90)
    print(name,len(rects),'darken %.2f lighten %.2f'%(md.max(),ml.max()))
