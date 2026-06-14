#!/usr/bin/env python3
"""Copy, inject back-nav + search into the 2 research-biostats files, update index.html."""
import os, shutil, re

DROPBOX = os.path.expanduser(
    "~/Library/CloudStorage/Dropbox/work docs/protocols in interactive dashboards/ABVP exam hub/epidemiology and biostats"
)
REPO    = os.path.expanduser("~/abvp-study")
DEST    = os.path.join(REPO, "research-biostats")

FILES = [
    ("epidemiology_biostats_hub.html", "Epidemiology and Biostats"),
    ("study_design_hub.html",          "Study Design"),
]

# Research domain colour: #8A3A52 (dark rose)
def back_nav(page_title):
    return (
        '<nav style="background:#6b2a3c;padding:9px 18px;display:flex;align-items:center;'
        'gap:10px;font-family:\'Public Sans\',system-ui,sans-serif;font-size:13px;'
        'font-weight:500;border-bottom:2px solid #8A3A52">'
        '<a href="../index.html" style="color:#e8b0c4;text-decoration:none;'
        'display:flex;align-items:center;gap:5px">'
        '<svg width="15" height="15" viewBox="0 0 15 15" fill="none">'
        '<path d="M9.5 11.5L5.5 7.5l4-4" stroke="currentColor" stroke-width="1.5" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>'
        'Study Hub</a>'
        '<span style="color:#7a3048;font-size:11px">›</span>'
        '<a href="../index.html#domain-research" style="color:#e8b0c4;text-decoration:none">'
        'Research and Biostats</a>'
        '<span style="color:#7a3048;font-size:11px">›</span>'
        f'<span style="color:#f5d8e4">{page_title}</span>'
        '</nav>'
    )

SEARCH_CSS = """  /* ── page search ── */
  .srch-wrap{position:sticky;top:54px;z-index:15;background:var(--surface,var(--paper2,#f5f5f5));border-bottom:1px solid var(--line);padding:5px 0}
  .srch-row{display:flex;align-items:center;gap:8px;background:#fff;border:1.5px solid var(--line);border-radius:10px;padding:5px 11px;transition:border-color .15s}
  .srch-row:focus-within{border-color:var(--ink)}
  .srch-row svg{flex-shrink:0;opacity:.45}
  .srch-row input{flex:1;border:none;outline:none;font-family:"Public Sans",system-ui,sans-serif;font-size:13.5px;color:var(--ink);background:transparent;min-width:0}
  .srch-row input::placeholder{color:var(--muted);opacity:.7;font-size:13px}
  #srchMeta{font-family:"JetBrains Mono",monospace;font-size:11px;color:var(--muted);white-space:nowrap;padding-right:4px}
  #srchClear{border:none;background:none;cursor:pointer;color:var(--muted);font-size:15px;padding:0 2px;line-height:1;display:none;flex-shrink:0}
  .srch-out{padding:20px 0 60px}
  .sr-group{margin-bottom:32px}
  .sr-tab{font-family:"JetBrains Mono",monospace;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:#fff;background:var(--ink);border-radius:999px;padding:4px 11px;display:inline-block;margin-bottom:10px}
  .sr-ctx{font-size:12px;color:var(--muted);font-style:italic;margin:-2px 0 6px 2px}
  .sr-item{margin:10px 0}
  mark.sh{background:#fff176;color:inherit;border-radius:2px;padding:0 1px}
  .srch-none{color:var(--muted);font-size:14px;padding:24px 0;font-style:italic}
"""

SEARCH_HTML = (
    '<div class="srch-wrap"><div class="wrap"><div class="srch-row">\n'
    '<svg width="14" height="14" viewBox="0 0 15 15" fill="none">'
    '<circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" stroke-width="1.5"/>'
    '<path d="m10.5 10.5 3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
    '</svg>\n'
    '<input type="text" id="srchIn" '
    'placeholder="Search all tabs… e.g. incidence, sensitivity, bias" '
    'autocomplete="off" spellcheck="false">\n'
    '<span id="srchMeta"></span>'
    '<button id="srchClear" title="Clear search">×</button>\n'
    '</div></div></div>\n'
    '<div class="srch-out" id="srchOut" style="display:none">'
    '<div class="wrap"><div id="srchList"></div></div></div>'
)

# Adapted JS: uses data-tab (not data-p), includes .box in content selectors
SEARCH_JS = r"""<script>
(function(){
  var inp=document.getElementById('srchIn');
  if(!inp)return;
  var meta=document.getElementById('srchMeta'),
      clr=document.getElementById('srchClear'),
      out=document.getElementById('srchOut'),
      list=document.getElementById('srchList'),
      mainEl=document.querySelector('main'),
      panels=Array.from(document.querySelectorAll('.panel'));

  var tabLabels={};
  document.querySelectorAll('button.tab[data-tab]').forEach(function(b){
    tabLabels[b.getAttribute('data-tab')]=b.textContent.replace(/\s+/g,' ').trim();
  });

  function hlNode(root,re){
    var walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null);
    var nodes=[],node;
    while((node=walker.nextNode()))nodes.push(node);
    nodes.forEach(function(t){
      var p=t.parentElement;
      if(!p||/^(SCRIPT|STYLE|INPUT|TEXTAREA|BUTTON)$/.test(p.tagName))return;
      re.lastIndex=0;if(!re.test(t.textContent))return;re.lastIndex=0;
      var f=document.createDocumentFragment(),last=0,m,txt=t.textContent;
      while((m=re.exec(txt))!==null){
        if(m.index>last)f.appendChild(document.createTextNode(txt.slice(last,m.index)));
        var mk=document.createElement('mark');mk.className='sh';mk.textContent=m[0];f.appendChild(mk);
        last=m.index+m[0].length;
      }
      if(last<txt.length)f.appendChild(document.createTextNode(txt.slice(last)));
      t.parentNode.replaceChild(f,t);
    });
  }

  function getCtx(el){
    if(el.classList.contains('q')){
      var tag=el.querySelector('.tag,.lbl');
      return tag?'MCQ — '+tag.textContent.trim():null;
    }
    var prev=el.previousElementSibling;
    while(prev){
      if(/^H[2-4]$/.test(prev.tagName))return prev.textContent.replace(/\s+/g,' ').trim();
      prev=prev.previousElementSibling;
    }
    return null;
  }

  function restore(){
    if(out)out.style.display='none';
    if(mainEl)mainEl.style.display='';
    meta.textContent='';clr.style.display='none';
  }

  var timer;
  inp.addEventListener('input',function(){
    clearTimeout(timer);
    timer=setTimeout(function(){
      var q=inp.value.trim();
      if(!q){restore();return;}
      clr.style.display='';
      var re=new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi');
      if(mainEl)mainEl.style.display='none';
      out.style.display='block';
      list.innerHTML='';
      var total=0;
      panels.forEach(function(panel){
        var label=tabLabels[panel.id]||panel.id;
        var blocks=Array.from(panel.querySelectorAll('.card,.q,.box,.trap,.corrbox,.aubox,.alertbox,.verifybox,.refonly'));
        var matched=[];
        blocks.forEach(function(b){re.lastIndex=0;if(re.test(b.textContent))matched.push(b);});
        if(!matched.length)return;
        var grp=document.createElement('div');grp.className='sr-group';
        var badge=document.createElement('div');badge.className='sr-tab';badge.textContent=label;grp.appendChild(badge);
        matched.forEach(function(block){
          var ctx=getCtx(block);
          var item=document.createElement('div');item.className='sr-item';
          if(ctx){var ce=document.createElement('div');ce.className='sr-ctx';ce.textContent='↳ '+ctx;item.appendChild(ce);}
          var clone=block.cloneNode(true);
          clone.querySelectorAll('button,input,select').forEach(function(el){el.disabled=true;el.style.pointerEvents='none';});
          re.lastIndex=0;hlNode(clone,re);
          item.appendChild(clone);grp.appendChild(item);total++;
        });
        list.appendChild(grp);
      });
      if(!total)list.innerHTML='<p class="srch-none">No results for "'+q.replace(/</g,'&lt;')+'"</p>';
      meta.textContent=total+' result'+(total!==1?'s':'');
    },220);
  });
  clr.addEventListener('click',function(){inp.value='';inp.dispatchEvent(new Event('input'));inp.focus();});
})();
</script>"""


def process_file(src_path, dest_path, page_title):
    with open(src_path, encoding='utf-8') as f:
        html = f.read()

    # 1. Back-nav before <header>
    html = html.replace('<header>', back_nav(page_title) + '\n<header>', 1)

    # 2. CSS before </style>
    html = html.replace('</style>', SEARCH_CSS + '</style>', 1)

    # 3. Search bar after tabs nav close (  </div>\n</nav>)
    html = html.replace('  </div>\n</nav>', '  </div>\n</nav>\n' + SEARCH_HTML, 1)

    # 4. JS before </body>
    html = html.replace('</body>', SEARCH_JS + '\n</body>')

    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK   research-biostats/{os.path.basename(dest_path)}')


def update_index():
    index_path = os.path.join(REPO, 'index.html')
    with open(index_path, encoding='utf-8') as f:
        html = f.read()

    html = html.replace(
        '{name:"Epidemiology and Biostats",w:54}',
        '{name:"Epidemiology and Biostats",w:54,emoji:"📈",url:"research-biostats/epidemiology_biostats_hub.html"}'
    )
    html = html.replace(
        '{name:"Study Design",w:46}',
        '{name:"Study Design",w:46,emoji:"🔬",url:"research-biostats/study_design_hub.html"}'
    )

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('  OK   index.html (research urls added)')


# --- run ---
os.makedirs(DEST, exist_ok=True)
for filename, title in FILES:
    src  = os.path.join(DROPBOX, filename)
    dest = os.path.join(DEST, filename)
    process_file(src, dest, title)

update_index()
print('\nDone.')
