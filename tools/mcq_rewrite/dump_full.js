// full dump incl. all options (for pages whose distractors need reviewing): node dump_full.js page [maxExplChars]
const fs=require('fs'),path=require('path');
const arr=JSON.parse(fs.readFileSync(path.join(__dirname,'orig',process.argv[2].replace(/\//g,'__')+'.json'),'utf8'));
const mx=+process.argv[3]||220;
console.log('# '+process.argv[2]+' | '+arr.length);
arr.forEach((q,i)=>console.log(i+'|'+(q.t||'-')+'|'+(q.f||'-')+'|'+q.q+'\n   '+q.o.map((o,k)=>(k===q.a?'*':' ')+'abcd'[k]+') '+o).join('\n   ')+'\n   E: '+q.e.slice(0,mx)));
