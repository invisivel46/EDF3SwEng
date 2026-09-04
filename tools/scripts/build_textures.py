"""Transplant Vita English DXT5/DXT3 blocks into Switch BNTX templates for the drop-in textures listed in
work/tex/report.md, writing to patch/romfs/JP/XUI/Res/<same relative path>. Also renders each result to
work/tex/patch_check/ for eyeballing."""
import sys,os,glob,io
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import tex_bntx,tex_vita
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W=os.environ.get('EDF3_WORK_DIR',os.path.join(ROOT,'work'))
SW=os.path.join(W,'switch/base_romfs/JP/XUI/Res'); VI=os.path.join(W,'vita_dec/psarc/XUI/Res')
OUT=os.path.join(os.environ.get('EDF3_OUTPUT_ROMFS',os.path.join(ROOT,'patch','romfs')),'JP/XUI/Res'); CHK=os.path.join(W,'tex/patch_check')
# map report key (XUI_<dir>_<file>) -> real relative path, using the real names from base_romfs
key2rel={}
for f in glob.glob(SW+'/**/*.bntx',recursive=True):
    rel=os.path.relpath(f,SW); key2rel['XUI_'+os.path.splitext(rel.replace(os.sep,'_'))[0]]=rel
written=[];skipped=[]
for l in open(os.path.join(ROOT,'work/tex/report.md'),encoding='utf-8'):
    if not l.startswith('| ') or l.startswith('| texture'): continue
    c=[x.strip() for x in l.strip().strip('|').split('|')]; key,swf,vif,verdict=c[0],c[1],c[2],c[4]
    if not verdict.startswith('DROP-IN'):
        skipped.append((key,verdict.split(':')[0].split(' [')[0])); continue
    # A BC7 Switch template is not a blocker when the Vita source already
    # contains DXT3/DXT5 blocks.  tex_bntx.encode rewrites the BRTI format and
    # swizzles those same-size (16-byte) blocks into the template.  Only an
    # actual resize or an uncompressed Vita source requires a new encoder.
    if not vif.split()[0].startswith('DXT'):
        skipped.append((key,'needs texture encode: '+verdict)); continue
    if key not in key2rel: skipped.append((key,'not a loose XUI file (lives in a resource.dxb pack)')); continue
    rel=key2rel[key]; t=open(os.path.join(SW,rel),'rb').read(); info=tex_bntx._info(t)
    im,w,h,fc,blocks,layout=tex_vita.load(os.path.join(VI,os.path.splitext(rel)[0]+'.dds'))
    if (w,h)!=(info['w'],info['h']):
        # The ending banner is the same artwork at twice the Switch width.
        # Resize in RGBA, then let Pillow's BCn encoder produce fresh blocks.
        im=im.resize((info['w'],info['h']),resample=Image.Resampling.LANCZOS)
        buf=io.BytesIO(); im.save(buf,format='DDS',pixel_format=fc)
        w,h,fc,blocks=tex_bntx.dds_blocks(buf.getvalue()); layout='resized-'+layout
    assert (w,h)==(info['w'],info['h']) and blocks
    b=tex_bntx.encode(t,blocks,fc); assert len(b)==len(t)
    op=os.path.join(OUT,rel); os.makedirs(os.path.dirname(op),exist_ok=True); open(op,'wb').write(b)
    os.makedirs(CHK,exist_ok=True); tex_bntx.decode(b).save(os.path.join(CHK,key+'.png'))
    written.append((rel.replace(os.sep,'/'),fc,layout))
print('WRITTEN',len(written)); [print(' ',*w) for w in written]
print('SKIPPED',len(skipped)); [print(' ',*s) for s in skipped]
