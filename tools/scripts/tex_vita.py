"""Vita DDS loading for EDF 2017 Portable: DXT blocks may be stored twiddled (square chunks along the long axis,
Morton order with y in the low bits). Layout is not flagged in the header, so choose by smoothness."""
import sys,os,io,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import sgsl,tex_bntx
from PIL import Image,ImageChops,ImageStat
_m=[0]*1024
for v in range(1024):
    r=0
    for i in range(10): r|=((v>>i)&1)<<(2*i)
    _m[v]=r
def morton_yx(x,y): return _m[y]|(_m[x]<<1)
def untwiddle(blocks,wb,hb,bpb):
    out=bytearray(len(blocks)); m=min(wb,hb)
    for y in range(hb):
        for x in range(wb):
            idx=(x//m)*m*m+morton_yx(x%m,y) if wb>=hb else (y//m)*m*m+morton_yx(x,y%m)
            out[(y*wb+x)*bpb:(y*wb+x+1)*bpb]=blocks[idx*bpb:(idx+1)*bpb]
    return bytes(out)
def tv(im):
    g=im.convert('L'); dx=ImageChops.difference(g,g.transform(g.size,Image.AFFINE,(1,0,1,0,1,0))); dy=ImageChops.difference(g,g.transform(g.size,Image.AFFINE,(1,0,0,0,1,1)))
    return ImageStat.Stat(dx).mean[0]+ImageStat.Stat(dy).mean[0]
def load(path):
    """Return (Image RGBA, w, h, fourcc, linear_blocks, layout)."""
    d=open(path,'rb').read()
    if d[:4]==b'SGSL': d=sgsl.decompress(d)
    fc=d[84:88]
    if fc not in (b'DXT1',b'DXT3',b'DXT5'):
        im=Image.open(io.BytesIO(d)); im.load(); return im.convert('RGBA'),im.width,im.height,'RGBA',None,'linear'
    w,h,fc,bl=tex_bntx.dds_blocks(d); bpb=8 if fc=='DXT1' else 16
    cands={'linear':bl,'twiddled':untwiddle(bl,max(1,w//4),max(1,h//4),bpb)}
    best=None
    for k,b in cands.items():
        im=Image.open(io.BytesIO(tex_bntx.dds_wrap(b,w,h,fc))).convert('RGBA'); s=tv(im)
        if best is None or s<best[0]: best=(s,k,im,b)
    return best[2],w,h,fc,best[3],best[1]
