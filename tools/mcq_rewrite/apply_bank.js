// usage: node apply_bank.js <relative/page.html> <items.json> [--dry]
// items.json = [{t,f,q,o,a,e}, ...]  -> replaces the page's `const Q=[...]` array in place (same one-object-per-line style),
// then syncs mock-data.js (removes old hub entries of this page, adds new ones under the same domain/sub).
const fs=require('fs'),path=require('path'),vm=require('vm');const {grab,root}=require('./extract_banks.js');
const [,, page, itemsFile, ...flags]=process.argv;const dry=flags.includes('--dry');const exclusive=flags.includes('--exclusive');const subFlag=(flags.find(f=>f.startsWith('--sub='))||'').slice(6);
const items=JSON.parse(fs.readFileSync(itemsFile,'utf8'));
for(const [i,q] of items.entries()){
  if(!q.q||!Array.isArray(q.o)||(q.o.length<3||q.o.length>4)||!(q.a>=0&&q.a<q.o.length)||!q.e)throw new Error('bad item '+i+': '+JSON.stringify(q).slice(0,120));
}
const pp=path.join(root,page);let src=fs.readFileSync(pp,'utf8');
const b=grab(src).find(x=>x.name==='Q');
const old=JSON.parse(fs.readFileSync(path.join(__dirname,'orig',page.replace(/\//g,'__')+'.json'),'utf8'));
const line=q=>' '+JSON.stringify(q);
const arrTxt='[\n'+items.map(line).join(',\n')+'\n]';
let out=src.slice(0,b.start)+arrTxt+src.slice(b.end);
// keep human-readable counts in sync ("holds 44 items", "30 exam-style questions", "44 questions")
const cre=new RegExp('\\b'+old.length+'(\\s+(?:exam-style\\s+)?(?:items|questions|MCQs))','g');
const headEnd=b.start;// only touch text before the bank literal
out=out.slice(0,headEnd).replace(cre,items.length+'$1')+out.slice(headEnd).replace(cre,items.length+'$1');
// refresh the static "All N" / "All (N)" chip count = hub bank + journal bank (JJ) if present
{const g=grab(out);const jj=g.find(x=>x.name==='JJ');const total=items.length+(jj?jj.arr.length:0);
 out=out.replace(/(data-f="all"[^>]*>All(?: \(| ))\d+(\)?)/,'$1'+total+'$2');}
// mock-data.js sync
const mp=path.join(root,'mock-data.js');const msrc=fs.readFileSync(mp,'utf8');
const ctx={window:{}};vm.runInNewContext(msrc,ctx);const M=ctx.window.MOCK;
const oldText=new Set(old.map(q=>q.q).concat(b.arr.map(q=>q.q)));
const hits=M.mcqs.filter(q=>q.source==='hub'&&oldText.has(q.q));
const subs={};hits.forEach(q=>{const k=q.domain+'|'+q.sub;subs[k]=(subs[k]||0)+1});
console.log(page,'old',old.length,'new',items.length,'mock hub matched',hits.length,JSON.stringify(subs));
if(dry)process.exit(0);
if(!hits.length&&!subFlag){console.error('WARNING: no mock-data match and no --sub=; mock-data.js not changed')}
fs.writeFileSync(pp,out);
if(hits.length||subFlag){
  // domain/sub for a new item: majority sub of the page (pages map to one sub in mock-data, except spay-neuter etc.)
  const top=(subFlag||Object.entries(subs).sort((a,b)=>b[1]-a[1])[0][0]).split('|');
  const keep=M.mcqs.filter(q=>!(q.source==='hub'&&oldText.has(q.q)));
  // insert at position of first removed item to keep grouping
  let firstIdx=M.mcqs.findIndex(q=>q.source==='hub'&&oldText.has(q.q));
  if(firstIdx<0){let last=-1;M.mcqs.forEach((q,i)=>{if(q.source==='hub'&&q.domain===top[0]&&q.sub===top[1])last=i});firstIdx=last+1||M.mcqs.length;}
  const before=M.mcqs.slice(0,firstIdx).filter(q=>!(q.source==='hub'&&oldText.has(q.q)));
  const after=M.mcqs.slice(firstIdx).filter(q=>!(q.source==='hub'&&oldText.has(q.q)));
  const have=new Set(M.mcqs.filter(q=>q.source==='hub'&&q.domain===top[0]&&q.sub===top[1]&&!oldText.has(q.q)).map(q=>q.q));
  const neu=items.filter(q=>!have.has(q.q)&&q.t!=='journal'&&q.f!=='journal').map(q=>({type:'mcq',domain:top[0],sub:top[1],q:q.q,o:q.o,a:q.a,e:q.e,source:'hub'}));
  M.mcqs=before.concat(neu,after);
  if(exclusive){const nt=new Set(items.map(q=>q.q));M.mcqs=M.mcqs.filter(q=>!(q.source==='hub'&&q.domain===top[0]&&q.sub===top[1]&&!nt.has(q.q)));}
  const m=/^window\.MOCK=/.exec(msrc);
  fs.writeFileSync(mp,'window.MOCK='+JSON.stringify(M)+';');
}
