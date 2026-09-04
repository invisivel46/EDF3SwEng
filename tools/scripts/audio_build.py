"""Encode verified English voice lines into patch/romfs/Sound/stream/ (same names as the JP streams)."""
import csv,os,sys,tempfile,shutil
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import audio_encode
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT=os.path.join(os.environ.get('EDF3_OUTPUT_ROMFS',os.path.join(ROOT,'patch','romfs')),'Sound/stream'); os.makedirs(OUT,exist_ok=True)
def job(args):
    i,name=args; out=os.path.join(OUT,name)
    if os.path.exists(out) and os.path.getsize(out)>0x100:
        with open(out,'rb') as f: header=f.read(6)
        if header[:4]==b'FSTM' and header[4:6]==b'\xff\xfe': return name,'exists'
    td=tempfile.mkdtemp()
    try: audio_encode.encode(i,out,48000,td); return name,'ok'
    except Exception as e: return name,f'ERR {e}'
    finally: shutil.rmtree(td,ignore_errors=True)
if __name__=='__main__':
    rows=list(csv.DictReader(open(os.path.join(ROOT,'work/audio/voice_review.csv'),encoding='utf-8')))
    # The review table contains one monotonic best Vita candidate for every
    # spoken cue. Duration parity is useful during review, but is not a valid
    # rejection rule for localized speech: official English delivery can be
    # much longer or shorter than Japanese. Exact-name Xbox XACT fallbacks are
    # applied afterwards and take precedence over these provisional matches.
    sel=[r for r in rows if r['verdict'] in ('confirmed','low-confidence','no-match')]
    print('selected',len(sel))
    jobs=[(int(r['vita_dpk_index']),r['switch_bfstm']) for r in sel]
    res={'ok':0,'exists':0}; errs=[]
    # Each job spends almost all its time in FFmpeg/VGAudio. Threads preserve
    # parallel encoding without spawning visible Python worker consoles.
    with ThreadPoolExecutor(8) as ex:
        for n,(name,st) in enumerate(ex.map(job,jobs,chunksize=8)):
            if st.startswith('ERR'): errs.append(f'{name}\t{st}')
            else: res[st]+=1
            if n%500==0: print(n,res,len(errs),flush=True)
    open(os.path.join(ROOT,'work/audio/encode_errors.txt'),'w',encoding='utf-8').write('\n'.join(errs))
    print('done',res,'errors',len(errs))
