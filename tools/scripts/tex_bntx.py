"""BNTX (Switch) texture read/write for EDF3. Only what the game uses: 2D, tile mode 0 (block linear), 1 mip
(or mips ignored beyond level 0), BC2/BC3/BC7. decode -> PIL Image via DDS wrapper; encode(template_bntx, dds_bytes)
replaces the level-0 block data (swizzled) in a copy of the template, optionally rewriting the format code."""
import struct, io, math, sys, os
from PIL import Image

BLOCK_FMTS={0x1a01:('DXT1',8),0x1b01:('DXT3',16),0x1c01:('DXT5',16),0x2001:('BC7',16)}

def _info(d):
    p=d.find(b'BRTI'); assert p>0
    flags,dim,tile,swz,mips,ms,res,fmt,acc,w,h,dep,arr,bhl=struct.unpack('<BBHHHHHIIIIIII',d[p+16:p+56])
    imgsize=struct.unpack('<I',d[p+0x50:p+0x54])[0]
    # pointer to mip offsets array
    ptrs_off=struct.unpack('<Q',d[p+0x70:p+0x78])[0]
    data_off=struct.unpack('<Q',d[ptrs_off:ptrs_off+8])[0]
    return dict(brti=p,fmt=fmt,w=w,h=h,mips=mips,bhl=bhl,tile=tile,imgsize=imgsize,data_off=data_off)

def _addr(x_bytes,y,width_gobs,bh):  # Tegra block-linear address
    gob=(y//(8*bh))*512*bh*width_gobs + (x_bytes//64)*512*bh + ((y%(8*bh))//8)*512
    return gob + ((x_bytes%64)//32)*256 + ((y%8)//2)*64 + ((x_bytes%32)//16)*32 + (y%2)*16 + (x_bytes%16)

def _swizzle_map(wb,hb,bpb,bh):
    width_bytes=wb*bpb; width_gobs=math.ceil(width_bytes/64)
    return [(_addr(x*bpb,y,width_gobs,bh),(y*wb+x)*bpb) for y in range(hb) for x in range(wb)]

def _bh(info):
    bh=1<<info['bhl']
    hb=max(1,info['h']//4)
    while bh>1 and bh*8>hb*2: bh//=2   # clamp like the SDK does
    return bh

def deswizzle(d,info=None):
    info=info or _info(d); name,bpb=BLOCK_FMTS[info['fmt']]
    wb,hb=max(1,info['w']//4),max(1,info['h']//4); bh=_bh(info)
    src=d[info['data_off']:]; out=bytearray(wb*hb*bpb)
    for s,t in _swizzle_map(wb,hb,bpb,bh): out[t:t+bpb]=src[s:s+bpb]
    return bytes(out)

def swizzle(blocks,info):
    name,bpb=BLOCK_FMTS[info['fmt']]
    wb,hb=max(1,info['w']//4),max(1,info['h']//4); bh=_bh(info)
    width_gobs=math.ceil(wb*bpb/64); size=width_gobs*512*bh*math.ceil(hb/(8*bh))
    out=bytearray(size)
    for s,t in _swizzle_map(wb,hb,bpb,bh): out[s:s+bpb]=blocks[t:t+bpb]
    return bytes(out)

def dds_wrap(blocks,w,h,fourcc):
    hdr=bytearray(128); hdr[:4]=b'DDS '; struct.pack_into('<IIIII',hdr,4,124,0x1|0x2|0x4|0x1000|0x80000,h,w,len(blocks))
    struct.pack_into('<I',hdr,28,1)
    struct.pack_into('<II',hdr,76,32,0x4)
    if fourcc=='BC7':
        hdr[84:88]=b'DX10'; ext=struct.pack('<IIIII',98,3,0,1,0); struct.pack_into('<I',hdr,108,0x1000); return bytes(hdr)+ext+blocks
    hdr[84:88]=fourcc.encode(); struct.pack_into('<I',hdr,108,0x1000)
    return bytes(hdr)+blocks

def decode(d):
    info=_info(d); name,bpb=BLOCK_FMTS[info['fmt']]
    im=Image.open(io.BytesIO(dds_wrap(deswizzle(d,info),info['w'],info['h'],name))); im.load(); return im.convert('RGBA')

def dds_blocks(dds):
    """Return (w,h,fourcc,level0 block bytes) from a DDS file (DXT1/3/5)."""
    h,w=struct.unpack('<II',dds[12:20]); fourcc=dds[84:88].decode('ascii','replace'); bpb=8 if fourcc=='DXT1' else 16
    n=max(1,w//4)*max(1,h//4)*bpb; return w,h,fourcc,dds[128:128+n]

def encode(template,blocks,fourcc):
    """Build a BNTX from template bytes, replacing level-0 data with `blocks` (linear BCn blocks of `fourcc`)."""
    info=_info(template); code={'DXT1':0x1a01,'DXT3':0x1b01,'DXT5':0x1c01,'BC7':0x2001}[fourcc]
    assert BLOCK_FMTS[code][1]==BLOCK_FMTS[info['fmt']][1],'block size mismatch'
    d=bytearray(template); p=info['brti']; struct.pack_into('<I',d,p+16+12,code)
    info['fmt']=code; sw=swizzle(blocks,info)
    assert len(sw)<=info['imgsize'],(len(sw),info['imgsize'])
    d[info['data_off']:info['data_off']+len(sw)]=sw
    return bytes(d)

if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='decode':
        for f in sys.argv[3:]:
            out=os.path.join(sys.argv[2],os.path.splitext(os.path.basename(f))[0]+'.png')
            try: decode(open(f,'rb').read()).save(out)
            except Exception as e: print('FAIL',f,e)
