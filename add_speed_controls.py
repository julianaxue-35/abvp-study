#!/usr/bin/env python3
"""Add 1x/1.25x/1.5x/2x playback-speed buttons under each podcast <audio>.
Idempotent: skips a file that already has the controls."""
import os

REPO = os.path.expanduser('~/abvp-study')

FILES = [
    'physical-health/euthanasia_hub.html',
    'physical-health/facility_shelter_design_hub.html',
    'physical-health/sanitation_biosecurity_hub.html',
    'companion-animal-homelessness/adoption_placement_hub.html',
    'shelter-management/01_population_management.html',
    'supplementary/additional_podcasts.html',
    'physical-health/parasites_hub.html',
    'physical-health/medical_health_hub.html',
    'physical-health/nutrition_husbandry_hub.html',
]

MARKER = 'data-speed-controls'

BTN = ('font:inherit;font-size:12px;padding:3px 10px;border:1px solid #b9cdc6;'
       'border-radius:6px;cursor:pointer;background:#fff;color:#0f3d3a')
BTN_ON = ('font:inherit;font-size:12px;padding:3px 10px;border:1px solid #b9cdc6;'
          'border-radius:6px;cursor:pointer;background:#0f3d3a;color:#fff')


def button(rate, label, active=False):
    style = BTN_ON if active else BTN
    return (f'<button type="button" onclick="setRate(this,{rate})" '
            f'style="{style}">{label}</button>')


SPEED_ROW = (
    f'\n    <div {MARKER} style="margin-top:10px;display:flex;gap:6px;'
    'align-items:center;flex-wrap:wrap">\n'
    '      <span style="font-size:12px;color:#5d6b62;margin-right:2px">Speed</span>\n'
    '      ' + button(1, '1×', active=True) + '\n'
    '      ' + button(1.25, '1.25×') + '\n'
    '      ' + button(1.5, '1.5×') + '\n'
    '      ' + button(2, '2×') + '\n'
    '    </div>'
)

SCRIPT = (
    '\n<script data-speed-js>\n'
    'function setRate(btn,r){\n'
    '  var row=btn.parentNode, card=row.parentNode;\n'
    '  var a=card.querySelector("audio"); if(a){a.playbackRate=r;}\n'
    '  var b=row.querySelectorAll("button");\n'
    '  for(var i=0;i<b.length;i++){b[i].style.background="#fff";b[i].style.color="#0f3d3a";}\n'
    '  btn.style.background="#0f3d3a"; btn.style.color="#fff";\n'
    '}\n'
    '</script>\n'
)

for rel in FILES:
    path = os.path.join(REPO, rel)
    with open(path, encoding='utf-8') as f:
        html = f.read()

    if MARKER in html:
        print(f'  SKIP (already has controls)  {rel}')
        continue
    if '</audio>' not in html:
        print(f'  WARN no <audio> in  {rel}')
        continue

    html = html.replace('</audio>', '</audio>' + SPEED_ROW)
    # add the helper script once, just before </body>
    if 'data-speed-js' not in html:
        html = html.replace('</body>', SCRIPT + '</body>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    n = html.count(MARKER)
    print(f'  OK ({n} player{"s" if n != 1 else ""})  {rel}')

print('done')
