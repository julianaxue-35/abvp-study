/* ABVP study hub: shared progress tracker.
   One set of initials follows you across the main page, every subdomain MCQ bank and the mock exam.
   Stored in this browser only (localStorage). Use Backup code to move progress between devices.
   Each question counts once, by your latest answer. Questions are identified by a hash of the stem text,
   so reordering a bank keeps your history; rewording a question starts it afresh. */
(function(root){
  if(root.ABVP) return;
  var K='abvp:prog:v1', LAST='abvpmock:lastInit';
  var ENT={amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' ',ndash:'-',mdash:'-',rsquo:"'",lsquo:"'",ldquo:'"',rdquo:'"'};

  /* ---------- pure helpers (shared with tools/build_qindex.js) ---------- */
  function norm(s){
    return String(s==null?'':s).replace(/<[^>]*>/g,'')
      .replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi,function(m,e){
        if(e.charAt(0)==='#'){var c=e.charAt(1).toLowerCase()==='x'?parseInt(e.slice(2),16):parseInt(e.slice(1),10);return c?String.fromCharCode(c):' ';}
        var v=ENT[e.toLowerCase()];return v===undefined?m:v;})
      .replace(/[‐-―]/g,'-').replace(/[‘’]/g,"'").replace(/[“”]/g,'"').replace(/ /g,' ')
      .replace(/\s+/g,' ').trim().toLowerCase();
  }
  function cyrb53(str){
    var h1=0xdeadbeef,h2=0x41c6ce57,ch;
    for(var i=0;i<str.length;i++){ch=str.charCodeAt(i);h1=Math.imul(h1^ch,2654435761);h2=Math.imul(h2^ch,1597334677);}
    h1=Math.imul(h1^(h1>>>16),2246822507)^Math.imul(h2^(h2>>>13),3266489909);
    h2=Math.imul(h2^(h2>>>16),2246822507)^Math.imul(h1^(h1>>>13),3266489909);
    return (4294967296*(2097151&h2)+(h1>>>0)).toString(36);
  }
  function key(stem){return cyrb53(norm(stem));}

  /* ---------- storage ---------- */
  function load(){try{var s=JSON.parse(localStorage.getItem(K));if(s&&s.u)return s;}catch(e){}return {cur:'',u:{}};}
  function save(s){try{localStorage.setItem(K,JSON.stringify(s));}catch(e){}}
  function cleanInit(v){return String(v||'').toUpperCase().replace(/[^A-Z0-9]/g,'').slice(0,6);}
  function cur(){
    var s=load(); if(s.cur) return s.cur;
    try{var l=cleanInit(localStorage.getItem(LAST)); if(l) return l;}catch(e){}
    return '';
  }
  function setCur(init){
    init=cleanInit(init); if(!init) return '';
    var s=load(); s.cur=init; if(!s.u[init]) s.u[init]={r:{},runs:0}; save(s);
    try{localStorage.setItem(LAST,init);}catch(e){}
    return init;
  }
  function profile(s,init){var p=s.u[init]; if(!p){p=s.u[init]={r:{},runs:0};} if(!p.r)p.r={}; return p;}
  function pagePath(){
    var parts=(location.pathname||'').split('/').filter(Boolean);
    return parts.length>=2?parts.slice(-2).join('/'):(parts[0]||'');
  }
  function idx(){return (root.ABVPIDX&&root.ABVPIDX.pages)||{};}
  var H2P=null;
  function h2p(){
    if(H2P) return H2P; H2P={}; var P=idx();
    for(var p in P){var hs=P[p].h||[];for(var i=0;i<hs.length;i++) if(!H2P[hs[i]]) H2P[hs[i]]=p;}
    return H2P;
  }

  /* record an answer: ok = true/false, meta = {p,d,s} optional */
  function rec(stem,ok,meta){
    var init=cur(); if(!init) return false;
    var s=load(); if(!s.cur){s.cur=init;} var P=profile(s,init), h=key(stem), o=P.r[h];
    meta=meta||{};
    var page=meta.p||h2p()[h]||'';
    var cell=o||{n:0,f:ok?1:0};
    cell.r=ok?1:0; cell.n=(cell.n||0)+1; cell.t=Date.now();
    if(page) cell.p=page; else if(meta.d) {cell.d=meta.d; cell.s=meta.s||'';}
    if(page&&idx()[page]&&idx()[page].d) cell.d=idx()[page].d;
    P.r[h]=cell; save(s); return true;
  }

  /* ---------- stats ---------- */
  function agg(P){
    var out={all:{n:0,ok:0},page:{},dom:{}};
    for(var h in P.r){
      var c=P.r[h]; out.all.n++; out.all.ok+=c.r?1:0;
      if(c.p){var g=out.page[c.p]=out.page[c.p]||{n:0,ok:0};g.n++;g.ok+=c.r?1:0;}
      if(c.d){var d=out.dom[c.d]=out.dom[c.d]||{n:0,ok:0};d.n++;d.ok+=c.r?1:0;}
    }
    return out;
  }
  function stats(){var init=cur(); if(!init) return null; var s=load(); var a=agg(profile(s,init)); a.init=init; return a;}
  function total(page){var p=idx()[page];return p&&p.h?p.h.length:0;}
  function pct(ok,n){return n?Math.round(ok/n*100):0;}
  function clearPage(page){
    var init=cur(); if(!init) return; var s=load(),P=profile(s,init);
    for(var h in P.r) if(P.r[h].p===page) delete P.r[h]; save(s);
  }

  /* ---------- backup ---------- */
  function exportCode(){
    var s=load(), init=cur(), obj={v:1,init:init,r:(s.u[init]||{r:{}}).r};
    try{return btoa(unescape(encodeURIComponent(JSON.stringify(obj))));}catch(e){return '';}
  }
  function importCode(code,initOverride){
    var obj; try{obj=JSON.parse(decodeURIComponent(escape(atob(String(code).replace(/\s+/g,'')))));}catch(e){return -1;}
    if(!obj||!obj.r) return -1;
    var init=cleanInit(initOverride||obj.init||cur()); if(!init) return -1;
    var s=load(),P=profile(s,init),add=0;
    for(var h in obj.r){var a=obj.r[h],b=P.r[h]; if(!b||(a.t||0)>(b.t||0)){P.r[h]=a;add++;}}
    s.cur=init; save(s); try{localStorage.setItem(LAST,init);}catch(e){}
    return add;
  }

  var API={key:key,norm:norm,cur:cur,setCur:setCur,rec:rec,stats:stats,total:total,pct:pct,clearPage:clearPage,
           exportCode:exportCode,importCode:importCode,pagePath:pagePath,listInits:function(){return Object.keys(load().u);},
           load:load,save:save,profile:profile,cleanInit:cleanInit,agg:agg,idx:idx};
  root.ABVP=API;
  if(typeof document==='undefined') return;

  /* ---------- UI ---------- */
  var css='#abvpPill{position:fixed;left:12px;bottom:12px;z-index:99990;font:600 12px/1 system-ui,sans-serif;background:#0f3d3a;color:#fff;border:0;border-radius:999px;padding:9px 13px;box-shadow:0 4px 14px rgba(0,0,0,.25);cursor:pointer}'+
  '#abvpPill.need{background:#b45309;animation:abvpP 1.6s infinite}@keyframes abvpP{50%{transform:scale(1.06)}}'+
  '#abvpPanel,#abvpAsk{position:fixed;inset:0;z-index:99995;background:rgba(0,0,0,.45);display:none;align-items:center;justify-content:center;padding:14px}'+
  '#abvpPanel.show,#abvpAsk.show{display:flex}'+
  '.abvpBox{background:#fff;color:#1c2b27;border-radius:14px;max-width:460px;width:100%;max-height:88vh;overflow:auto;padding:18px;font:14px/1.45 system-ui,sans-serif;box-shadow:0 14px 40px rgba(0,0,0,.35)}'+
  '.abvpBox h3{margin:0 0 6px;font-size:16px;color:#0f3d3a}.abvpBox input[type=text],.abvpBox textarea{width:100%;box-sizing:border-box;font:inherit;padding:8px;border:1px solid #b9cdc6;border-radius:8px}'+
  '.abvpBox button{font:inherit;font-size:13px;padding:7px 12px;border-radius:8px;border:1px solid #0f3d3a;background:#fff;color:#0f3d3a;cursor:pointer;margin:6px 6px 0 0}.abvpBox button.pri{background:#0f3d3a;color:#fff}'+
  '.abvpBox table{width:100%;border-collapse:collapse;font-size:13px}.abvpBox td{padding:3px 4px;border-bottom:1px solid #e3ece9}'+
  '#abvpBar{margin:10px 0;padding:8px 12px;border:1px solid #b9cdc6;background:#f2f8f6;border-radius:10px;font:13px/1.4 system-ui,sans-serif;color:#0f3d3a;display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center}'+
  '#abvpBar button{font:inherit;font-size:12px;padding:3px 9px;border-radius:6px;border:1px solid #0f3d3a;background:#fff;color:#0f3d3a;cursor:pointer}'+
  '#abvpBar .trk{flex:1 1 120px;height:7px;background:#dbe7e3;border-radius:4px;overflow:hidden}#abvpBar .trk i{display:block;height:100%;background:#2f7d52}';
  var st=document.createElement('style'); st.textContent=css; (document.head||document.documentElement).appendChild(st);

  function el(tag,attrs,html){var e=document.createElement(tag);for(var k in (attrs||{}))e.setAttribute(k,attrs[k]);if(html!=null)e.innerHTML=html;return e;}
  var pill,panel,ask,pendingAnswer=null;

  function refreshPill(){
    if(!pill) return; var a=stats();
    if(!a){pill.className='need';pill.id='abvpPill';pill.textContent='Set your initials';return;}
    pill.className='';pill.textContent=a.init+' · '+(a.all.n?pct(a.all.ok,a.all.n)+'% · '+a.all.n+' done':'no answers yet');
  }
  function refreshBar(){
    var bar=document.getElementById('abvpBar'); if(!bar) return;
    var pg=pagePath(), tot=total(pg), a=stats();
    if(!a){bar.innerHTML='<b>Progress tracking is off.</b> <button id="abvpBarSet">Set initials</button>';
      document.getElementById('abvpBarSet').onclick=openAsk;return;}
    var g=a.page[pg]||{n:0,ok:0};
    var denom=tot||document.querySelectorAll('.q').length;
    bar.innerHTML='<b>'+a.init+'</b><span>'+g.n+' / '+denom+' answered in this bank</span><span><b>'+pct(g.ok,g.n)+'%</b> correct (latest answer per question)</span>'+
      '<span class="trk"><i style="width:'+pct(g.n,denom)+'%"></i></span><button id="abvpBarReset">Reset this bank</button>';
    document.getElementById('abvpBarReset').onclick=function(){
      if(confirm('Clear '+a.init+"'s saved answers for this bank only?")){clearPage(pg);refreshAll();}};
  }
  function refreshAll(){refreshPill();refreshBar();if(root.ABVPonChange)try{root.ABVPonChange();}catch(e){}}
  API.refresh=refreshAll;

  function openAsk(then){
    if(!ask){
      ask=el('div',{id:'abvpAsk'},'<div class="abvpBox"><h3>Who is studying?</h3><p style="margin:0 0 8px;font-size:13px">Enter your initials (up to 6 letters). Your answers across every question bank and mock exam are saved under them on this device.</p><input type="text" id="abvpInit" maxlength="6" placeholder="e.g. JX" autocomplete="off" style="text-transform:uppercase"><div id="abvpKnown" style="font-size:12px;margin-top:6px"></div><button class="pri" id="abvpGo">Save</button><button id="abvpNo">Cancel</button></div>');
      document.body.appendChild(ask);
      ask.querySelector('#abvpNo').onclick=function(){ask.classList.remove('show');pendingAnswer=null;};
      var go=function(){var v=setCur(ask.querySelector('#abvpInit').value); if(!v)return; ask.classList.remove('show');
        if(pendingAnswer){rec(pendingAnswer.stem,pendingAnswer.ok,pendingAnswer.meta);pendingAnswer=null;}
        refreshAll(); if(root.ABVPonInit)try{root.ABVPonInit(v);}catch(e){}};
      ask.querySelector('#abvpGo').onclick=go;
      ask.querySelector('#abvpInit').addEventListener('keydown',function(e){if(e.key==='Enter')go();});
    }
    var known=API.listInits(); ask.querySelector('#abvpKnown').innerHTML=known.length?'On this device: '+known.map(function(k){return '<a href="#" data-i="'+k+'">'+k+'</a>';}).join(' · '):'';
    [].forEach.call(ask.querySelectorAll('#abvpKnown a'),function(a){a.onclick=function(e){e.preventDefault();ask.querySelector('#abvpInit').value=a.getAttribute('data-i');};});
    ask.querySelector('#abvpInit').value=cur();
    ask.classList.add('show'); setTimeout(function(){ask.querySelector('#abvpInit').focus();},50);
  }
  API.openAsk=openAsk;

  function openPanel(){
    var a=stats();
    if(!panel){panel=el('div',{id:'abvpPanel'},'<div class="abvpBox" id="abvpPanelBox"></div>');document.body.appendChild(panel);
      panel.addEventListener('click',function(e){if(e.target===panel)panel.classList.remove('show');});}
    var box=panel.querySelector('#abvpPanelBox'), h='<h3>Your progress'+(a?' — '+a.init:'')+'</h3>';
    if(!a) h+='<p>Set your initials to start tracking.</p>';
    else{
      h+='<p style="margin:0 0 8px">'+a.all.n+' questions answered · <b>'+pct(a.all.ok,a.all.n)+'%</b> correct on your latest answer to each.</p><table>';
      var order=['Physical Health','Shelter Management','Behavioral Health','Companion Animal Homelessness','Community & Public Health','Animals & Public Policy','Research & Biostats'];
      Object.keys(a.dom).sort(function(x,y){var i=order.indexOf(x),j=order.indexOf(y);return (i<0?99:i)-(j<0?99:j);}).forEach(function(d){
        var v=a.dom[d];h+='<tr><td>'+d+'</td><td style="text-align:right;white-space:nowrap">'+v.ok+' / '+v.n+' · <b>'+pct(v.ok,v.n)+'%</b></td></tr>';});
      h+='</table>';
    }
    h+='<div style="margin-top:10px"><button class="pri" id="abvpChg">'+(a?'Change initials':'Set initials')+'</button>';
    if(a) h+='<button id="abvpExp">Copy backup code</button><button id="abvpImp">Import backup code</button><button id="abvpRst">Reset all mine</button>';
    h+='<button id="abvpCls">Close</button></div><div id="abvpMsg" style="font-size:12px;margin-top:6px"></div>';
    box.innerHTML=h; panel.classList.add('show');
    box.querySelector('#abvpCls').onclick=function(){panel.classList.remove('show');};
    box.querySelector('#abvpChg').onclick=function(){panel.classList.remove('show');openAsk();};
    if(a){
      var msg=box.querySelector('#abvpMsg');
      box.querySelector('#abvpExp').onclick=function(){var c=exportCode();
        if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(c).then(function(){msg.textContent='Backup code copied. Paste it into "Import backup code" on your other device.';},function(){msg.innerHTML='<textarea rows="4">'+c+'</textarea>';});}
        else msg.innerHTML='<textarea rows="4">'+c+'</textarea>';};
      box.querySelector('#abvpImp').onclick=function(){var c=prompt('Paste your backup code:'); if(!c)return; var n=importCode(c);
        msg.textContent=n<0?'That code could not be read.':'Imported '+n+' answers.'; refreshAll(); if(n>=0)openPanel();};
      box.querySelector('#abvpRst').onclick=function(){if(confirm('Delete ALL saved progress for '+a.init+' on this device?')){var s=load();delete s.u[a.init];s.cur=a.init;save(s);refreshAll();openPanel();}};
    }
  }
  API.openPanel=openPanel;

  /* answer capture for question-bank pages (cards: .q > .stem + .opt buttons) */
  function hookBank(){
    var tag=document.currentScript||document.querySelector('script[src$="progress.js"]');
    document.addEventListener('click',function(e){
      var b=e.target.closest&&e.target.closest('.q .opt'); if(!b) return;
      setTimeout(function(){
        var card=b.closest('.q'); if(!card||card.getAttribute('data-abvp'))return;
        var ok=b.classList.contains('correct'), bad=b.classList.contains('wrong');
        if(!ok&&!bad) return;
        var stem=card.querySelector('.stem'); if(!stem) return;
        card.setAttribute('data-abvp','1');
        var meta={p:pagePath()};
        if(!cur()){pendingAnswer={stem:stem.innerHTML,ok:ok,meta:meta};openAsk();return;}
        rec(stem.innerHTML,ok,meta); refreshAll();
      },0);
    },false);
    var q=document.querySelector('#qhost')||document.querySelector('.q'); if(!q) return;
    var bar=el('div',{id:'abvpBar'}); var anchor=document.getElementById('qhost');
    if(anchor) anchor.parentNode.insertBefore(bar,anchor); else q.parentNode.insertBefore(bar,q);
  }

  function init(){
    pill=el('button',{id:'abvpPill',type:'button','aria-label':'Progress'}); pill.onclick=openPanel; document.body.appendChild(pill);
    var hook=false; var scr=document.querySelectorAll('script[src*="progress.js"]');
    for(var i=0;i<scr.length;i++) if(scr[i].hasAttribute('data-hook')) hook=true;
    if(hook) hookBank();
    refreshAll();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})(typeof window!=='undefined'?window:this);
