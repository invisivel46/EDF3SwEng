"""DXB resource pack: 'DXB\0', u32 count, u32 table_off(16), u32 0; entries 32 bytes:
   u32 name_off, u32 type_off (UTF-16LE strs), u32 hash?, u32 ?, u32 size, u32 data_off, u32 0, u32 0 — offsets relative to the entry's own position.
   Vita packs may be SGSL-compressed."""
import struct,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import sgsl
def u16(d,o):
    e=o
    while d[e:e+2]!=b'\0\0': e+=2
    return d[o:e].decode('utf-16-le')
def load(path):
    d=open(path,'rb').read()
    if d[:4]==b'SGSL': d=sgsl.decompress(d)
    assert d[:4]==b'DXB\0'
    n,toff,_=struct.unpack('<III',d[4:16]); ents=[]
    for i in range(n):
        ep=toff+i*32; f=struct.unpack('<8I',d[ep:ep+32])   # all offsets are relative to the entry position
        ents.append(dict(name=u16(d,ep+f[0]),type=u16(d,ep+f[1]),h=f[2],x=f[3],size=f[4],off=ep+f[5],entry=ep))
    return d,ents
if __name__=='__main__':
    d,ents=load(sys.argv[1]); out=sys.argv[2] if len(sys.argv)>2 else None
    for e in ents:
        data=d[e['off']:e['off']+e['size']]
        print(f"{e['name']:40s} {e['type']:12s} size={e['size']:8d} off={e['off']:#x} magic={data[:4]}")
        if out:
            os.makedirs(out,exist_ok=True); ext='.bntx' if data[:4]==b'BNTX' else '.dds' if data[:4]==b'DDS ' else '.bin'
            open(os.path.join(out,e['name']+ext),'wb').write(data)
