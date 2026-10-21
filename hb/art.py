"""只保留照片占位和中性纸面；内容图解使用实际素材，不生成退役风格底纹。"""
import numpy as np
from PIL import Image

def hx(c):
    c=c.lstrip('#');return np.array([int(c[i:i+2],16) for i in (0,2,4)],np.float32)
def mix(a,b,t):return a*(1-t)+b*t
def grain(arr,rng,amt):return arr+rng.normal(0,amt,arr.shape[:2])[...,None]

def photo(w, h, rng, C, B):          # 深色占位（照片之后再换）
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (y / h)[..., None]; img = mix(C['G'] * .75 + C['INK'] * .1, C['G'] * .45, t)
    bx, by, bw, bh = B; cx, cy = bx + rng.uniform(.25, .75) * bw, by + rng.uniform(.3, .7) * bh
    r = np.exp(-(((x - cx) / (w * .35)) ** 2 + ((y - cy) / (h * .3)) ** 2))[..., None]
    img = img * (1 - .35 * r) + C['GOLD'] * .35 * r
    return grain(img, rng, 4)

def paper(w,h,rng,C,B):return np.zeros((h,w,3),np.float32)+C['PAPER']
STYLES=dict(photo=photo,editorial=paper,swiss=paper)
TONE=dict(photo='dark',editorial='light',swiss='light')
def make(style,w,h,seed,colors,box=(0,0,1,1)):
    C={k:hx(v) for k,v in colors.items()};rng=np.random.default_rng(seed)
    B=(box[0]*w,box[1]*h,(box[2]-box[0])*w,(box[3]-box[1])*h)
    arr=STYLES[style](w,h,rng,C,B)
    return Image.fromarray(np.asarray(arr).clip(0,255).astype(np.uint8))
