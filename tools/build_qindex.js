// usage: node tools/build_qindex.js  -> writes qindex.js (per-page question hashes + domain) for progress.js
// Re-run after adding/rewording questions so the main page shows correct totals.
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.join(__dirname,'..');
const {grab}=require(path.join(__dirname,'mcq_rewrite','extract_banks.js'));
const sc=require(path.join(__dirname,'mcq_rewrite','static_cards.js'));
const ctx={window:{}};vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(root,'progress.js'),'utf8'),ctx);
const key=ctx.window.ABVP.key;
// mock-data: stem hash -> domain, used to label each page with its exam domain
const mctx={window:{}};vm.createContext(mctx);vm.runInContext(fs.readFileSync(path.join(root,'mock-data.js'),'utf8'),mctx);
const h2d={};for(const q of mctx.window.MOCK.mcqs){if(q.q&&q.domain)h2d[key(q.q)]=q.domain;}
const FD={'physical-health':'Physical Health','shelter-management':'Shelter Management','behavioral-health':'Behavioral Health','companion-animal-homelessness':'Companion Animal Homelessness','community-public-health':'Community & Public Health','animals-public-policy':'Animals & Public Policy','research-biostats':'Research & Biostats'};
const out={};
const dirs=fs.readdirSync(root).filter(d=>fs.statSync(path.join(root,d)).isDirectory()&&!/^(\.|node_modules|tools|audio|subdomain-sheets|summary)/.test(d));
for(const d of dirs){
  for(const f of fs.readdirSync(path.join(root,d)).filter(x=>x.endsWith('.html'))){
    const rel=d+'/'+f, src=fs.readFileSync(path.join(root,rel),'utf8');
    let stems=[];
    const b=grab(src).find(x=>x.name==='Q');
    if(b&&b.arr.length) stems=b.arr.map(x=>x.q); else stems=sc.parse(src).map(x=>x.q);
    if(!stems.length) continue;
    const hs=[...new Set(stems.map(key))];
    const vote={};hs.forEach(h=>{const dm=h2d[h];if(dm)vote[dm]=(vote[dm]||0)+1;});
    const dom=Object.keys(vote).sort((a,b)=>vote[b]-vote[a])[0]||FD[d]||'';
    out[rel]={d:dom,h:hs};
  }
}
// Journal questions outside the mock exam's "JSMCAH + Diplomate studies (2021-2025)" subset do not count toward the
// running average (progress.js agg() skips these stem hashes). jset is set by tools/build_mock_journal.py.
const jctx={window:{MOCK:{mcqs:[]}}};vm.createContext(jctx);vm.runInContext(fs.readFileSync(path.join(root,'mock-data-journal.js'),'utf8'),jctx);
const xs=new Set(),keep=new Set();
for(const q of jctx.window.MOCK.mcqs){ if(q.source!=='journal'||!q.q) continue; (q.jset?keep:xs).add(key(q.q)); }
const cat=JSON.parse(fs.readFileSync(path.join(__dirname,'journal-catalog.json'),'utf8'));
// catalog stems for out-of-focus articles too (covers questions held back from the mock pool, e.g. 2026 articles)
const focusStems=new Set(keep);
for(const a of cat) for(const m of (a.mcqs||[])) if(m&&m.q&&!focusStems.has(key(m.q))) xs.add(key(m.q));
keep.forEach(h=>xs.delete(h));
fs.writeFileSync(path.join(root,'qindex.js'),'window.ABVPIDX={pages:'+JSON.stringify(out)+',x:'+JSON.stringify([...xs])+'};\n');
console.log('journal subset questions counting toward average:',keep.size,'| journal questions excluded from average:',xs.size);
const n=Object.values(out).reduce((a,v)=>a+v.h.length,0);
console.log('pages',Object.keys(out).length,'questions',n);
for(const [p,v] of Object.entries(out)) if(!v.d) console.log('no domain:',p,v.h.length);
