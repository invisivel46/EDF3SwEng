import struct
N=4096; F=18; THR=2; R0=N-F
def decompress(data):
    assert data[:4]==b'SGSL'
    size=struct.unpack('<I',data[4:8])[0]
    win=bytearray(N); r=R0; out=bytearray(); i=8; flags=0; fb=0
    while len(out)<size:
        if fb==0: flags=data[i]; i+=1; fb=8
        if flags&1:
            b=data[i]; i+=1; out.append(b); win[r]=b; r=(r+1)%N
        else:
            b1,b2=data[i],data[i+1]; i+=2
            off=b1|((b2&0xF0)<<4); ln=(b2&0x0F)+THR+1
            for k in range(ln):
                b=win[(off+k)%N]; out.append(b); win[r]=b; r=(r+1)%N
                if len(out)>=size: break
        fb-=1; flags>>=1
    return bytes(out)
def compress(raw):
    """LZSS encoder compatible with decompress(). Window position = (R0 + absolute index) % N; window starts zero-filled."""
    n=len(raw); out=bytearray(b'SGSL'+struct.pack('<I',n)); i=0
    # hash chains on 3-byte prefixes over absolute positions; also allow matching into the zero-filled pre-window
    from collections import defaultdict
    chains=defaultdict(list)
    def match(i):
        best=0;bp=0; maxl=min(F,n-i)
        if maxl<THR+1: return 0,0
        # zero-run match against pre-window (positions R0-d for d in 1..R0 are zero) when raw starts with zeros
        if i<N-R0 or True:
            z=0
            while z<maxl and raw[i+z]==0: z+=1
            if z>=THR+1 and i< R0:  # window slot before data start is zero: pick slot (R0+i - (z+?)) any slot in [0, R0) not yet overwritten
                # slot s is untouched if s < R0 and s not in written range [R0, R0+i) mod N -> true when i<=R0... use s = max(0, R0+i-N) .. R0-1
                s=(R0+i)%N - 1 - z if (R0+i)%N-1-z>=0 else None
                # simpler: slot 0 is zero until absolute index N-R0+... use slot region [0,R0) which is overwritten only after i>=N-R0
                if i+z <= N-R0+0 and i< N-R0:
                    best=z; bp=0
        for p in chains.get(raw[i:i+3],())[-64:][::-1]:
            if i-p>=N: break
            l=0
            while l<maxl and raw[p+l]==raw[i+l]: l+=1
            if l>best: best=l; bp=(R0+p)%N
            if best==maxl: break
        return best,bp
    while i<n:
        flags=0; buf=bytearray()
        for bit in range(8):
            if i>=n: break
            l,p=match(i)
            if l>=THR+1:
                buf+=bytes([p&0xFF, ((p>>4)&0xF0)|(l-THR-1)])
                for k in range(l): chains[raw[i+k:i+k+3]].append(i+k)
                i+=l
            else:
                flags|=1<<bit; buf.append(raw[i]); chains[raw[i:i+3]].append(i); i+=1
        out.append(flags); out+=buf
    return bytes(out)
if __name__=='__main__':
    import sys,glob,time
    bad=0; t0=time.time()
    for f in glob.glob(sys.argv[1]+'/**/*.sgo',recursive=True):
        d=open(f,'rb').read()
        if d[:4]!=b'SGSL': continue
        o=decompress(d); rc=compress(o); ok=decompress(rc)==o
        if not ok: bad+=1; print('FAIL',f)
    print('bad',bad,'time',round(time.time()-t0,1))
