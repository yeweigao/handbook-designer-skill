import json,re,numpy as np
from PIL import Image
B=json.load(open('.qa/b3.json', encoding='utf-8'));imgs={}
def lum(c):
    c=c/255.0; c=np.where(c<=.03928,c/12.92,((c+.055)/1.055)**2.4); return .2126*c[...,0]+.7152*c[...,1]+.0722*c[...,2]
bad=0
for b in B:
    i=b['pg']; im=imgs.setdefault(i,np.asarray(Image.open(f'.qa/bg{i}.png').convert('RGB')).astype(float))
    x0,y0=max(0,int(b['x'])),max(0,int(b['y'])); x1,y1=int(b['x']+b['w'])+1,int(b['y']+b['h'])+1
    reg=im[y0:y1,x0:x1]
    if reg.size==0: continue
    c=b['color']
    rgb=np.array([float(v) for v in re.findall(r'[\d.]+',c)[:3]]) if 'rgb' in c else np.array([int(c[k:k+2],16) for k in (1,3,5)]) if c.startswith('#') and len(c)==7 else np.array([255.,255,255])
    Lt=lum(rgb); L=lum(reg).ravel()
    Lb=np.percentile(L,95) if Lt>.4 else np.percentile(L,5)
    cr=(max(Lt,Lb)+.05)/(min(Lt,Lb)+.05)
    need=3 if (b['fs']>=24 or (b['fs']>=18.66 and b.get('fw',400)>=700)) else 4.5   # WCAG AA：大字=24px，或 18.66px 粗体
    if cr<need: bad+=1; print(f"p{i+1} {cr:4.1f} fs{b['fs']:.0f} {b['t']}")
print('FAIL',bad,'of',len(B),'（文字/背景颜色对比，按 WCAG AA 阈值；不等于完整无障碍检查）')
import sys; sys.exit(1 if bad else 0)
