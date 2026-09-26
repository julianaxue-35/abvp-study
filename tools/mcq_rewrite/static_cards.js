// Parse / regenerate static-HTML MCQ cards (<div class="q" data-tag=...>).
const CARD=/<div class="q"([^>]*)>\n([\s\S]*?)\n[ \t]*<\/div>/g;
const OPT=/<button class="opt" onclick="ans\(this,(true|false)\)"><span class="k">[A-Z]<\/span>([\s\S]*?)<\/button>/g;
const strip=s=>s.replace(/<[^>]+>/g,'').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/\s+/g,' ').trim();
function parse(src){
  const out=[];let m;CARD.lastIndex=0;
  while((m=CARD.exec(src))){
    const attrs=m[1],body=m[2];
    const tag=(/data-tag="([^"]*)"/.exec(attrs)||[])[1]||'';
    const label=(/<span class="tag">([\s\S]*?)<\/span>/.exec(body)||[])[1]||'';
    const stem=(/<p class="stem">([\s\S]*?)<\/p>/.exec(body)||[])[1]||'';
    const expl=(/<div class="expl">([\s\S]*?)<\/div>/.exec(body)||[])[1]||'';
    const opts=[];let a=-1,om;OPT.lastIndex=0;
    while((om=OPT.exec(body))){if(om[1]==='true')a=opts.length;opts.push(strip(om[2]))}
    out.push({start:m.index,end:m.index+m[0].length,t:tag,f:strip(label),q:strip(stem),o:opts,a,e:strip(expl).replace(/^[A-Z] is correct\.\s*/,''),raw:m[0]});
  }
  return out;
}
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
function render(items,i){
  const K='ABCD';
  return `  <!-- Q${i+1} -->\n  <div class="q" data-tag="${items.t}">\n    <div class="meta"><span class="num">Q${i+1}</span><span class="tag">${esc(items.f||items.t)}</span></div>\n    <p class="stem">${esc(items.q)}</p>\n`+
    items.o.map((o,k)=>`    <button class="opt" onclick="ans(this,${k===items.a})"><span class="k">${K[k]}</span>${esc(o)}</button>`).join('\n')+
    `\n    <div class="expl"><b class="cor">${K[items.a]} is correct.</b> ${esc(items.e)}</div>\n  </div>`;
}
module.exports={parse,render,strip};
