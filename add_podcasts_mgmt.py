#!/usr/bin/env python3
"""Inject NotebookLM podcast card + speed controls + floating player into
shelter-management subdomain pages that have no audio yet. Idempotent."""
import os

REPO = os.path.expanduser('~/abvp-study')

# relative path -> (audio filename, display title)
TARGETS = {
    'shelter-management/03_management_leadership.html':
        ('management_leadership.m4a', 'Management and Leadership'),
    'shelter-management/04_record_keeping.html':
        ('record_keeping.m4a', 'Record Keeping'),
    'shelter-management/06_mental_health.html':
        ('mental_health.m4a', 'Mental Health and Compassion Fatigue'),
    'shelter-management/07_regulatory.html':
        ('regulatory.m4a', 'Regulatory'),
    'shelter-management/08_liability.html':
        ('liability.m4a', 'Liability'),
    'shelter-management/09_resource_allocation.html':
        ('resource_allocation.m4a', 'Resource Allocation'),
}

CARD_MARKER = 'data-podcast-card'

BTN = ('font:inherit;font-size:12px;padding:3px 10px;border:1px solid #b9cdc6;'
       'border-radius:6px;cursor:pointer;background:#fff;color:#0f3d3a')
BTN_ON = ('font:inherit;font-size:12px;padding:3px 10px;border:1px solid #b9cdc6;'
          'border-radius:6px;cursor:pointer;background:#0f3d3a;color:#fff')


def card(filename, title):
    return (
        f'\n  <div class="card" {CARD_MARKER} style="border-left:4px solid #0f3d3a;'
        'background:#eef3f1;border-radius:8px;padding:14px 16px;margin:16px 0">\n'
        '    <h4 style="margin:0 0 6px;display:flex;align-items:center;gap:8px;'
        'color:#0f3d3a">\U0001F3A7 NotebookLM Podcast</h4>\n'
        f'    <p style="color:#5d6b62;margin:0 0 8px;font-size:14px">{title}</p>\n'
        '    <audio controls preload="metadata" style="width:100%">\n'
        f'      <source src="audio/{filename}" type="audio/mp4">\n'
        '    </audio>\n'
        '    <div data-speed-controls style="margin-top:10px;display:flex;gap:6px;'
        'align-items:center;flex-wrap:wrap">\n'
        '      <span style="font-size:12px;color:#5d6b62;margin-right:2px">Speed</span>\n'
        f'      <button type="button" onclick="setRate(this,1)" style="{BTN_ON}">1×</button>\n'
        f'      <button type="button" onclick="setRate(this,1.25)" style="{BTN}">1.25×</button>\n'
        f'      <button type="button" onclick="setRate(this,1.5)" style="{BTN}">1.5×</button>\n'
        f'      <button type="button" onclick="setRate(this,2)" style="{BTN}">2×</button>\n'
        '    </div>\n'
        '  </div>'
    )


SPEED_JS = (
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

FLOAT_JS = (
    '<script data-floating-player>\n'
    '/* Floating play/stop control — follows scroll on the left edge so you can\n'
    '   pause/resume the podcast while reading the notes. Controls whichever\n'
    '   episode is currently active and shows its title. */\n'
    '(function(){\n'
    "  var audios = Array.prototype.slice.call(document.querySelectorAll('audio'));\n"
    '  if(!audios.length) return;\n'
    '  var active = null;\n'
    '\n'
    '  var PLAY = \'<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>\';\n'
    '  var PAUSE = \'<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>\';\n'
    '\n'
    "  var wrap = document.createElement('div');\n"
    "  wrap.id = 'floatPlayer';\n"
    "  wrap.style.cssText = 'position:fixed;left:0;top:50%;transform:translateY(-50%);z-index:99999;display:none;align-items:center;font-family:inherit';\n"
    '\n'
    "  var btn = document.createElement('button');\n"
    "  btn.type = 'button';\n"
    "  btn.setAttribute('aria-label','Play or pause podcast');\n"
    "  btn.style.cssText = 'width:52px;height:52px;border-radius:0 26px 26px 0;border:none;background:#0f3d3a;color:#fff;cursor:pointer;box-shadow:2px 2px 12px rgba(0,0,0,.28);display:flex;align-items:center;justify-content:center;flex:0 0 auto;padding:0';\n"
    '  btn.innerHTML = PLAY;\n'
    '\n'
    "  var label = document.createElement('div');\n"
    "  label.style.cssText = 'max-width:0;overflow:hidden;white-space:nowrap;background:#0f3d3a;color:#fff;font-size:12px;line-height:1.3;border-radius:0 8px 8px 0;transition:max-width .3s ease,padding .3s ease;padding:0;box-shadow:2px 2px 12px rgba(0,0,0,.28);margin-left:-1px';\n"
    '\n'
    '  wrap.appendChild(btn);\n'
    '  wrap.appendChild(label);\n'
    '  document.body.appendChild(wrap);\n'
    '\n'
    '  var hideT;\n'
    "  function showLabel(){ clearTimeout(hideT); label.style.maxWidth='230px'; label.style.padding='8px 14px 8px 10px'; }\n"
    "  function hideLabel(){ label.style.maxWidth='0'; label.style.padding='0'; }\n"
    "  wrap.addEventListener('mouseenter', showLabel);\n"
    "  wrap.addEventListener('mouseleave', hideLabel);\n"
    '\n'
    '  function titleFor(a){\n'
    "    var card = a.closest('[data-podcast-card]');\n"
    "    if(card){ var p = card.querySelector('p'); if(p) return p.textContent.trim(); }\n"
    '    var prev = a.previousElementSibling;\n'
    "    while(prev){ if(prev.tagName === 'P') return prev.textContent.trim(); prev = prev.previousElementSibling; }\n"
    "    var src = a.querySelector('source');\n"
    "    if(src){ return (src.getAttribute('src')||'').split('/').pop().replace(/\\.[^.]+$/,'').replace(/_/g,' '); }\n"
    "    return 'Podcast';\n"
    '  }\n'
    '\n'
    '  function render(){\n'
    "    if(!active){ wrap.style.display='none'; return; }\n"
    "    wrap.style.display = 'flex';\n"
    '    var playing = !active.paused && !active.ended;\n'
    '    btn.innerHTML = playing ? PAUSE : PLAY;\n'
    '    label.textContent = titleFor(active);\n'
    '  }\n'
    '\n'
    '  audios.forEach(function(a){\n'
    "    a.addEventListener('play', function(){\n"
    '      audios.forEach(function(o){ if(o !== a) o.pause(); });\n'
    '      active = a; render();\n'
    '      showLabel(); hideT = setTimeout(hideLabel, 2500);\n'
    '    });\n'
    "    a.addEventListener('pause', render);\n"
    "    a.addEventListener('ended', render);\n"
    '  });\n'
    '\n'
    "  btn.addEventListener('click', function(){\n"
    '    if(!active) return;\n'
    '    if(active.paused) active.play(); else active.pause();\n'
    '  });\n'
    '})();\n'
    '</script>\n'
)

for rel, (filename, title) in TARGETS.items():
    path = os.path.join(REPO, rel)
    with open(path, encoding='utf-8') as f:
        html = f.read()

    changed = False
    if CARD_MARKER not in html:
        lead = html.find('<p class="lead">')
        if lead == -1:
            print(f'  WARN no <p class="lead"> in  {rel}')
            continue
        end = html.find('</p>', lead) + len('</p>')
        html = html[:end] + card(filename, title) + html[end:]
        changed = True
    else:
        print(f'  card SKIP (already injected)  {rel}')

    inject = ''
    if 'data-speed-js' not in html:
        inject += SPEED_JS
    if 'data-floating-player' not in html:
        inject += FLOAT_JS
    if inject:
        html = html.replace('</body>', inject + '</body>', 1)
        changed = True

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  OK   {rel}')

print('done')
