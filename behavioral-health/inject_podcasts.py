#!/usr/bin/env python3
"""Idempotent podcast injection for animals-public-policy pages.
Inserts a podcast card after the first <p class="lead">, plus the
data-speed-js and data-floating-player scripts before </body>."""
import os, re, sys

PAGES = [
    ("06_stress.html",                   "audio/stress.m4a",                   "Stress"),
    ("14_training_bmod_playgroups.html", "audio/training_bmod_playgroups.m4a", "Training, B-Mod &amp; Playgroups"),
]

def card(src, title):
    return f'''   <div class="card" data-podcast-card style="border-left:4px solid #0f3d3a;background:#eef3f1;border-radius:8px;padding:14px 16px;margin:16px 0">
     <h4 style="margin:0 0 6px;display:flex;align-items:center;gap:8px;color:#0f3d3a">🎧 NotebookLM Podcast</h4>
     <p style="color:#5d6b62;margin:0 0 8px;font-size:14px">{title}</p>
     <audio controls preload="metadata" style="width:100%">
       <source src="{src}" type="audio/mp4">
     </audio>
     <div data-speed-controls style="margin-top:10px;display:flex;gap:6px;align-items:center;flex-wrap:wrap">
       <span style="font-size:12px;color:#5d6b62;margin-right:2px">Speed</span>
       <button type="button" onclick="setRate(this,1)" style="font:inherit;font-size:12px;padding:3px 10px;border:1px solid #b9cdc6;border-radius:6px;cursor:pointer;background:#0f3d3a;color:#fff">1×</button>
       <button type="button" onclick="setRate(this,1.25)" style="font:inherit;font-size:12px;padding:3px 10px;border:1px solid #b9cdc6;border-radius:6px;cursor:pointer;background:#fff;color:#0f3d3a">1.25×</button>
       <button type="button" onclick="setRate(this,1.5)" style="font:inherit;font-size:12px;padding:3px 10px;border:1px solid #b9cdc6;border-radius:6px;cursor:pointer;background:#fff;color:#0f3d3a">1.5×</button>
       <button type="button" onclick="setRate(this,2)" style="font:inherit;font-size:12px;padding:3px 10px;border:1px solid #b9cdc6;border-radius:6px;cursor:pointer;background:#fff;color:#0f3d3a">2×</button>
     </div>
   </div>
'''

SPEED_JS = '''<script data-speed-js>
function setRate(btn,r){
  var row=btn.parentNode, card=row.parentNode;
  var a=card.querySelector("audio"); if(a){a.playbackRate=r;}
  var b=row.querySelectorAll("button");
  for(var i=0;i<b.length;i++){b[i].style.background="#fff";b[i].style.color="#0f3d3a";}
  btn.style.background="#0f3d3a"; btn.style.color="#fff";
}
</script>
'''

FLOAT_JS = '''<script data-floating-player>
/* Floating podcast control — follows scroll on the left edge so you can
   control the episode while reading the notes. Compact column: skip back 15s,
   play/pause, skip forward 15s. Controls whichever episode is active and
   shows its title. */
(function(){
  var audios = Array.prototype.slice.call(document.querySelectorAll('audio'));
  if(!audios.length) return;
  var active = null;

  var PLAY = '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
  var PAUSE = '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>';
  var ARROW_BACK = '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>';
  var ARROW_FWD = '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 5V1l5 5-5 5V7c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6h2c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8z"/></svg>';

  var wrap = document.createElement('div');
  wrap.id = 'floatPlayer';
  wrap.style.cssText = 'position:fixed;left:0;top:50%;transform:translateY(-50%);z-index:99999;display:none;align-items:center;font-family:inherit';

  var col = document.createElement('div');
  col.style.cssText = 'display:flex;flex-direction:column;flex:0 0 auto;box-shadow:2px 2px 12px rgba(0,0,0,.28);border-radius:0 16px 16px 0;overflow:hidden';

  function mkBtn(html, h, aria){
    var b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('aria-label', aria);
    b.style.cssText = 'width:54px;height:'+h+'px;border:none;background:#0f3d3a;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:1px;padding:0;font-family:inherit;font-size:11px;font-weight:700';
    b.innerHTML = html;
    return b;
  }

  var rew = mkBtn(ARROW_BACK + '<span>15</span>', 32, 'Skip back 15 seconds');
  var btn = mkBtn(PLAY, 50, 'Play or pause podcast');
  var fwd = mkBtn('<span>15</span>' + ARROW_FWD, 32, 'Skip forward 15 seconds');
  btn.style.borderTop = '1px solid rgba(255,255,255,.14)';
  fwd.style.borderTop = '1px solid rgba(255,255,255,.14)';

  col.appendChild(rew);
  col.appendChild(btn);
  col.appendChild(fwd);

  var label = document.createElement('div');
  label.style.cssText = 'max-width:0;overflow:hidden;white-space:nowrap;background:#0f3d3a;color:#fff;font-size:12px;line-height:1.3;border-radius:0 8px 8px 0;transition:max-width .3s ease,padding .3s ease;padding:0;box-shadow:2px 2px 12px rgba(0,0,0,.28);margin-left:-1px';

  wrap.appendChild(col);
  wrap.appendChild(label);
  document.body.appendChild(wrap);

  var hideT;
  function showLabel(){ clearTimeout(hideT); label.style.maxWidth='230px'; label.style.padding='8px 14px 8px 10px'; }
  function hideLabel(){ label.style.maxWidth='0'; label.style.padding='0'; }
  wrap.addEventListener('mouseenter', showLabel);
  wrap.addEventListener('mouseleave', hideLabel);

  function titleFor(a){
    var card = a.closest('[data-podcast-card]');
    if(card){ var p = card.querySelector('p'); if(p) return p.textContent.trim(); }
    var prev = a.previousElementSibling;
    while(prev){ if(prev.tagName === 'P') return prev.textContent.trim(); prev = prev.previousElementSibling; }
    var src = a.querySelector('source');
    if(src){ return (src.getAttribute('src')||'').split('/').pop().replace(/\\.[^.]+$/,'').replace(/_/g,' '); }
    return 'Podcast';
  }

  function render(){
    if(!active){ wrap.style.display='none'; return; }
    wrap.style.display = 'flex';
    var playing = !active.paused && !active.ended;
    btn.innerHTML = playing ? PAUSE : PLAY;
    label.textContent = titleFor(active);
  }

  function skip(sec){
    if(!active) return;
    var d = active.duration;
    var t = active.currentTime + sec;
    if(isFinite(d)) t = Math.min(d, t);
    active.currentTime = Math.max(0, t);
  }

  audios.forEach(function(a){
    a.addEventListener('play', function(){
      audios.forEach(function(o){ if(o !== a) o.pause(); });
      active = a; render();
      showLabel(); hideT = setTimeout(hideLabel, 2500);
    });
    a.addEventListener('pause', render);
    a.addEventListener('ended', render);
  });

  btn.addEventListener('click', function(){
    if(!active) return;
    if(active.paused) active.play(); else active.pause();
  });
  rew.addEventListener('click', function(){ skip(-15); });
  fwd.addEventListener('click', function(){ skip(15); });
})();
</script>
'''

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    for page, src, title in PAGES:
        path = os.path.join(here, page)
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        changed = False
        # 1. card after first <p class="lead">...</p>
        if "data-podcast-card" not in html:
            m = re.search(r'<p class="lead">.*?</p>', html, re.S)
            if not m:
                print(f"  !! {page}: no <p class=\"lead\"> found, SKIPPED card")
            else:
                idx = m.end()
                html = html[:idx] + "\n" + card(src, title) + html[idx:]
                changed = True
        # 2. speed-js + floating-player before </body>
        inject = ""
        if "data-speed-js" not in html:
            inject += SPEED_JS
        if "data-floating-player" not in html:
            inject += FLOAT_JS
        if inject:
            html = html.replace("</body>", inject + "</body>", 1)
            changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(html)
            print(f"  ✓ {page}: injected")
        else:
            print(f"  – {page}: already done, no change")

if __name__ == "__main__":
    main()
