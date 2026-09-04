import struct, sys, json, os
sys.path.insert(0,os.path.dirname(__file__)); import sgsl
def load(path):
    d=open(path,'rb').read()
    if d[:4]==b'SGSL': d=sgsl.decompress(d)
    return d
def parse(data):
    be = data[:4]==b'\0OGS'
    E='>' if be else '<'
    cnt,noff,doff=struct.unpack(E+'III',data[4:16])
    def node(off):
        t,c,v=struct.unpack(E+'III',data[off:off+12])
        if t==0: return [node(off+v+i*12) for i in range(c)]
        if t==1: return struct.unpack(E+'i',data[off+8:off+12])[0]
        if t==2: return struct.unpack(E+'f',data[off+8:off+12])[0]
        if t==3: return data[off+v:off+v+c*2].decode('utf-16-be' if be else 'utf-16-le')
        if t==4: return {'raw':data[off+v:off+v+c].hex()}
        return {'t':t,'c':c,'v':v}
    return [node(noff+i*12) for i in range(cnt)], doff
if __name__=='__main__':
    tree,doff=parse(load(sys.argv[1]))
    print(json.dumps(tree,ensure_ascii=False,indent=1))

def build(tree, doff_unused=None):
    """Serialize tree (list of nodes) to LE SGO bytes. Strings deduplicated, stored after the node table."""
    import struct
    nodes=bytearray(); strings=bytearray(); fixups=[]  # (node_off, str_key)
    strpos={}
    def add_str(s):
        b=s.encode('utf-16-le')+b'\0\0'
        if b not in strpos:
            strpos[b]=len(strings); strings.extend(b)
        return strpos[b]
    def emit_list(items, base_off):
        # writes items' nodes starting at base_off; children of lists appended afterwards (depth-first, breadth per list)
        pending=[]
        for i,it in enumerate(items):
            off=base_off+i*12
            if isinstance(it,list):
                pending.append((off,it)); nodes[off:off+12]=struct.pack('<III',0,len(it),0)
            elif isinstance(it,bool): nodes[off:off+12]=struct.pack('<IIi',1,4,int(it))
            elif isinstance(it,int): nodes[off:off+12]=struct.pack('<IIi',1,4,it)
            elif isinstance(it,float): nodes[off:off+12]=struct.pack('<IIf',2,4,it)
            elif isinstance(it,str):
                nodes[off:off+12]=struct.pack('<III',3,len(it.encode('utf-16-le'))//2,0); fixups.append((off,add_str(it)))
            elif isinstance(it,dict) and 't' in it:
                nodes[off:off+12]=struct.pack('<III',it['t'],it['c'],it['v'])
            elif isinstance(it,dict) and 'raw' in it:
                raw=bytes.fromhex(it['raw']); nodes[off:off+12]=struct.pack('<III',4,len(raw),0); fixups.append((off,('raw',raw)))
            else: raise ValueError(it)
        for off,it in pending:
            child=len(nodes); nodes.extend(b'\0'*(12*len(it)))
            nodes[off+8:off+12]=struct.pack('<I',child-off)
            emit_list(it,child)
    nodes.extend(b'\0'*(12*len(tree))); emit_list(tree,0)
    hdr=16; data_off=hdr+len(nodes)
    raws=bytearray()
    out=bytearray(b'SGO\0'+struct.pack('<III',len(tree),hdr,data_off))
    body=nodes
    for off,key in fixups:
        if isinstance(key,tuple):
            p=len(nodes)+len(strings)+len(raws); raws.extend(key[1])
            while len(raws)%4: raws.append(0)
        else: p=len(nodes)+key
        body[off+8:off+12]=struct.pack('<I',p-off)
    out+=body+strings+raws
    return bytes(out)

def parse_keys(data):
    """Return list of key names (one per root entry) if the file has a key table between nodes and strings, else None."""
    import struct
    be = data[:4]==b'\0OGS'; E='>' if be else '<'
    cnt,noff,doff=struct.unpack(E+'III',data[4:16])
    if doff+4*cnt>len(data): return None
    # detect: string data must not start inside the table region
    minstr=len(data)
    for i in range(cnt):
        t,c,v=struct.unpack(E+'III',data[noff+i*12:noff+i*12+12])
        if t==3: minstr=min(minstr,noff+i*12+v)
    if minstr<doff+4*cnt: return None
    keys=[]
    for i in range(cnt):
        p=doff+4*i+struct.unpack(E+'I',data[doff+4*i:doff+4*i+4])[0]
        e=p
        while data[e:e+2]!=b'\0\0': e+=2
        keys.append(data[p:e].decode('utf-16-be' if be else 'utf-16-le'))
    return keys

def build_keyed(tree, keys):
    """Serialize root list of values with a per-entry key table (text.sgo layout)."""
    import struct
    assert len(tree)==len(keys)
    base=build(tree)                      # header + nodes + strings
    cnt,noff,doff=struct.unpack('<III',base[4:16])
    nodes=bytearray(base[16:doff]); strings=bytearray(base[doff:])
    tbl_len=4*cnt
    # node string offsets are relative to node position; strings shift by tbl_len -> patch every type-3 node
    for i in range(0,len(nodes),12):
        t,c,v=struct.unpack('<III',nodes[i:i+12])
        if t in (3,4): nodes[i+8:i+12]=struct.pack('<I',v+tbl_len)
    strpos={}
    tbl=bytearray()
    for i,k in enumerate(keys):
        b=k.encode('utf-16-le')+b'\0\0'
        if b not in strpos: strpos[b]=len(strings); strings+=b
        entry_pos=doff+4*i; target=doff+tbl_len+strpos[b]
        tbl+=struct.pack('<I',target-entry_pos)
    return bytes(b'SGO\0'+struct.pack('<III',cnt,16,doff)+nodes+tbl+strings)
