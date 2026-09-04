import struct, sys, os, zlib
def read_psarc(path):
    f=open(path,'rb'); h=f.read(32)
    magic,ver,comp,toc_len,toc_entry_size,toc_entries,block_size,flags=struct.unpack('>4sIIIIIII',h)
    assert magic==b'PSAR', magic
    toc=f.read(toc_len-32)
    entries=[]
    for i in range(toc_entries):
        e=toc[i*30:(i+1)*30]
        md5=e[:16]; idx=struct.unpack('>I',e[16:20])[0]
        size=int.from_bytes(e[20:25],'big'); off=int.from_bytes(e[25:30],'big')
        entries.append([md5,idx,size,off])
    nblocks=(toc_len-32-toc_entries*30)
    bsz=1
    while (1<<(8*bsz))<block_size: bsz+=1
    nb=nblocks//bsz
    blocks=[int.from_bytes(toc[toc_entries*30+i*bsz:toc_entries*30+(i+1)*bsz],'big') for i in range(nb)]
    def extract(e):
        md5,idx,size,off=e; f.seek(off); out=b''
        while len(out)<size:
            bl=blocks[idx]; idx+=1
            if bl==0: out+=f.read(block_size)
            else:
                d=f.read(bl)
                if d[:2]==b'x\x9c' or d[:1]==b'x': out+=zlib.decompress(d)
                else: out+=d
        return out[:size]
    manifest=extract(entries[0]).decode('utf-8').split('\n')
    names=['/manifest']+manifest
    return f,entries,names,extract,dict(comp=comp,block_size=block_size,flags=flags)
if __name__=='__main__':
    src,dst=sys.argv[1],sys.argv[2]
    f,entries,names,extract,info=read_psarc(src)
    print(info,len(entries),'entries')
    for e,n in zip(entries,names):
        n=n.strip().lstrip('/')
        if not n or n=='manifest': continue
        p=os.path.join(dst,n); os.makedirs(os.path.dirname(p),exist_ok=True)
        open(p,'wb').write(extract(e))
    print('done')
