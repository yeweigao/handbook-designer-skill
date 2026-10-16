# photo + translucent paper wash, baked; varied layouts (T top / B bottom / SL,SR side / HOLE window)
import numpy as np
from PIL import Image
S=2; PAPERC=np.array([251,250,247],np.float32); A=0.86
def ss(e0,e1,x):
    t=np.clip((x-e0)/(e1-e0),0,1); return t*t*(3-2*t)
def bake2(src,out,W2,H2,focus,target,zoom,mask):
    im=Image.open(src).convert('RGB'); iw,ih=im.size
    PW,PH=W2+4,H2+2
    s=max(PW/iw,PH/ih)*zoom; nw,nh=iw*s,ih*s
    ox=min(0,max(PW-nw,target[0]+2-focus[0]*nw)); oy=min(0,max(PH-nh,target[1]+1-focus[1]*nh))
    big=im.resize((round(nw*S),round(nh*S)),Image.LANCZOS)
    x0,y0=round(-ox*S),round(-oy*S)
    a=np.asarray(big.crop((x0,y0,x0+PW*S,y0+PH*S)),np.float32)
    gy,gx=np.mgrid[0:PH*S,0:PW*S].astype(np.float32)
    X=gx/S-2; Y=gy/S-1
    al=mask(X,Y)[...,None]
    o=a*(1-al)+PAPERC*al
    Image.fromarray(o.clip(0,255).astype(np.uint8)).save(out,quality=90)
    return (ox,oy,s)
def M_T(y0=120,y1=260): return lambda X,Y: A*ss(y0,y1,Y)
def M_B(y0=540,y1=700): return lambda X,Y: A*(1-ss(y0,y1,Y))
def M_SL(x0=96,x1=215): return lambda X,Y: A*ss(x0,x1,X)
def M_SR(W2,x0=96,x1=215): return lambda X,Y: A*(1-ss(W2-x1,W2-x0,X))
def M_HOLE(cx,cy,rx,ry,r0=.42,r1=.95): return lambda X,Y: A*ss(r0,r1,np.sqrt(((X-cx)/rx)**2+((Y-cy)/ry)**2))
