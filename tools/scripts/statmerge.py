import re
FW={i+0xFF10-0x30:chr(i) for i in range(0x30,0x3A)}; FW.update({0xFF0E:'.',0xFF05:'%',0xFF0B:'+',0xFF0D:'-',0xFF0F:'/',0xFF38:'X',0xD7:'x'})
num=re.compile(r'\d+(?:\.\d+)?')
def merge(jp,en,log=None,key=''):
    """Return EN text with stat numbers taken from JP stat lines ('!' lines)."""
    jp=jp.translate(FW)
    jl=[l for l in jp.split('\n') if l.startswith('!')]
    out=[]; ji=0
    for l in en.split('\n'):
        if not l.startswith('!') or ji>=len(jl): out.append(l); continue
        j=jl[ji]; ji+=1
        na=num.findall(j); nb=num.findall(l)
        if na==nb: out.append(l); continue
        if len(na)==len(nb):
            it=iter(na); l2=num.sub(lambda m:next(it),l); out.append(l2)
            if log is not None: log.append(f'{key}: {l.strip()} -> {l2.strip()}')
        else:
            # value-level substitution: pairs 'Label: value'
            jv=[p.strip() for p in re.findall(r'[：:]\s*([^\s　]+(?:[×x]\d+)?)',j)]
            parts=re.split(r'(:\s*)',l)
            # parts: [label, ': ', value..., ': ', value] -> replace value tokens
            if len(jv)==len(parts)//2:
                k=0; new=[]
                for idx,p in enumerate(parts):
                    if idx%2==0 and idx>0:
                        m=re.match(r'(\S+)(.*)',p,re.S); new.append(jv[k]+(m.group(2) if m else '')); k+=1
                    else: new.append(p)
                l2=''.join(new); out.append(l2)
                if log is not None: log.append(f'{key}: {l.strip()} -> {l2.strip()}  [value-level]')
            else:
                out.append(l)
                if log is not None: log.append(f'{key}: UNRESOLVED {j.strip()} | {l.strip()}')
    return '\n'.join(out)
