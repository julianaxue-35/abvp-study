// prints the ORIGINAL (pre-rewrite) Q bank of a page from orig/ snapshot as JSON
const fs=require('fs'),path=require('path');
const f=path.join(__dirname,'orig',process.argv[2].replace(/\//g,'__')+'.json');
process.stdout.write(fs.readFileSync(f,'utf8'));
