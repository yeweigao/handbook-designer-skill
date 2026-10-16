#!/usr/bin/env python3
"""看图拼版：封面单独一格，之后按跨页（2|3, 4|5 …）左右拼接，每张 4 行×2 跨页。 python3 montage.py <project_dir>
文件名带时间戳（view_image 会缓存同名文件）。"""
import sys,os,glob,time
from PIL import Image,ImageDraw
P=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else '.'); Q=os.path.join(P,'.qa'); ts=time.strftime('%H%M%S')
for f in glob.glob(os.path.join(Q,'review_*.jpg')): os.remove(f)
fs=sorted(glob.glob(os.path.join(Q,'pg*.png')),key=lambda f:int(os.path.basename(f)[2:-4]))
ims=[Image.open(f).convert('RGB').resize((397,561)) for f in fs]; n=len(ims); w,h=397,561
rows=[[None,0]]+[[i,i+1 if i+1<n else None] for i in range(1,n,2)]
for k in range(0,len(rows),8):
    ch=rows[k:k+8]; R=(len(ch)+1)//2
    sh=Image.new('RGB',(4*w+60,R*(h+30)+10),'#5a5a5a'); d=ImageDraw.Draw(sh)
    for j,(a,b) in enumerate(ch):
        x0=20+(j%2)*(2*w+20); y0=10+(j//2)*(h+30)
        for t,i in enumerate((a,b)):
            if i is None: continue
            sh.paste(ims[i],(x0+t*w,y0)); d.text((x0+t*w+4,y0+h+6),f'p{i+1}',fill='white')
    out=os.path.join(Q,f'review_{k//8+1:02d}_{ts}.jpg'); sh.save(out,quality=80); print(out)
