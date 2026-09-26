// usage: node dump_bank.js <relative/page.html>  -> numbered dump of the ORIGINAL hub `Q` bank
const fs=require('fs'),path=require('path');
const arr=JSON.parse(fs.readFileSync(path.join(__dirname,'orig',process.argv[2].replace(/\//g,'__')+'.json'),'utf8'));
const tags={};arr.forEach(q=>tags[q.t||'-']=(tags[q.t||'-']||0)+1);
console.log('# '+process.argv[2]+' | '+arr.length+' items | tags '+JSON.stringify(tags));
arr.forEach((q,i)=>console.log(i+'|'+(q.t||'-')+'|'+(q.f||'-')+'|'+q.q+' ->'+q.o[q.a]+' || '+q.e));
