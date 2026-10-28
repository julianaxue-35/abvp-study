import json,glob,random,sys,os
here=os.path.dirname(os.path.abspath(__file__)); root=os.path.join(here,'..','..')
dump={o['i']:o for o in json.load(open(here+'/fc_dump.json'))}
rw={}
for f in sorted(glob.glob(here+'/b*.py')):
    ns={}; exec(open(f).read(),ns)
    for t in ns['R']: rw[t[0]]=t
p=root+'/mock-data.js'; s=open(p).read(); head=s[:s.index('=')+1]
d=json.loads(s[s.index('=')+1:].rstrip().rstrip(';'))
byq={}
for k,q in enumerate(d['mcqs']):
    if q.get('source')=='fc': byq.setdefault(q['q'],[]).append(k)
drop=set(); n=0
for i,(idx,stem,cor,dis,ex) in rw.items():
    k=byq.get(dump[i]['q'])
    if not k: continue
    k=k[0]
    if stem is None: drop.add(k); continue
    opts=[cor]+list(dis); assert len(dis)==2 and len(set(opts))==3,(i,opts)
    r=random.Random(i); r.shuffle(opts)
    q=d['mcqs'][k]; q['q']=stem; q['o']=opts; q['a']=opts.index(cor); q['e']=ex; q['source']='fcr'; n+=1
d['mcqs']=[q for k,q in enumerate(d['mcqs']) if k not in drop]
open(p,'w').write(head+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n')
print('rewritten',n,'dropped',len(drop),'remaining fc in-exam',sum(1 for q in d['mcqs'] if q.get('source')=='fc' and q['domain']!='General'))
