# photo + translucent paper wash, baked; mask（纸面淡出的形状）由调用方按版面传入，本模块不预设版式坐标
import numpy as np
from PIL import Image
S=2; PAPERC=np.array([251,250,247],np.float32); A=0.86
def ss(e0,e1,x):
    t=np.clip((x-e0)/(e1-e0),0,1); return t*t*(3-2*t)
def bake2(src,out,W2,H2,focus,target,zoom,mask,box=(0,0,1,1)):
    im=Image.open(src).convert('RGB'); iw,ih=im.size
    PW,PH=W2+4,H2+2
    # 按真正露出的图框铺图，而不是把上半页照片先放大到整页再裁掉下半。
    bx0=0 if box[0]==0 else box[0]*W2+2; by0=0 if box[1]==0 else box[1]*H2+1
    bx1=PW if box[2]==1 else box[2]*W2+2; by1=PH if box[3]==1 else box[3]*H2+1
    s=max((bx1-bx0)/iw,(by1-by0)/ih)*zoom; nw,nh=iw*s,ih*s
    ox=min(bx0,max(bx1-nw,target[0]+2-focus[0]*nw)); oy=min(by0,max(by1-nh,target[1]+1-focus[1]*nh))
    big=im.resize((round(nw*S),round(nh*S)),Image.LANCZOS)
    x0,y0=round(-ox*S),round(-oy*S)
    a=np.asarray(big.crop((x0,y0,x0+PW*S,y0+PH*S)),np.float32)
    gy,gx=np.mgrid[0:PH*S,0:PW*S].astype(np.float32)
    X=gx/S-2; Y=gy/S-1
    al=mask(X,Y)[...,None]
    o=a*(1-al)+PAPERC*al
    Image.fromarray(o.clip(0,255).astype(np.uint8)).save(out,quality=90)
    return (ox,oy,s)
