"""Vita dpk entry -> Switch bfstm. Usage: audio_encode.py <dpk_index> <out.bfstm> [rate]"""
import sys,os,json,struct,subprocess,tempfile
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK=os.environ.get('EDF3_WORK_DIR',os.path.join(ROOT,'work'))
DPK=os.path.join(WORK,'vita_dec/psarc/Sound/Voice/Sound_Sgo.dpk')
VGA=os.path.join(ROOT,'tools/vgaudio/net451_standalone/VGAudioCli.exe')
FFMPEG=os.environ.get('EDF3_FFMPEG','ffmpeg')
NO_WINDOW=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
IDX=json.load(open(os.path.join(ROOT,'work/audio/dpk_index.json')))['entries']
def extract(i,path):
    off,sz=IDX[i]
    with open(DPK,'rb') as f: f.seek(off); open(path,'wb').write(f.read(sz))
def encode(i,out,rate=48000,tmpdir=None):
    tmpdir=tmpdir or tempfile.mkdtemp()
    at9=os.path.join(tmpdir,f'{i}.at9.wav'); pcm=os.path.join(tmpdir,f'{i}.pcm.wav')
    extract(i,at9)
    subprocess.run([FFMPEG,'-y','-loglevel','error','-i',at9,'-ar',str(rate),'-ac','1','-sample_fmt','s16',pcm],check=True,creationflags=NO_WINDOW)
    # Switch retail streams are little-endian FSTM (BOM FF FE). VGAudio's
    # default is big-endian, which decodes on desktop tools but is rejected by
    # EDF3's Switch stream loader.
    subprocess.run([VGA,'-i',pcm,'-o',out,'--no-loop','--little-endian'],check=True,capture_output=True,creationflags=NO_WINDOW)
    os.remove(at9); os.remove(pcm)
if __name__=='__main__':
    i=int(sys.argv[1]); encode(i,sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 48000); print('ok',sys.argv[2],os.path.getsize(sys.argv[2]))
