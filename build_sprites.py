"""Pre-bake sprites for the static site.

Run from the repo root (next to data.json and images/):

    pip3 install pillow
    python3 build_sprites.py

Body and mouth sprites are palette-indexed, and the generator swaps their palette
at runtime. Browsers decode palette PNGs straight to RGBA, which loses the index,
so this script writes "index maps" to sprites/: the palette index sits in the red
channel and index 0 (the transparent index) gets alpha 0. The original palettes go
to sprite-palettes.json. Eye sprites are never recoloured and are used from images/.

Re-run it whenever you add or change characters in data.json or images/.
"""
import json
import os
from PIL import Image

OUT = 'sprites'
os.makedirs(OUT, exist_ok=True)

with open('data.json') as f:
    data = json.load(f)

palettes = {}
for chara in data['Characters']:
    cid = chara['Id']
    entry = {}
    for kind in ('body', 'mouth'):
        with Image.open(os.path.join('images', f'{cid}_{kind}.png')) as im:
            if im.mode != 'P':
                raise SystemExit(f'{cid}_{kind}.png is not palette-indexed')
            if im.info.get('transparency') != 0:
                raise SystemExit(f'{cid}_{kind}.png: expected index 0 to be the transparent index')
            rgba_pal = im.getpalette('RGBA')
            entry[kind] = [rgba_pal[i * 4:i * 4 + 3] for i in range(len(rgba_pal) // 4)]
            idx = im.tobytes()
            px = bytearray()
            for v in idx:
                px += bytes((v, 0, 0, 0 if v == 0 else 255))
            out = Image.frombytes('RGBA', im.size, bytes(px))
            out.save(os.path.join(OUT, f'{cid}_{kind}.png'), optimize=True)
    palettes[str(cid)] = entry

with open('sprite-palettes.json', 'w') as f:
    json.dump(palettes, f, separators=(',', ':'))

print(f'Wrote {len(palettes)} characters to {OUT}/ and sprite-palettes.json')
