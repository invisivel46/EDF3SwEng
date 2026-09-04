import struct,re
import xml.etree.ElementTree as ET
JP=re.compile(r'[\u3040-\u30ff\u4e00-\u9fff]')
def read(data):
    n=struct.unpack('<I',data[:4])[0]; hdr=data[4:8]; tb=8+8*n; recs=[]
    for i in range(n):
        f=data[8+8*i:12+8*i]; off=struct.unpack('<I',data[12+8*i:16+8*i])[0]
        e=data.find(b'\0',tb+off); recs.append((f,data[tb+off:e].decode('utf-8')))
    return hdr,recs
def write(hdr,recs):
    out=bytearray(struct.pack('<I',len(recs))+hdr); strs=bytearray(); pos={}
    for f,s in recs:
        if s not in pos: pos[s]=len(strs); strs+=s.encode('utf-8')+b'\0'
        out+=f+struct.pack('<I',pos[s])
    return bytes(out+strs)
T='{urn:oasis:names:tc:opendocument:xmlns:table:1.0}'; X='{urn:oasis:names:tc:opendocument:xmlns:text:1.0}'
def sheet_tables(f):
    """ODF sheet -> list of (name, {(row,col):text})."""
    root=ET.parse(f).getroot(); out=[]
    for tbl in root.iter(T+'table'):
        cells={}; r=0
        for row in tbl.iter(T+'table-row'):
            rep=int(row.get(T+'number-rows-repeated','1')); c=0
            for cell in row:
                if cell.tag!=T+'table-cell': continue
                n=int(cell.get(T+'number-columns-repeated','1')); txt=chr(10).join(''.join(p.itertext()) for p in cell.iter(X+'p'))
                if txt: cells[(r,c)]=txt
                c+=n
            r+=rep
        out.append((tbl.get(T+'name'),cells))
    return out
def translate(recs, tables, extra=None):
    """Replace JP record strings with the English sheet cell at the same (table,row,col). Returns (new_recs, unresolved)."""
    extra=extra or {}; new=[]; unresolved=[]
    for f,s in recs:
        a,_,b,c=f
        t=s
        if JP.search(s):
            if s in extra: t=extra[s]
            elif 0<=a-1<len(tables):
                name,cells=tables[a-1]
                cell=cells.get((c-1,b-1)) if c>0 else name
                if cell and not JP.search(cell): t=cell
                else: unresolved.append((f.hex(' '),s,cell))
            else: unresolved.append((f.hex(' '),s,None))
        new.append((f,t))
    return new,unresolved
