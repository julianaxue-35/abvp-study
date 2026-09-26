import json, importlib.util, pathlib
PAGE = "physical-health/infectious_disease_hub.html"
H = pathlib.Path(__file__).parent
MP = {int(k): v for k, v in json.load(open(H.parent / "id_dump_to_page.json")).items()}

def _load(name):
    spec = importlib.util.spec_from_file_location(name, H / (name + ".py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def M(idxs):
    return [MP[i] for i in idxs if i in MP]

ITEMS = []
# 1) the approved pilot (indices there are mock-dump indices)
_pilot = importlib.util.spec_from_file_location("pilot", H.parent / "pilot_infectious_disease.py")
_p = importlib.util.module_from_spec(_pilot); _pilot.loader.exec_module(_p)
for topic, reps, stem, ok, w1, w2, expl in _p.ITEMS:
    r = M(reps)
    ITEMS.append((r, stem, ok, w1, w2, expl) if r else (r, stem, ok, w1, w2, expl, "intro"))
# 2) expansion
for part in ("id_part_canine", "id_part_feline"):
    for it in _load(part).ITEMS:
        r = M(it[0]); rest = tuple(it[1:])
        if not r and len(rest) < 6: r = [0]
        ITEMS.append((r,) + rest)
