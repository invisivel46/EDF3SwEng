"""Build English Switch controller-help textures.

The Vita images supply the official English labels.  Only the PlayStation
button glyph rectangles are removed; authentic glyphs are cropped from the
matching Japanese Switch texture and centred in their place.  The result is
encoded as DXT5 and inserted into the original BNTX template.
"""
import io, os, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tex_bntx, tex_vita, tex_dxb

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.environ.get('EDF3_WORK_DIR', os.path.join(ROOT, 'work'))
ROMFS = os.environ.get('EDF3_OUTPUT_ROMFS', os.path.join(ROOT, 'patch', 'romfs'))
SW = os.path.join(WORK, 'switch/base_romfs/JP/XUI/Res')
VI = os.path.join(WORK, 'vita_dec/psarc/XUI/Res')
OUT = os.path.join(ROMFS, 'JP/XUI/Res')
CHK = os.path.join(WORK, 'tex/controller_check')

# Each tuple is (Vita rectangle to erase, Switch rectangle to copy).  Rectangle
# coordinates are half-open PIL boxes.  Source glyphs are deliberately not
# scaled, preserving the shipped Switch artwork.
RECIPES = {
    'loading_technical/loading_02_bg_06.bntx': [
        ((27, 114, 94, 180), (31, 53, 95, 116)),       # left stick
        ((27, 197, 94, 263), (31, 119, 95, 182)),      # right stick
        ((390, 154, 477, 207), (426, 158, 473, 205)),  # SELECT -> A
        ((43, 286, 101, 345), (16, 296, 104, 339)),    # triangle -> L
        ((583, 286, 642, 345), (559, 296, 647, 339)),  # circle -> R
        ((1, 394, 107, 435), (33, 391, 104, 437)),     # L -> ZL
        ((325, 394, 431, 435), (356, 391, 427, 437)),  # R -> ZR
    ],
    'Loading_Skin_06/bb_02_02.bntx': [
        ((253, 10, 310, 64), (260, 16, 303, 59)),      # square -> Y
        ((489, 10, 546, 64), (501, 16, 544, 59)),      # triangle -> X
        ((253, 72, 310, 127), (260, 77, 303, 121)),    # cross -> B
        ((489, 72, 546, 127), (426, 158, 473, 205),
         'loading_technical/loading_02_bg_06.bntx'),    # circle -> A
        ((250, 166, 314, 232), (251, 170, 312, 231)),  # left stick
        ((607, 166, 671, 232), (607, 170, 670, 231)),  # right stick
        ((225, 282, 330, 322), (243, 281, 312, 325)),  # L -> ZL
        ((540, 282, 646, 322), (560, 281, 628, 325)),  # R -> ZR
    ],
    'Loading_Skin_05/ef24_02_02.bntx': [
        ((252, 9, 311, 65), (260, 16, 303, 59), 'Loading_Skin_06/bb_02_02.bntx'),
        ((541, 9, 601, 65), (501, 16, 544, 59), 'Loading_Skin_06/bb_02_02.bntx'),
        ((252, 71, 311, 128), (260, 77, 303, 121), 'Loading_Skin_06/bb_02_02.bntx'),
        ((249, 165, 315, 233), (251, 170, 312, 231), 'Loading_Skin_06/bb_02_02.bntx'),
        ((224, 320, 331, 361), (233, 320, 319, 360)),  # L
        ((539, 320, 647, 361), (550, 320, 636, 360)),  # R
    ],
    'Loading_Skin_05/e551_02_02.bntx': [
        ((252, 9, 311, 65), (260, 16, 303, 59), 'Loading_Skin_06/bb_02_02.bntx'),
        ((249, 165, 315, 233), (251, 170, 312, 231), 'Loading_Skin_06/bb_02_02.bntx'),
        ((554, 165, 618, 233), (607, 170, 670, 231), 'Loading_Skin_06/bb_02_02.bntx'),
        ((224, 282, 331, 323), (560, 281, 628, 325), 'Loading_Skin_06/bb_02_02.bntx'),
    ],
    'Loading_Skin_06/sdl2_02_02.bntx': [
        ((252, 35, 311, 92), (260, 16, 303, 59), 'Loading_Skin_06/bb_02_02.bntx'),
        ((249, 165, 315, 233), (251, 170, 312, 231), 'Loading_Skin_06/bb_02_02.bntx'),
        ((224, 282, 331, 323), (560, 281, 628, 325), 'Loading_Skin_06/bb_02_02.bntx'),
    ],
}


def centre_paste(dst, src, dst_box, src_box):
    fill = dst.getpixel((0, 0))
    dst.paste(fill, dst_box)
    glyph = src.crop(src_box)
    x = dst_box[0] + ((dst_box[2] - dst_box[0]) - glyph.width) // 2
    y = dst_box[1] + ((dst_box[3] - dst_box[1]) - glyph.height) // 2
    if dst.mode == 'RGBA' and glyph.mode == 'RGBA':
        dst.alpha_composite(glyph, (x, y))
    else:
        dst.paste(glyph, (x, y))


def main():
    os.makedirs(CHK, exist_ok=True)
    for rel, replacements in RECIPES.items():
        template = open(os.path.join(SW, rel), 'rb').read()
        switch = tex_bntx.decode(template)
        vita_path = os.path.join(VI, os.path.splitext(rel)[0] + '.dds')
        english, w, h, _fc, _blocks, _layout = tex_vita.load(vita_path)
        assert english.size == switch.size == (w, h)
        for replacement in replacements:
            dst_box, src_box = replacement[:2]
            glyph_source = switch
            if len(replacement) == 3:
                glyph_source = tex_bntx.decode(open(os.path.join(SW, replacement[2]), 'rb').read())
            centre_paste(english, glyph_source, dst_box, src_box)

        dds = io.BytesIO()
        english.save(dds, format='DDS', pixel_format='DXT5')
        ew, eh, fc, blocks = tex_bntx.dds_blocks(dds.getvalue())
        assert (ew, eh) == (w, h)
        result = tex_bntx.encode(template, blocks, fc)
        out_path = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'wb') as f:
            f.write(result)
        tex_bntx.decode(result).save(os.path.join(CHK, rel.replace('/', '_')[:-5] + '.png'))
        print('wrote', rel)

    # Backup/Ride lives inside System/resource.dxb rather than as a loose BNTX.
    pack_path = os.path.join(WORK, 'switch/base_romfs/JP/System/resource.dxb')
    pack, entries = tex_dxb.load(pack_path)
    entry = next(e for e in entries if e['type'].lower() == 'rescue.bntx')
    template = pack[entry['off']:entry['off'] + entry['size']]
    switch = tex_bntx.decode(template)
    vita_pack, vita_entries = tex_dxb.load(os.path.join(WORK, 'vita_dec/psarc/System/Resource.Dxb'))
    vita_entry = next(e for e in vita_entries if e['type'].lower() == 'rescue.dds')
    vita_path = os.path.join(WORK, 'vita_dec', 'rescue.dds')
    with open(vita_path, 'wb') as f:
        f.write(vita_pack[vita_entry['off']:vita_entry['off'] + vita_entry['size']])
    english, w, h, _fc, _blocks, _layout = tex_vita.load(vita_path)
    assert english.size == switch.size == (w, h) == (256, 128)
    # The row frame geometry is identical.  Copy its left side wholesale so
    # the original gradient/border survives while the English words to the
    # right remain untouched.
    english.paste(switch.crop((12, 1, 91, 57)), (12, 1))
    english.paste(switch.crop((12, 59, 91, 116)), (12, 59))
    dds = io.BytesIO(); english.save(dds, format='DDS', pixel_format='DXT5')
    ew, eh, fc, blocks = tex_bntx.dds_blocks(dds.getvalue())
    assert (ew, eh) == (w, h)
    result = tex_bntx.encode(template, blocks, fc)
    assert len(result) == entry['size']
    patched_pack = bytearray(pack)
    patched_pack[entry['off']:entry['off'] + entry['size']] = result
    out_path = os.path.join(ROMFS, 'JP/System/resource.dxb')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(patched_pack)
    tex_bntx.decode(result).save(os.path.join(CHK, 'System_rescue.png'))
    print('wrote JP/System/resource.dxb (rescue.bntx)')


if __name__ == '__main__':
    main()
