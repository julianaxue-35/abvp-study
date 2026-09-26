// usage: node check_page.js page.html ... -> syntax-checks every inline <script> and re-parses the Q bank
const fs=require('fs'),path=require('path'),vm=require('vm');const {grab,root}=require('./extract_banks.js');
let bad=0;
for(const f of process.argv.slice(2)){
  const src=fs.readFileSync(path.join(root,f),'utf8');
  const re=/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g;let m,n=0;
  while((m=re.exec(src))){n++;try{new vm.Script(m[1])}catch(e){bad++;console.log('SYNTAX',f,'script#'+n,e.message)}}
  const b=grab(src).find(x=>x.name==='Q');
  console.log(f,'scripts',n,'Q',b?b.arr.length:'none');
}
process.exit(bad?1:0);
