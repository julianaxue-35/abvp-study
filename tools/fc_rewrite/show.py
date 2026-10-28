import json,sys
a,b=int(sys.argv[1]),int(sys.argv[2])
for o in json.load(open('fc_dump.json')):
    if a<=o['i']<b: print(o['i'],'|',o['q'],'=>',o['ans'][:160])
