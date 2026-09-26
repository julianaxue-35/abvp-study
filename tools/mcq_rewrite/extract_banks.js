// Extract `const Q=[...]` (or similar) from each hub page by bracket-scanning + eval.
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'../..');
const skip=/^(docs|cheat-sheets|subdomain-sheets|disease-one-pagers|supplementary|biostats|tools|audio|images)$/;
function grab(src){
  const out=[];
  const re=/(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*\[/g;let m;
  while((m=re.exec(src))){
    let i=m.index+m[0].length-1,d=0,s=i,inStr=null,esc=false,inC=false,inL=false;
    for(;i<src.length;i++){const c=src[i],n=src[i+1];
      if(inL){if(c=='\n')inL=false;continue}
      if(inC){if(c=='*'&&n=='/'){inC=false;i++}continue}
      if(inStr){if(esc)esc=false;else if(c=='\\')esc=true;else if(c==inStr)inStr=null;continue}
      if(c=='/'&&n=='/'){inL=true;continue}if(c=='/'&&n=='*'){inC=true;continue}
      if(c=='"'||c=="'"||c=='`'){inStr=c;continue}
      if(c=='[')d++;else if(c==']'){d--;if(!d){i++;break}}}
    const txt=src.slice(s,i);
    if(!/["']?\bq["']?\s*:/.test(txt.slice(0,3000)))continue;
    try{const arr=vm.runInNewContext('('+txt+')',{});
      if(Array.isArray(arr)&&arr.length&&arr[0]&&('q' in arr[0]))out.push({name:m[1],arr,start:s,end:i})}catch(e){out.push({name:m[1],err:String(e).slice(0,80)})}
  }
  return out;
}
module.exports={grab,root,skip};
if(require.main===module){
  for(const d of fs.readdirSync(root)){
    if(skip.test(d)||!fs.statSync(path.join(root,d)).isDirectory())continue;
    for(const f of fs.readdirSync(path.join(root,d)).filter(x=>x.endsWith('.html')).sort()){
      const src=fs.readFileSync(path.join(root,d,f),'utf8');
      const r=grab(src);
      console.log(d+'/'+f, r.map(x=>x.err?x.name+':ERR '+x.err:x.name+'='+x.arr.length+' keys['+Object.keys(x.arr[0]).join(',')+']').join(' ; ')||'(none)');
    }
  }
}
