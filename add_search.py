#!/usr/bin/env python3
"""Inject unified cross-tab search into all ABVP subdomain HTML files."""
import os, glob

SEARCH_CSS = """  /* ── page search ── */
  .srch-wrap{position:sticky;top:54px;z-index:15;background:var(--paper2);border-bottom:1px solid var(--line);padding:5px 0}
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
    'placeholder="Search all tabs… e.g. IFA, FeLV, penalty" '
    'autocomplete="off" spellcheck="false">\n'
    '<span id="srchMeta"></span>'
    '<button id="srchClear" title="Clear search">×</button>\n'
    '</div></div></div>\n'
    '<div class="srch-out" id="srchOut" style="display:none">'
    '<div class="wrap"><div id="srchList"></div></div></div>'
)

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

  /* map panel id -> tab label from the tabrow buttons */
  var tabLabels={};
  document.querySelectorAll('.tabrow button[data-p]').forEach(function(b){
    tabLabels[b.getAttribute('data-p')]=b.textContent.replace(/\s+/g,' ').trim();
  });

  /* highlight matching text nodes inside a cloned element */
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

  /* get contextual heading for a matched block */
  function getCtx(el){
    if(el.classList.contains('q')){
      var tag=el.querySelector('.tag');
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
    meta.textContent='';
    clr.style.display='none';
  }

  var timer;
  inp.addEventListener('input',function(){
    clearTimeout(timer);
    timer=setTimeout(function(){
      var q=inp.value.trim();
      if(!q){restore();return;}

      clr.style.display='';
      var re=new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi');

      /* swap: hide main tabs, show results panel */
      if(mainEl)mainEl.style.display='none';
      out.style.display='block';
      list.innerHTML='';

      var total=0;
      panels.forEach(function(panel){
        var label=tabLabels[panel.id]||panel.id;
        var blocks=Array.from(panel.querySelectorAll(
          '.card,.q,.trap,.corrbox,.aubox,.alertbox,.verifybox,.refonly'
        ));
        var matched=[];
        blocks.forEach(function(b){
          re.lastIndex=0;
          if(re.test(b.textContent))matched.push(b);
        });
        if(!matched.length)return;

        /* tab group header */
        var grp=document.createElement('div');grp.className='sr-group';
        var badge=document.createElement('div');badge.className='sr-tab';
        badge.textContent=label;grp.appendChild(badge);

        matched.forEach(function(block){
          var ctx=getCtx(block);
          var item=document.createElement('div');item.className='sr-item';

          if(ctx){
            var ce=document.createElement('div');ce.className='sr-ctx';
            ce.textContent='↳ '+ctx;item.appendChild(ce);
          }

          /* clone block, disable interactive controls, highlight */
          var clone=block.cloneNode(true);
          clone.querySelectorAll('button,input,select').forEach(function(el){
            el.disabled=true;el.style.pointerEvents='none';
          });
          re.lastIndex=0;hlNode(clone,re);
          item.appendChild(clone);
          grp.appendChild(item);
          total++;
        });
        list.appendChild(grp);
      });

      if(!total){
        list.innerHTML='<p class="srch-none">No results for “'
          +q.replace(/</g,'&lt;')+'”</p>';
      }
      meta.textContent=total+' result'+(total!==1?'s':'');
    },220);
  });

  clr.addEventListener('click',function(){
    inp.value='';inp.dispatchEvent(new Event('input'));inp.focus();
  });
})();
</script>"""


def process(path):
    with open(path, encoding='utf-8') as f:
        html = f.read()

    if 'id="srchIn"' in html:
        return 'skip'

    changed = html

    # 1. Inject CSS before </style>
    if '</style>' in changed:
        changed = changed.replace('</style>', SEARCH_CSS + '</style>', 1)

    # 2. Push mcqbar below the new search bar (desktop + mobile)
    changed = changed.replace('top:54px;z-index:10}', 'top:100px;z-index:10}')
    changed = changed.replace('top:50px}.score', 'top:94px}.score')

    # 3. Inject search bar + results div after tabs nav closing tag
    if '</div></div></nav>' in changed:
        changed = changed.replace('</div></div></nav>',
                                  '</div></div></nav>\n' + SEARCH_HTML, 1)

    # 4. Inject JS before </body>
    if '</body>' in changed:
        changed = changed.replace('</body>', SEARCH_JS + '\n</body>')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(changed)
    return 'ok'


base = os.path.expanduser('~/abvp-study')
domains = [
    'animals-public-policy', 'behavioral-health', 'community-public-health',
    'companion-animal-homelessness', 'physical-health', 'shelter-management',
]

ok = skip = err = 0
for d in domains:
    for path in sorted(glob.glob(os.path.join(base, d, '*.html'))):
        result = process(path)
        label = path.split('abvp-study/')[-1]
        if result == 'ok':
            ok += 1
            print(f'  OK   {label}')
        elif result == 'skip':
            skip += 1
            print(f'  --   {label}  (already done)')
        else:
            err += 1
            print(f'  ERR  {label}')

print(f'\nDone: {ok} updated, {skip} skipped, {err} errors')
