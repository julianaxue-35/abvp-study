import json,sys
d=json.load(open(f"banks/{sys.argv[1]}.json"));th=int(sys.argv[2]) if len(sys.argv)>2 else 20
for n,i in enumerate(d,1):
    ok=len(i["o"][i["a"]]); w=[len(o) for k,o in enumerate(i["o"]) if k!=i["a"]]
    if ok-max(w)>th:
        print(n,"|",i["q"][:80])
        for k,o in enumerate(i["o"]): print("   ","*" if k==i["a"] else " ",o)
