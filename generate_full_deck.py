#!/usr/bin/env python3
"""
Generate the complete 107-slide PÉNÉLOPE × MONOPRIX AO 2027 HTML deck.
Reads all slide JSON files and produces a single HTML file with the premium design system.
"""

import json
import os
import glob
import html as html_mod

SLIDES_DIR = '/Users/maxwell/.openclaw/workspace/penelope-v2/slides'
IMAGES_DIR = '/Users/maxwell/.openclaw/workspace/penelope-v2/assets/images'
OUTPUT_FILE = '/Users/maxwell/.openclaw/workspace/penelope-v2/deck/full-deck-107.html'
# Relative path from deck/ to images/
IMG_REL = '../assets/images'

# Special slide numbers
COVER = 1
SOMMAIRE = 2
CLOSING = 107
DIVIDERS = {7, 12, 24, 37, 47, 81, 88, 93, 103}
TABLE_SLIDES = {50, 51, 52, 53}

def esc(t):
    return html_mod.escape(str(t), quote=False)

def load_all_slides():
    slides = {}
    for f in sorted(glob.glob(os.path.join(SLIDES_DIR, '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        num = d.get('number')
        if num:
            slides[num] = d
    return slides

def get_images(num):
    """Return list of image paths relative to deck/ directory."""
    import glob as gl
    files = sorted(gl.glob(os.path.join(IMAGES_DIR, f'slide{num:03d}_*')))
    # Convert to relative paths from deck/
    return [os.path.join(IMG_REL, os.path.basename(f)) for f in files]

def get_shape_text_blocks(shapes):
    """Return list of {text, runs, position, font_info, is_image} for all text shapes."""
    blocks = []
    for s in shapes:
        has_img = 'image' in s
        left = s.get('left_in', 0)
        top = s.get('top_in', 0)
        w = s.get('width_in', 0)
        h = s.get('height_in', 0)
        
        for tf in s.get('text_frame', []):
            text = tf.get('text', '').strip()
            runs = tf.get('runs', [])
            if not text and not runs:
                continue
            
            main_run = runs[0] if runs else {}
            blocks.append({
                'text': text,
                'runs': runs,
                'left': left,
                'top': top,
                'width': w,
                'height': h,
                'font_size': main_run.get('font_size_pt', 10),
                'bold': main_run.get('bold', False),
                'italic': main_run.get('italic', False),
                'color': main_run.get('color', ''),
                'font': main_run.get('font', ''),
                'is_image': has_img,
                'alignment': tf.get('alignment', ''),
            })
    return blocks

def get_table_data(shapes):
    """Extract table data from TABLE shapes."""
    for s in shapes:
        if 'TABLE' in s.get('type', '') and 'table' in s:
            return s['table'], s.get('table_cols', 0), s.get('table_rows', 0)
    return None, 0, 0

def is_dark_slide(blocks):
    """Detect dark bg by counting light vs dark text colors."""
    light = sum(1 for b in blocks if b['color'] in ['FFFFFF','E4D0CF','CBB07E','B5969C','FAF6F3','D4B87A'])
    dark = sum(1 for b in blocks if b['color'] in ['2D1A1F','6D1E31','4A3540','2A141A','8C7B7F'])
    return light > dark and light > 2

def has_kpi_values(blocks):
    """Find KPI-style big gold values."""
    return [b for b in blocks if b['font_size'] >= 24 and b['color'] in ['B0894F','B8965A','CBB07E']]

def footer(n):
    return f'<div class="footer"><span>{n} sur 107</span><span>PÉNÉLOPE × MONOPRIX · AO 2027</span></div>'

def render_runs_html(runs):
    """Render runs to HTML with formatting."""
    parts = []
    for r in runs:
        t = esc(r.get('text', ''))
        if not t:
            continue
        styles = []
        if r.get('bold'):
            styles.append('font-weight:700')
        if r.get('italic'):
            styles.append('font-style:italic')
        c = r.get('color', '')
        if c:
            if not c.startswith('#'):
                c = '#' + c
            styles.append(f'color:{c}')
        f = r.get('font', '')
        if 'Georgia' in f:
            styles.append("font-family:'Playfair Display',serif")
        fs = r.get('font_size_pt', 0)
        if fs >= 20:
            styles.append(f'font-size:{fs*0.75:.0f}pt')
        if styles:
            parts.append(f'<span style="{";".join(styles)}">{t}</span>')
        else:
            parts.append(t)
    return ''.join(parts)

# =========== SLIDE BUILDERS ===========

def build_cover(num, data, blocks, images):
    bg_img = images[0] if images else ''
    logo_img = images[3] if len(images) > 3 else (images[1] if len(images) > 1 else '')
    
    overline = blocks[0]['text'] if blocks else ''
    
    return f'''<div class="page s1">
  <div class="s1-bg">{f'<img src="{esc(bg_img)}" alt="">' if bg_img else ''}</div>
  <div class="s1-content">
    {f'<img src="{esc(logo_img)}" style="height:12mm;margin-bottom:14mm" alt="Pénélope">' if logo_img else ''}
    <div class="overline">{esc(overline)}</div>
    <div class="heading" style="font-size:42pt;color:#fff;margin-bottom:8mm">La beauté,<br><em style="color:var(--gold-lt)">autrement.</em></div>
    <div style="font-family:'Playfair Display',serif;font-size:11pt;font-style:italic;color:var(--rose);margin-bottom:12mm">Mémoire de renouvellement pour le compte Monoprix Beauté.</div>
    <div style="font-size:8.5pt;color:rgba(255,255,255,.35);margin-top:auto;padding-top:8mm;border-top:1px solid rgba(184,150,90,.15)">
      <strong style="color:rgba(255,255,255,.6)">PÉNÉLOPE</strong> · Remise via NeoGrid · 29 mai 2026
    </div>
  </div>
</div>'''

def build_sommaire(num, data, blocks, images):
    return f'''<div class="page page-light">
  <div style="padding:14mm 20mm 8mm">
    <div class="overline">PRÉAMBULE · SOMMAIRE</div>
    <div class="heading" style="font-size:24pt">Le parcours, <em>en neuf temps.</em></div>
    <div style="font-size:8.5pt;color:var(--muted);margin-bottom:6mm">Un fil unique : la conseillère comme levier de transformation, de la conviction au déploiement.</div>
    <div style="display:flex;gap:8mm;margin-bottom:6mm">
      <div><div style="font-family:'Playfair Display',serif;font-size:18pt;font-weight:700;color:var(--gold)">9</div><div style="font-size:6.5pt;color:var(--muted);text-transform:uppercase;letter-spacing:.08em">parties</div></div>
      <div><div style="font-family:'Playfair Display',serif;font-size:18pt;font-weight:700;color:var(--gold)">107</div><div style="font-size:6.5pt;color:var(--muted);text-transform:uppercase;letter-spacing:.08em">slides</div></div>
      <div><div style="font-family:'Playfair Display',serif;font-size:18pt;font-weight:700;color:var(--gold)">1</div><div style="font-size:6.5pt;color:var(--muted);text-transform:uppercase;letter-spacing:.08em">fil conducteur</div></div>
    </div>
    <div class="som-grid">
      <div class="som-item"><div class="num">I</div><h4>Notre conviction pour Monoprix 2027</h4></div>
      <div class="som-item"><div class="num">II</div><h4>Ce que Monoprix veut réussir</h4></div>
      <div class="som-item"><div class="num">III</div><h4>Pourquoi Pénélope, l'évidence</h4></div>
      <div class="som-item"><div class="num">IV</div><h4>Le conseil beauté — notre méthode signature</h4></div>
      <div class="som-item"><div class="num">V</div><h4>Le capital humain, notre différenciateur</h4></div>
      <div class="som-item"><div class="num">VI</div><h4>Le pilotage de la performance</h4></div>
      <div class="som-item"><div class="num">VII</div><h4>L'innovation au cœur de la performance</h4></div>
      <div class="som-item"><div class="num">VIII</div><h4>L'accompagnement de la transformation</h4></div>
      <div class="som-item"><div class="num">IX</div><h4>Nos engagements & le déploiement</h4></div>
    </div>
  </div>
  {footer(num)}
</div>'''

def build_divider(num, data, blocks, images):
    ft = [b['text'] for b in blocks]
    
    # Parse divider content
    num_text = ''
    part_text = ''
    title_parts = []
    desc = ''
    
    for t in ft:
        t = t.strip()
        if t in ('1 sur 107', 'PÉNÉLOPE × MONOPRIX · AO 2027'):
            continue
        if t.isdigit() or (len(t) <= 2 and t.startswith('0')):
            num_text = t
        elif 'PARTIE' in t.upper():
            part_text = t
        elif not desc and len(title_parts) < 3 and len(t) < 60:
            title_parts.append(t)
        else:
            desc = t
    
    title_html = '<br>'.join(esc(t) for t in title_parts)
    
    return f'''<div class="page page-dark">
  <div class="divider-inner">
    <div class="divider-num">{esc(num_text)}</div>
    <div class="divider-line"></div>
    <div class="overline" style="text-align:center">{esc(part_text)}</div>
    <div class="divider-title">{title_html}</div>
    <div class="divider-desc">{esc(desc)}</div>
  </div>
  {footer(num)}
</div>'''

def build_closing(num, data, blocks, images):
    ft = [b['text'] for b in blocks]
    ft = [t for t in ft if t not in ('1 sur 107', 'PÉNÉLOPE × MONOPRIX · AO 2027')]
    
    bg_img = images[0] if images else ''
    title = ft[0] if ft else 'Merci.'
    sub = ft[1] if len(ft) > 1 else ''
    tag = ft[2] if len(ft) > 2 else ''
    date = ft[3] if len(ft) > 3 else ''
    
    return f'''<div class="page page-dark" style="display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;position:relative;overflow:hidden">
  {'<div style="position:absolute;inset:0;opacity:.08"><img src="'+esc(bg_img)+'" style="width:100%;height:100%;object-fit:cover"></div>' if bg_img else ''}
  <div style="position:relative;z-index:2;padding:20mm">
    <div style="font-family:'Playfair Display',serif;font-size:48pt;font-weight:700;color:#fff;margin-bottom:10mm">{esc(title)}</div>
    <div style="font-family:'Playfair Display',serif;font-size:14pt;font-style:italic;color:var(--rose-lt);line-height:1.6;margin-bottom:12mm">{esc(sub)}</div>
    <div style="font-size:10pt;color:var(--gold);margin-bottom:8mm">{esc(tag)}</div>
    <div style="width:40mm;height:2px;background:linear-gradient(90deg,transparent,var(--gold),transparent);margin:0 auto 10mm"></div>
    <div style="font-size:8.5pt;color:rgba(255,255,255,.4)">{esc(date)}</div>
  </div>
  {footer(num)}
</div>'''

def build_table_slide(num, data, blocks, images):
    table_data, cols, rows = get_table_data(data.get('shapes', []))
    
    ft = [b['text'] for b in blocks if b['text'] not in ('1 sur 107', 'PÉNÉLOPE × MONOPRIX · AO 2027')]
    overline = ft[0] if ft else ''
    intro = ft[1] if len(ft) > 1 else ''
    
    if not table_data:
        # Fallback to content
        return build_generic_content(num, data, blocks, images)
    
    tbl = '<table class="data-table">'
    for i, row in enumerate(table_data):
        tbl += '<tr>'
        for j, cell in enumerate(row):
            ct = esc(str(cell)) if cell else ''
            if i == 0:
                tbl += f'<th>{ct}</th>'
            else:
                # Bold the dimension column
                if j == 0:
                    tbl += f'<td><strong>{ct}</strong></td>'
                else:
                    tbl += f'<td>{ct}</td>'
        tbl += '</tr>'
    tbl += '</table>'
    
    return f'''<div class="page page-light">
  <div style="padding:14mm 20mm 8mm">
    <div class="overline">{esc(overline)}</div>
    <div style="font-size:8.5pt;color:var(--muted);margin-bottom:4mm">{esc(intro)}</div>
    {tbl}
  </div>
  {footer(num)}
</div>'''

def build_quote_slide(num, data, blocks, images):
    ft = [b['text'] for b in blocks]
    ft = [t for t in ft if t not in ('1 sur 107', 'PÉNÉLOPE × MONOPRIX · AO 2027')]
    
    overline = ft[0] if ft else ''
    quote_lines = [t for t in ft[1:] if t and 'sur 107' not in t and 'PÉNÉLOPE' not in t]
    
    quote_html = '<br>'.join(esc(l) for l in quote_lines)
    
    return f'''<div class="page page-deep">
  <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;height:100%;padding:20mm 30mm">
    <div style="font-size:60pt;color:rgba(184,150,90,.12);font-family:'Playfair Display',serif;line-height:1;margin-bottom:8mm">«</div>
    <div style="font-family:'Playfair Display',serif;font-size:22pt;font-style:italic;color:var(--rose-lt);line-height:1.4;margin-bottom:10mm">
      {quote_html}
    </div>
    <div style="width:40mm;height:2px;background:linear-gradient(90deg,transparent,var(--gold),transparent)"></div>
  </div>
  {footer(num)}
</div>'''

def build_generic_content(num, data, blocks, images):
    """Build a generic content slide, adapting layout based on content analysis."""
    shapes = data.get('shapes', [])
    is_dark = is_dark_slide(blocks)
    kpis = has_kpi_values(blocks)
    
    # Filter out footer blocks
    content_blocks = [b for b in blocks if b['text'] not in ('1 sur 107', 'PÉNÉLOPE × MONOPRIX · AO 2027')
                      and ' sur 107' not in b['text'][:8]
                      and b['text'] != 'PÉNÉLOPE × MONOPRIX · AO 2027']
    
    if not content_blocks:
        # Empty slide fallback
        return f'''<div class="page {"page-dark" if is_dark else "page-light"}">
  <div style="padding:14mm 20mm 8mm;display:flex;flex-direction:column;height:100%">
    <div class="body-text">Slide {num}</div>
  </div>
  {footer(num)}
</div>'''
    
    # Identify overline (first small bold uppercase text)
    overline = ''
    overline_idx = -1
    for i, b in enumerate(content_blocks):
        if b['font_size'] <= 12 and b['bold'] and b['text'].isupper():
            overline = b['text']
            overline_idx = i
            break
        elif '·' in b['text'] and b['font_size'] <= 12:
            overline = b['text']
            overline_idx = i
            break
    
    # Identify heading (large font, bold)
    heading_blocks = []
    heading_end = overline_idx + 1
    for i in range(overline_idx + 1, len(content_blocks)):
        b = content_blocks[i]
        if b['font_size'] >= 20 or (b['bold'] and b['font_size'] >= 16):
            heading_blocks.append(b)
            heading_end = i + 1
        elif heading_blocks:
            break
        elif i == overline_idx + 1:
            # First block after overline is likely heading
            heading_blocks.append(b)
            heading_end = i + 1
            if b['font_size'] >= 18:
                continue
            else:
                break
    
    if not heading_blocks:
        heading_blocks = [content_blocks[0]] if content_blocks else []
        heading_end = 1
    
    # Build heading HTML
    heading_parts = []
    for hb in heading_blocks:
        runs_html = render_runs_html(hb['runs'])
        if hb.get('italic') or any(r.get('italic') for r in hb['runs']):
            heading_parts.append(f'<em>{runs_html}</em>')
        else:
            heading_parts.append(runs_html)
    heading_html = '<br>'.join(heading_parts)
    
    # Remaining content
    remaining = content_blocks[heading_end:]
    
    # Separate into categories
    # Subtitle (short text, muted)
    subtitle = ''
    subtitle_idx = -1
    for i, b in enumerate(remaining):
        if b['font_size'] <= 12 and len(b['text']) < 120 and not b['bold']:
            subtitle = b['text']
            subtitle_idx = i
            break
    
    # KPI pairs (big number + label below)
    if kpis and len(kpis) >= 2:
        return build_kpi_layout(num, overline, heading_html, kpis, remaining, is_dark)
    
    # Body text (regular text blocks)
    body_texts = []
    quote_text = ''
    stat_pairs = []
    signature = ''
    
    for i, b in enumerate(remaining):
        if i == subtitle_idx:
            continue
        t = b['text']
        if not t:
            continue
        
        # Quote detection (large italic)
        if b.get('italic') and b['font_size'] >= 18 and len(t) > 20:
            quote_text = t
            continue
        
        # Stat value (big gold)
        if b['font_size'] >= 24 and b['color'] in ['B0894F','B8965A','CBB07E']:
            # Find label below
            label = ''
            for b2 in remaining:
                if b2['top'] > b['top'] and abs(b2['left'] - b['left']) < 2 and b2['top'] - b['top'] < 1.5:
                    label = b2['text']
                    break
            stat_pairs.append({'val': t, 'label': label})
            continue
        
        # Stat label (muted, below a KPI)
        if b['color'] in ['8C7B7F','AA999D'] and b['font_size'] <= 12:
            is_kpi_label = False
            for sp in stat_pairs:
                if sp['label'] == t:
                    is_kpi_label = True
                    break
            if is_kpi_label:
                continue
        
        # Signature (name/role at bottom)
        if b['top'] > 5.5 and ('Pénélope' in t or 'Directrice' in t or 'Directeur' in t or '—' in t):
            signature += esc(t) + '<br>'
            continue
        
        # Regular body text
        if b['font_size'] >= 10 and len(t) > 15:
            body_texts.append(t)
    
    # Check for images
    has_split_img = False
    main_img_src = None
    for s in shapes:
        if 'image' in s:
            w = s.get('width_in', 0)
            h = s.get('height_in', 0)
            # Large image = potential split/background
            if w > 3 and h > 3:
                has_split_img = True
                # Find matching image file by shape index
                idx = shapes.index(s)
                for img_path in images:
                    basename = os.path.basename(img_path)
                    # Match slideXXX_imgYY where YY == shape index
                    img_idx = basename.split('_img')[-1].split('.')[0]
                    try:
                        if int(img_idx) == idx:
                            main_img_src = img_path
                            break
                    except ValueError:
                        # Handle grpXX_img format
                        pass
                if not main_img_src and images:
                    main_img_src = images[0]
                break
    if not has_split_img and images:
        # Smaller images (logos, icons) - still include them
        for s in shapes:
            if 'image' in s:
                has_split_img = True
                main_img_src = images[0]
                break
    
    # Determine layout
    page_class = 'page-dark' if is_dark else 'page-light'
    text_color = '#fff' if is_dark else 'var(--dark)'
    body_color = 'rgba(255,255,255,.5)' if is_dark else 'var(--body)'
    
    # Dark centered layout
    if is_dark and not stat_pairs and not has_split_img:
        body_html = '<br>'.join(esc(t) for t in body_texts[:3])
        return f'''<div class="page {page_class}">
  <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;height:100%;padding:16mm 20mm">
    <div class="overline">{esc(overline)}</div>
    <div class="heading" style="font-size:26pt;color:#fff;margin-bottom:10mm">{heading_html}</div>
    <div style="font-size:10pt;color:rgba(255,255,255,.5);line-height:1.7;max-width:70%">{body_html}</div>
  </div>
  {footer(num)}
</div>'''
    
    # Split layout with image
    if has_split_img and main_img_src and not is_dark:
        img_src = main_img_src
        # Check image position - is it on right or left?
        img_on_right = False
        for s in shapes:
            if 'image' in s and s.get('left_in', 0) > 6:
                img_on_right = True
                break
        
        body_html = '<br>'.join(esc(t) for t in body_texts[:2])
        quote_html = f'<div class="quote"><p>{esc(quote_text)}</p></div>' if quote_text else ''
        stats_html = ''
        if stat_pairs:
            stats_html = '<div class="stat-row">' + ''.join(
                f'<div class="stat-item"><div class="val">{esc(sp["val"])}</div><div class="lbl">{esc(sp["label"])}</div></div>'
                for sp in stat_pairs
            ) + '</div>'
        sig_html = f'<div style="font-size:8pt;color:var(--muted);padding-top:3mm;border-top:1px solid rgba(122,38,57,.06)">{signature}</div>' if signature else ''
        
        if img_on_right:
            return f'''<div class="page split">
  <div class="split-body" style="background:var(--cream);flex:1">
    <div>
      <div class="overline">{esc(overline)}</div>
      <div class="heading" style="font-size:22pt">{heading_html}</div>
    </div>
    <div class="body-text">{body_html}</div>
    {quote_html}
    {stats_html}
    {sig_html}
  </div>
  <div class="split-img"><img src="{esc(img_src)}" alt=""></div>
  {footer(num)}
</div>'''
        
        return f'''<div class="page split">
  <div class="split-img"><img src="{esc(img_src)}" alt=""></div>
  <div class="split-body" style="background:var(--cream)">
    <div>
      <div class="overline">{esc(overline)}</div>
      <div class="heading" style="font-size:22pt">{heading_html}</div>
    </div>
    <div class="body-text">{body_html}</div>
    {quote_html}
    {stats_html}
    {sig_html}
  </div>
  {footer(num)}
</div>'''
    
    # Card layout (many content blocks with similar structure)
    # Detect card-like patterns: bold titles + descriptions
    card_items = []
    for i, b in enumerate(remaining):
        if b['bold'] and b['font_size'] >= 9 and b['font_size'] <= 16 and len(b['text']) < 80:
            # Find description below or after
            desc = ''
            for b2 in remaining:
                if b2['top'] > b['top'] and abs(b2['left'] - b['left']) < 3 and b2 != b and len(b2['text']) > 20:
                    desc = b2['text']
                    break
                elif b2['top'] == b['top'] and abs(b2['left'] - b['left']) < 3 and not b2['bold'] and len(b2['text']) > 20:
                    desc = b2['text']
                    break
            card_items.append({'title': b['text'], 'desc': desc})
    
    if len(card_items) >= 4:
        n = len(card_items)
        grid = 'card-grid-2' if n <= 6 else 'card-grid-3'
        cards_html = ''.join(
            f'<div class="card"><h3>{esc(c["title"])}</h3><p>{esc(c["desc"])}</p></div>'
            for c in card_items
        )
        
        return f'''<div class="page page-light">
  <div style="padding:14mm 20mm 8mm">
    <div class="overline">{esc(overline)}</div>
    <div class="heading" style="font-size:22pt">{heading_html}</div>
    <div class="card-grid {grid}" style="margin-top:5mm">
      {cards_html}
    </div>
  </div>
  {footer(num)}
</div>'''
    
    # Pillar layout (numbered columns)
    pillar_items = []
    for i, b in enumerate(remaining):
        if b['font_size'] >= 14 and b['color'] in ['B0894F','B8965A','CBB07E'] and (b['text'].isdigit() or (len(b['text']) <= 2)):
            # Find title and description
            title = ''
            desc = ''
            for b2 in remaining:
                if b2['top'] > b['top'] and abs(b2['left'] - b['left']) < 3 and b2['bold'] and b2 != b:
                    title = b2['text']
                elif b2['top'] > b['top'] and abs(b2['left'] - b['left']) < 3 and not b2['bold'] and len(b2['text']) > 15:
                    desc = b2['text']
            if title:
                pillar_items.append({'num': b['text'], 'title': title, 'desc': desc})
    
    if len(pillar_items) >= 3:
        pillars_html = ''.join(
            f'<div class="pillar"><div class="num">{esc(p["num"])}</div><h4>{esc(p["title"])}</h4><p>{esc(p["desc"])}</p></div>'
            for p in pillar_items
        )
        
        return f'''<div class="page page-light">
  <div style="padding:14mm 20mm 8mm">
    <div class="overline">{esc(overline)}</div>
    <div class="heading" style="font-size:20pt">{heading_html}</div>
    <div style="font-size:8.5pt;color:var(--muted);margin-bottom:5mm">{esc(subtitle)}</div>
    <div class="pillar-grid">
      {pillars_html}
    </div>
  </div>
  {footer(num)}
</div>'''
    
    # Default: simple text layout with optional image
    body_html = ''
    for t in body_texts:
        body_html += f'<p style="margin-bottom:3mm">{esc(t)}</p>'
    
    stats_html = ''
    if stat_pairs:
        stats_html = '<div class="stat-row">' + ''.join(
            f'<div class="stat-item"><div class="val">{esc(sp["val"])}</div><div class="lbl">{esc(sp["label"])}</div></div>'
            for sp in stat_pairs
        ) + '</div>'
    
    img_html = ''
    if images and not has_split_img:
        img_src = images[0]
        img_html = f'<img src="{esc(img_src)}" style="max-width:100%;max-height:35mm;border-radius:8px;margin-top:4mm" alt="">'
    
    return f'''<div class="page {page_class}">
  <div style="padding:14mm 20mm 8mm">
    <div class="overline">{esc(overline)}</div>
    <div class="heading" style="font-size:22pt">{heading_html}</div>
    {f'<div style="font-size:8.5pt;color:var(--muted);margin-bottom:4mm">{esc(subtitle)}</div>' if subtitle else ''}
    <div class="body-text" style="margin-top:4mm">
      {body_html}
    </div>
    {stats_html}
    {img_html}
  </div>
  {footer(num)}
</div>'''

def build_kpi_layout(num, overline, heading_html, kpis, remaining, is_dark):
    """KPI-focused layout."""
    page_class = 'page-dark' if is_dark else 'page-light'
    
    # Build KPI boxes with descriptions
    kpi_html = ''
    for kp in kpis:
        val = kp['text']
        # Find label below
        label = ''
        desc = ''
        for b in remaining:
            if b['top'] > kp['top'] and abs(b['left'] - kp['left']) < 2:
                if b['color'] in ['8C7B7F','AA999D'] and not label:
                    label = b['text']
                elif len(b['text']) > 20 and not desc:
                    desc = b['text']
        
        # KPI label from shape above
        kpi_label = ''
        for b in remaining:
            if b['top'] < kp['top'] and abs(b['left'] - kp['left']) < 2 and b['font_size'] <= 10:
                kpi_label = b['text']
                break
        
        kpi_html += f'''<div class="kpi-box" style="flex:1">
      {'<div class="kpi-label">'+esc(kpi_label)+'</div>' if kpi_label else ''}
      <div class="kpi-val">{esc(val)}</div>
      <div class="kpi-desc">{esc(desc if desc else label)}</div>
    </div>'''
    
    # Footnote
    footnote = ''
    for b in remaining:
        if b['font_size'] <= 8 and b.get('italic') and len(b['text']) > 30:
            footnote = b['text']
            break
    
    return f'''<div class="page {page_class}">
  <div style="padding:14mm 20mm 8mm;display:flex;flex-direction:column;height:100%">
    <div style="text-align:center;margin-bottom:8mm">
      <div class="overline">{esc(overline)}</div>
      <div class="heading" style="font-size:22pt;color:#fff">{heading_html}</div>
    </div>
    <div class="kpi-grid" style="flex:1;display:flex;align-items:center">
      {kpi_html}
    </div>
    {'<div style="text-align:center;font-size:7.5pt;color:rgba(255,255,255,.3);font-style:italic">'+esc(footnote)+'</div>' if footnote else ''}
  </div>
  {footer(num)}
</div>'''


def classify_and_build(num, data):
    """Main routing function."""
    shapes = data.get('shapes', [])
    blocks = get_shape_text_blocks(shapes)
    images = get_images(num)
    
    if num == COVER:
        return build_cover(num, data, blocks, images)
    if num == SOMMAIRE:
        return build_sommaire(num, data, blocks, images)
    if num == CLOSING:
        return build_closing(num, data, blocks, images)
    if num in DIVIDERS:
        return build_divider(num, data, blocks, images)
    
    # Check for tables
    for s in shapes:
        if 'TABLE' in s.get('type', ''):
            return build_table_slide(num, data, blocks, images)
    
    # Check for quote (few shapes, has « or »)
    ft = data.get('full_text', [])
    ft_joined = ' '.join(ft)
    is_dark = is_dark_slide(blocks)
    kpis = has_kpi_values(blocks)
    
    if len(shapes) <= 6 and ('«' in ft_joined or '»' in ft_joined) and not kpis:
        return build_quote_slide(num, data, blocks, images)
    
    # Everything else: generic content handler
    return build_generic_content(num, data, blocks, images)


CSS = '''<style>
:root{--b:#7A2639;--b-dk:#3D1220;--b-lt:#9E4A5A;--gold:#B8965A;--gold-lt:#D4B87A;--rose:#C9A8A0;--rose-lt:#E3CEC8;--cream:#FAF6F3;--dark:#2D1A1F;--body:#4A3540;--muted:#8A7580}
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:'Inter',sans-serif;background:#1a1a1a}
.page{width:297mm;height:210mm;position:relative;overflow:hidden;page-break-after:always;break-after:page;margin:12px auto;box-shadow:0 20px 60px rgba(0,0,0,.3)}
@media print{.page{margin:0;box-shadow:none}}
.page-light{background:var(--cream);color:var(--dark)}
.page-dark{background:var(--b);color:#fff}
.page-deep{background:var(--b-dk);color:#fff}
.overline{font-size:7.5pt;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);margin-bottom:3mm}
.heading{font-family:'Playfair Display',serif;line-height:1.15;color:var(--dark);margin-bottom:3mm}
.heading em{font-style:italic;color:var(--b)}
.page-dark .heading{color:#fff}
.page-dark .heading em{color:var(--rose-lt)}
.body-text{font-size:9.5pt;color:var(--body);line-height:1.65}
.body-text strong{color:var(--b)}
.footer{position:absolute;bottom:5mm;left:18mm;right:18mm;display:flex;justify-content:space-between;font-size:6.5pt;letter-spacing:.1em;text-transform:uppercase;color:rgba(138,117,128,.5)}
.page-dark .footer{color:rgba(255,255,255,.15)}
.page-deep .footer{color:rgba(255,255,255,.15)}
.s1{display:flex;background:linear-gradient(160deg,rgba(61,18,32,.96),rgba(122,38,57,.82),rgba(61,18,32,.92))}
.s1-bg{position:absolute;right:0;top:0;width:38%;height:100%}
.s1-bg img{width:100%;height:100%;object-fit:cover;opacity:.35}
.s1-bg::after{content:'';position:absolute;left:0;top:0;width:8mm;height:100%;background:linear-gradient(90deg,var(--b),transparent)}
.s1-content{position:relative;z-index:2;display:flex;flex-direction:column;justify-content:center;padding:20mm 12mm 16mm 22mm;flex:1}
.split{display:flex;height:100%}
.split-img{flex:0 0 42%;position:relative;overflow:hidden}
.split-img img{width:100%;height:100%;object-fit:cover}
.split-img::after{content:'';position:absolute;right:0;top:0;width:3mm;height:100%;background:linear-gradient(90deg,transparent,var(--cream))}
.split-body{flex:1;padding:14mm 16mm 14mm 14mm;display:flex;flex-direction:column;justify-content:space-between}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:5mm}
.kpi-box{text-align:center;padding:6mm 4mm;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);border-radius:8px}
.kpi-label{font-size:6pt;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--gold);margin-bottom:3mm}
.kpi-val{font-family:'Playfair Display',serif;font-size:28pt;font-weight:700;color:#fff;line-height:1}
.kpi-desc{font-size:7.5pt;color:rgba(255,255,255,.4);margin-top:2mm;line-height:1.5}
.card-grid{display:grid;gap:5mm}
.card-grid-2{grid-template-columns:1fr 1fr}
.card-grid-3{grid-template-columns:repeat(3,1fr)}
.card{background:#fff;border-radius:10px;padding:5mm 6mm;border:1px solid rgba(122,38,57,.05);border-top:2.5px solid var(--gold)}
.card h3{font-family:'Playfair Display',serif;font-size:10pt;font-weight:700;color:var(--dark);margin-bottom:2mm}
.card p{font-size:8pt;color:var(--body);line-height:1.5}
.pillar-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:5mm}
.pillar{background:#fff;border-radius:10px;padding:6mm;border:1px solid rgba(122,38,57,.04);border-left:3px solid var(--gold)}
.pillar .num{font-family:'Playfair Display',serif;font-size:16pt;font-weight:700;color:var(--gold);font-style:italic;margin-bottom:2mm}
.pillar h4{font-family:'Playfair Display',serif;font-size:10pt;font-weight:700;color:var(--dark);margin-bottom:2mm}
.pillar p{font-size:8pt;color:var(--body);line-height:1.5}
.quote{position:relative;padding:4mm 4mm 4mm 8mm;border-left:2px solid var(--gold);background:rgba(184,150,90,.03);border-radius:0 6px 6px 0}
.quote p{font-family:'Playfair Display',serif;font-size:12pt;font-style:italic;color:var(--b);line-height:1.45}
.page-dark .quote{background:rgba(255,255,255,.03);border-left-color:var(--gold)}
.page-dark .quote p{color:var(--rose-lt)}
.divider-inner{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;height:100%;padding:16mm;position:relative}
.divider-num{font-family:'Playfair Display',serif;font-size:100pt;font-weight:700;color:rgba(255,255,255,.04);position:absolute;top:8mm;left:16mm;line-height:1;pointer-events:none}
.divider-line{width:40mm;height:2px;background:linear-gradient(90deg,var(--gold),transparent);margin-bottom:5mm}
.divider-title{font-family:'Playfair Display',serif;font-size:28pt;font-weight:700;font-style:italic;color:#fff;line-height:1.2;margin-bottom:6mm}
.divider-desc{font-size:10pt;color:var(--rose);line-height:1.6;max-width:60%}
.promise{display:flex;gap:3mm;align-items:baseline;padding:3mm 0;border-bottom:1px solid rgba(122,38,57,.05)}
.promise:last-child{border-bottom:none}
.promise .dot{width:5px;height:5px;border-radius:50%;background:var(--gold);flex-shrink:0;margin-top:3px}
.promise h4{font-family:'Playfair Display',serif;font-size:9.5pt;font-weight:700;color:var(--b);margin-bottom:1mm}
.promise p{font-size:8pt;color:var(--body);line-height:1.5}
.stat-row{display:flex;gap:6mm;margin-bottom:4mm}
.stat-item{text-align:left}
.stat-item .val{font-family:'Playfair Display',serif;font-size:18pt;font-weight:700;color:var(--gold)}
.stat-item .lbl{font-size:6.5pt;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-top:1mm}
.som-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.som-item{display:flex;gap:3mm;align-items:center;padding:3mm 4mm;border-radius:6px;background:#fff;border:1px solid rgba(122,38,57,.04)}
.som-item .num{font-family:'Playfair Display',serif;font-size:12pt;font-weight:700;color:var(--gold);font-style:italic;flex-shrink:0}
.som-item h4{font-family:'Playfair Display',serif;font-size:8.5pt;font-weight:700;color:var(--dark);line-height:1.3}
.data-table{width:100%;border-collapse:collapse;font-size:8pt;margin-top:4mm}
.data-table th{background:var(--b);color:#fff;font-family:'Playfair Display',serif;font-weight:600;padding:3mm 4mm;text-align:left;font-size:8.5pt;border:1px solid rgba(122,38,57,.1)}
.data-table td{padding:3mm 4mm;border:1px solid rgba(122,38,57,.08);color:var(--body);line-height:1.5;vertical-align:top}
.data-table tr:nth-child(even){background:rgba(122,38,57,.02)}
.data-table td strong{color:var(--b);font-weight:600}
</style>'''


def main():
    slides = load_all_slides()
    print(f"Loaded {len(slides)} slides")
    
    parts = [f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>PÉNÉLOPE × MONOPRIX · AO 2027</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,800;0,900;1,400;1,600;1,700&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
{CSS}
</head>
<body>
''']
    
    for num in sorted(slides.keys()):
        data = slides[num]
        ft = data.get('full_text', [''])
        print(f"  {num:3d} | {ft[0][:60]}")
        slide_html = classify_and_build(num, data)
        parts.append(slide_html)
    
    parts.append('''<script>
// Keyboard navigation
const pages = document.querySelectorAll('.page');
let current = 0;
function showSlide(n) {
  if (n < 0 || n >= pages.length) return;
  current = n;
  pages[current].scrollIntoView({behavior:'smooth',block:'start'});
}
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
    e.preventDefault(); showSlide(current + 1);
  } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    e.preventDefault(); showSlide(current - 1);
  } else if (e.key === 'Home') {
    e.preventDefault(); showSlide(0);
  } else if (e.key === 'End') {
    e.preventDefault(); showSlide(pages.length - 1);
  }
});
</script>
</body>\n</html>''')
    
    full = '\n\n'.join(parts)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full)
    
    size = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"\n✅ Generated {OUTPUT_FILE} ({size:.0f} KB, {len(slides)} slides)")


if __name__ == '__main__':
    main()
