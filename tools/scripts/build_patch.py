import sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import sgo,sgsl,statmerge
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W=os.environ.get('EDF3_WORK_DIR',os.path.join(ROOT,'work')); VITA=os.path.join(W,'vita_dec','psarc'); SW=os.path.join(os.environ.get('EDF3_SWITCH_ROMFS',os.path.join(W,'switch','upd_romfs')),'JP')
OUT=sys.argv[1] if len(sys.argv)>1 else os.environ.get('EDF3_OUTPUT_ROMFS',os.path.join(ROOT,'patch','romfs'))
def write(rel,tree,keys):
    src=open(os.path.join(SW,rel),'rb').read()
    b=sgo.build_keyed(tree,keys)
    if src[:4]==b'SGSL': b=sgsl.compress(b)
    p=os.path.join(OUT,'JP',rel); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'wb').write(b); print('wrote',rel,len(b))
def keyed(path):
    d=sgo.load(path); t,_=sgo.parse(d); k=sgo.parse_keys(d); assert k and len(k)==len(t),path; return t,k
# MainSequence: English derived from the user's own Vita dump by slot->index map.
# Switch-only strings (Switch button names, Reload, TV-mode option, ...) have no
# Vita source and use this project's own English from the map's overrides.
st,sk=keyed(os.path.join(SW,'MainSequence/text.sgo'))
spec=json.load(open(os.path.join(ROOT,'work','mainseq_map.json'),encoding='utf-8'))
vms,_=keyed(os.path.join(VITA,'MainSequence/text.sgo'))
def mainseq(i):
    k=str(i)
    if k in spec['overrides']: return spec['overrides'][k]
    s=vms[spec['vita_index'][k]]
    for a,b in spec['substitutions'].get(k,[]): s=s.replace(a,b)
    return s
ms=[mainseq(i) for i in range(spec['count'])]; assert len(ms)==len(sk)
write('MainSequence/text.sgo',ms,sk)
# Mission + weapons: Vita text looked up by key; fall back to JP if a key is missing
for rel in ['Mission/text.sgo','Weapon/weapontext.sgo','Weapon/weapontextp.sgo']:
    st,sk=keyed(os.path.join(SW,rel)); vt,vk=keyed(os.path.join(VITA,rel)); vm=dict(zip(vk,vt))
    miss=[k for k in sk if k not in vm]; print(rel,'missing keys',miss)
    log=[]
    vals=[statmerge.merge(st[i],vm[k],log,k) if (k in vm and k.startswith('WeaponText_')) else vm.get(k,st[i]) for i,k in enumerate(sk)]
    if log: print('  stat lines merged from JP:',len(log),'unresolved:',sum('UNRESOLVED' in l for l in log))
    # Switch description renderer drops ASCII spaces; U+3000 renders correctly (tested in-game)
    vals=[chr(10).join(l if l.startswith('!') else l.replace(' ',chr(0x3000)) for l in v.split(chr(10))) if k.startswith('WeaponText_') else v for k,v in zip(sk,vals)]
    write(rel,vals,sk)
# Online chat-phrase / room-setting sheets: compiled spreadsheets; take English cells from the Vita ODF sheets by (table,row,col)
import xmlbin
EXTRA={'説明':'Description','テンプレート':'Template','実際に送受信されるメッセージ':'Message actually sent','リンク':'Link'}
for b,sh in {'network_room_menu':'ROOM','network_mission':'MISSION','network_room_setting':'PlayStyle'}.items():
    d=open(os.path.join(SW,'XML',b+'.xml.bin'),'rb').read(); hdr,recs=xmlbin.read(d)
    tables=xmlbin.sheet_tables(os.path.join(VITA,'XML',sh,'content.xml'))
    new,un=xmlbin.translate(recs,tables,EXTRA); assert not un,un
    p=os.path.join(OUT,'JP','XML',b+'.xml.bin'); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'wb').write(xmlbin.write(hdr,new)); print('wrote XML/'+b+'.xml.bin',len(new),'records')
# In-game HUD weapon names come from the 'name' field of each Weapon/*.sgo: take the Vita English name, keep all other data
import glob,re
JPRE=re.compile(r'[\u3040-\u30ff\u4e00-\u9fff\uff01-\uff5e]')
n=0
for f in sorted(glob.glob(os.path.join(SW,'Weapon','*.sgo'))):
    base=os.path.basename(f)
    if 'text' in base: continue
    raw=open(f,'rb').read(); d=sgo.load(f); t,_=sgo.parse(d); k=sgo.parse_keys(d)
    if not k or 'name' not in k: continue
    vf=os.path.join(VITA,'Weapon',base)
    if not os.path.exists(vf): continue
    vd=sgo.load(vf); vt,_=sgo.parse(vd); vk=sgo.parse_keys(vd); vn=dict(zip(vk,vt)).get('name')
    i=k.index('name')
    if not isinstance(vn,str) or vn==t[i] or JPRE.search(vn): continue
    t[i]=vn; b=sgo.build_keyed(t,k)
    assert sgo.parse(b)[0]==t and sgo.parse_keys(b)==k
    if raw[:4]==b'SGSL': b=sgsl.compress(b)
    p=os.path.join(OUT,'JP','Weapon',base); open(p,'wb').write(b); n+=1
print('weapon name files written',n)
