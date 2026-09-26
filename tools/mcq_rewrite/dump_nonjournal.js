const fs=require('fs'),path=require('path');
const arr=JSON.parse(fs.readFileSync(path.join(__dirname,'orig',process.argv[2].replace(/\//g,'__')+'.json'),'utf8'));
const mx=+process.argv[3]||130;let n=0;
arr.forEach((q,i)=>{if(q.t==='journal'||q.f==='journal')return;n++;console.log(i+'|'+(q.t||'-')+'|'+q.q+'\n   '+q.o.map((o,k)=>(k===q.a?'*':' ')+'abcd'[k]+') '+o).join('\n   ')+'\n   E: '+q.e.slice(0,mx))});
console.error('non-journal',n,'of',arr.length);
