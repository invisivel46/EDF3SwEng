"""Structural verification for the generated EDF3 Switch LayerFS patch."""
import glob, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sgo, sgsl, tex_bntx, tex_dxb

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.environ.get('EDF3_WORK_DIR', os.path.join(ROOT, 'work'))
ROMFS = os.environ.get('EDF3_OUTPUT_ROMFS', os.path.join(ROOT, 'patch', 'romfs'))


def files(pattern):
    return glob.glob(os.path.join(ROMFS, pattern), recursive=True)


def main():
    expected = {
        'SGO': (files('**/*.sgo'), 413),
        'loose BNTX': (files('**/*.bntx'), 46),
        'voice BFSTM': (files('Sound/stream/*.bfstm'), 4807),
        'XML tables': (files('**/*.xml.bin'), 3),
    }
    for label, (paths, count) in expected.items():
        assert len(paths) == count, f'{label}: expected {count}, found {len(paths)}'
        assert all(os.path.getsize(p) > 0 for p in paths), f'{label}: empty output'
        print(label, len(paths))

    for path in files('Sound/stream/*.bfstm'):
        with open(path, 'rb') as f:
            header = f.read(6)
        assert header == b'FSTM\xff\xfe', f'not a little-endian Switch BFSTM: {path}'
    print('all BFSTM streams use the Switch little-endian byte order')

    for path in files('**/*.sgo'):
        data = open(path, 'rb').read()
        if data[:4] == b'SGSL':
            data = sgsl.decompress(data)
        sgo.parse(data)
    print('parsed all SGO files')

    for path in files('**/*.bntx'):
        tex_bntx.decode(open(path, 'rb').read()).load()
    print('decoded all loose BNTX files')

    base_path = os.path.join(WORK, 'switch/base_romfs/JP/System/resource.dxb')
    patch_path = os.path.join(ROMFS, 'JP/System/resource.dxb')
    base, base_entries = tex_dxb.load(base_path)
    patched, patched_entries = tex_dxb.load(patch_path)
    assert len(base) == len(patched)
    be = next(e for e in base_entries if e['type'].lower() == 'rescue.bntx')
    pe = next(e for e in patched_entries if e['type'].lower() == 'rescue.bntx')
    assert (be['off'], be['size']) == (pe['off'], pe['size'])
    start, end = be['off'], be['off'] + be['size']
    assert base[:start] == patched[:start] and base[end:] == patched[end:]
    rescue = patched[start:end]
    assert tex_bntx.decode(rescue).size == (256, 128)
    print('System/resource.dxb changed only rescue.bntx')
    print('PATCH VERIFIED')


if __name__ == '__main__':
    main()
