#!/usr/bin/env python3
"""Inject podcast audio cards into each infectious disease tab."""
import os

REPO = os.path.expanduser('~/abvp-study')
FILE = os.path.join(REPO, 'physical-health', 'infectious_disease_hub.html')

# panel_id -> (filename, display_title)
# FIP gets special double-card treatment
SINGLE = {
    'cpv':     ('Clinical_Management_of_Mutating_Canine_Parvovirus.m4a',
                'Clinical Management of Mutating Canine Parvovirus'),
    'cdv':     ('Canine_Distemper_Virus_Shelter_Medicine_Mastery.m4a',
                'Canine Distemper Virus — Shelter Medicine Mastery'),
    'cird':    ('Stopping_Lethal_CIRD_Outbreaks_in_Shelters.m4a',
                'Stopping Lethal CIRD Outbreaks in Shelters'),
    'civ':     ('Controlling_H3N2_Canine_Influenza_in_Shelters.m4a',
                'Controlling H3N2 Canine Influenza in Shelters'),
    'rw':      ('Stopping_shelter_ringworm_with_toothbrushes_and_data.m4a',
                'Stopping Shelter Ringworm with Toothbrushes and Data'),
    'fivfelv': ('FeLV_and_FIV_Shelter_Management_Protocols.m4a',
                'FeLV and FIV — Shelter Management Protocols'),
    'furi':    ('Physics_and_Psychology_of_Shelter_FURI.m4a',
                'Physics and Psychology of Shelter FURI'),
}

FIP_EPISODES = [
    ('Feline_Infectious_Peritonitis_Pathogenesis_and_Management.m4a',
     'Pathogenesis and Management'),
    ('Feline_Infectious_Peritonitis_From_Mutation_To_Cure.m4a',
     'From Mutation to Cure'),
]


def single_card(filename, title):
    return (
        '\n  <div class="card" style="border-left:4px solid var(--id);background:var(--id-soft)">\n'
        '    <h4 style="margin-top:0;display:flex;align-items:center;gap:8px;color:var(--id)">'
        '&#127911;&nbsp;NotebookLM Podcast</h4>\n'
        f'    <p class="note" style="color:var(--muted);margin-bottom:8px">{title}</p>\n'
        f'    <audio controls style="width:100%;border-radius:6px">\n'
        f'      <source src="audio/{filename}" type="audio/mp4">\n'
        '    </audio>\n'
        '  </div>'
    )


def double_card(episodes):
    inner = ''
    for i, (filename, title) in enumerate(episodes):
        mb = '' if i == 0 else ''
        inner += (
            f'    <p class="note" style="color:var(--muted);margin-bottom:6px">'
            f'Episode {i+1} — {title}</p>\n'
            f'    <audio controls style="width:100%;border-radius:6px;'
            f'{"margin-bottom:14px" if i < len(episodes)-1 else ""}">\n'
            f'      <source src="audio/{filename}" type="audio/mp4">\n'
            f'    </audio>\n'
        )
    return (
        '\n  <div class="card" style="border-left:4px solid var(--id);background:var(--id-soft)">\n'
        '    <h4 style="margin-top:0;display:flex;align-items:center;gap:8px;color:var(--id)">'
        '&#127911;&nbsp;NotebookLM Podcasts</h4>\n'
        + inner +
        '  </div>'
    )


def inject_after_lead(html, panel_id, card_html):
    panel_pos = html.find(f'id="{panel_id}"')
    if panel_pos == -1:
        print(f'  WARN: panel id="{panel_id}" not found')
        return html
    lead_start = html.find('<p class="lead">', panel_pos)
    if lead_start == -1:
        print(f'  WARN: no lead paragraph in panel "{panel_id}"')
        return html
    lead_end = html.find('</p>', lead_start) + len('</p>')
    return html[:lead_end] + card_html + html[lead_end:]


with open(FILE, encoding='utf-8') as f:
    html = f.read()

if 'NotebookLM Podcast' in html:
    print('Already injected — exiting.')
else:
    # Inject single-episode cards
    for panel_id, (filename, title) in SINGLE.items():
        card = single_card(filename, title)
        html = inject_after_lead(html, panel_id, card)
        print(f'  OK   {panel_id}')

    # Inject double-episode card for FIP
    card = double_card(FIP_EPISODES)
    html = inject_after_lead(html, 'fip', card)
    print('  OK   fip (2 episodes)')

    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print('\nDone.')
