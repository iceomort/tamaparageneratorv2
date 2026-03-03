from collections import OrderedDict
import json
import os.path
from PIL import Image
import random
import streamlit as st

with open('data.json') as f:
    data = json.load(f)


# ── Character type mapping (Land / Water / Sky / Jade) ────────────────────────
CHAR_TYPES = {
    # LAND adults
    'MEOWTCHI': 'land', 'POCHITCHI': 'land', 'GUMAX': 'land', 'RATCHI': 'land',
    'MAMETCHI': 'land', 'MIMITCHI': 'land', 'MOLMOTCHI': 'land', 'SHEEPTCHI': 'land',
    'LEOPATCHI': 'land', 'SEBIRETCHI': 'land', 'ELIZARDOTCHI': 'land', 'HEAVYTCHI': 'land',
    'FURAWATCHI': 'land', 'POTSUNENTCHI': 'land', 'TUSTUSTCHI': 'land', 'SHIGEMI-SAN': 'land',
    'CHODRACOTCHI': 'land',
    # WATER adults
    'IRUKATCHI': 'water', 'KAMETCHI': 'water', 'KUJIRATCHI': 'water', 'URUOTCHI': 'water',
    'AXOLOPATCHI': 'water', 'IMORITCHI': 'water', 'KAWAZUTCHI': 'water', 'BEAVERTCHI': 'water',
    'TACHUTCHI': 'water', 'SHARKTCHI': 'water', 'ANKOTCHI': 'water', 'OTOTOTCHI': 'water',
    'KURARATCHI': 'water', 'MENDAKOTCHI': 'water', 'AMEFURATCHI': 'water', 'GUSOKUTCHI': 'water',
    'MERMARINTCHI': 'water',
    # SKY adults
    'HORHOTCHI': 'sky', 'MONGATCHI': 'sky', 'EAGLETCHI': 'sky', 'BATCHI': 'sky',
    'PEACOTCHI': 'sky', 'BATATCHI': 'sky', 'KUCHIPATCHI': 'sky', 'KIWITCHI': 'sky',
    'PAPILLOTCHI': 'sky', 'KABUTOTCHI': 'sky', 'TENTOTCHI': 'sky', 'HATCHITCHI': 'sky',
    'GEMTCHI': 'sky', 'ORETATCHI': 'sky', 'ISHIKOROTCHI': 'sky', 'MAGMATCHI': 'sky',
    'YAYACORNTCHI': 'sky',
    # JADE adults
    'FOREST HORHOTCHI': 'jade', 'KONKOTCHI': 'jade', 'TIGAOTCHI': 'jade', 'TANOONTCHI': 'jade',
    'LESSAPANTCHI': 'jade', 'KANOKOTCHI': 'jade', 'SUIGYUTCHI': 'jade', 'PANBOOTCHI': 'jade',
    'KACHITCHI': 'jade', 'TOKIPATCHI': 'jade', 'FOREST KUCHIPATCHI': 'jade', 'SPARROTCHI': 'jade',
    'SHIITAKETCHI': 'jade', 'PEATCHI': 'jade', 'NAPPATCHI': 'jade', 'RUSHRADITCHI': 'jade',
    'TATSUTCHI': 'jade',
}

def get_char_type(chara):
    return CHAR_TYPES.get(chara['Name'].upper(), 'other')

st.set_page_config(page_title="Tamagotchi Paradise Genes Generator", layout="wide")

# ── CSS for the image picker grid ──────────────────────────────────────────────
st.markdown("""
<style>
/* Card grid */
.tama-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-start;
    padding: 8px 0;
}
.tama-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 6px;
    border-radius: 8px;
    border: 2px solid transparent;
    background: rgba(255,255,255,0.04);
    cursor: pointer;
    transition: all 0.15s ease;
    min-width: 70px;
}
.tama-card:hover {
    background: rgba(255,255,255,0.10);
    border-color: rgba(255,255,255,0.25);
}
.tama-card.selected {
    background: rgba(99,102,241,0.25);
    border-color: #6366f1;
}
.tama-card img {
    image-rendering: pixelated;
    width: 48px;
    height: 48px;
    object-fit: contain;
}
.tama-card .label {
    font-size: 9px;
    text-align: center;
    color: #ccc;
    word-break: break-word;
    max-width: 68px;
    line-height: 1.2;
}
.tama-card.selected .label {
    color: #a5b4fc;
    font-weight: bold;
}
/* Shrink picker button text */
div[data-testid="stButton"] button p {
    font-size: 9px !important;
    line-height: 1.1 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
/* Section header for picker */
.picker-header {
    font-size: 13px;
    font-weight: 600;
    color: #aaa;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
/* Selected display badge */
.selected-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: rgba(99,102,241,0.2);
    border: 1px solid #6366f1;
    border-radius: 20px;
    font-size: 13px;
    color: #a5b4fc;
    font-weight: 600;
    margin-bottom: 8px;
}
/* History delete button — small ✕ overlaid top-right */
.history-del {
    position: relative;
    display: inline-block;
}
.history-del button {
    position: absolute;
    top: 4px;
    right: 4px;
    width: 20px !important;
    height: 20px !important;
    min-height: 20px !important;
    padding: 0 !important;
    font-size: 11px !important;
    border-radius: 50% !important;
    background: rgba(0,0,0,0.5) !important;
    color: white !important;
    border: none !important;
    line-height: 1 !important;
    z-index: 10;
}
.history-del button:hover {
    background: rgba(220,50,50,0.8) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Image helpers ──────────────────────────────────────────────────────────────

def get_image_b64(path):
    """Return a base64-encoded data URI for an image file."""
    import base64
    try:
        with open(path, 'rb') as f:
            data_bytes = f.read()
        ext = path.rsplit('.', 1)[-1].lower()
        mime = 'image/png' if ext == 'png' else 'image/jpeg'
        return f"data:{mime};base64,{base64.b64encode(data_bytes).decode()}"
    except Exception:
        return ""

def body_image_path(chara_id):
    return os.path.join('images', f'{chara_id}_body.png')

def eyes_image_path(chara_id):
    return os.path.join('images', f'{chara_id}_eyes.png')

def composite_thumb(chara):
    """Generate composite (body+eyes+mouth) and return as base64 data URI."""
    import io, base64 as b64
    try:
        body_path = body_image_path(chara['Id'])
        eyes_path = eyes_image_path(chara['Id'])
        mouth_path = os.path.join('images', f'{chara["Id"]}_mouth.png')
        if not all(os.path.exists(p) for p in [body_path, eyes_path, mouth_path]):
            return get_image_b64(body_path)
        with Image.open(body_path) as bi, Image.open(eyes_path) as ei, Image.open(mouth_path) as mi:
            draw_offset = [0, 0]
            for prop in ('EyePos', 'MouthPos'):
                for i in range(2):
                    if chara[prop][i] < draw_offset[i]:
                        draw_offset[i] = chara[prop][i]
            draw_offset = [-draw_offset[0], -draw_offset[1]]
            dim = [0, 0]
            for img in (bi, ei, mi):
                if img.width + draw_offset[0] > dim[0]: dim[0] = img.width + draw_offset[0]
                if img.height + draw_offset[1] > dim[1]: dim[1] = img.height + draw_offset[1]
            comp = Image.new('RGBA', dim, (0,0,0,0))
            comp.paste(bi.convert('RGBA'), (draw_offset[0], draw_offset[1]), bi.convert('RGBA'))
            comp.paste(ei.convert('RGBA'), (draw_offset[0]+chara['EyePos'][0], draw_offset[1]+chara['EyePos'][1]), ei.convert('RGBA'))
            comp.paste(mi.convert('RGBA'), (draw_offset[0]+chara['MouthPos'][0], draw_offset[1]+chara['MouthPos'][1]), mi.convert('RGBA'))
            buf = io.BytesIO()
            comp.save(buf, format='PNG')
            return f"data:image/png;base64,{b64.b64encode(buf.getvalue()).decode()}"
    except Exception:
        return get_image_b64(body_image_path(chara['Id']))

def thumb_src(chara, kind='body'):
    """Return a base64 data URI for the character thumbnail."""
    return composite_thumb(chara)

# ── Image picker component ─────────────────────────────────────────────────────

def image_picker(label, characters, key, kind='body'):
    if key not in st.session_state or st.session_state[key] not in characters:
        st.session_state[key] = characters[0] if characters else None

    selected = st.session_state[key]

    st.markdown(f'<div class="picker-header">{label}</div>', unsafe_allow_html=True)

    if selected:
        src = thumb_src(selected, kind)
        img_tag = f'<img src="{src}" style="width:24px;height:24px;image-rendering:pixelated;" />' if src else ""
        st.markdown(f'<div class="selected-badge">{img_tag} {selected["Name"]}</div>', unsafe_allow_html=True)

    cols_per_row = 6
    rows = [characters[i:i+cols_per_row] for i in range(0, len(characters), cols_per_row)]

    with st.expander(f"Pick {label} ▼", expanded=False):
        for row in rows:
            cols = st.columns(len(row))
            for col, chara in zip(cols, row):
                with col:
                    src = thumb_src(chara, kind)
                    is_selected = selected and chara['Id'] == selected['Id']
                    border = "2px solid #6366f1" if is_selected else "2px solid transparent"
                    bg = "rgba(99,102,241,0.2)" if is_selected else "rgba(255,255,255,0.04)"

                    if src:
                        st.markdown(
                            f'''<div style="text-align:center;padding:4px;border-radius:8px;
                                border:{border};background:{bg};margin-bottom:2px;">
                                <img src="{src}" style="width:40px;height:40px;
                                image-rendering:pixelated;object-fit:contain;" />
                            </div>''',
                            unsafe_allow_html=True
                        )

                    btn_label = chara['Name'][:8]
                    if st.button(btn_label, key=f"pick_{key}_{chara['Id']}", use_container_width=True):
                        st.session_state[key] = chara
                        st.rerun()

    return st.session_state[key]

# ── Generate composite image ───────────────────────────────────────────────────

def generate_image(body, eyes, color):
    with Image.open(os.path.join('images', f'{body["Id"]}_body.png')) as body_image, \
         Image.open(os.path.join('images', f'{eyes["Id"]}_eyes.png')) as eyes_image, \
         Image.open(os.path.join('images', f'{body["Id"]}_mouth.png')) as mouth_image:

        draw_offset = [0, 0]
        for prop in ('EyePos', 'MouthPos'):
            for i in range(2):
                if body[prop][i] < draw_offset[i]:
                    draw_offset[i] = body[prop][i]
        draw_offset = [-draw_offset[0], -draw_offset[1]]

        image_dimension = [0, 0]
        for image in (body_image, eyes_image, mouth_image):
            part_max_x = image.width + draw_offset[0]
            part_max_y = image.height + draw_offset[1]
            if part_max_x > image_dimension[0]:
                image_dimension[0] = part_max_x
            if part_max_y > image_dimension[1]:
                image_dimension[1] = part_max_y

        def replace_palette(image, new_palette):
            curr_palette = image.getpalette('RGBA')
            curr_palette[:len(new_palette)] = new_palette
            image.putpalette(curr_palette, 'RGBA')

        if color['Colors']:
            replace_palette(body_image, color['Colors'])
            replace_palette(mouth_image, color['Colors'])

        composite_image = Image.new('RGBA', image_dimension, '#fff0')
        composite_image.paste(body_image, (draw_offset[0], draw_offset[1]), body_image.convert('RGBA'))
        composite_image.paste(eyes_image, (draw_offset[0] + body['EyePos'][0], draw_offset[1] + body['EyePos'][1]), eyes_image.convert('RGBA'))
        composite_image.paste(mouth_image, (draw_offset[0] + body['MouthPos'][0], draw_offset[1] + body['MouthPos'][1]), mouth_image.convert('RGBA'))
        return composite_image


# ── Layout ─────────────────────────────────────────────────────────────────────

# Pick 2 random adult tamas for the header (fixed per session)
if 'header_tamas' not in st.session_state:
    adults = [c for c in data['Characters'] if c['Stage'] == 5]
    st.session_state['header_tamas'] = random.sample(adults, 2)

header_tamas = st.session_state['header_tamas']
left_src = composite_thumb(header_tamas[0])
right_src = composite_thumb(header_tamas[1])

st.markdown(f'''
<div style="text-align:center; padding: 16px 0 4px 0;">
    <div style="display:inline-flex; align-items:center; gap:12px;">
        <img src="{left_src}" style="width:56px;height:56px;image-rendering:pixelated;" />
        <span style="font-size:1.8rem; font-weight:800; letter-spacing:0.02em;">Tamagotchi Paradise Genes Generator</span>
        <img src="{right_src}" style="width:56px;height:56px;image-rendering:pixelated;" />
    </div>
    <div style="font-size:0.78rem; color:#888; margin-top:4px;">
        created by <a href="https://github.com/scalynko/tamaparagenerator" target="_blank" style="color:#a5b4fc;">Scalynko</a>
        &nbsp;/&nbsp; modified by <em>Iceomort</em> (24 Feb 2026)
    </div>
</div>
''', unsafe_allow_html=True)

# ── Options ───────────────────────────────────────────────────────────────────
with st.container(border=True):
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        opt_include_land = st.checkbox('🌿 Land', True)
    with fc2:
        opt_include_water = st.checkbox('💧 Water', True)
    with fc3:
        opt_include_sky = st.checkbox('☁️ Sky', True)
    with fc4:
        opt_include_jade = st.checkbox('🎋 Jade', True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        opt_include_non_breedable = st.checkbox('Include non-breedable eyes')
    with c2:
        opt_include_external_eyes = st.checkbox('Include Lab Tama eyes')
    with c3:
        opt_include_external_bodies = st.checkbox('Include Lab Tama bodies')
    with c4:
        opt_include_non_adult_bodies = st.checkbox('Include non-adult bodies')

# ── Filtering ─────────────────────────────────────────────────────────────────

def chara_filter(chara):
    ctype = get_char_type(chara)
    if ctype == 'land' and not opt_include_land: return False
    if ctype == 'water' and not opt_include_water: return False
    if ctype == 'sky' and not opt_include_sky: return False
    if ctype == 'jade' and not opt_include_jade: return False
    # For non-adults (kids, young, baby), follow jade flag for jade chars
    if chara['IsJade'] and not opt_include_jade: return False
    return True

def body_filter(chara):
    if not opt_include_external_bodies:
        if chara['IsExternal']:
            return False
    if not opt_include_non_adult_bodies:
        if chara['Stage'] < 5:
            return False
    return True

def eyes_filter(chara):
    if not opt_include_non_breedable:
        if chara['Stage'] < 5 or chara['Name'] == 'BBMARUTCHI':
            return False
    if not opt_include_external_eyes:
        if chara['IsExternal']:
            return False
    return True

charas_list  = list(filter(chara_filter, data['Characters']))
bodies_list  = list(filter(body_filter, charas_list))
eyes_list    = list(filter(eyes_filter, charas_list))

# ── Session state init ─────────────────────────────────────────────────────────
if 'history' not in st.session_state:
    st.session_state['history'] = OrderedDict()

# ── Pickers ────────────────────────────────────────────────────────────────────
with st.container(border=True):
    col_body, col_eyes = st.columns(2)

    with col_body:
        # Random button
        if st.button('🎲 Random Body', use_container_width=True):
            st.session_state['body'] = random.choice(bodies_list)
            st.rerun()
        selected_body = image_picker('Body', bodies_list, 'body', kind='body')

    with col_eyes:
        if st.button('🎲 Random Eyes', use_container_width=True):
            st.session_state['eyes'] = random.choice(eyes_list)
            st.rerun()
        selected_eyes = image_picker('Eyes', eyes_list, 'eyes', kind='body')  # show body sprite as thumbnail for eyes character

    # Color selector (kept as selectbox since it's palette-based, not character)
    color_names = [p['Name'] for p in data['Palettes']]
    if 'color' not in st.session_state:
        st.session_state['color'] = data['Palettes'][0]

    if 'color_idx' not in st.session_state:
        st.session_state['color_idx'] = 0

    col_color, col_rand_color = st.columns([4, 1])
    with col_color:
        color_idx = st.selectbox(
            'Color Palette',
            range(len(data['Palettes'])),
            format_func=lambda i: data['Palettes'][i]['Name'],
            index=st.session_state['color_idx'],
        )
        st.session_state['color_idx'] = color_idx
        selected_color = data['Palettes'][color_idx]
    with col_rand_color:
        st.write("")  # spacer
        if st.button('🎲', use_container_width=True, key='random_color'):
            st.session_state['color_idx'] = random.randint(0, len(data['Palettes']) - 1)
            st.rerun()

# Randomise all
if st.button('🎲 Randomise All', use_container_width=True):
    st.session_state['body'] = random.choice(bodies_list)
    st.session_state['eyes'] = random.choice(eyes_list)
    st.session_state['color_idx'] = random.randint(0, len(data['Palettes']) - 1)
    st.rerun()

# ── Generate & display ─────────────────────────────────────────────────────────
cache_key = f'{selected_body["Id"]}_{selected_eyes["Id"]}_{selected_color["Name"]}'

if cache_key in st.session_state['history']:
    composite_image = st.session_state['history'][cache_key]['image']
else:
    composite_image = generate_image(selected_body, selected_eyes, selected_color)
    st.session_state['history'][cache_key] = {
        'selected_body': selected_body['Name'],
        'selected_eyes': selected_eyes['Name'],
        'selected_color': selected_color['Name'],
        'image': composite_image
    }

with st.container(border=True):
    col_big, col_small = st.columns(2, vertical_alignment='center')
    with col_big:
        st.image(composite_image, width=160)
        st.caption(f"**{selected_body['Name']}** body × **{selected_eyes['Name']}** eyes — {selected_color['Name']}")
    with col_small:
        st.image(composite_image)

# ── History ────────────────────────────────────────────────────────────────────
st.header('History')

if 'selected_to_delete' not in st.session_state:
    st.session_state['selected_to_delete'] = set()

with st.container():
    history_list = list(st.session_state['history'].items())
    history_list.reverse()

    if history_list:
        # Action buttons
        col_del, col_rand, col_clear = st.columns([1, 1, 1])
        n_selected = len(st.session_state['selected_to_delete'])
        with col_del:
            if st.button(f'🗑️ Delete selected ({n_selected})', disabled=n_selected == 0, use_container_width=True):
                for k in st.session_state['selected_to_delete']:
                    st.session_state['history'].pop(k, None)
                st.session_state['selected_to_delete'] = set()
                st.rerun()
        with col_rand:
            if st.button(f'🎲 Randomise selected ({n_selected})', disabled=n_selected == 0, use_container_width=True):
                selected_entries = [st.session_state['history'][k] for k in st.session_state['selected_to_delete'] if k in st.session_state['history']]
                if selected_entries:
                    if len(selected_entries) == 1:
                        # 1 tama selected: mix its body/eyes with the full available pool
                        entry = selected_entries[0]
                        tama_body = next((c for c in bodies_list if c['Name'] == entry['selected_body']), None)
                        tama_eyes = next((c for c in eyes_list if c['Name'] == entry['selected_eyes']), None)
                        tama_color = next((i for i, p in enumerate(data['Palettes']) if p['Name'] == entry['selected_color']), None)
                        # Randomly decide: keep body or eyes from the selected tama, randomise the other
                        if random.random() < 0.5:
                            if tama_body: st.session_state['body'] = tama_body
                            st.session_state['eyes'] = random.choice(eyes_list)
                        else:
                            st.session_state['body'] = random.choice(bodies_list)
                            if tama_eyes: st.session_state['eyes'] = tama_eyes
                        # Color: 50/50 between tama's color or fully random
                        if tama_color is not None and random.random() < 0.5:
                            st.session_state['color_idx'] = tama_color
                        else:
                            st.session_state['color_idx'] = random.randint(0, len(data['Palettes']) - 1)
                    else:
                        # 2+ selected: pick body, eyes, color independently from the selected pool
                        body_pool = [next((c for c in bodies_list if c['Name'] == e['selected_body']), None) for e in selected_entries]
                        eyes_pool = [next((c for c in eyes_list if c['Name'] == e['selected_eyes']), None) for e in selected_entries]
                        color_pool = [next((i for i, p in enumerate(data['Palettes']) if p['Name'] == e['selected_color']), None) for e in selected_entries]
                        body_pool = [b for b in body_pool if b]
                        eyes_pool = [e for e in eyes_pool if e]
                        color_pool = [c for c in color_pool if c is not None]
                        if body_pool: st.session_state['body'] = random.choice(body_pool)
                        if eyes_pool: st.session_state['eyes'] = random.choice(eyes_pool)
                        if color_pool: st.session_state['color_idx'] = random.choice(color_pool)
                    st.rerun()
        with col_clear:
            if st.button('✕ Clear all history', use_container_width=True):
                st.session_state['history'] = OrderedDict()
                st.session_state['selected_to_delete'] = set()
                st.rerun()

        cols = st.columns(min(len(history_list), 6))
        for idx, (k, v) in enumerate(history_list[:18]):
            with cols[idx % 6]:
                is_checked = k in st.session_state['selected_to_delete']
                if st.checkbox('', value=is_checked, key=f'chk_{k}'):
                    st.session_state['selected_to_delete'].add(k)
                else:
                    st.session_state['selected_to_delete'].discard(k)
                st.image(v['image'], width=96)
                st.caption(f"{v['selected_body']} × {v['selected_eyes']}\n{v['selected_color']}")
    else:
        st.write("No history yet.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Original Generator created by [Scalynko](https://github.com/scalynko/tamaparagenerator) — I just made some edits! - ice")
